import uuid

from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.core.trace_middleware import TraceContextMiddleware
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

trace_app = FastAPI()
trace_app.add_middleware(TraceContextMiddleware)

trace_context_dependency = Depends(get_trace_context)


@trace_app.get("/trace")
def read_trace_context(
    trace_context: TraceContext = trace_context_dependency,
) -> dict[str, str | None]:
    return {
        "trace_id": str(trace_context.trace_id),
        "request_id": str(trace_context.request_id),
        "action_id": (
            str(trace_context.action_id)
            if trace_context.action_id is not None
            else None
        ),
    }


def test_trace_dependency_returns_request_context() -> None:
    client = TestClient(trace_app)
    trace_id = uuid.uuid4()

    response = client.get(
        "/trace",
        headers={
            "X-Trace-ID": str(trace_id),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["trace_id"] == str(trace_id)
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["action_id"] is None