from datetime import UTC, datetime

from app.integrations.erp_adapter import ErpRecordAdapter


def test_erp_adapter_normalizes_record() -> None:
    occurred_at = datetime(
        2026,
        9,
        18,
        8,
        30,
        tzinfo=UTC,
    )

    record = ErpRecordAdapter.from_record(
        source_system="erp",
        record_type="order",
        external_id="ORDER-001",
        payload={
            "status": "confirmed",
            "customer_id": "CUSTOMER-001",
            "total_net": 12500.0,
        },
        occurred_at=occurred_at,
    )

    assert record.source_system == "erp"
    assert record.external_id == "ORDER-001"
    assert record.record_type == "order"

    assert record.payload == {
        "status": "confirmed",
        "customer_id": "CUSTOMER-001",
        "total_net": 12500.0,
    }

    assert record.occurred_at == occurred_at