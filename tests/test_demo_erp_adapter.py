import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.erp.adapter import ERPAdapter
from app.erp.demo_adapter import DemoERPAdapter
from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPOrderLine,
    ERPOrderStatus,
    ERPProduct,
    ERPSourceMetadata,
)


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
    )


def test_demo_adapter_implements_erp_adapter() -> None:
    adapter = DemoERPAdapter()

    assert isinstance(adapter, ERPAdapter)


def test_products_are_isolated_by_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    product_a = ERPProduct(
        id=uuid.uuid4(),
        organization_id=organization_a,
        sku="NX-A",
        name="Produkt A",
        unit="szt.",
        source=make_source("PRODUCT-A"),
    )
    product_b = ERPProduct(
        id=uuid.uuid4(),
        organization_id=organization_b,
        sku="NX-B",
        name="Produkt B",
        unit="szt.",
        source=make_source("PRODUCT-B"),
    )

    adapter = DemoERPAdapter(products=[product_a, product_b])

    assert adapter.list_products(organization_id=organization_a) == [
        product_a
    ]
    assert (
        adapter.get_product(
            organization_id=organization_a,
            product_id=product_b.id,
        )
        is None
    )


def test_customer_cannot_be_read_from_another_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    customer = ERPCustomer(
        id=uuid.uuid4(),
        organization_id=organization_b,
        customer_number="C-001",
        name="Klient B",
        source=make_source("CUSTOMER-B"),
    )

    adapter = DemoERPAdapter(customers=[customer])

    assert (
        adapter.get_customer(
            organization_id=organization_a,
            customer_id=customer.id,
        )
        is None
    )
    assert (
        adapter.get_customer(
            organization_id=organization_b,
            customer_id=customer.id,
        )
        == customer
    )


def test_inventory_locations_are_isolated_by_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    location_a = ERPInventoryLocation(
        id=uuid.uuid4(),
        organization_id=organization_a,
        code="WAW",
        name="Magazyn Warszawa",
        source=make_source("LOCATION-A"),
    )
    location_b = ERPInventoryLocation(
        id=uuid.uuid4(),
        organization_id=organization_b,
        code="KRK",
        name="Magazyn Kraków",
        source=make_source("LOCATION-B"),
    )

    adapter = DemoERPAdapter(
        inventory_locations=[location_a, location_b]
    )

    assert adapter.list_inventory_locations(
        organization_id=organization_a
    ) == [location_a]


def test_inventory_can_be_filtered_by_product_and_location() -> None:
    organization_id = uuid.uuid4()
    product_a = uuid.uuid4()
    product_b = uuid.uuid4()
    location_a = uuid.uuid4()
    location_b = uuid.uuid4()

    item_a = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_a,
        location_id=location_a,
        on_hand=Decimal("100"),
        reserved=Decimal("20"),
        source=make_source("INVENTORY-A"),
    )
    item_b = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_b,
        location_id=location_b,
        on_hand=Decimal("50"),
        reserved=Decimal("5"),
        source=make_source("INVENTORY-B"),
    )

    adapter = DemoERPAdapter(inventory_items=[item_a, item_b])

    assert adapter.list_inventory(
        organization_id=organization_id,
        product_id=product_a,
    ) == [item_a]

    assert adapter.list_inventory(
        organization_id=organization_id,
        location_id=location_b,
    ) == [item_b]

    assert adapter.list_inventory(
        organization_id=organization_id,
        product_id=product_a,
        location_id=location_b,
    ) == []


def test_inventory_reservations_can_be_filtered() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    other_product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("10"),
        source=make_source("RESERVATION-A"),
    )
    other_reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=other_product_id,
        location_id=location_id,
        quantity=Decimal("5"),
        source=make_source("RESERVATION-B"),
    )

    adapter = DemoERPAdapter(
        inventory_reservations=[reservation, other_reservation]
    )

    assert adapter.list_inventory_reservations(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
    ) == [reservation]


def test_orders_are_isolated_by_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()
    product_id = uuid.uuid4()

    line = ERPOrderLine(
        id=uuid.uuid4(),
        organization_id=organization_a,
        product_id=product_id,
        quantity=Decimal("4"),
        unit_price=Decimal("25.50"),
        currency="PLN",
        source=make_source("ORDER-LINE-A"),
    )
    order_a = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_a,
        order_number="ORD-A",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.CONFIRMED,
        ordered_at=datetime(2026, 9, 17, 10, 0, tzinfo=UTC),
        lines=[line],
        source=make_source("ORDER-A"),
    )
    order_b = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_b,
        order_number="ORD-B",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.DRAFT,
        ordered_at=datetime(2026, 9, 17, 11, 0, tzinfo=UTC),
        source=make_source("ORDER-B"),
    )

    adapter = DemoERPAdapter(orders=[order_a, order_b])

    assert adapter.list_orders(organization_id=organization_a) == [
        order_a
    ]
    assert (
        adapter.get_order(
            organization_id=organization_a,
            order_id=order_b.id,
        )
        is None
    )
    assert (
        adapter.get_order(
            organization_id=organization_a,
            order_id=order_a.id,
        )
        == order_a
    )


def test_erp_adapter_contract_contains_only_read_operations() -> None:
    public_methods = {
        name
        for name in dir(ERPAdapter)
        if not name.startswith("_")
    }

    forbidden_write_methods = {
        "create_order",
        "update_order",
        "delete_order",
        "create_product",
        "update_product",
        "delete_product",
        "update_inventory",
        "change_inventory",
    }

    assert public_methods.isdisjoint(forbidden_write_methods)