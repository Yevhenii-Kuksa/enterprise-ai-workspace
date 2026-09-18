from base64 import urlsafe_b64decode
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from app.integrations.email_inbox import EmailMessage


class GmailMessageAdapter:
    @staticmethod
    def from_api_message(
        message: dict[str, Any],
    ) -> EmailMessage:
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        header_map = {
            str(header.get("name", "")).lower(): str(
                header.get("value", "")
            )
            for header in headers
        }

        message_id = str(message["id"])
        thread_id = message.get("threadId")

        sender = header_map.get(
            "from",
            "unknown",
        )

        recipients_raw = header_map.get(
            "to",
            "",
        )

        recipients = tuple(
            recipient.strip()
            for recipient in recipients_raw.split(",")
            if recipient.strip()
        )

        subject = header_map.get(
            "subject",
            "",
        )

        received_at = GmailMessageAdapter._received_at(
            message=message,
            header_map=header_map,
        )

        body_text = GmailMessageAdapter._extract_body_text(
            payload
        )

        return EmailMessage(
            message_id=message_id,
            thread_id=(
                str(thread_id)
                if thread_id is not None
                else None
            ),
            sender=sender,
            recipients=recipients,
            subject=subject,
            body_text=body_text,
            received_at=received_at,
            source_url=(
                "https://mail.google.com/mail/u/0/"
                f"#all/{message_id}"
            ),
        )

    @staticmethod
    def _received_at(
        *,
        message: dict[str, Any],
        header_map: dict[str, str],
    ) -> datetime:
        internal_date = message.get("internalDate")

        if internal_date is not None:
            milliseconds = int(
                str(internal_date)
            )

            return datetime.fromtimestamp(
                milliseconds / 1000,
                tz=UTC,
            )

        date_header = header_map.get("date")

        if date_header:
            parsed = parsedate_to_datetime(
                date_header
            )

            if parsed.tzinfo is None:
                return parsed.replace(
                    tzinfo=UTC
                )

            return parsed

        return datetime.now(UTC)

    @staticmethod
    def _extract_body_text(
        payload: dict[str, Any],
    ) -> str:
        mime_type = payload.get("mimeType")

        body = payload.get(
            "body",
            {},
        )

        if mime_type == "text/plain":
            data = body.get("data")

            if data:
                return GmailMessageAdapter._decode_body(
                    str(data)
                )

        for part in payload.get(
            "parts",
            [],
        ):
            if part.get("mimeType") == "text/plain":
                data = part.get(
                    "body",
                    {},
                ).get("data")

                if data:
                    return GmailMessageAdapter._decode_body(
                        str(data)
                    )

        return ""

    @staticmethod
    def _decode_body(
        data: str,
    ) -> str:
        padding = "=" * (
            -len(data) % 4
        )

        decoded = urlsafe_b64decode(
            data + padding
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )