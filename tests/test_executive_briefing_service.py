import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.erp.demo_adapter import DemoERPAdapter
from app.erp.facts import FactType
from app.erp.intelligence import (
    InventoryAvailabilityState,
    OrderDelayState,
)
from app.erp.schemas import (
    ERPInventoryItem,
    ERPOrder,
    ERPOrderStatus,
    ERPSourceMetadata,
)
from app.erp.service import ERPService
from app.executive.schemas import ExecutiveRiskLevel
from app.executive.service import ExecutiveBriefingService

NOW = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=NOW - timedelta(minutes=10),
    )


def test_generate_briefing_summary() -> None:
    organization_id = uuid.uuid4()

    unavailable_item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("10"),
        reserved=Decimal("10"),
        source=make_source("INVENTORY-001"),
    )

    limited_item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("100"),
        reserved=Decimal("25"),
        source=make_source("INVENTORY-002"),
    )

    delayed_order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=3),
        confirmed_delivery_at=NOW - timedelta(hours=2),
        source=make_source("ORDER-001"),
    )

    at_risk_order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-002",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.CONFIRMED,
        ordered_at=NOW - timedelta(days=1),
        confirmed_delivery_at=NOW + timedelta(hours=12),
        source=make_source("ORDER-002"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                inventory_items=[
                    unavailable_item,
                    limited_item,
                ],
                orders=[
                    delayed_order,
                    at_risk_order,
                ],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    assert briefing.title_pl == "Briefing zarządczy"
    assert briefing.summary.inventory_items == 2
    assert briefing.summary.unavailable_inventory_items == 1
    assert briefing.summary.limited_inventory_items == 1
    assert briefing.summary.active_orders == 2
    assert briefing.summary.delayed_orders == 1
    assert briefing.summary.at_risk_orders == 1
    assert len(briefing.inventory_risks) == 2
    assert len(briefing.order_exceptions) == 2


def test_inventory_risks_have_polish_messages_and_evidence() -> None:
    organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("20"),
        reserved=Decimal("20"),
        source=make_source("INVENTORY-001"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                inventory_items=[item],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    risk = briefing.inventory_risks[0]

    assert risk.availability_state == (
        InventoryAvailabilityState.UNAVAILABLE
    )
    assert risk.risk_level == ExecutiveRiskLevel.CRITICAL
    assert risk.message_pl == "Brak dostępnego zapasu."
    assert len(risk.evidence) == 1
    assert risk.evidence[0].fact_type == FactType.SYSTEM_FACT
    assert risk.evidence[0].source_system == "demo_erp"


def test_order_exception_keeps_lifecycle_and_delay_separate() -> None:
    organization_id = uuid.uuid4()

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=3),
        confirmed_delivery_at=NOW - timedelta(hours=1),
        source=make_source("ORDER-001"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                orders=[order],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    exception = briefing.order_exceptions[0]

    assert exception.lifecycle_status == ERPOrderStatus.PROCESSING
    assert exception.delay_state == OrderDelayState.DELAYED
    assert exception.risk_level == ExecutiveRiskLevel.CRITICAL
    assert exception.message_pl == "Zamówienie jest opóźnione."


def test_healthy_items_and_on_time_orders_are_not_exceptions() -> None:
    organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("100"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-001"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        confirmed_delivery_at=NOW + timedelta(days=3),
        source=make_source("ORDER-001"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                inventory_items=[item],
                orders=[order],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    assert briefing.inventory_risks == []
    assert briefing.order_exceptions == []
    assert briefing.summary.delayed_orders == 0
    assert briefing.summary.at_risk_orders == 0


def test_briefing_is_tenant_isolated() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("0"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-OTHER"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        order_number="ORD-OTHER",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=3),
        confirmed_delivery_at=NOW - timedelta(days=1),
        source=make_source("ORDER-OTHER"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                inventory_items=[item],
                orders=[order],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    assert briefing.summary.inventory_items == 0
    assert briefing.summary.active_orders == 0
    assert briefing.inventory_risks == []
    assert briefing.order_exceptions == []
    assert briefing.evidence == []


def test_briefing_collects_top_level_evidence() -> None:
    organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("0"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-001"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=2),
        confirmed_delivery_at=NOW - timedelta(hours=1),
        source=make_source("ORDER-001"),
    )

    service = ExecutiveBriefingService(
        ERPService(
            DemoERPAdapter(
                inventory_items=[item],
                orders=[order],
            )
        )
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    assert len(briefing.evidence) == 2
    assert all(
        evidence.fact_type == FactType.SYSTEM_FACT
        for evidence in briefing.evidence
    )


def test_approvals_are_placeholder_until_approval_engine() -> None:
    organization_id = uuid.uuid4()

    service = ExecutiveBriefingService(
        ERPService(DemoERPAdapter())
    )

    briefing = service.generate_briefing(
        organization_id=organization_id,
        now=NOW,
    )

    assert briefing.approvals.pending == 0
    assert briefing.approvals.approved == 0
    assert briefing.approvals.rejected == 0