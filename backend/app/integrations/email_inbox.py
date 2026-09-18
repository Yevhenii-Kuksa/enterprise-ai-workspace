from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.schemas import IntegrationRecord


class EmailMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    message_id: str = Field(min_length=1, max_length=255)
    thread_id: str | None = Field(default=None, max_length=255)

    sender: str = Field(min_length=1, max_length=500)
    recipients: tuple[str, ...] = ()

    subject: str = Field(default="", max_length=1000)
    body_text: str = ""

    received_at: datetime

    source_url: str | None = None


class EmailInboxClient(Protocol):
    def list_messages(
        self,
    ) -> Sequence[EmailMessage]:
        ...


class EmailInboxProvider:
    def __init__(
        self,
        *,
        source_system: str,
        client: EmailInboxClient,
    ) -> None:
        self.source_system = source_system
        self.client = client

    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        messages = self.client.list_messages()

        return [
            IntegrationRecord(
                source_system=self.source_system,
                external_id=message.message_id,
                record_type="email_message",
                payload={
                    "thread_id": message.thread_id,
                    "sender": message.sender,
                    "recipients": list(message.recipients),
                    "subject": message.subject,
                    "body_text": message.body_text,
                },
                source_url=message.source_url,
                occurred_at=message.received_at,
                fetched_at=datetime.now(
                    message.received_at.tzinfo
                ),
            )
            for message in messages
        ]