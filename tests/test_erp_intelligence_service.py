import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.erp.demo_adapter import DemoERPAdapter
from app.erp.intelligence import (
    InventoryAvailabilityState,
    OrderDelayState,
)
from app.erp.schemas import (
    ERPInventoryItem,
    ERPInventoryReservation,
    ERPOrder,
    ERPOrderStatus,
    ERPSourceMetadata,
)
from app.erp.service import ERPService

NOW = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(2026, 9, 18, 10, 0, tzinfo=UTC),
    )


def test_service_calculates_inventory_availability() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("10"),
        source=make_source("INVENTORY-001"),
    )

    reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("25"),
        source=make_source("RESERVATION-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
            inventory_reservations=[reservation],
        )
    )

    result = service.get_inventory_availability(
        organization_id=organization_id,
        now=NOW,
    )

    assert len(result) == 1
    assert result[0].on_hand == Decimal("100")
    assert result[0].reserved == Decimal("25")
    assert result[0].available == Decimal("75")
    assert result[0].state == InventoryAvailabilityState.LIMITED


def test_service_ignores_expired_reservation() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-001"),
    )

    reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("25"),
        expires_at=NOW - timedelta(minutes=1),
        source=make_source("RESERVATION-EXPIRED"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
            inventory_reservations=[reservation],
        )
    )

    result = service.get_inventory_availability(
        organization_id=organization_id,
        now=NOW,
    )

    assert len(result) == 1
    assert result[0].reserved == Decimal("0")
    assert result[0].available == Decimal("100")
    assert result[0].state == InventoryAvailabilityState.AVAILABLE


def test_service_inventory_is_tenant_isolated() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("100"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
        )
    )

    result = service.get_inventory_availability(
        organization_id=organization_id,
        now=NOW,
    )

    assert result == []


def test_service_calculates_order_delay_state() -> None:
    organization_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = ERPOrder(
        id=order_id,
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=2),
        confirmed_delivery_at=NOW - timedelta(hours=2),
        source=make_source("ORDER-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            orders=[order],
        )
    )

    result = service.get_order_delay_state(
        organization_id=organization_id,
        order_id=order_id,
        now=NOW,
    )

    assert result == OrderDelayState.DELAYED


def test_service_returns_none_for_cross_tenant_order() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = ERPOrder(
        id=order_id,
        organization_id=other_organization_id,
        order_number="ORD-OTHER",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        source=make_source("ORDER-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            orders=[order],
        )
    )

    result = service.get_order_delay_state(
        organization_id=organization_id,
        order_id=order_id,
        now=NOW,
    )

    assert result is None