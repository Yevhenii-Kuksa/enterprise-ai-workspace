import logging
import uuid

from app.main import app
from fastapi.testclient import TestClient


@app.get("/test-observability-error")
def raise_observability_error() -> None:
    raise RuntimeError("Synthetic observability test error.")


def test_response_contains_trace_headers() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    trace_id = uuid.UUID(response.headers["X-Trace-ID"])
    request_id = uuid.UUID(response.headers["X-Request-ID"])

    assert trace_id != request_id


def test_existing_trace_id_is_propagated() -> None:
    client = TestClient(app)
    trace_id = uuid.uuid4()

    response = client.get(
        "/health",
        headers={
            "X-Trace-ID": str(trace_id),
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == str(trace_id)

    request_id = uuid.UUID(response.headers["X-Request-ID"])

    assert request_id != trace_id


def test_each_request_gets_unique_request_id() -> None:
    client = TestClient(app)
    trace_id = uuid.uuid4()

    first_response = client.get(
        "/health",
        headers={
            "X-Trace-ID": str(trace_id),
        },
    )
    second_response = client.get(
        "/health",
        headers={
            "X-Trace-ID": str(trace_id),
        },
    )

    assert (
        first_response.headers["X-Trace-ID"]
        == second_response.headers["X-Trace-ID"]
        == str(trace_id)
    )
    assert (
        first_response.headers["X-Request-ID"]
        != second_response.headers["X-Request-ID"]
    )


def test_completed_request_emits_correlated_log(
    caplog,
) -> None:
    client = TestClient(app)
    trace_id = uuid.uuid4()

    application_logger = logging.getLogger(
        "enterprise_ai_workspace"
    )

    application_logger.addHandler(
        caplog.handler
    )

    try:
        with caplog.at_level(
            "INFO",
            logger="enterprise_ai_workspace.http",
        ):
            response = client.get(
                "/health",
                headers={
                    "X-Trace-ID": str(trace_id),
                },
            )
    finally:
        application_logger.removeHandler(
            caplog.handler
        )

    assert response.status_code == 200

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "http_request_completed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_id)
    assert record.request_id == response.headers["X-Request-ID"]
    assert record.action_id is None
    assert record.method == "GET"
    assert record.path == "/health"
    assert record.status_code == 200
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0


def test_failed_request_emits_correlated_error_log(
    caplog,
) -> None:
    client = TestClient(app)
    trace_id = uuid.uuid4()

    application_logger = logging.getLogger(
        "enterprise_ai_workspace"
    )

    application_logger.addHandler(
        caplog.handler
    )

    try:
        with caplog.at_level(
            "ERROR",
            logger="enterprise_ai_workspace.http",
        ):
            try:
                client.get(
                    "/test-observability-error",
                    headers={
                        "X-Trace-ID": str(trace_id),
                    },
                )
            except RuntimeError:
                pass
    finally:
        application_logger.removeHandler(
            caplog.handler
        )

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "http_request_failed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_id)
    assert record.action_id is None
    assert record.method == "GET"
    assert record.path == "/test-observability-error"
    assert record.error_type == "RuntimeError"
    assert record.error_category == "internal"
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0