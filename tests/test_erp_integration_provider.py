import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.erp.demo_adapter import DemoERPAdapter
from app.erp.schemas import (
    ERPInventoryItem,
    ERPOrder,
    ERPOrderStatus,
    ERPProduct,
    ERPSourceMetadata,
)
from app.erp.service import ERPService
from app.integrations.erp_provider import ERPIntegrationProvider

NOW = datetime(
    2026,
    9,
    18,
    12,
    0,
    tzinfo=UTC,
)


def source(
    record_id: str,
) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo-erp",
        source_record_id=record_id,
        last_synced_at=NOW,
    )


def test_erp_integration_provider_normalizes_tenant_data() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    product = ERPProduct(
        id=product_id,
        organization_id=organization_id,
        sku="SKU-001",
        name="Produkt testowy",
        unit="szt.",
        source=source("PRODUCT-001"),
    )

    inventory = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("20"),
        source=source("INVENTORY-001"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.CONFIRMED,
        ordered_at=NOW,
        source=source("ORDER-001"),
    )

    foreign_product = ERPProduct(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        sku="SKU-OTHER",
        name="Obcy produkt",
        unit="szt.",
        source=source("PRODUCT-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            products=[
                product,
                foreign_product,
            ],
            inventory_items=[
                inventory,
            ],
            orders=[
                order,
            ],
        )
    )

    provider = ERPIntegrationProvider(
        service=service,
        organization_id=organization_id,
    )

    records = provider.fetch_records()

    assert len(records) == 3

    assert {
        record.record_type
        for record in records
    } == {
        "product",
        "inventory_item",
        "order",
    }

    assert {
        record.external_id
        for record in records
    } == {
        "PRODUCT-001",
        "INVENTORY-001",
        "ORDER-001",
    }

    assert all(
        record.source_system == "erp"
        for record in records
    )

    assert "PRODUCT-OTHER" not in {
        record.external_id
        for record in records
    }