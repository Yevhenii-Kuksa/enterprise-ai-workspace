from app.demo.sales import (
    NEXALVORA_CUSTOMERS,
    NEXALVORA_OPPORTUNITIES,
    OPEN_PIPELINE_VALUE_PLN,
    WON_VALUE_PLN,
    OpportunityStage,
)


def test_customer_codes_are_unique() -> None:
    customer_codes = [
        customer.customer_code
        for customer in NEXALVORA_CUSTOMERS
    ]

    assert len(customer_codes) == len(set(customer_codes))


def test_customer_ids_are_unique() -> None:
    customer_ids = [
        customer.id
        for customer in NEXALVORA_CUSTOMERS
    ]

    assert len(customer_ids) == len(set(customer_ids))


def test_opportunity_codes_are_unique() -> None:
    opportunity_codes = [
        opportunity.opportunity_code
        for opportunity in NEXALVORA_OPPORTUNITIES
    ]

    assert len(opportunity_codes) == len(set(opportunity_codes))


def test_opportunity_ids_are_unique() -> None:
    opportunity_ids = [
        opportunity.id
        for opportunity in NEXALVORA_OPPORTUNITIES
    ]

    assert len(opportunity_ids) == len(set(opportunity_ids))


def test_all_opportunities_reference_existing_customers() -> None:
    customer_ids = {
        customer.id
        for customer in NEXALVORA_CUSTOMERS
    }

    assert all(
        opportunity.customer_id in customer_ids
        for opportunity in NEXALVORA_OPPORTUNITIES
    )


def test_open_pipeline_value_is_correct() -> None:
    assert OPEN_PIPELINE_VALUE_PLN == 920_000


def test_won_value_is_correct() -> None:
    assert WON_VALUE_PLN == 686_400


def test_main_opportunity_is_won() -> None:
    opportunity = next(
        opportunity
        for opportunity in NEXALVORA_OPPORTUNITIES
        if opportunity.opportunity_code == "OPP-2026-041"
    )

    assert opportunity.stage == OpportunityStage.WON
    assert opportunity.value_pln == 686_400