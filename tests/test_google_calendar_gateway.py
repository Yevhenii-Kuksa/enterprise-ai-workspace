from typing import Any

from app.integrations.google_calendar_gateway import (
    GoogleCalendarApiGateway,
)


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
    def __init__(self) -> None:
        self.list_call: dict[str, Any] | None = None

    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        self.list_call = kwargs

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
                    }
                ]
            }
        )


class FakeGoogleCalendarService:
    def __init__(self) -> None:
        self.events_resource = FakeEventsResource()

    def events(
        self,
    ) -> FakeEventsResource:
        return self.events_resource


def test_google_calendar_gateway_lists_events() -> None:
    service = FakeGoogleCalendarService()

    gateway = GoogleCalendarApiGateway(
        service=service,
        calendar_id="primary",
    )

    events = gateway.list_events(
        max_results=25,
    )

    assert len(events) == 1
    assert events[0]["id"] == "event-001"

    assert service.events_resource.list_call == {
        "calendarId": "primary",
        "maxResults": 25,
        "singleEvents": True,
        "orderBy": "startTime",
    }