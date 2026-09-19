from decimal import Decimal

from app.demo.business_scenario import (
    MAIN_ORD_1048_SCENARIO,
    validate_main_business_scenario,
)
from app.demo.email import NEXALVORA_EMAIL_MESSAGES
from app.demo.erp_data import NEXALVORA_ORDERS
from app.demo.risk_story import (
    MAT_204_DELIVERIES,
    MAT_204_PURCHASE_ORDER,
)
from app.demo.sales import NEXALVORA_OPPORTUNITIES, OpportunityStage


def test_main_business_scenario_is_valid() -> None:
    validate_main_business_scenario()


def test_main_scenario_links_won_opportunity_to_order() -> None:
    opportunity = next(
        opportunity
        for opportunity in NEXALVORA_OPPORTUNITIES
        if opportunity.id == MAIN_ORD_1048_SCENARIO.opportunity_id
    )

    order = next(
        order
        for order in NEXALVORA_ORDERS
        if order.id == MAIN_ORD_1048_SCENARIO.order_id
    )

    assert opportunity.stage == OpportunityStage.WON
    assert opportunity.customer_id == order.customer_id


def test_main_scenario_has_expected_material_shortage() -> None:
    assert MAIN_ORD_1048_SCENARIO.shortage_quantity == Decimal("80")
    assert MAIN_ORD_1048_SCENARIO.risk_level == "HIGH"


def test_purchase_order_covers_material_shortage() -> None:
    assert (
        MAT_204_PURCHASE_ORDER.quantity
        > MAIN_ORD_1048_SCENARIO.shortage_quantity
    )


def test_supplier_delivery_is_split_into_two_parts() -> None:
    assert len(MAT_204_DELIVERIES) == 2

    assert sum(
        delivery.quantity
        for delivery in MAT_204_DELIVERIES
    ) == MAT_204_PURCHASE_ORDER.quantity


def test_main_scenario_links_expected_emails() -> None:
    known_email_ids = {
        message.message_id
        for message in NEXALVORA_EMAIL_MESSAGES
    }

    assert set(MAIN_ORD_1048_SCENARIO.linked_email_ids).issubset(
        known_email_ids
    )
    assert len(MAIN_ORD_1048_SCENARIO.linked_email_ids) == 3


def test_main_scenario_links_operational_calendar_events() -> None:
    assert len(
        MAIN_ORD_1048_SCENARIO.linked_calendar_event_ids
    ) >= 3


def test_main_scenario_links_required_documents() -> None:
    assert len(MAIN_ORD_1048_SCENARIO.linked_document_ids) == 2