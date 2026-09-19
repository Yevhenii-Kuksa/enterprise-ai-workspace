from datetime import UTC, datetime

from app.demo.erp_data import (
    NEXALVORA_INVENTORY,
    NEXALVORA_ORDERS,
)
from app.erp.demo_adapter import DemoERPAdapter
from app.erp.schemas import (
    ERPInventoryItem,
    ERPOrder,
    ERPOrderStatus,
    ERPSourceMetadata,
)


def _make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(
            2026,
            9,
            19,
            12,
            0,
            tzinfo=UTC,
        ),
    )


def _map_order_status(lifecycle: str) -> ERPOrderStatus:
    mapping = {
        "DRAFT": ERPOrderStatus.DRAFT,
        "CONFIRMED": ERPOrderStatus.CONFIRMED,
        "IN_PROGRESS": ERPOrderStatus.PROCESSING,
        "READY": ERPOrderStatus.READY,
    }

    return mapping[lifecycle]


def build_nexalvora_erp_adapter() -> DemoERPAdapter:
    orders = [
        ERPOrder(
            id=order.id,
            organization_id=order.organization_id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            status=_map_order_status(order.lifecycle),
            ordered_at=order.ordered_at,
            confirmed_delivery_at=order.confirmed_delivery_at,
            source=_make_source(order.order_number),
        )
        for order in NEXALVORA_ORDERS
    ]

    inventory_items = [
        ERPInventoryItem(
            id=item.id,
            organization_id=item.organization_id,
            product_id=item.material_id,
            location_id=item.location_id,
            on_hand=item.on_hand,
            reserved=item.reserved,
            source=_make_source(
                f"INVENTORY-{item.material_id}",
            ),
        )
        for item in NEXALVORA_INVENTORY
    ]

    return DemoERPAdapter(
        inventory_items=inventory_items,
        orders=orders,
    )