from app.demo.erp_adapter import build_nexalvora_erp_adapter
from app.demo.erp_data import (
    NEXALVORA_INVENTORY,
    NEXALVORA_ORDERS,
)
from app.erp.demo_adapter import DemoERPAdapter
from app.erp.schemas import ERPOrderStatus


def test_nexalvora_erp_adapter_is_created() -> None:
    adapter = build_nexalvora_erp_adapter()

    assert isinstance(adapter, DemoERPAdapter)


def test_nexalvora_demo_contains_expected_orders() -> None:
    assert len(NEXALVORA_ORDERS) == 5


def test_nexalvora_demo_contains_expected_inventory() -> None:
    assert len(NEXALVORA_INVENTORY) == 6


def test_ord_1048_has_expected_business_state() -> None:
    order = next(
        order
        for order in NEXALVORA_ORDERS
        if order.order_number == "ORD-1048"
    )

    assert order.lifecycle == "IN_PROGRESS"
    assert order.delay_state == "AT_RISK"
    assert order.confirmed_delivery_at is not None
    assert order.confirmed_delivery_at.year == 2026
    assert order.confirmed_delivery_at.month == 9
    assert order.confirmed_delivery_at.day == 23


def test_processing_status_exists_for_ord_1048_mapping() -> None:
    assert ERPOrderStatus.PROCESSING.value