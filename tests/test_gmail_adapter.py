from base64 import urlsafe_b64encode
from datetime import UTC, datetime

from app.integrations.gmail_adapter import GmailMessageAdapter


def test_gmail_adapter_normalizes_api_message() -> None:
    body = urlsafe_b64encode(
        "Dzień dobry, proszę o ofertę.".encode()
    ).decode("ascii")

    message = {
        "id": "gmail-msg-001",
        "threadId": "gmail-thread-001",
        "internalDate": "1789727400000",
        "payload": {
            "mimeType": "multipart/alternative",
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
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": body,
                    },
                }
            ],
        },
    }

    normalized = GmailMessageAdapter.from_api_message(
        message
    )

    assert normalized.message_id == "gmail-msg-001"
    assert normalized.thread_id == "gmail-thread-001"

    assert normalized.sender == "klient@example.com"

    assert normalized.recipients == (
        "sprzedaz@nexalvora.example",
    )

    assert normalized.subject == "Zapytanie ofertowe"

    assert (
        normalized.body_text
        == "Dzień dobry, proszę o ofertę."
    )

    assert normalized.received_at == datetime(
        2026,
        9,
        18,
        10,
        30,
        tzinfo=UTC,
    )

    assert normalized.source_url is not None