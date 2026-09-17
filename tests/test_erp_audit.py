import uuid

from app.db.dependencies import get_db
from app.main import app
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient


class FakeDb:
    def __init__(self) -> None:
        self.events: list[object] = []

    def add(self, event: object) -> None:
        self.events.append(event)

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        pass


client = TestClient(app)


def test_erp_permission_denial_creates_audit_event() -> None:
    organization_id = uuid.uuid4()
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions={"knowledge.read"},
    )

    try:
        response = client.get("/api/erp/products")

        assert response.status_code == 403
        assert len(fake_db.events) == 1

        event = fake_db.events[0]

        assert event.event_type == "permission_denied"
        assert event.resource_type == "permission"
        assert event.resource_id == "erp.read"
        assert event.organization_id == organization_id
    finally:
        app.dependency_overrides.clear()