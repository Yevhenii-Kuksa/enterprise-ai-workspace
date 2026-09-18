from datetime import UTC, datetime

from app.integrations.sharepoint_adapter import (
    SharePointFileAdapter,
)


def test_sharepoint_adapter_normalizes_file() -> None:
    item = {
        "id": "sp-file-001",
        "name": "Instrukcja BHP.pdf",
        "lastModifiedDateTime": (
            "2026-09-18T14:00:00Z"
        ),
        "webUrl": (
            "https://nexalvora.sharepoint.com/"
            "documents/sp-file-001"
        ),
        "file": {
            "mimeType": "application/pdf",
        },
        "parentReference": {
            "driveId": "drive-001",
            "path": (
                "/drives/drive-001/root:/Procedury"
            ),
        },
    }

    normalized = SharePointFileAdapter.from_api_item(
        item
    )

    assert normalized.file_id == "sp-file-001"
    assert normalized.name == "Instrukcja BHP.pdf"
    assert normalized.mime_type == "application/pdf"

    assert normalized.modified_at == datetime(
        2026,
        9,
        18,
        14,
        0,
        tzinfo=UTC,
    )

    assert normalized.source_url == (
        "https://nexalvora.sharepoint.com/"
        "documents/sp-file-001"
    )

    assert normalized.metadata == {
        "parent_drive_id": "drive-001",
        "parent_path": (
            "/drives/drive-001/root:/Procedury"
        ),
    }