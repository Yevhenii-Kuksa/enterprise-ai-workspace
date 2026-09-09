import uuid

from app.security.current_user import CurrentUser


def get_tenant_id(current_user: CurrentUser) -> uuid.UUID:
    return current_user.organization_id