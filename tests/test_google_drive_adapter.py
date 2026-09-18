from datetime import UTC, datetime

from app.integrations.google_drive_adapter import (
    GoogleDriveFileAdapter,
)


def test_google_drive_adapter_normalizes_file() -> None:
    file_data = {
        "id": "file-001",
        "name": "Procedura magazynowa.pdf",
        "mimeType": "application/pdf",
        "modifiedTime": "2026-09-18T12:00:00Z",
        "driveId": "drive-001",
        "webViewLink": (
            "https://drive.google.com/file/d/file-001/view"
        ),
    }

    normalized = GoogleDriveFileAdapter.from_api_file(
        file_data
    )

    assert normalized.file_id == "file-001"
    assert normalized.name == "Procedura magazynowa.pdf"
    assert normalized.mime_type == "application/pdf"

    assert normalized.modified_at == datetime(
        2026,
        9,
        18,
        12,
        0,
        tzinfo=UTC,
    )

    assert normalized.source_url == (
        "https://drive.google.com/open?id=file-001"
    )

    assert normalized.metadata == {
        "drive_id": "drive-001",
        "web_view_link": (
            "https://drive.google.com/file/d/file-001/view"
        ),
    }