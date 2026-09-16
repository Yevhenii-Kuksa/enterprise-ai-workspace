import json
import logging
from datetime import UTC, datetime


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

        return json.dumps(
            payload,
            ensure_ascii=False,
        )