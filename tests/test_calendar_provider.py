from datetime import UTC, datetime

from app.integrations.calendar import (
    CalendarEvent,
    CalendarProvider,
)


class FakeCalendarClient:
    def list_events(
        self,
    ) -> list[CalendarEvent]:
        return [
            CalendarEvent(
                event_id="event-001",
                title="Spotkanie sprzedażowe",
                starts_at=datetime(
                    2026,
                    9,
                    18,
                    9,
                    0,
                    tzinfo=UTC,
                ),
                ends_at=datetime(
                    2026,
                    9,
                    18,
                    10,
                    0,
                    tzinfo=UTC,
                ),
                organizer="manager@nexalvora.example",
                attendees=(
                    "sales@nexalvora.example",
                ),
                location="Sala 2",
                description="Omówienie pipeline.",
                source_url=(
                    "https://calendar.example/event-001"
                ),
            )
        ]


def test_calendar_provider_normalizes_events() -> None:
    provider = CalendarProvider(
        source_system="google-calendar",
        client=FakeCalendarClient(),
    )

    records = provider.fetch_records()

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "google-calendar"
    assert record.external_id == "event-001"
    assert record.record_type == "calendar_event"

    assert record.payload["title"] == "Spotkanie sprzedażowe"
    assert record.payload["organizer"] == (
        "manager@nexalvora.example"
    )
    assert record.payload["attendees"] == [
        "sales@nexalvora.example"
    ]

    assert record.occurred_at == datetime(
        2026,
        9,
        18,
        9,
        0,
        tzinfo=UTC,
    )