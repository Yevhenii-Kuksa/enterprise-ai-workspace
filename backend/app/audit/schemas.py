import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None
    trace_id: uuid.UUID
    request_id: uuid.UUID
    action_id: uuid.UUID | None
    event_type: str
    resource_type: str | None
    resource_id: str | None
    metadata_json: dict[str, Any]
    created_at: datetime