from datetime import UTC, datetime

from app.integrations.email_inbox import (
    EmailInboxProvider,
    EmailMessage,
)


class FakeEmailClient:
    def list_messages(
        self,
    ) -> list[EmailMessage]:
        return [
            EmailMessage(
                message_id="msg-001",
                thread_id="thread-001",
                sender="klient@example.com",
                recipients=(
                    "sprzedaz@nexalvora.example",
                ),
                subject="Zapytanie o zamówienie",
                body_text="Proszę o informację o dostępności.",
                received_at=datetime(
                    2026,
                    9,
                    18,
                    10,
                    30,
                    tzinfo=UTC,
                ),
                source_url="https://mail.example/msg-001",
            )
        ]


def test_email_inbox_provider_normalizes_messages() -> None:
    provider = EmailInboxProvider(
        source_system="gmail",
        client=FakeEmailClient(),
    )

    records = provider.fetch_records()

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "gmail"
    assert record.external_id == "msg-001"
    assert record.record_type == "email_message"

    assert record.payload == {
        "thread_id": "thread-001",
        "sender": "klient@example.com",
        "recipients": [
            "sprzedaz@nexalvora.example",
        ],
        "subject": "Zapytanie o zamówienie",
        "body_text": "Proszę o informację o dostępności.",
    }

    assert record.occurred_at == datetime(
        2026,
        9,
        18,
        10,
        30,
        tzinfo=UTC,
    )