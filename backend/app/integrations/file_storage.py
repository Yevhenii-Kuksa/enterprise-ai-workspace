from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.schemas import IntegrationRecord


class FileStorageItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    file_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=1000)
    mime_type: str = Field(min_length=1, max_length=255)

    modified_at: datetime | None = None
    source_url: str | None = None

    metadata: dict[str, str] = Field(
        default_factory=dict
    )


class FileStorageClient(Protocol):
    def list_files(
        self,
    ) -> Sequence[FileStorageItem]:
        ...


class FileStorageProvider:
    def __init__(
        self,
        *,
        source_system: str,
        client: FileStorageClient,
    ) -> None:
        self.source_system = source_system
        self.client = client

    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        files = self.client.list_files()

        return [
            IntegrationRecord(
                source_system=self.source_system,
                external_id=file.file_id,
                record_type="file",
                payload={
                    "name": file.name,
                    "mime_type": file.mime_type,
                    "metadata": file.metadata,
                },
                source_url=file.source_url,
                occurred_at=file.modified_at,
                fetched_at=datetime.now(
                    file.modified_at.tzinfo
                    if file.modified_at is not None
                    else None
                ),
            )
            for file in files
        ]