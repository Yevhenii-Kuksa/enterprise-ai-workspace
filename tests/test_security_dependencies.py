import uuid

from app.db.session import SessionLocal
from app.models.department import Department  # noqa: F401
from app.models.organization import Organization
from app.models.permission import Permission  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.role_permission import role_permissions  # noqa: F401
from app.models.user import User
from app.models.user_role import user_roles  # noqa: F401
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete

app = FastAPI()

current_user_dependency = Depends(get_current_user)


@app.get("/test-protected")
def protected_endpoint(
    current_user: CurrentUser = current_user_dependency,
) -> dict[str, str]:
    return {"user_id": str(current_user.id)}


client = TestClient(app)


def test_get_current_user_rejects_missing_identity() -> None:
    response = client.get("/test-protected")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing user identity."}


def test_get_current_user_rejects_invalid_identity() -> None:
    response = client.get(
        "/test-protected",
        headers={"X-User-ID": "not-a-valid-uuid"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid user identity."}


def test_get_current_user_rejects_unknown_user() -> None:
    response = client.get(
        "/test-protected",
        headers={"X-User-ID": "00000000-0000-0000-0000-000000000001"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User not found."}


def test_get_current_user_rejects_inactive_user() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"TEST-{organization_id.hex[:8]}",
                name="Test Organization",
            )
        )
        db.add(
            User(
                id=user_id,
                organization_id=organization_id,
                email=f"{user_id.hex}@example.com",
                full_name="Inactive User",
                is_active=False,
            )
        )
        db.commit()

    response = client.get(
        "/test-protected",
        headers={"X-User-ID": str(user_id)},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Inactive user."}

    with SessionLocal() as db:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Organization).where(Organization.id == organization_id))
        db.commit()

def test_get_current_user_allows_active_user() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"TEST-{organization_id.hex[:8]}",
                name="Test Organization",
            )
        )
        db.add(
            User(
                id=user_id,
                organization_id=organization_id,
                email=f"{user_id.hex}@example.com",
                full_name="Active User",
                is_active=True,
            )
        )
        db.commit()

    response = client.get(
        "/test-protected",
        headers={"X-User-ID": str(user_id)},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user_id)}

    with SessionLocal() as db:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Organization).where(Organization.id == organization_id))
        db.commit()