import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.trace_context import TraceContext
from app.models.audit_event import AuditEvent
from app.security.current_user import CurrentUser


def record_audit_event(
    session: Session,
    *,
    current_user: CurrentUser,
    trace_context: TraceContext,
    event_type: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    normalized_event_type = event_type.strip()

    if not normalized_event_type:
        raise ValueError("Audit event type must not be empty.")

    event = AuditEvent(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        trace_id=trace_context.trace_id,
        request_id=trace_context.request_id,
        action_id=trace_context.action_id,
        event_type=normalized_event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata or {},
    )

    session.add(event)
    session.flush()

    return event


def build_audit_events_query(
    *,
    current_user: CurrentUser,
    event_type: str | None = None,
    user_id: uuid.UUID | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> Select[tuple[AuditEvent]]:
    query = select(AuditEvent).where(
        AuditEvent.organization_id
        == current_user.organization_id
    )

    if event_type is not None:
        normalized_event_type = event_type.strip()

        if normalized_event_type:
            query = query.where(
                AuditEvent.event_type == normalized_event_type
            )

    if user_id is not None:
        query = query.where(
            AuditEvent.user_id == user_id
        )

    if created_from is not None:
        query = query.where(
            AuditEvent.created_at >= created_from
        )

    if created_to is not None:
        query = query.where(
            AuditEvent.created_at <= created_to
        )

    return query.order_by(
        AuditEvent.created_at.desc(),
        AuditEvent.id.desc(),
    )


def list_audit_events(
    session: Session,
    *,
    current_user: CurrentUser,
    event_type: str | None = None,
    user_id: uuid.UUID | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    limit: int = 100,
) -> list[AuditEvent]:
    if limit < 1 or limit > 500:
        raise ValueError(
            "Audit event limit must be between 1 and 500."
        )

    query = build_audit_events_query(
        current_user=current_user,
        event_type=event_type,
        user_id=user_id,
        created_from=created_from,
        created_to=created_to,
    ).limit(limit)

    return list(
        session.scalars(query).all()
    )