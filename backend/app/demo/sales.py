from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.demo.ids import (
    BALTIC_CONSTRUCTION_GROUP_ID,
    KAROLINA_WOJCIK_ID,
    MAZOVIA_LOGISTICS_PARKS_ID,
    MICHAL_KAMINSKI_ID,
    NORDBUILD_DEVELOPMENT_ID,
    OPP_2026_041_ID,
    OPP_2026_042_ID,
    OPP_2026_043_ID,
    OPP_2026_044_ID,
    POLARIS_INDUSTRIAL_DEVELOPMENT_ID,
    TOMASZ_WISNIEWSKI_ID,
    VISTULA_PROPERTY_GROUP_ID,
)


class OpportunityStage(StrEnum):
    LEAD = "LEAD"
    QUALIFIED = "QUALIFIED"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


@dataclass(frozen=True, slots=True)
class DemoCustomer:
    id: UUID
    customer_code: str
    name: str
    city: str
    country: str = "PL"


@dataclass(frozen=True, slots=True)
class DemoOpportunity:
    id: UUID
    opportunity_code: str
    customer_id: UUID
    owner_id: UUID
    title: str
    stage: OpportunityStage
    value_pln: int


NEXALVORA_CUSTOMERS = (
    DemoCustomer(
        id=BALTIC_CONSTRUCTION_GROUP_ID,
        customer_code="CUS-001",
        name="Baltic Construction Group Sp. z o.o.",
        city="Warszawa",
    ),
    DemoCustomer(
        id=NORDBUILD_DEVELOPMENT_ID,
        customer_code="CUS-002",
        name="NordBuild Development Sp. z o.o.",
        city="Gdańsk",
    ),
    DemoCustomer(
        id=MAZOVIA_LOGISTICS_PARKS_ID,
        customer_code="CUS-003",
        name="Mazovia Logistics Parks S.A.",
        city="Warszawa",
    ),
    DemoCustomer(
        id=VISTULA_PROPERTY_GROUP_ID,
        customer_code="CUS-004",
        name="Vistula Property Group Sp. z o.o.",
        city="Kraków",
    ),
    DemoCustomer(
        id=POLARIS_INDUSTRIAL_DEVELOPMENT_ID,
        customer_code="CUS-005",
        name="Polaris Industrial Development Sp. z o.o.",
        city="Poznań",
    ),
)


NEXALVORA_OPPORTUNITIES = (
    DemoOpportunity(
        id=OPP_2026_041_ID,
        opportunity_code="OPP-2026-041",
        customer_id=BALTIC_CONSTRUCTION_GROUP_ID,
        owner_id=KAROLINA_WOJCIK_ID,
        title="Warsaw Logistics Center — Building B",
        stage=OpportunityStage.WON,
        value_pln=686_400,
    ),
    DemoOpportunity(
        id=OPP_2026_042_ID,
        opportunity_code="OPP-2026-042",
        customer_id=NORDBUILD_DEVELOPMENT_ID,
        owner_id=TOMASZ_WISNIEWSKI_ID,
        title="NordBuild Business Park — Office Modules",
        stage=OpportunityStage.NEGOTIATION,
        value_pln=420_000,
    ),
    DemoOpportunity(
        id=OPP_2026_043_ID,
        opportunity_code="OPP-2026-043",
        customer_id=MAZOVIA_LOGISTICS_PARKS_ID,
        owner_id=KAROLINA_WOJCIK_ID,
        title="Mazovia Logistics Park — Wall Systems",
        stage=OpportunityStage.PROPOSAL_SENT,
        value_pln=315_000,
    ),
    DemoOpportunity(
        id=OPP_2026_044_ID,
        opportunity_code="OPP-2026-044",
        customer_id=VISTULA_PROPERTY_GROUP_ID,
        owner_id=MICHAL_KAMINSKI_ID,
        title="Vistula Retail Hub — Facade Modules",
        stage=OpportunityStage.QUALIFIED,
        value_pln=185_000,
    ),
)


OPEN_PIPELINE_VALUE_PLN = sum(
    opportunity.value_pln
    for opportunity in NEXALVORA_OPPORTUNITIES
    if opportunity.stage
    not in {
        OpportunityStage.WON,
        OpportunityStage.LOST,
    }
)

WON_VALUE_PLN = sum(
    opportunity.value_pln
    for opportunity in NEXALVORA_OPPORTUNITIES
    if opportunity.stage == OpportunityStage.WON
)