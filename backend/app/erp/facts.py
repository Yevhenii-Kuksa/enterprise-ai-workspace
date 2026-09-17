from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.erp.schemas import ERPSourceMetadata


class FactType(StrEnum):
    SYSTEM_FACT = "system_fact"
    DOCUMENT_FACT = "document_fact"


class SystemFact(BaseModel):
    fact_type: FactType = FactType.SYSTEM_FACT

    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: str = Field(min_length=1, max_length=255)
    field_name: str = Field(min_length=1, max_length=100)

    value: Any

    source: ERPSourceMetadata

    observed_at: datetime | None = None