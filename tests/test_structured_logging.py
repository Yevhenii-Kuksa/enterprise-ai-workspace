import json
import logging

from app.core.structured_logging import JsonFormatter


def test_json_formatter_outputs_structured_log() -> None:
    record = logging.LogRecord(
        name="enterprise_ai_workspace",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Request completed.",
        args=(),
        exc_info=None,
    )

    record.trace_id = "trace-123"
    record.request_id = "request-456"
    record.action_id = None
    record.event_type = "http_request_completed"

    formatter = JsonFormatter()

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "enterprise_ai_workspace"
    assert payload["message"] == "Request completed."
    assert payload["trace_id"] == "trace-123"
    assert payload["request_id"] == "request-456"
    assert payload["action_id"] is None
    assert payload["event_type"] == "http_request_completed"
    assert "timestamp" in payload


def test_json_formatter_handles_missing_trace_metadata() -> None:
    record = logging.LogRecord(
        name="enterprise_ai_workspace",
        level=logging.WARNING,
        pathname=__file__,
        lineno=20,
        msg="Standalone event.",
        args=(),
        exc_info=None,
    )

    formatter = JsonFormatter()

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "WARNING"
    assert payload["message"] == "Standalone event."
    assert payload["trace_id"] is None
    assert payload["request_id"] is None
    assert payload["action_id"] is None
    assert payload["event_type"] is None

def test_json_formatter_includes_safe_telemetry_fields() -> None:
    record = logging.LogRecord(
        name="enterprise_ai_workspace.ai",
        level=logging.INFO,
        pathname=__file__,
        lineno=30,
        msg="AI generation completed.",
        args=(),
        exc_info=None,
    )

    record.event_type = "ai_generation_completed"
    record.trace_id = "trace-123"
    record.request_id = "request-456"
    record.action_id = None

    record.model_name = "fake-answer-model"
    record.evidence_count = 3
    record.citation_count = 2
    record.invalid_citation_count = 0
    record.reliability_decision = "allow"
    record.duration_ms = 42.5

    formatter = JsonFormatter()

    payload = json.loads(formatter.format(record))

    assert payload["model_name"] == "fake-answer-model"
    assert payload["evidence_count"] == 3
    assert payload["citation_count"] == 2
    assert payload["invalid_citation_count"] == 0
    assert payload["reliability_decision"] == "allow"
    assert payload["duration_ms"] == 42.5