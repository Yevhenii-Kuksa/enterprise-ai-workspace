from collections.abc import Sequence
from typing import Any, Protocol

from app.integrations.file_storage import FileStorageItem
from app.integrations.sharepoint_adapter import SharePointFileAdapter


class SharePointGateway(Protocol):
    def list_items(
        self,
        *,
        page_size: int,
    ) -> Sequence[dict[str, Any]]:
        ...


class SharePointReadOnlyClient:
    def __init__(
        self,
        *,
        gateway: SharePointGateway,
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
        items = self.gateway.list_items(
            page_size=self.page_size,
        )

        return [
            SharePointFileAdapter.from_api_item(
                item
            )
            for item in items
            if "file" in item
        ]