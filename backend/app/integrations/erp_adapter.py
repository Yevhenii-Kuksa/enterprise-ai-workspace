from datetime import UTC, datetime
from typing import Any

from app.integrations.schemas import IntegrationRecord


class ErpRecordAdapter:
    @staticmethod
    def from_record(
        *,
        source_system: str,
        record_type: str,
        external_id: str,
        payload: dict[str, Any],
        occurred_at: datetime | None = None,
    ) -> IntegrationRecord:
        return IntegrationRecord(
            source_system=source_system,
            external_id=external_id,
            record_type=record_type,
            payload=payload,
            occurred_at=occurred_at,
            fetched_at=datetime.now(UTC),
        )