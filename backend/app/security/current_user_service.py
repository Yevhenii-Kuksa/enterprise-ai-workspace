import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.security.current_user import CurrentUser
from app.security.service import get_user_permission_codes


def build_current_user(
    db: Session,
    user_id: uuid.UUID,
) -> CurrentUser | None:
    user = db.get(User, user_id)

    if user is None:
        return None

    permissions = get_user_permission_codes(db, user_id)

    return CurrentUser(
        id=user.id,
        organization_id=user.organization_id,
        department_id=user.department_id,
        is_active=user.is_active,
        permissions=permissions,
    )