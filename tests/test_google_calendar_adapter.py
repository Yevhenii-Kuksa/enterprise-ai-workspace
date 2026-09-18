from datetime import UTC, datetime

from app.integrations.google_calendar_adapter import (
    GoogleCalendarEventAdapter,
)


def test_google_calendar_adapter_normalizes_event() -> None:
    event = {
        "id": "event-001",
        "summary": "Spotkanie sprzedażowe",
        "start": {
            "dateTime": "2026-09-18T09:00:00Z",
        },
        "end": {
            "dateTime": "2026-09-18T10:00:00Z",
        },
        "organizer": {
            "email": "manager@nexalvora.example",
        },
        "attendees": [
            {
                "email": "sales@nexalvora.example",
            }
        ],
        "location": "Sala 2",
        "description": "Omówienie pipeline.",
        "htmlLink": (
            "https://calendar.google.com/event-001"
        ),
    }

    normalized = GoogleCalendarEventAdapter.from_api_event(
        event
    )

    assert normalized.event_id == "event-001"

    assert normalized.title == "Spotkanie sprzedażowe"

    assert normalized.starts_at == datetime(
        2026,
        9,
        18,
        9,
        0,
        tzinfo=UTC,
    )

    assert normalized.ends_at == datetime(
        2026,
        9,
        18,
        10,
        0,
        tzinfo=UTC,
    )

    assert normalized.organizer == (
        "manager@nexalvora.example"
    )

    assert normalized.attendees == (
        "sales@nexalvora.example",
    )

    assert normalized.location == "Sala 2"

    assert normalized.description == (
        "Omówienie pipeline."
    )

    assert normalized.source_url == (
        "https://calendar.google.com/event-001"
    )