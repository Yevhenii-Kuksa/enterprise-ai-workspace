from typing import Any

from app.integrations.calendar import CalendarProvider
from app.integrations.google_calendar_client import (
    GoogleCalendarReadOnlyClient,
)
from app.integrations.google_calendar_gateway import (
    GoogleCalendarApiGateway,
)
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService


class FakeRequest:
    def __init__(
        self,
        response: dict[str, Any],
    ) -> None:
        self.response = response

    def execute(
        self,
    ) -> dict[str, Any]:
        return self.response


class FakeEventsResource:
    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        return FakeRequest(
            {
                "items": [
                    {
                        "id": "event-001",
                        "summary": "Spotkanie sprzedażowe",
                        "start": {
                            "dateTime": (
                                "2026-09-18T09:00:00Z"
                            ),
                        },
                        "end": {
                            "dateTime": (
                                "2026-09-18T10:00:00Z"
                            ),
                        },
                        "organizer": {
                            "email": (
                                "manager@nexalvora.example"
                            ),
                        },
                        "attendees": [
                            {
                                "email": (
                                    "sales@nexalvora.example"
                                ),
                            }
                        ],
                        "location": "Sala 2",
                        "description": "Omówienie pipeline.",
                        "htmlLink": (
                            "https://calendar.google.com/"
                            "event-001"
                        ),
                    }
                ]
            }
        )


class FakeGoogleCalendarService:
    def __init__(self) -> None:
        self._events = FakeEventsResource()

    def events(
        self,
    ) -> FakeEventsResource:
        return self._events


def test_google_calendar_end_to_end_integration_flow() -> None:
    gateway = GoogleCalendarApiGateway(
        service=FakeGoogleCalendarService(),
        calendar_id="primary",
    )

    client = GoogleCalendarReadOnlyClient(
        gateway=gateway,
        max_results=10,
    )

    provider = CalendarProvider(
        source_system="google-calendar",
        client=client,
    )

    integration_registry = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="google-calendar",
                kind=IntegrationKind.CALENDAR,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_CALENDAR_EVENTS,
                ),
            )
        ]
    )

    provider_registry = ProviderRegistry()
    provider_registry.register(
        "google-calendar",
        provider,
    )

    service = IntegrationService(
        integration_registry,
        provider_registry,
    )

    records = service.fetch_records(
        integration_key="google-calendar",
    )

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "google-calendar"
    assert record.external_id == "event-001"
    assert record.record_type == "calendar_event"

    assert record.payload["title"] == "Spotkanie sprzedażowe"
    assert record.payload["organizer"] == (
        "manager@nexalvora.example"
    )
    assert record.payload["location"] == "Sala 2"