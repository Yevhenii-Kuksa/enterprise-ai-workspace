import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class ERPOrderStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    READY = "ready"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ERPSourceMetadata(BaseModel):
    source_system: str = Field(min_length=1, max_length=100)
    source_record_id: str = Field(min_length=1, max_length=255)
    last_synced_at: datetime


class ERPProduct(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)

    unit: str = Field(min_length=1, max_length=50)
    active: bool = True

    source: ERPSourceMetadata


class ERPCustomer(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    customer_number: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)

    active: bool = True

    source: ERPSourceMetadata


class ERPInventoryLocation(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)

    source: ERPSourceMetadata


class ERPInventoryReservation(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    product_id: uuid.UUID
    location_id: uuid.UUID

    quantity: Decimal = Field(ge=0)
    expires_at: datetime | None = None

    source: ERPSourceMetadata


class ERPInventoryItem(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    product_id: uuid.UUID
    location_id: uuid.UUID

    on_hand: Decimal = Field(ge=0)
    reserved: Decimal = Field(ge=0)

    source: ERPSourceMetadata


class ERPOrderLine(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    product_id: uuid.UUID
    quantity: Decimal = Field(gt=0)

    unit_price: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)

    source: ERPSourceMetadata


class ERPOrder(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID

    order_number: str = Field(min_length=1, max_length=100)
    customer_id: uuid.UUID

    status: ERPOrderStatus

    ordered_at: datetime
    requested_delivery_at: datetime | None = None
    confirmed_delivery_at: datetime | None = None
    completed_at: datetime | None = None

    lines: list[ERPOrderLine] = Field(default_factory=list)

    source: ERPSourceMetadata