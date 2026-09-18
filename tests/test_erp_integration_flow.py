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
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService

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


def test_erp_end_to_end_integration_flow() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    erp_service = ERPService(
        DemoERPAdapter(
            products=[
                ERPProduct(
                    id=product_id,
                    organization_id=organization_id,
                    sku="SKU-001",
                    name="Produkt testowy",
                    unit="szt.",
                    source=source("PRODUCT-001"),
                )
            ],
            inventory_items=[
                ERPInventoryItem(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    product_id=product_id,
                    location_id=location_id,
                    on_hand=Decimal("100"),
                    reserved=Decimal("20"),
                    source=source("INVENTORY-001"),
                )
            ],
            orders=[
                ERPOrder(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    order_number="ORD-001",
                    customer_id=uuid.uuid4(),
                    status=ERPOrderStatus.CONFIRMED,
                    ordered_at=NOW,
                    source=source("ORDER-001"),
                )
            ],
        )
    )

    provider = ERPIntegrationProvider(
        service=erp_service,
        organization_id=organization_id,
        source_system="erp",
    )

    integration_registry = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="erp",
                kind=IntegrationKind.ERP,
                provider="internal",
                capabilities=(
                    IntegrationCapability.READ_ERP_DATA,
                ),
            )
        ]
    )

    provider_registry = ProviderRegistry()
    provider_registry.register(
        "erp",
        provider,
    )

    integration_service = IntegrationService(
        integration_registry,
        provider_registry,
    )

    records = integration_service.fetch_records(
        integration_key="erp",
    )

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