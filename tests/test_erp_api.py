import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.db.dependencies import get_db
from app.erp.demo_adapter import DemoERPAdapter
from app.erp.dependencies import get_erp_service
from app.erp.schemas import ERPInventoryItem, ERPProduct, ERPSourceMetadata
from app.erp.service import ERPService
from app.main import app
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient


class FakeDb:
    def add(self, _event: object) -> None:
        pass

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        pass


client = TestClient(app)


def make_source(record_id: str) -> ERPSourceMetadata:
    return ERPSourceMetadata(
        source_system="demo_erp",
        source_record_id=record_id,
        last_synced_at=datetime(
            2026,
            9,
            17,
            12,
            0,
            tzinfo=UTC,
        ),
    )


def test_erp_api_requires_erp_read_permission() -> None:
    organization_id = uuid.uuid4()

    app.dependency_overrides[get_db] = lambda: FakeDb()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions={"knowledge.read"},
    )

    try:
        response = client.get("/api/erp/products")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Permission denied.",
        }
    finally:
        app.dependency_overrides.clear()


def test_erp_api_allows_erp_read_permission() -> None:
    organization_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions={"erp.read"},
    )

    try:
        response = client.get("/api/erp/products")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_erp_api_cannot_read_product_from_another_organization() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()
    product_id = uuid.uuid4()

    product = ERPProduct(
        id=product_id,
        organization_id=organization_b,
        sku="NX-B",
        name="Produkt B",
        unit="szt.",
        source=make_source("PRODUCT-B"),
    )

    service = ERPService(
        DemoERPAdapter(products=[product])
    )

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_a,
        is_active=True,
        permissions={"erp.read"},
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        response = client.get(
            f"/api/erp/products/{product_id}"
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "ERP product not found.",
        }
    finally:
        app.dependency_overrides.clear()


def test_erp_api_lists_only_current_organization_products() -> None:
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    product_a = ERPProduct(
        id=uuid.uuid4(),
        organization_id=organization_a,
        sku="NX-A",
        name="Produkt A",
        unit="szt.",
        source=make_source("PRODUCT-A"),
    )
    product_b = ERPProduct(
        id=uuid.uuid4(),
        organization_id=organization_b,
        sku="NX-B",
        name="Produkt B",
        unit="szt.",
        source=make_source("PRODUCT-B"),
    )

    service = ERPService(
        DemoERPAdapter(
            products=[product_a, product_b],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_a,
        is_active=True,
        permissions={"erp.read"},
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        response = client.get("/api/erp/products")

        assert response.status_code == 200
        assert response.json() == [
            product_a.model_dump(mode="json")
        ]
    finally:
        app.dependency_overrides.clear()


def test_erp_api_inventory_respects_product_and_location_filters() -> None:
    organization_id = uuid.uuid4()
    product_id = uuid.uuid4()
    location_id = uuid.uuid4()

    inventory = ERPInventoryItem(
        id=uuid.uuid4(),
        organization_id=organization_id,
        product_id=product_id,
        location_id=location_id,
        on_hand=Decimal("100"),
        reserved=Decimal("25"),
        source=make_source("INVENTORY-001"),
    )

    service = ERPService(
        DemoERPAdapter(
            inventory_items=[inventory],
        )
    )

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions={"erp.read"},
    )
    app.dependency_overrides[get_erp_service] = lambda: service

    try:
        response = client.get(
            "/api/erp/inventory",
            params={
                "product_id": str(product_id),
                "location_id": str(location_id),
            },
        )

        assert response.status_code == 200
        assert response.json() == [
            inventory.model_dump(mode="json")
        ]
    finally:
        app.dependency_overrides.clear()