import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions
from app.models.user import User
from app.models.user_role import user_roles


def get_user_permission_codes(
    db: Session,
    user_id: uuid.UUID,
) -> set[str]:
    statement = (
        select(Permission.code)
        .join(
            role_permissions,
            role_permissions.c.permission_id == Permission.id,
        )
        .join(
            Role,
            Role.id == role_permissions.c.role_id,
        )
        .join(
            user_roles,
            user_roles.c.role_id == Role.id,
        )
        .join(
            User,
            User.id == user_roles.c.user_id,
        )
        .where(
            user_roles.c.user_id == user_id,
            Role.organization_id == User.organization_id,
        )
        .distinct()
    )

    return set(db.scalars(statement).all())