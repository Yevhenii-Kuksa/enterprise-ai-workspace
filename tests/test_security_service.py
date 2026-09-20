import uuid

from app.db.session import SessionLocal
from app.models.department import Department  # noqa: F401
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions
from app.models.user import User
from app.models.user_role import user_roles
from app.security.service import get_user_permission_codes
from sqlalchemy import delete


def test_get_user_permission_codes_returns_permissions_from_roles() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    permission_id = uuid.uuid4()

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
                full_name="Test User",
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
                code=f"test.permission.{permission_id.hex[:8]}",
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

        permissions = get_user_permission_codes(
            db,
            user_id,
        )

        assert permissions == {
            f"test.permission.{permission_id.hex[:8]}",
        }

        db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role_id
            )
        )
        db.execute(
            delete(user_roles).where(
                user_roles.c.user_id == user_id
            )
        )
        db.execute(
            delete(Permission).where(
                Permission.id == permission_id
            )
        )
        db.execute(
            delete(Role).where(
                Role.id == role_id
            )
        )
        db.execute(
            delete(User).where(
                User.id == user_id
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )
        db.commit()


def test_get_user_permission_codes_rejects_cross_tenant_role() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()
    user_id = uuid.uuid4()
    foreign_role_id = uuid.uuid4()
    permission_id = uuid.uuid4()

    permission_code = (
        f"test.cross_tenant.{permission_id.hex[:8]}"
    )

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"TEST-A-{organization_a_id.hex[:8]}",
                    name="Test Organization A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"TEST-B-{organization_b_id.hex[:8]}",
                    name="Test Organization B",
                ),
                User(
                    id=user_id,
                    organization_id=organization_a_id,
                    email=f"{user_id.hex}@example.com",
                    full_name="Tenant A User",
                ),
                Role(
                    id=foreign_role_id,
                    organization_id=organization_b_id,
                    code=f"ROLE-{foreign_role_id.hex[:8]}",
                    name="Tenant B Role",
                ),
                Permission(
                    id=permission_id,
                    code=permission_code,
                    name="Cross Tenant Test Permission",
                ),
            ]
        )

        db.flush()

        db.execute(
            user_roles.insert().values(
                user_id=user_id,
                role_id=foreign_role_id,
            )
        )
        db.execute(
            role_permissions.insert().values(
                role_id=foreign_role_id,
                permission_id=permission_id,
            )
        )
        db.commit()

        permissions = get_user_permission_codes(
            db,
            user_id,
        )

        assert permission_code not in permissions
        assert permissions == set()

        db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == foreign_role_id
            )
        )
        db.execute(
            delete(user_roles).where(
                user_roles.c.user_id == user_id
            )
        )
        db.execute(
            delete(Permission).where(
                Permission.id == permission_id
            )
        )
        db.execute(
            delete(Role).where(
                Role.id == foreign_role_id
            )
        )
        db.execute(
            delete(User).where(
                User.id == user_id
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id.in_(
                    [
                        organization_a_id,
                        organization_b_id,
                    ]
                )
            )
        )
        db.commit()