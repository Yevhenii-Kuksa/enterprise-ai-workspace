from typing import Any

from app.integrations.google_drive_gateway import (
    GoogleDriveApiGateway,
)


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


class FakeFilesResource:
    def __init__(self) -> None:
        self.list_call: dict[str, Any] | None = None

    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        self.list_call = kwargs

        return FakeRequest(
            {
                "files": [
                    {
                        "id": "file-001",
                        "name": "Procedura magazynowa.pdf",
                        "mimeType": "application/pdf",
                        "modifiedTime": "2026-09-18T12:00:00Z",
                        "driveId": "drive-001",
                        "webViewLink": (
                            "https://drive.google.com/"
                            "file/d/file-001/view"
                        ),
                    }
                ]
            }
        )


class FakeGoogleDriveService:
    def __init__(self) -> None:
        self.files_resource = FakeFilesResource()

    def files(
        self,
    ) -> FakeFilesResource:
        return self.files_resource


def test_google_drive_gateway_lists_files() -> None:
    service = FakeGoogleDriveService()

    gateway = GoogleDriveApiGateway(
        service=service,
    )

    files = gateway.list_files(
        page_size=25,
    )

    assert len(files) == 1
    assert files[0]["id"] == "file-001"

    assert service.files_resource.list_call == {
        "pageSize": 25,
        "fields": (
            "files("
            "id,"
            "name,"
            "mimeType,"
            "modifiedTime,"
            "driveId,"
            "webViewLink"
            ")"
        ),
    }