import uuid

from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from app.security.permission_dependency import require_permission
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

knowledge_read_dependency = require_permission("knowledge.read")
required_permission_dependency = Depends(knowledge_read_dependency)


@app.get("/test-permission")
def protected_endpoint(
    current_user: CurrentUser = required_permission_dependency,
) -> dict[str, str]:
    return {"user_id": str(current_user.id)}


client = TestClient(app)


def test_permission_dependency_allows_required_permission() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"knowledge.read"},
    )

    try:
        response = client.get("/test-permission")

        assert response.status_code == 200
        assert response.json() == {"user_id": str(user_id)}
    finally:
        app.dependency_overrides.clear()


def test_permission_dependency_rejects_missing_permission() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"audit.read"},
    )

    try:
        response = client.get("/test-permission")

        assert response.status_code == 403
        assert response.json() == {"detail": "Permission denied."}
    finally:
        app.dependency_overrides.clear()