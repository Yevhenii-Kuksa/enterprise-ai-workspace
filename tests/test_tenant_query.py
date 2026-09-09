import uuid

from app.db.session import SessionLocal
from app.models.department import Department  # noqa: F401
from app.models.organization import Organization
from app.models.permission import Permission  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.role_permission import role_permissions  # noqa: F401
from app.models.user import User
from app.models.user_role import user_roles  # noqa: F401
from app.security.tenant_query import apply_tenant_filter
from sqlalchemy import delete, select


def test_tenant_filter_isolates_users_by_organization() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()

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
                    id=user_a_id,
                    organization_id=organization_a_id,
                    email=f"{user_a_id.hex}@example.com",
                    full_name="User A",
                ),
                User(
                    id=user_b_id,
                    organization_id=organization_b_id,
                    email=f"{user_b_id.hex}@example.com",
                    full_name="User B",
                ),
            ]
        )
        db.commit()

        statement = apply_tenant_filter(
            select(User),
            User.organization_id,
            organization_a_id,
        )

        users = db.scalars(statement).all()

        assert [user.id for user in users] == [user_a_id]
        assert user_b_id not in {user.id for user in users}

        db.execute(delete(User).where(User.id.in_([user_a_id, user_b_id])))
        db.execute(
            delete(Organization).where(
                Organization.id.in_([organization_a_id, organization_b_id])
            )
        )
        db.commit()