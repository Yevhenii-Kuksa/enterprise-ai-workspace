from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.demo.ids import NEXALVORA_ORGANIZATION_ID
from app.demo.organization import (
    NEXALVORA_DEPARTMENTS,
    NEXALVORA_ORGANIZATION,
)
from app.demo.users import NEXALVORA_USERS
from app.models.department import Department
from app.models.organization import Organization
from app.models.user import User


def seed_organization(db: Session) -> None:
    organization = db.get(
        Organization,
        NEXALVORA_ORGANIZATION.id,
    )

    if organization is None:
        organization = Organization(
            id=NEXALVORA_ORGANIZATION.id,
            code=NEXALVORA_ORGANIZATION.code,
            name=NEXALVORA_ORGANIZATION.name,
        )
        db.add(organization)
        return

    organization.code = NEXALVORA_ORGANIZATION.code
    organization.name = NEXALVORA_ORGANIZATION.name


def seed_departments(db: Session) -> None:
    for demo_department in NEXALVORA_DEPARTMENTS:
        department = db.get(
            Department,
            demo_department.id,
        )

        if department is None:
            department = Department(
                id=demo_department.id,
                organization_id=demo_department.organization_id,
                code=demo_department.code,
                name=demo_department.name,
            )
            db.add(department)
            continue

        department.organization_id = demo_department.organization_id
        department.code = demo_department.code
        department.name = demo_department.name


def seed_users(db: Session) -> None:
    for demo_user in NEXALVORA_USERS:
        user = db.get(
            User,
            demo_user.id,
        )

        if user is None:
            user = User(
                id=demo_user.id,
                organization_id=NEXALVORA_ORGANIZATION_ID,
                department_id=demo_user.department_id,
                email=demo_user.email,
                full_name=demo_user.full_name,
                is_active=demo_user.is_active,
            )
            db.add(user)
            continue

        user.organization_id = NEXALVORA_ORGANIZATION_ID
        user.department_id = demo_user.department_id
        user.email = demo_user.email
        user.full_name = demo_user.full_name
        user.is_active = demo_user.is_active


def seed_demo_identity(db: Session) -> None:
    seed_organization(db)
    db.flush()

    seed_departments(db)
    db.flush()

    seed_users(db)


def seed_demo_data() -> None:
    with SessionLocal() as db:
        seed_demo_identity(db)
        db.commit()


if __name__ == "__main__":
    seed_demo_data()