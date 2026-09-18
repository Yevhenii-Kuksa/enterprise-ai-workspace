from collections.abc import Sequence
from typing import Any, Protocol

from app.integrations.calendar import CalendarEvent
from app.integrations.google_calendar_adapter import (
    GoogleCalendarEventAdapter,
)


class GoogleCalendarGateway(Protocol):
    def list_events(
        self,
        *,
        max_results: int,
    ) -> Sequence[dict[str, Any]]:
        ...


class GoogleCalendarReadOnlyClient:
    def __init__(
        self,
        *,
        gateway: GoogleCalendarGateway,
        max_results: int = 100,
    ) -> None:
        if max_results < 1:
            raise ValueError(
                "max_results must be greater than zero."
            )

        self.gateway = gateway
        self.max_results = max_results

    def list_events(
        self,
    ) -> list[CalendarEvent]:
        events = self.gateway.list_events(
            max_results=self.max_results,
        )

        return [
            GoogleCalendarEventAdapter.from_api_event(
                event
            )
            for event in events
        ]