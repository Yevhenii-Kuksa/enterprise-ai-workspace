import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.audit.service import list_audit_events, record_audit_event
from app.core.trace_context import TraceContext
from app.db.session import SessionLocal
from app.models.audit_event import AuditEvent
from app.models.organization import Organization
from app.models.user import User
from app.security.current_user import CurrentUser
from sqlalchemy import delete


def _current_user(
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions=set(),
    )


def test_record_audit_event_persists_event_with_trace_context() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    trace_context = TraceContext.create()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"AUDIT-{organization_id.hex[:8]}",
                name="Audit Test Organization",
            )
        )
        db.add(
            User(
                id=user_id,
                organization_id=organization_id,
                email=f"{user_id.hex}@example.com",
                full_name="Audit Test User",
            )
        )
        db.commit()

        current_user = _current_user(
            user_id=user_id,
            organization_id=organization_id,
        )

        event = record_audit_event(
            db,
            current_user=current_user,
            trace_context=trace_context,
            event_type="knowledge_search",
            resource_type="document",
            resource_id="document-123",
            metadata={"result_count": 3},
        )
        db.commit()

        event_id = event.id

        persisted = db.get(AuditEvent, event_id)

        assert persisted is not None
        assert persisted.organization_id == organization_id
        assert persisted.user_id == user_id
        assert persisted.trace_id == trace_context.trace_id
        assert persisted.request_id == trace_context.request_id
        assert persisted.action_id == trace_context.action_id
        assert persisted.event_type == "knowledge_search"
        assert persisted.resource_type == "document"
        assert persisted.resource_id == "document-123"
        assert persisted.metadata_json == {"result_count": 3}

        db.execute(delete(AuditEvent).where(AuditEvent.id == event_id))
        db.execute(delete(User).where(User.id == user_id))
        db.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )
        db.commit()


def test_list_audit_events_isolates_organizations() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"AUD-A-{organization_a_id.hex[:8]}",
                    name="Audit Organization A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"AUD-B-{organization_b_id.hex[:8]}",
                    name="Audit Organization B",
                ),
                User(
                    id=user_a_id,
                    organization_id=organization_a_id,
                    email=f"{user_a_id.hex}@example.com",
                    full_name="Audit User A",
                ),
                User(
                    id=user_b_id,
                    organization_id=organization_b_id,
                    email=f"{user_b_id.hex}@example.com",
                    full_name="Audit User B",
                ),
            ]
        )
        db.commit()

        current_user_a = _current_user(
            user_id=user_a_id,
            organization_id=organization_a_id,
        )
        current_user_b = _current_user(
            user_id=user_b_id,
            organization_id=organization_b_id,
        )

        event_a = record_audit_event(
            db,
            current_user=current_user_a,
            trace_context=TraceContext.create(),
            event_type="knowledge_search",
        )
        event_b = record_audit_event(
            db,
            current_user=current_user_b,
            trace_context=TraceContext.create(),
            event_type="rag_query",
        )
        db.commit()

        events_for_a = list_audit_events(
            db,
            current_user=current_user_a,
        )

        event_ids = {event.id for event in events_for_a}

        assert event_a.id in event_ids
        assert event_b.id not in event_ids

        db.execute(
            delete(AuditEvent).where(
                AuditEvent.id.in_([event_a.id, event_b.id])
            )
        )
        db.execute(
            delete(User).where(
                User.id.in_([user_a_id, user_b_id])
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id.in_(
                    [organization_a_id, organization_b_id]
                )
            )
        )
        db.commit()


def test_list_audit_events_filters_events() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"AUD-F-{organization_id.hex[:8]}",
                name="Audit Filter Organization",
            )
        )
        db.add_all(
            [
                User(
                    id=user_id,
                    organization_id=organization_id,
                    email=f"{user_id.hex}@example.com",
                    full_name="Audit Filter User",
                ),
                User(
                    id=other_user_id,
                    organization_id=organization_id,
                    email=f"{other_user_id.hex}@example.com",
                    full_name="Other Audit User",
                ),
            ]
        )
        db.commit()

        current_user = _current_user(
            user_id=user_id,
            organization_id=organization_id,
        )
        other_user = _current_user(
            user_id=other_user_id,
            organization_id=organization_id,
        )

        matching_event = record_audit_event(
            db,
            current_user=current_user,
            trace_context=TraceContext.create(),
            event_type="knowledge_search",
        )
        other_type_event = record_audit_event(
            db,
            current_user=current_user,
            trace_context=TraceContext.create(),
            event_type="rag_query",
        )
        other_user_event = record_audit_event(
            db,
            current_user=other_user,
            trace_context=TraceContext.create(),
            event_type="knowledge_search",
        )
        db.commit()

        now = datetime.now(UTC)

        events = list_audit_events(
            db,
            current_user=current_user,
            event_type="knowledge_search",
            user_id=user_id,
            created_from=now - timedelta(minutes=5),
            created_to=now + timedelta(minutes=5),
        )

        event_ids = {event.id for event in events}

        assert matching_event.id in event_ids
        assert other_type_event.id not in event_ids
        assert other_user_event.id not in event_ids

        db.execute(
            delete(AuditEvent).where(
                AuditEvent.id.in_(
                    [
                        matching_event.id,
                        other_type_event.id,
                        other_user_event.id,
                    ]
                )
            )
        )
        db.execute(
            delete(User).where(
                User.id.in_([user_id, other_user_id])
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )
        db.commit()


def test_list_audit_events_rejects_invalid_limit() -> None:
    current_user = _current_user(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
    )

    with SessionLocal() as db:
        with pytest.raises(
            ValueError,
            match="Audit event limit must be between 1 and 500.",
        ):
            list_audit_events(
                db,
                current_user=current_user,
                limit=501,
            )