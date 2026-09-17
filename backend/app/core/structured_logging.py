import json
import logging
from datetime import UTC, datetime

TELEMETRY_FIELDS = (
    "method",
    "path",
    "status_code",
    "error_type",
    "duration_ms",
    "organization_id",
    "user_id",
    "embedding_model",
    "requested_limit",
    "evidence_count",
    "best_distance",
    "model_name",
    "citation_count",
    "invalid_citation_count",
    "reliability_decision",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "request_id": getattr(record, "request_id", None),
            "action_id": getattr(record, "action_id", None),
            "event_type": getattr(record, "event_type", None),
        }

        for field_name in TELEMETRY_FIELDS:
            if hasattr(record, field_name):
                payload[field_name] = getattr(record, field_name)

        return json.dumps(
            payload,
            ensure_ascii=False,
        )