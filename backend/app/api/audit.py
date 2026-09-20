import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.audit.schemas import AuditEventResponse
from app.audit.service import (
    AuditQueryValidationError,
    list_audit_events,
)
from app.db.dependencies import get_db
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit & Access"],
)

db_dependency = Depends(get_db)
audit_reader_dependency = Depends(
    require_permission("audit.read")
)


@router.get(
    "/events",
    response_model=list[AuditEventResponse],
)
def get_audit_events(
    event_type: Annotated[
        str | None,
        Query(
            max_length=100,
        ),
    ] = None,
    user_id: uuid.UUID | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
        ),
    ] = 100,
    db: Session = db_dependency,
    current_user: CurrentUser = audit_reader_dependency,
) -> list[AuditEventResponse]:
    try:
        events = list_audit_events(
            db,
            current_user=current_user,
            event_type=event_type,
            user_id=user_id,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
        )
    except AuditQueryValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return [
        AuditEventResponse.model_validate(event)
        for event in events
    ]