import uuid

from app.core.trace_context import TraceContext


def test_trace_context_creates_unique_identifiers() -> None:
    context = TraceContext.create()

    assert isinstance(context.trace_id, uuid.UUID)
    assert isinstance(context.request_id, uuid.UUID)
    assert context.trace_id != context.request_id
    assert context.action_id is None


def test_trace_context_accepts_existing_trace_id() -> None:
    trace_id = uuid.uuid4()

    context = TraceContext.create(
        trace_id=trace_id,
    )

    assert context.trace_id == trace_id
    assert isinstance(context.request_id, uuid.UUID)
    assert context.action_id is None


def test_trace_context_accepts_action_id() -> None:
    action_id = uuid.uuid4()

    context = TraceContext.create(
        action_id=action_id,
    )

    assert isinstance(context.trace_id, uuid.UUID)
    assert isinstance(context.request_id, uuid.UUID)
    assert context.action_id == action_id