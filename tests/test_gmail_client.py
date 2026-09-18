from base64 import urlsafe_b64encode

import pytest
from app.integrations.gmail_client import GmailReadOnlyClient


class FakeGmailGateway:
    def __init__(self) -> None:
        self.requested_max_results: int | None = None
        self.requested_message_ids: list[str] = []

    def list_message_ids(
        self,
        *,
        max_results: int,
    ) -> list[str]:
        self.requested_max_results = max_results

        return [
            "msg-001",
            "msg-002",
        ]

    def get_message(
        self,
        *,
        message_id: str,
    ) -> dict[str, object]:
        self.requested_message_ids.append(
            message_id
        )

        body = urlsafe_b64encode(
            f"Treść {message_id}".encode()
        ).decode("ascii")

        return {
            "id": message_id,
            "threadId": f"thread-{message_id}",
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
                        "value": "Zapytanie",
                    },
                ],
                "body": {
                    "data": body,
                },
            },
        }


def test_gmail_read_only_client_fetches_messages() -> None:
    gateway = FakeGmailGateway()

    client = GmailReadOnlyClient(
        gateway=gateway,
        max_results=25,
    )

    messages = client.list_messages()

    assert len(messages) == 2

    assert gateway.requested_max_results == 25

    assert gateway.requested_message_ids == [
        "msg-001",
        "msg-002",
    ]

    assert messages[0].message_id == "msg-001"
    assert messages[1].message_id == "msg-002"

    assert messages[0].subject == "Zapytanie"
    assert messages[0].body_text == "Treść msg-001"


def test_gmail_read_only_client_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError):
        GmailReadOnlyClient(
            gateway=FakeGmailGateway(),
            max_results=0,
        )