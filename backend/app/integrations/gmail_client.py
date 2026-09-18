from collections.abc import Sequence
from typing import Any, Protocol

from app.integrations.email_inbox import EmailMessage
from app.integrations.gmail_adapter import GmailMessageAdapter


class GmailApiGateway(Protocol):
    def list_message_ids(
        self,
        *,
        max_results: int,
    ) -> Sequence[str]:
        ...

    def get_message(
        self,
        *,
        message_id: str,
    ) -> dict[str, Any]:
        ...


class GmailReadOnlyClient:
    def __init__(
        self,
        *,
        gateway: GmailApiGateway,
        max_results: int = 100,
    ) -> None:
        if max_results < 1:
            raise ValueError(
                "max_results must be greater than zero."
            )

        self.gateway = gateway
        self.max_results = max_results

    def list_messages(
        self,
    ) -> list[EmailMessage]:
        message_ids = self.gateway.list_message_ids(
            max_results=self.max_results,
        )

        return [
            GmailMessageAdapter.from_api_message(
                self.gateway.get_message(
                    message_id=message_id,
                )
            )
            for message_id in message_ids
        ]