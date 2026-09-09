import uuid

from app.db.session import SessionLocal
from app.models.department import Department  # noqa: F401
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions
from app.models.user import User
from app.models.user_role import user_roles
from app.security.current_user_service import build_current_user
from sqlalchemy import delete


def test_build_current_user_returns_user_with_permissions() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    permission_id = uuid.uuid4()

    permission_code = f"test.current_user.{permission_id.hex[:8]}"

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
                full_name="Test Current User",
                is_active=True,
            )
        )
        db.add(
            Role(
                id=role_id,
                organization_id=organization_id,
                code=f"ROLE-{role_id.hex[:8]}",
                name="Test Role",
            )
        )
        db.add(
            Permission(
                id=permission_id,
                code=permission_code,
                name="Test Permission",
            )
        )

        db.flush()

        db.execute(
            user_roles.insert().values(
                user_id=user_id,
                role_id=role_id,
            )
        )
        db.execute(
            role_permissions.insert().values(
                role_id=role_id,
                permission_id=permission_id,
            )
        )
        db.commit()

        current_user = build_current_user(db, user_id)

        assert current_user is not None
        assert current_user.id == user_id
        assert current_user.organization_id == organization_id
        assert current_user.is_active is True
        assert current_user.permissions == {permission_code}

        db.execute(delete(role_permissions).where(role_permissions.c.role_id == role_id))
        db.execute(delete(user_roles).where(user_roles.c.user_id == user_id))
        db.execute(delete(Permission).where(Permission.id == permission_id))
        db.execute(delete(Role).where(Role.id == role_id))
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Organization).where(Organization.id == organization_id))
        db.commit()