from datetime import datetime
from typing import Any

from app.integrations.file_storage import FileStorageItem


class GoogleDriveFileAdapter:
    @staticmethod
    def from_api_file(
        file_data: dict[str, Any],
    ) -> FileStorageItem:
        modified_at_raw = file_data.get("modifiedTime")

        modified_at = (
            datetime.fromisoformat(
                str(modified_at_raw).replace("Z", "+00:00")
            )
            if modified_at_raw
            else None
        )

        file_id = str(file_data["id"])

        return FileStorageItem(
            file_id=file_id,
            name=str(file_data["name"]),
            mime_type=str(
                file_data.get(
                    "mimeType",
                    "application/octet-stream",
                )
            ),
            modified_at=modified_at,
            source_url=(
                "https://drive.google.com/open"
                f"?id={file_id}"
            ),
            metadata={
                "drive_id": str(
                    file_data.get("driveId", "")
                ),
                "web_view_link": str(
                    file_data.get("webViewLink", "")
                ),
            },
        )