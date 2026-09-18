from base64 import urlsafe_b64encode
from typing import Any

from app.integrations.email_inbox import EmailInboxProvider
from app.integrations.gmail_client import GmailReadOnlyClient
from app.integrations.gmail_gateway import GmailApiGateway
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService


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


class FakeMessagesResource:
    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        return FakeRequest(
            {
                "messages": [
                    {
                        "id": "msg-001",
                    }
                ]
            }
        )

    def get(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        body = urlsafe_b64encode(
            "Proszę o ofertę.".encode()
        ).decode("ascii")

        return FakeRequest(
            {
                "id": kwargs["id"],
                "threadId": "thread-001",
                "internalDate": "1789727400000",
                "payload": {
                    "mimeType": "text/plain",
                    "headers": [
                        {
                            "name": "From",
                            "value": "klient@example.com",
                        },
                        {
                            "name": "To",
                            "value": (
                                "sprzedaz@nexalvora.example"
                            ),
                        },
                        {
                            "name": "Subject",
                            "value": "Zapytanie ofertowe",
                        },
                    ],
                    "body": {
                        "data": body,
                    },
                },
            }
        )


class FakeUsersResource:
    def __init__(self) -> None:
        self._messages = FakeMessagesResource()

    def messages(
        self,
    ) -> FakeMessagesResource:
        return self._messages


class FakeGmailService:
    def users(
        self,
    ) -> FakeUsersResource:
        return FakeUsersResource()


def test_gmail_end_to_end_integration_flow() -> None:
    gateway = GmailApiGateway(
        service=FakeGmailService(),
    )

    client = GmailReadOnlyClient(
        gateway=gateway,
        max_results=10,
    )

    provider = EmailInboxProvider(
        source_system="gmail",
        client=client,
    )

    integration_registry = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="gmail",
                kind=IntegrationKind.EMAIL,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_MESSAGES,
                ),
            )
        ]
    )

    provider_registry = ProviderRegistry()
    provider_registry.register(
        "gmail",
        provider,
    )

    service = IntegrationService(
        integration_registry,
        provider_registry,
    )

    records = service.fetch_records(
        integration_key="gmail",
    )

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "gmail"
    assert record.external_id == "msg-001"
    assert record.record_type == "email_message"

    assert record.payload["sender"] == "klient@example.com"
    assert record.payload["subject"] == "Zapytanie ofertowe"
    assert record.payload["body_text"] == "Proszę o ofertę."