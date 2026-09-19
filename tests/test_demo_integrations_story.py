from app.demo.calendar import NEXALVORA_CALENDAR_EVENTS
from app.demo.email import NEXALVORA_EMAIL_MESSAGES
from app.demo.integrations import (
    NEXALVORA_INTEGRATIONS,
    DemoIntegrationStatus,
)


def test_expected_number_of_email_messages() -> None:
    assert len(NEXALVORA_EMAIL_MESSAGES) == 3


def test_email_message_ids_are_unique() -> None:
    message_ids = [
        message.message_id
        for message in NEXALVORA_EMAIL_MESSAGES
    ]

    assert len(message_ids) == len(set(message_ids))


def test_ord_1048_email_story_is_present() -> None:
    subjects = {
        message.subject
        for message in NEXALVORA_EMAIL_MESSAGES
    }

    assert "ORD-1048 — ryzyko terminu produkcji" in subjects
    assert "Potwierdzenie terminu dostawy ORD-1048" in subjects


def test_supplier_email_contains_purchase_order_reference() -> None:
    supplier_email = next(
        message
        for message in NEXALVORA_EMAIL_MESSAGES
        if "MAT-204" in message.subject
    )

    assert "PO-2026-0914" in supplier_email.subject
    assert "21.09.2026" in supplier_email.body
    assert "25.09.2026" in supplier_email.body


def test_expected_number_of_calendar_events() -> None:
    assert len(NEXALVORA_CALENDAR_EVENTS) == 4


def test_calendar_event_ids_are_unique() -> None:
    event_ids = [
        event.event_id
        for event in NEXALVORA_CALENDAR_EVENTS
    ]

    assert len(event_ids) == len(set(event_ids))


def test_ord_1048_calendar_story_is_present() -> None:
    titles = {
        event.title
        for event in NEXALVORA_CALENDAR_EVENTS
    }

    assert "Przegląd ryzyka ORD-1048" in titles
    assert "Kontrola gotowości produkcyjnej ORD-1048" in titles
    assert "Potwierdzenie dostawy ORD-1048 z klientem" in titles


def test_expected_integrations_are_ready() -> None:
    integration_keys = {
        integration.integration_key
        for integration in NEXALVORA_INTEGRATIONS
    }

    assert integration_keys == {
        "gmail",
        "google-drive",
        "sharepoint",
        "google-calendar",
        "erp",
    }

    assert all(
        integration.status == DemoIntegrationStatus.READY
        for integration in NEXALVORA_INTEGRATIONS
    )