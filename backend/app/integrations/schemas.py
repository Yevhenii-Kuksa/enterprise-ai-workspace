from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IntegrationKind(StrEnum):
    EMAIL = "email"
    FILE_STORAGE = "file_storage"
    CALENDAR = "calendar"
    ERP = "erp"


class IntegrationStatus(StrEnum):
    DISABLED = "disabled"
    READY = "ready"
    DEGRADED = "degraded"
    ERROR = "error"


class IntegrationCapability(StrEnum):
    READ_MESSAGES = "read_messages"
    READ_FILES = "read_files"
    READ_CALENDAR_EVENTS = "read_calendar_events"
    READ_ERP_DATA = "read_erp_data"


class IntegrationDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1, max_length=100)
    kind: IntegrationKind
    provider: str = Field(min_length=1, max_length=100)
    capabilities: tuple[IntegrationCapability, ...] = ()
    enabled: bool = True


class IntegrationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_system: str = Field(min_length=1, max_length=100)
    external_id: str = Field(min_length=1, max_length=255)
    record_type: str = Field(min_length=1, max_length=100)

    payload: dict[str, Any] = Field(default_factory=dict)

    source_url: str | None = None
    occurred_at: datetime | None = None
    fetched_at: datetime