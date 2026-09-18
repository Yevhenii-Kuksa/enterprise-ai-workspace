from datetime import UTC, datetime

from app.integrations.file_storage import (
    FileStorageItem,
    FileStorageProvider,
)


class FakeFileStorageClient:
    def list_files(
        self,
    ) -> list[FileStorageItem]:
        return [
            FileStorageItem(
                file_id="file-001",
                name="Procedura magazynowa.pdf",
                mime_type="application/pdf",
                modified_at=datetime(
                    2026,
                    9,
                    18,
                    12,
                    0,
                    tzinfo=UTC,
                ),
                source_url=(
                    "https://drive.example/file-001"
                ),
                metadata={
                    "department": "magazyn",
                },
            )
        ]


def test_file_storage_provider_normalizes_files() -> None:
    provider = FileStorageProvider(
        source_system="google-drive",
        client=FakeFileStorageClient(),
    )

    records = provider.fetch_records()

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "google-drive"
    assert record.external_id == "file-001"
    assert record.record_type == "file"

    assert record.payload == {
        "name": "Procedura magazynowa.pdf",
        "mime_type": "application/pdf",
        "metadata": {
            "department": "magazyn",
        },
    }

    assert record.source_url == (
        "https://drive.example/file-001"
    )

    assert record.occurred_at == datetime(
        2026,
        9,
        18,
        12,
        0,
        tzinfo=UTC,
    )