import uuid

from app.security.current_user import CurrentUser


def test_current_user_stores_identity_and_permissions() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={
            "knowledge.read",
            "audit.read",
        },
    )

    assert current_user.id == user_id
    assert current_user.organization_id == organization_id
    assert current_user.is_active is True
    assert current_user.permissions == {
        "knowledge.read",
        "audit.read",
    }