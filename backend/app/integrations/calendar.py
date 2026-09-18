from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.schemas import IntegrationRecord


class CalendarEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=1000)

    starts_at: datetime
    ends_at: datetime

    organizer: str | None = Field(
        default=None,
        max_length=500,
    )

    attendees: tuple[str, ...] = ()

    location: str | None = Field(
        default=None,
        max_length=1000,
    )

    description: str = ""
    source_url: str | None = None


class CalendarClient(Protocol):
    def list_events(
        self,
    ) -> Sequence[CalendarEvent]:
        ...


class CalendarProvider:
    def __init__(
        self,
        *,
        source_system: str,
        client: CalendarClient,
    ) -> None:
        self.source_system = source_system
        self.client = client

    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        events = self.client.list_events()

        return [
            IntegrationRecord(
                source_system=self.source_system,
                external_id=event.event_id,
                record_type="calendar_event",
                payload={
                    "title": event.title,
                    "ends_at": event.ends_at.isoformat(),
                    "organizer": event.organizer,
                    "attendees": list(event.attendees),
                    "location": event.location,
                    "description": event.description,
                },
                source_url=event.source_url,
                occurred_at=event.starts_at,
                fetched_at=datetime.now(
                    event.starts_at.tzinfo
                ),
            )
            for event in events
        ]