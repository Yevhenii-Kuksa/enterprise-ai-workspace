from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationKind,
    IntegrationRecord,
    IntegrationStatus,
)


class IntegrationSummaryResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    kind: IntegrationKind
    provider: str
    capabilities: tuple[IntegrationCapability, ...]
    enabled: bool
    status: IntegrationStatus


class IntegrationRecordResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_system: str
    external_id: str
    record_type: str
    payload: dict[str, Any]
    source_url: str | None
    occurred_at: datetime | None
    fetched_at: datetime

    @classmethod
    def from_record(
        cls,
        record: IntegrationRecord,
    ) -> "IntegrationRecordResponse":
        return cls(
            source_system=record.source_system,
            external_id=record.external_id,
            record_type=record.record_type,
            payload=record.payload,
            source_url=record.source_url,
            occurred_at=record.occurred_at,
            fetched_at=record.fetched_at,
        )