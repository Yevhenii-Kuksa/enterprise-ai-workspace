from collections.abc import Sequence
from typing import Any, Protocol

from app.integrations.file_storage import FileStorageItem
from app.integrations.google_drive_adapter import GoogleDriveFileAdapter


class GoogleDriveGateway(Protocol):
    def list_files(
        self,
        *,
        page_size: int,
    ) -> Sequence[dict[str, Any]]:
        ...


class GoogleDriveReadOnlyClient:
    def __init__(
        self,
        *,
        gateway: GoogleDriveGateway,
        page_size: int = 100,
    ) -> None:
        if page_size < 1:
            raise ValueError(
                "page_size must be greater than zero."
            )

        self.gateway = gateway
        self.page_size = page_size

    def list_files(
        self,
    ) -> list[FileStorageItem]:
        files = self.gateway.list_files(
            page_size=self.page_size,
        )

        return [
            GoogleDriveFileAdapter.from_api_file(
                file_data
            )
            for file_data in files
        ]