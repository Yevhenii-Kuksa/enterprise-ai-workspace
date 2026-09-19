from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from app.demo.erp_data import (
    MAT_204_REQUIRED_FOR_ORD_1048,
    MAT_204_SAFETY_STOCK,
    NEXALVORA_INVENTORY,
)
from app.demo.ids import (
    BUILDCORE_MATERIALS_ID,
    MAT_204_ID,
    ORD_1048_ID,
    PO_2026_0914_ID,
)


@dataclass(frozen=True, slots=True)
class DemoPurchaseOrder:
    id: UUID
    purchase_order_number: str
    supplier_id: UUID
    material_id: UUID
    quantity: Decimal
    ordered_at: datetime
    originally_expected_at: datetime


@dataclass(frozen=True, slots=True)
class DemoSupplierDelivery:
    purchase_order_id: UUID
    quantity: Decimal
    expected_at: datetime
    status: str


MAT_204_PURCHASE_ORDER = DemoPurchaseOrder(
    id=PO_2026_0914_ID,
    purchase_order_number="PO-2026-0914",
    supplier_id=BUILDCORE_MATERIALS_ID,
    material_id=MAT_204_ID,
    quantity=Decimal("400"),
    ordered_at=datetime(
        2026,
        9,
        14,
        8,
        30,
        tzinfo=UTC,
    ),
    originally_expected_at=datetime(
        2026,
        9,
        19,
        8,
        0,
        tzinfo=UTC,
    ),
)


MAT_204_DELIVERIES = (
    DemoSupplierDelivery(
        purchase_order_id=PO_2026_0914_ID,
        quantity=Decimal("200"),
        expected_at=datetime(
            2026,
            9,
            21,
            8,
            0,
            tzinfo=UTC,
        ),
        status="DELAYED",
    ),
    DemoSupplierDelivery(
        purchase_order_id=PO_2026_0914_ID,
        quantity=Decimal("200"),
        expected_at=datetime(
            2026,
            9,
            25,
            8,
            0,
            tzinfo=UTC,
        ),
        status="DELAYED",
    ),
)


def get_mat_204_on_hand() -> Decimal:
    item = next(
        item
        for item in NEXALVORA_INVENTORY
        if item.material_id == MAT_204_ID
    )

    return item.on_hand


def get_mat_204_shortage() -> Decimal:
    shortage = MAT_204_REQUIRED_FOR_ORD_1048 - get_mat_204_on_hand()

    return max(shortage, Decimal("0"))


def get_mat_204_safety_stock_gap() -> Decimal:
    gap = MAT_204_SAFETY_STOCK - get_mat_204_on_hand()

    return max(gap, Decimal("0"))


ORD_1048_RISK_CONTEXT = {
    "order_id": ORD_1048_ID,
    "material_id": MAT_204_ID,
    "required_quantity": MAT_204_REQUIRED_FOR_ORD_1048,
    "on_hand_quantity": get_mat_204_on_hand(),
    "shortage_quantity": get_mat_204_shortage(),
    "safety_stock": MAT_204_SAFETY_STOCK,
    "safety_stock_gap": get_mat_204_safety_stock_gap(),
    "risk_level": "HIGH",
    "reason": (
        "MAT-204 stock is below the quantity required for ORD-1048, "
        "while the supplier delivery has been postponed."
    ),
}