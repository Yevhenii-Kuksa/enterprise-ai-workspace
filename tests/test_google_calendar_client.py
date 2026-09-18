import pytest
from app.integrations.google_calendar_client import (
    GoogleCalendarReadOnlyClient,
)


class FakeGoogleCalendarGateway:
    def __init__(self) -> None:
        self.requested_max_results: int | None = None

    def list_events(
        self,
        *,
        max_results: int,
    ) -> list[dict[str, object]]:
        self.requested_max_results = max_results

        return [
            {
                "id": "event-001",
                "summary": "Spotkanie sprzedażowe",
                "start": {
                    "dateTime": "2026-09-18T09:00:00Z",
                },
                "end": {
                    "dateTime": "2026-09-18T10:00:00Z",
                },
            },
            {
                "id": "event-002",
                "summary": "Przegląd operacyjny",
                "start": {
                    "dateTime": "2026-09-18T11:00:00Z",
                },
                "end": {
                    "dateTime": "2026-09-18T12:00:00Z",
                },
            },
        ]


def test_google_calendar_read_only_client_fetches_events() -> None:
    gateway = FakeGoogleCalendarGateway()

    client = GoogleCalendarReadOnlyClient(
        gateway=gateway,
        max_results=25,
    )

    events = client.list_events()

    assert gateway.requested_max_results == 25

    assert len(events) == 2

    assert events[0].event_id == "event-001"
    assert events[0].title == "Spotkanie sprzedażowe"

    assert events[1].event_id == "event-002"
    assert events[1].title == "Przegląd operacyjny"


def test_google_calendar_read_only_client_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError):
        GoogleCalendarReadOnlyClient(
            gateway=FakeGoogleCalendarGateway(),
            max_results=0,
        )