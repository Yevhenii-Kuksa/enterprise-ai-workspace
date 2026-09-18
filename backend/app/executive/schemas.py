import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field

from app.erp.facts import FactType
from app.erp.intelligence import (
    InventoryAvailabilityState,
    OrderDelayState,
)
from app.erp.schemas import ERPOrderStatus


class ExecutiveRiskLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ExecutiveEvidence(BaseModel):
    fact_type: FactType
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: str = Field(min_length=1, max_length=255)
    source_system: str = Field(min_length=1, max_length=100)
    source_record_id: str = Field(min_length=1, max_length=255)
    last_synced_at: datetime
    document_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None


class ExecutiveInventoryRisk(BaseModel):
    product_id: uuid.UUID
    location_id: uuid.UUID
    on_hand: Decimal
    reserved: Decimal
    available: Decimal
    availability_state: InventoryAvailabilityState
    risk_level: ExecutiveRiskLevel
    message_pl: str = Field(min_length=1)
    evidence: list[ExecutiveEvidence] = Field(default_factory=list)


class ExecutiveOrderException(BaseModel):
    order_id: uuid.UUID
    order_number: str
    lifecycle_status: ERPOrderStatus
    delay_state: OrderDelayState
    risk_level: ExecutiveRiskLevel
    message_pl: str = Field(min_length=1)
    evidence: list[ExecutiveEvidence] = Field(default_factory=list)


class ExecutiveApprovalSummary(BaseModel):
    pending: int = Field(ge=0)
    approved: int = Field(ge=0)
    rejected: int = Field(ge=0)


class ExecutiveBriefingSummary(BaseModel):
    inventory_items: int = Field(ge=0)
    unavailable_inventory_items: int = Field(ge=0)
    limited_inventory_items: int = Field(ge=0)
    active_orders: int = Field(ge=0)
    delayed_orders: int = Field(ge=0)
    at_risk_orders: int = Field(ge=0)


class ExecutiveBriefing(BaseModel):
    organization_id: uuid.UUID
    generated_at: datetime
    title_pl: str = "Briefing zarządczy"
    summary: ExecutiveBriefingSummary
    inventory_risks: list[ExecutiveInventoryRisk] = Field(
        default_factory=list
    )
    order_exceptions: list[ExecutiveOrderException] = Field(
        default_factory=list
    )
    approvals: ExecutiveApprovalSummary
    evidence: list[ExecutiveEvidence] = Field(default_factory=list)