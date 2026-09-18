from typing import Any


class GmailApiGateway:
    def __init__(
        self,
        *,
        service: Any,
        user_id: str = "me",
    ) -> None:
        self.service = service
        self.user_id = user_id

    def list_message_ids(
        self,
        *,
        max_results: int,
    ) -> list[str]:
        response = (
            self.service.users()
            .messages()
            .list(
                userId=self.user_id,
                maxResults=max_results,
            )
            .execute()
        )

        messages = response.get(
            "messages",
            [],
        )

        return [
            str(message["id"])
            for message in messages
            if message.get("id")
        ]

    def get_message(
        self,
        *,
        message_id: str,
    ) -> dict[str, Any]:
        response = (
            self.service.users()
            .messages()
            .get(
                userId=self.user_id,
                id=message_id,
                format="full",
            )
            .execute()
        )

        return dict(response)