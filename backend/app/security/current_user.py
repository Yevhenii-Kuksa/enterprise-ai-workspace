import uuid

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    department_id: uuid.UUID | None = None
    is_active: bool
    permissions: set[str]