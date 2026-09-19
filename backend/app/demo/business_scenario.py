from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.demo.calendar import NEXALVORA_CALENDAR_EVENTS
from app.demo.email import NEXALVORA_EMAIL_MESSAGES
from app.demo.erp_data import NEXALVORA_ORDERS
from app.demo.ids import (
    BALTIC_CONSTRUCTION_GROUP_ID,
    MAT_204_ID,
    OPP_2026_041_ID,
    ORD_1048_ID,
    PROD_W38_DOCUMENT_ID,
    TECH_12_DOCUMENT_ID,
)
from app.demo.knowledge_content import NEXALVORA_KNOWLEDGE_CONTENT
from app.demo.risk_story import (
    MAT_204_DELIVERIES,
    MAT_204_PURCHASE_ORDER,
    ORD_1048_RISK_CONTEXT,
)
from app.demo.sales import NEXALVORA_OPPORTUNITIES


@dataclass(frozen=True, slots=True)
class DemoBusinessScenario:
    scenario_key: str
    opportunity_id: UUID
    order_id: UUID
    customer_id: UUID
    material_id: UUID
    risk_level: str
    shortage_quantity: Decimal
    linked_document_ids: tuple[UUID, ...]
    linked_email_ids: tuple[str, ...]
    linked_calendar_event_ids: tuple[str, ...]


MAIN_ORD_1048_SCENARIO = DemoBusinessScenario(
    scenario_key="ORD-1048-MAT-204-RISK",
    opportunity_id=OPP_2026_041_ID,
    order_id=ORD_1048_ID,
    customer_id=BALTIC_CONSTRUCTION_GROUP_ID,
    material_id=MAT_204_ID,
    risk_level=str(ORD_1048_RISK_CONTEXT["risk_level"]),
    shortage_quantity=Decimal(
        str(ORD_1048_RISK_CONTEXT["shortage_quantity"])
    ),
    linked_document_ids=(
        TECH_12_DOCUMENT_ID,
        PROD_W38_DOCUMENT_ID,
    ),
    linked_email_ids=tuple(
        message.message_id
        for message in NEXALVORA_EMAIL_MESSAGES
        if message.thread_key in {"ORD-1048", "PO-2026-0914"}
    ),
    linked_calendar_event_ids=tuple(
        event.event_id
        for event in NEXALVORA_CALENDAR_EVENTS
        if (
            "ORD-1048" in event.title
            or "MAT-204" in event.title
        )
    ),
)


def validate_main_business_scenario() -> None:
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

    assert opportunity.customer_id == order.customer_id
    assert order.customer_id == MAIN_ORD_1048_SCENARIO.customer_id

    assert MAIN_ORD_1048_SCENARIO.material_id == MAT_204_ID
    assert MAIN_ORD_1048_SCENARIO.shortage_quantity == Decimal("80")
    assert MAIN_ORD_1048_SCENARIO.risk_level == "HIGH"

    assert MAT_204_PURCHASE_ORDER.material_id == MAT_204_ID
    assert MAT_204_PURCHASE_ORDER.quantity == Decimal("400")
    assert len(MAT_204_DELIVERIES) == 2

    assert TECH_12_DOCUMENT_ID in NEXALVORA_KNOWLEDGE_CONTENT
    assert PROD_W38_DOCUMENT_ID in NEXALVORA_KNOWLEDGE_CONTENT