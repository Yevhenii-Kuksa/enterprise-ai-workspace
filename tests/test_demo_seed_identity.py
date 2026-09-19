from app.db.session import SessionLocal
from app.demo.ids import NEXALVORA_ORGANIZATION_ID
from app.demo.organization import NEXALVORA_DEPARTMENTS
from app.demo.seed import seed_demo_identity
from app.demo.users import NEXALVORA_USERS
from app.models.department import Department
from app.models.organization import Organization
from app.models.user import User
from sqlalchemy import func, select


def test_seed_demo_identity_is_idempotent() -> None:
    with SessionLocal() as db:
        seed_demo_identity(db)
        db.flush()

        seed_demo_identity(db)
        db.flush()

        organization_count = db.scalar(
            select(func.count())
            .select_from(Organization)
            .where(Organization.id == NEXALVORA_ORGANIZATION_ID)
        )

        department_count = db.scalar(
            select(func.count())
            .select_from(Department)
            .where(
                Department.organization_id
                == NEXALVORA_ORGANIZATION_ID
            )
        )

        user_count = db.scalar(
            select(func.count())
            .select_from(User)
            .where(
                User.organization_id
                == NEXALVORA_ORGANIZATION_ID
            )
        )

        assert organization_count == 1
        assert department_count == len(NEXALVORA_DEPARTMENTS)
        assert user_count == len(NEXALVORA_USERS)

        db.rollback()