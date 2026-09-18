from datetime import UTC, datetime

from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
    IntegrationRecord,
)


def test_integration_contracts() -> None:
    definition = IntegrationDefinition(
        key="google-drive",
        kind=IntegrationKind.FILE_STORAGE,
        provider="google",
        capabilities=(
            IntegrationCapability.READ_FILES,
        ),
    )

    record = IntegrationRecord(
        source_system="google-drive",
        external_id="file-001",
        record_type="document",
        payload={
            "name": "Procedura magazynowa.pdf",
        },
        source_url="https://example.test/file-001",
        fetched_at=datetime.now(UTC),
    )

    assert definition.key == "google-drive"
    assert definition.kind == IntegrationKind.FILE_STORAGE
    assert definition.capabilities == (
        IntegrationCapability.READ_FILES,
    )

    assert record.source_system == "google-drive"
    assert record.external_id == "file-001"
    assert record.payload["name"] == "Procedura magazynowa.pdf"