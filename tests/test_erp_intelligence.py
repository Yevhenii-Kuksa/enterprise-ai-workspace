import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.erp.intelligence import (
    InventoryAvailabilityState,
    OrderDelayState,
    calculate_available,
    calculate_inventory_availability,
    calculate_inventory_state,
    calculate_order_delay_state,
    is_reservation_active,
)
from app.erp.schemas import (
    ERPInventoryItem,
    ERPInventoryReservation,
    ERPOrder,
    ERPOrderStatus,
    ERPSourceMetadata,
)

NOW = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(2026, 9, 18, 10, 0, tzinfo=UTC),
    )


def make_inventory_item(
    *,
    organization_id: uuid.UUID,
    product_id: uuid.UUID,
    location_id: uuid.UUID,
    on_hand: Decimal = Decimal("100"),
    reserved: Decimal = Decimal("0"),
) -> ERPInventoryItem:
    return ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=on_hand,
        reserved=reserved,
        source=make_source("INVENTORY-001"),
    )


def make_reservation(
    *,
    organization_id: uuid.UUID,
    product_id: uuid.UUID,
    location_id: uuid.UUID,
    quantity: Decimal,
    expires_at: datetime | None = None,
) -> ERPInventoryReservation:
    return ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=quantity,
        expires_at=expires_at,
        source=make_source("RESERVATION-001"),
    )


def test_calculate_available() -> None:
    assert calculate_available(
        on_hand=Decimal("100"),
        reserved=Decimal("25"),
    ) == Decimal("75")


def test_available_never_becomes_negative() -> None:
    assert calculate_available(
        on_hand=Decimal("20"),
        reserved=Decimal("30"),
    ) == Decimal("0")


def test_inventory_state_available() -> None:
    assert (
        calculate_inventory_state(
            available=Decimal("100"),
            on_hand=Decimal("100"),
        )
        == InventoryAvailabilityState.AVAILABLE
    )


def test_inventory_state_limited() -> None:
    assert (
        calculate_inventory_state(
            available=Decimal("30"),
            on_hand=Decimal("100"),
        )
        == InventoryAvailabilityState.LIMITED
    )


def test_inventory_state_unavailable() -> None:
    assert (
        calculate_inventory_state(
            available=Decimal("0"),
            on_hand=Decimal("100"),
        )
        == InventoryAvailabilityState.UNAVAILABLE
    )


def test_reservation_without_expiry_is_active() -> None:
    reservation = make_reservation(
        organization_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        quantity=Decimal("10"),
    )

    assert is_reservation_active(
        reservation,
        now=NOW,
    )


def test_future_reservation_is_active() -> None:
    reservation = make_reservation(
        organization_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        quantity=Decimal("10"),
        expires_at=NOW + timedelta(hours=1),
    )

    assert is_reservation_active(
        reservation,
        now=NOW,
    )


def test_expired_reservation_is_inactive() -> None:
    reservation = make_reservation(
        organization_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        quantity=Decimal("10"),
        expires_at=NOW - timedelta(seconds=1),
    )

    assert not is_reservation_active(
        reservation,
        now=NOW,
    )


def test_inventory_availability_uses_active_reservation() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    item = make_inventory_item(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
    )

    reservation = make_reservation(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("25"),
        expires_at=NOW + timedelta(hours=1),
    )

    result = calculate_inventory_availability(
        item,
        [reservation],
        now=NOW,
    )

    assert result.reserved == Decimal("25")
    assert result.available == Decimal("75")
    assert result.state == InventoryAvailabilityState.LIMITED


def test_inventory_availability_ignores_expired_reservation() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    item = make_inventory_item(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
    )

    reservation = make_reservation(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("25"),
        expires_at=NOW - timedelta(minutes=1),
    )

    result = calculate_inventory_availability(
        item,
        [reservation],
        now=NOW,
    )

    assert result.reserved == Decimal("0")
    assert result.available == Decimal("100")
    assert result.state == InventoryAvailabilityState.AVAILABLE


def test_inventory_ignores_unrelated_reservations() -> None:
    organization_id = uuid.uuid4()

    item = make_inventory_item(
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        reserved=Decimal("10"),
    )

    reservation = make_reservation(
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        quantity=Decimal("80"),
    )

    result = calculate_inventory_availability(
        item,
        [reservation],
        now=NOW,
    )

    assert result.reserved == Decimal("10")
    assert result.available == Decimal("90")


def test_order_without_delivery_date_is_on_time() -> None:
    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        source=make_source("ORDER-001"),
    )

    assert (
        calculate_order_delay_state(order, now=NOW)
        == OrderDelayState.ON_TIME
    )


def test_order_far_from_delivery_is_on_time() -> None:
    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        order_number="ORD-002",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        confirmed_delivery_at=NOW + timedelta(hours=48),
        source=make_source("ORDER-002"),
    )

    assert (
        calculate_order_delay_state(order, now=NOW)
        == OrderDelayState.ON_TIME
    )


def test_order_close_to_delivery_is_at_risk() -> None:
    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        order_number="ORD-003",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        confirmed_delivery_at=NOW + timedelta(hours=12),
        source=make_source("ORDER-003"),
    )

    assert (
        calculate_order_delay_state(order, now=NOW)
        == OrderDelayState.AT_RISK
    )


def test_order_after_delivery_deadline_is_delayed() -> None:
    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        order_number="ORD-004",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=2),
        confirmed_delivery_at=NOW - timedelta(hours=2),
        source=make_source("ORDER-004"),
    )

    assert (
        calculate_order_delay_state(order, now=NOW)
        == OrderDelayState.DELAYED
    )


def test_completed_order_is_not_marked_delayed() -> None:
    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        order_number="ORD-005",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.COMPLETED,
        ordered_at=NOW - timedelta(days=3),
        confirmed_delivery_at=NOW - timedelta(days=1),
        completed_at=NOW - timedelta(days=1),
        source=make_source("ORDER-005"),
    )

    assert (
        calculate_order_delay_state(order, now=NOW)
        == OrderDelayState.ON_TIME
    )