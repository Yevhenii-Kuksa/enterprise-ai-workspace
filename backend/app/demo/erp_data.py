from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from app.demo.ids import (
    BALTIC_CONSTRUCTION_GROUP_ID,
    MAIN_WAREHOUSE_ID,
    MAT_086_ID,
    MAT_086_INVENTORY_ID,
    MAT_118_ID,
    MAT_118_INVENTORY_ID,
    MAT_204_ID,
    MAT_204_INVENTORY_ID,
    MAT_331_ID,
    MAT_331_INVENTORY_ID,
    MAT_412_ID,
    MAT_412_INVENTORY_ID,
    MAT_509_ID,
    MAT_509_INVENTORY_ID,
    MAZOVIA_LOGISTICS_PARKS_ID,
    NEXALVORA_ORGANIZATION_ID,
    NORDBUILD_DEVELOPMENT_ID,
    ORD_1044_ID,
    ORD_1045_ID,
    ORD_1046_ID,
    ORD_1047_ID,
    ORD_1048_ID,
    POLARIS_INDUSTRIAL_DEVELOPMENT_ID,
    VISTULA_PROPERTY_GROUP_ID,
)


class DemoOrderLifecycle(StrEnum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"


class DemoDelayState(StrEnum):
    ON_TIME = "ON_TIME"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"


@dataclass(frozen=True, slots=True)
class DemoOrder:
    id: UUID
    organization_id: UUID
    order_number: str
    customer_id: UUID
    lifecycle: DemoOrderLifecycle
    delay_state: DemoDelayState
    ordered_at: datetime
    confirmed_delivery_at: datetime | None


@dataclass(frozen=True, slots=True)
class DemoInventoryItem:
    id: UUID
    organization_id: UUID
    material_id: UUID
    location_id: UUID
    on_hand: Decimal
    reserved: Decimal


NEXALVORA_ORDERS = (
    DemoOrder(
        id=ORD_1048_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        order_number="ORD-1048",
        customer_id=BALTIC_CONSTRUCTION_GROUP_ID,
        lifecycle=DemoOrderLifecycle.IN_PROGRESS,
        delay_state=DemoDelayState.AT_RISK,
        ordered_at=datetime(
            2026,
            9,
            3,
            9,
            0,
            tzinfo=UTC,
        ),
        confirmed_delivery_at=datetime(
            2026,
            9,
            23,
            8,
            0,
            tzinfo=UTC,
        ),
    ),
    DemoOrder(
        id=ORD_1047_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        order_number="ORD-1047",
        customer_id=NORDBUILD_DEVELOPMENT_ID,
        lifecycle=DemoOrderLifecycle.IN_PROGRESS,
        delay_state=DemoDelayState.ON_TIME,
        ordered_at=datetime(
            2026,
            9,
            1,
            8,
            30,
            tzinfo=UTC,
        ),
        confirmed_delivery_at=datetime(
            2026,
            9,
            28,
            8,
            0,
            tzinfo=UTC,
        ),
    ),
    DemoOrder(
        id=ORD_1046_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        order_number="ORD-1046",
        customer_id=MAZOVIA_LOGISTICS_PARKS_ID,
        lifecycle=DemoOrderLifecycle.READY,
        delay_state=DemoDelayState.ON_TIME,
        ordered_at=datetime(
            2026,
            8,
            26,
            10,
            0,
            tzinfo=UTC,
        ),
        confirmed_delivery_at=datetime(
            2026,
            9,
            20,
            8,
            0,
            tzinfo=UTC,
        ),
    ),
    DemoOrder(
        id=ORD_1045_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        order_number="ORD-1045",
        customer_id=VISTULA_PROPERTY_GROUP_ID,
        lifecycle=DemoOrderLifecycle.IN_PROGRESS,
        delay_state=DemoDelayState.DELAYED,
        ordered_at=datetime(
            2026,
            8,
            20,
            9,
            15,
            tzinfo=UTC,
        ),
        confirmed_delivery_at=datetime(
            2026,
            9,
            18,
            8,
            0,
            tzinfo=UTC,
        ),
    ),
    DemoOrder(
        id=ORD_1044_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        order_number="ORD-1044",
        customer_id=POLARIS_INDUSTRIAL_DEVELOPMENT_ID,
        lifecycle=DemoOrderLifecycle.DRAFT,
        delay_state=DemoDelayState.ON_TIME,
        ordered_at=datetime(
            2026,
            9,
            17,
            12,
            0,
            tzinfo=UTC,
        ),
        confirmed_delivery_at=None,
    ),
)


NEXALVORA_INVENTORY = (
    DemoInventoryItem(
        id=MAT_204_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_204_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("180"),
        reserved=Decimal("160"),
    ),
    DemoInventoryItem(
        id=MAT_118_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_118_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("920"),
        reserved=Decimal("310"),
    ),
    DemoInventoryItem(
        id=MAT_331_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_331_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("640"),
        reserved=Decimal("210"),
    ),
    DemoInventoryItem(
        id=MAT_086_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_086_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("780"),
        reserved=Decimal("190"),
    ),
    DemoInventoryItem(
        id=MAT_412_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_412_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("520"),
        reserved=Decimal("140"),
    ),
    DemoInventoryItem(
        id=MAT_509_INVENTORY_ID,
        organization_id=NEXALVORA_ORGANIZATION_ID,
        material_id=MAT_509_ID,
        location_id=MAIN_WAREHOUSE_ID,
        on_hand=Decimal("1100"),
        reserved=Decimal("260"),
    ),
)


MAT_204_REQUIRED_FOR_ORD_1048 = Decimal("260")
MAT_204_SAFETY_STOCK = Decimal("300")