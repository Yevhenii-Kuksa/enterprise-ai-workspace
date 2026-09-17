from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit.service import record_audit_event
from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.db.dependencies import get_db
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user


def require_permission(
    permission_code: str,
) -> Callable[..., CurrentUser]:
    current_user_dependency = Depends(get_current_user)
    db_dependency = Depends(get_db)
    trace_context_dependency = Depends(get_trace_context)

    def dependency(
        current_user: CurrentUser = current_user_dependency,
        db: Session = db_dependency,
        trace_context: TraceContext = trace_context_dependency,
    ) -> CurrentUser:
        if permission_code not in current_user.permissions:
            record_audit_event(
                db,
                current_user=current_user,
                trace_context=trace_context,
                event_type="permission_denied",
                resource_type="permission",
                resource_id=permission_code,
                metadata={},
            )

            db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )

        return current_user

    return dependency