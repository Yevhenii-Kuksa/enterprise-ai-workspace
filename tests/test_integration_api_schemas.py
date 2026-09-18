from datetime import UTC, datetime

from app.integrations.api_schemas import (
    IntegrationRecordResponse,
    IntegrationSummaryResponse,
)
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationKind,
    IntegrationRecord,
    IntegrationStatus,
)


def test_integration_summary_response() -> None:
    response = IntegrationSummaryResponse(
        key="google-drive",
        kind=IntegrationKind.FILE_STORAGE,
        provider="google",
        capabilities=(
            IntegrationCapability.READ_FILES,
        ),
        enabled=True,
        status=IntegrationStatus.READY,
    )

    assert response.key == "google-drive"
    assert response.status == IntegrationStatus.READY


def test_integration_record_response_from_record() -> None:
    fetched_at = datetime(
        2026,
        9,
        18,
        15,
        0,
        tzinfo=UTC,
    )

    record = IntegrationRecord(
        source_system="google-drive",
        external_id="file-001",
        record_type="file",
        payload={
            "name": "Procedura.pdf",
        },
        source_url="https://example.test/file-001",
        occurred_at=None,
        fetched_at=fetched_at,
    )

    response = IntegrationRecordResponse.from_record(
        record
    )

    assert response.source_system == "google-drive"
    assert response.external_id == "file-001"
    assert response.record_type == "file"
    assert response.payload == {
        "name": "Procedura.pdf",
    }
    assert response.fetched_at == fetched_at