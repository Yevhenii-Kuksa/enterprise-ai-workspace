import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.db.dependencies import get_db
from app.erp.demo_adapter import DemoERPAdapter
from app.erp.dependencies import get_erp_service
from app.erp.schemas import (
    ERPInventoryItem,
    ERPOrder,
    ERPOrderStatus,
    ERPSourceMetadata,
)
from app.erp.service import ERPService
from app.main import app
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient

NOW = datetime.now(UTC)


class FakeDb:
    def add(self, _object: object) -> None:
        pass

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        pass


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=NOW,
    )


def make_user(
    *,
    organization_id: uuid.UUID,
) -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions={"executive.read"},
    )


def test_executive_briefing_api() -> None:
    organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("10"),
        reserved=Decimal("10"),
        source=make_source("INVENTORY-001"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=organization_id,
        order_number="ORD-001",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=2),
        confirmed_delivery_at=NOW - timedelta(hours=1),
        source=make_source("ORDER-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
            orders=[order],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get("/api/executive/briefing")

        assert response.status_code == 200

        data = response.json()

        assert data["organization_id"] == str(organization_id)
        assert data["title_pl"] == "Briefing zarządczy"

        assert data["summary"]["inventory_items"] == 1
        assert data["summary"]["unavailable_inventory_items"] == 1
        assert data["summary"]["active_orders"] == 1
        assert data["summary"]["delayed_orders"] == 1

        assert len(data["inventory_risks"]) == 1
        assert (
            data["inventory_risks"][0]["message_pl"]
            == "Brak dostępnego zapasu."
        )

        assert len(data["order_exceptions"]) == 1
        assert (
            data["order_exceptions"][0]["message_pl"]
            == "Zamówienie jest opóźnione."
        )

        assert data["approvals"] == {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
        }

        assert len(data["evidence"]) == 2
    finally:
        app.dependency_overrides.clear()


def test_executive_briefing_api_is_tenant_isolated() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("0"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-OTHER"),
    )

    order = ERPOrder(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        order_number="ORD-OTHER",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW - timedelta(days=2),
        confirmed_delivery_at=NOW - timedelta(hours=1),
        source=make_source("ORDER-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
            orders=[order],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get("/api/executive/briefing")

        assert response.status_code == 200

        data = response.json()

        assert data["summary"]["inventory_items"] == 0
        assert data["summary"]["active_orders"] == 0
        assert data["inventory_risks"] == []
        assert data["order_exceptions"] == []
        assert data["evidence"] == []
    finally:
        app.dependency_overrides.clear()


def test_executive_briefing_api_requires_permission() -> None:
    organization_id = uuid.uuid4()

    user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions=set(),
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: FakeDb()

    try:
        client = TestClient(app)

        response = client.get("/api/executive/briefing")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Permission denied.",
        }
    finally:
        app.dependency_overrides.clear()