import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.erp.demo_adapter import DemoERPAdapter
from app.erp.dependencies import get_erp_service
from app.erp.schemas import (
    ERPInventoryItem,
    ERPInventoryReservation,
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
        permissions={"erp.read"},
    )


def test_inventory_availability_api() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-001"),
    )

    reservation = ERPInventoryReservation(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        quantity=Decimal("25"),
        expires_at=NOW + timedelta(hours=1),
        source=make_source("RESERVATION-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
            inventory_reservations=[reservation],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get(
            "/api/erp/intelligence/inventory/availability"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["on_hand"] == "100"
        assert data[0]["reserved"] == "25"
        assert data[0]["available"] == "75"
        assert data[0]["state"] == "limited"
    finally:
        app.dependency_overrides.clear()


def test_inventory_availability_api_is_tenant_isolated() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    item = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=other_organization_id,
        product_id=uuid.uuid4(),
        location_id=uuid.uuid4(),
        on_hand=Decimal("100"),
        reserved=Decimal("0"),
        source=make_source("INVENTORY-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[item],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get(
            "/api/erp/intelligence/inventory/availability"
        )

        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_order_delay_state_api() -> None:
    organization_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = ERPOrder(
        id=order_id,
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
            orders=[order],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get(
            f"/api/erp/intelligence/orders/{order_id}/delay-state"
        )

        assert response.status_code == 200
        assert response.json() == "delayed"
    finally:
        app.dependency_overrides.clear()


def test_order_delay_state_api_hides_cross_tenant_order() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    order_id = uuid.uuid4()

    order = ERPOrder(
        id=order_id,
        organization_id=other_organization_id,
        order_number="ORD-OTHER",
        customer_id=uuid.uuid4(),
        status=ERPOrderStatus.PROCESSING,
        ordered_at=NOW,
        source=make_source("ORDER-OTHER"),
    )

    service = ERPService(
        DemoERPAdapter(
            orders=[order],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        organization_id=organization_id,
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.get(
            f"/api/erp/intelligence/orders/{order_id}/delay-state"
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "ERP order not found.",
        }
    finally:
        app.dependency_overrides.clear()