from typing import Any


class GoogleCalendarApiGateway:
    def __init__(
        self,
        *,
        service: Any,
        calendar_id: str = "primary",
    ) -> None:
        self.service = service
        self.calendar_id = calendar_id

    def list_events(
        self,
        *,
        max_results: int,
    ) -> list[dict[str, Any]]:
        response = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = response.get(
            "items",
            [],
        )

        return [
            dict(event)
            for event in events
        ]