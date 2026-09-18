from datetime import UTC, datetime

from app.integrations.provider import IntegrationProvider
from app.integrations.schemas import IntegrationRecord


class FakeProvider:
    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        return [
            IntegrationRecord(
                source_system="demo",
                external_id="record-001",
                record_type="document",
                payload={
                    "name": "Demo record",
                },
                fetched_at=datetime.now(UTC),
            )
        ]


def use_provider(
    provider: IntegrationProvider,
) -> list[IntegrationRecord]:
    return list(
        provider.fetch_records()
    )


def test_provider_contract_returns_records() -> None:
    records = use_provider(
        FakeProvider()
    )

    assert len(records) == 1
    assert records[0].source_system == "demo"
    assert records[0].external_id == "record-001"