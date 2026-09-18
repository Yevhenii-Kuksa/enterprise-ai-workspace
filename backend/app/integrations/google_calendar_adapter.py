from datetime import UTC, datetime
from typing import Any

from app.integrations.calendar import CalendarEvent


class GoogleCalendarEventAdapter:
    @staticmethod
    def from_api_event(
        event: dict[str, Any],
    ) -> CalendarEvent:
        start_data = event.get("start", {})
        end_data = event.get("end", {})

        starts_at = GoogleCalendarEventAdapter._parse_datetime(
            start_data
        )

        ends_at = GoogleCalendarEventAdapter._parse_datetime(
            end_data
        )

        organizer_data = event.get(
            "organizer",
            {},
        )

        organizer = organizer_data.get(
            "email"
        )

        attendees = tuple(
            str(attendee["email"])
            for attendee in event.get(
                "attendees",
                [],
            )
            if attendee.get("email")
        )

        return CalendarEvent(
            event_id=str(event["id"]),
            title=str(
                event.get(
                    "summary",
                    "Bez tytułu",
                )
            ),
            starts_at=starts_at,
            ends_at=ends_at,
            organizer=(
                str(organizer)
                if organizer
                else None
            ),
            attendees=attendees,
            location=(
                str(event["location"])
                if event.get("location")
                else None
            ),
            description=str(
                event.get(
                    "description",
                    "",
                )
            ),
            source_url=(
                str(event["htmlLink"])
                if event.get("htmlLink")
                else None
            ),
        )

    @staticmethod
    def _parse_datetime(
        value: dict[str, Any],
    ) -> datetime:
        date_time = value.get(
            "dateTime"
        )

        if date_time:
            return datetime.fromisoformat(
                str(date_time).replace(
                    "Z",
                    "+00:00",
                )
            )

        date_value = value.get(
            "date"
        )

        if date_value:
            return datetime.fromisoformat(
                str(date_value)
            ).replace(
                tzinfo=UTC
            )

        raise ValueError(
            "Calendar event is missing dateTime or date."
        )