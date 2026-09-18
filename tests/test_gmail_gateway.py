from typing import Any

from app.integrations.gmail_gateway import GmailApiGateway


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
    def __init__(self) -> None:
        self.list_call: dict[str, Any] | None = None
        self.get_call: dict[str, Any] | None = None

    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        self.list_call = kwargs

        return FakeRequest(
            {
                "messages": [
                    {"id": "msg-001"},
                    {"id": "msg-002"},
                ]
            }
        )

    def get(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        self.get_call = kwargs

        return FakeRequest(
            {
                "id": kwargs["id"],
                "threadId": "thread-001",
                "payload": {},
            }
        )


class FakeUsersResource:
    def __init__(
        self,
        messages: FakeMessagesResource,
    ) -> None:
        self._messages = messages

    def messages(
        self,
    ) -> FakeMessagesResource:
        return self._messages


class FakeGmailService:
    def __init__(self) -> None:
        self.messages_resource = FakeMessagesResource()
        self.users_resource = FakeUsersResource(
            self.messages_resource
        )

    def users(
        self,
    ) -> FakeUsersResource:
        return self.users_resource


def test_gateway_lists_message_ids() -> None:
    service = FakeGmailService()

    gateway = GmailApiGateway(
        service=service,
    )

    message_ids = gateway.list_message_ids(
        max_results=25,
    )

    assert message_ids == [
        "msg-001",
        "msg-002",
    ]

    assert service.messages_resource.list_call == {
        "userId": "me",
        "maxResults": 25,
    }


def test_gateway_gets_full_message() -> None:
    service = FakeGmailService()

    gateway = GmailApiGateway(
        service=service,
    )

    message = gateway.get_message(
        message_id="msg-001",
    )

    assert message["id"] == "msg-001"

    assert service.messages_resource.get_call == {
        "userId": "me",
        "id": "msg-001",
        "format": "full",
    }