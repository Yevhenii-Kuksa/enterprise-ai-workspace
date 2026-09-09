import uuid

from app.security.current_user import CurrentUser
from app.security.tenant import get_tenant_id


def test_get_tenant_id_returns_current_user_organization_id() -> None:
    organization_id = uuid.uuid4()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        is_active=True,
        permissions=set(),
    )

    assert get_tenant_id(current_user) == organization_id