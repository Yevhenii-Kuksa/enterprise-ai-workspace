import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.erp.demo_adapter import DemoERPAdapter
from app.erp.schemas import (
    ERPCustomer,
    ERPInventoryItem,
    ERPInventoryLocation,
    ERPInventoryReservation,
    ERPOrder,
    ERPOrderStatus,
    ERPProduct,
    ERPSourceMetadata,
)
from app.erp.service import ERPService


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
    )


def test_service_lists_products_for_organization() -> None:
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

    service = ERPService(
        DemoERPAdapter(products=[product_a, product_b])
    )

    assert service.list_products(
        organization_id=organization_a
    ) == [product_a]


def test_service_gets_product_without_cross_tenant_access() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    product = ERPProduct(
        id=uuid.uuid4(),
        organization_id=organization_b,
        sku="NX-B",
        name="Produkt B",
        unit="szt.",
        source=make_source("PRODUCT-B"),
    )

    service = ERPService(DemoERPAdapter(products=[product]))

    assert (
        service.get_product(
            organization_id=organization_a,
            product_id=product.id,
        )
        is None
    )
    assert (
        service.get_product(
            organization_id=organization_b,
            product_id=product.id,
        )
        == product
    )


def test_service_gets_customer() -> None:
    organization_id = uuid.uuid4()

    customer = ERPCustomer(
        id=uuid.uuid4(),
        organization_id=organization_id,
        customer_number="C-001",
        name="Klient Testowy",
        source=make_source("CUSTOMER-001"),
    )

    service = ERPService(DemoERPAdapter(customers=[customer]))

    assert (
        service.get_customer(
            organization_id=organization_id,
            customer_id=customer.id,
        )
        == customer
    )


def test_service_lists_inventory_locations() -> None:
    organization_id = uuid.uuid4()

    location = ERPInventoryLocation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        code="WAW",
        name="Magazyn Warszawa",
        source=make_source("LOCATION-WAW"),
    )

    service = ERPService(
        DemoERPAdapter(inventory_locations=[location])
    )

    assert service.list_inventory_locations(
        organization_id=organization_id
    ) == [location]


def test_service_passes_inventory_filters() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    expected_item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("25"),
        source=make_source("INVENTORY-001"),
    )
    other_item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=location_id,
        on_hand=Decimal("50"),
        reserved=Decimal("5"),
        source=make_source("INVENTORY-002"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[expected_item, other_item],
        )
    )

    assert service.list_inventory(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
    ) == [expected_item]


def test_service_passes_reservation_filters() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("12"),
        source=make_source("RESERVATION-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_reservations=[reservation],
        )
    )

    assert service.list_inventory_reservations(
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
    ) == [reservation]


def test_service_gets_and_lists_orders_for_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    order_a = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_a,
        order_number="ORD-A",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.CONFIRMED,
        ordered_at=datetime(2026, 9, 17, 10, 0, tzinfo=UTC),
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

    service = ERPService(
        DemoERPAdapter(orders=[order_a, order_b])
    )

    assert service.list_orders(
        organization_id=organization_a
    ) == [order_a]

    assert (
        service.get_order(
            organization_id=organization_a,
            order_id=order_a.id,
        )
        == order_a
    )

    assert (
        service.get_order(
            organization_id=organization_a,
            order_id=order_b.id,
        )
        is None
    )


def test_erp_service_exposes_no_write_operations() -> None:
    public_methods = {
        name
        for name in dir(ERPService)
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