from decimal import Decimal

from app.demo.risk_story import (
    MAT_204_DELIVERIES,
    MAT_204_PURCHASE_ORDER,
    ORD_1048_RISK_CONTEXT,
    get_mat_204_on_hand,
    get_mat_204_safety_stock_gap,
    get_mat_204_shortage,
)


def test_mat_204_on_hand_is_expected() -> None:
    assert get_mat_204_on_hand() == Decimal("180")


def test_mat_204_shortage_is_expected() -> None:
    assert get_mat_204_shortage() == Decimal("80")


def test_mat_204_safety_stock_gap_is_expected() -> None:
    assert get_mat_204_safety_stock_gap() == Decimal("120")


def test_mat_204_purchase_order_quantity_is_expected() -> None:
    assert MAT_204_PURCHASE_ORDER.quantity == Decimal("400")


def test_mat_204_delivery_split_is_expected() -> None:
    assert len(MAT_204_DELIVERIES) == 2
    assert sum(
        delivery.quantity
        for delivery in MAT_204_DELIVERIES
    ) == Decimal("400")


def test_first_delivery_is_after_original_expected_date() -> None:
    first_delivery = MAT_204_DELIVERIES[0]

    assert (
        first_delivery.expected_at
        > MAT_204_PURCHASE_ORDER.originally_expected_at
    )


def test_ord_1048_risk_context_is_high() -> None:
    assert ORD_1048_RISK_CONTEXT["risk_level"] == "HIGH"
    assert ORD_1048_RISK_CONTEXT["shortage_quantity"] == Decimal("80")