from datetime import datetime
from typing import Any

from app.integrations.file_storage import FileStorageItem


class SharePointFileAdapter:
    @staticmethod
    def from_api_item(
        item: dict[str, Any],
    ) -> FileStorageItem:
        modified_at_raw = item.get(
            "lastModifiedDateTime"
        )

        modified_at = (
            datetime.fromisoformat(
                str(modified_at_raw).replace(
                    "Z",
                    "+00:00",
                )
            )
            if modified_at_raw
            else None
        )

        item_id = str(item["id"])

        return FileStorageItem(
            file_id=item_id,
            name=str(item["name"]),
            mime_type=str(
                item.get(
                    "file",
                    {},
                ).get(
                    "mimeType",
                    "application/octet-stream",
                )
            ),
            modified_at=modified_at,
            source_url=(
                str(item.get("webUrl"))
                if item.get("webUrl")
                else None
            ),
            metadata={
                "parent_drive_id": str(
                    item.get(
                        "parentReference",
                        {},
                    ).get(
                        "driveId",
                        "",
                    )
                ),
                "parent_path": str(
                    item.get(
                        "parentReference",
                        {},
                    ).get(
                        "path",
                        "",
                    )
                ),
            },
        )