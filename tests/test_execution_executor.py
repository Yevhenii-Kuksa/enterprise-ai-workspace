import uuid

import pytest
from app.core.trace_context import TraceContext
from app.execution.executor import (
    ExecutionContext,
    ExecutorAlreadyRegisteredError,
    ExecutorNotRegisteredError,
    ExecutorRegistry,
)
from app.execution.schemas import ExecutionResult


class FakeExecutor:
    def execute(
        self,
        *,
        context: ExecutionContext,
    ) -> ExecutionResult:
        return ExecutionResult(
            succeeded=True,
            output={
                "resource_id": context.resource_id,
            },
        )


def _context() -> ExecutionContext:
    action_id = uuid.uuid4()

    trace_context = TraceContext.create(
        action_id=action_id,
    )

    return ExecutionContext(
        action_id=action_id,
        organization_id=uuid.uuid4(),
        proposal_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        action_type="order.update",
        resource_type="order",
        resource_id="ORDER-001",
        payload={
            "status": "confirmed",
        },
        trace_context=trace_context,
    )


def test_executor_registry_registers_and_returns_executor() -> None:
    registry = ExecutorRegistry()
    executor = FakeExecutor()

    registry.register(
        "fake",
        executor,
    )

    assert registry.get("fake") is executor


def test_executor_registry_rejects_duplicate_name() -> None:
    registry = ExecutorRegistry()

    registry.register(
        "fake",
        FakeExecutor(),
    )

    with pytest.raises(
        ExecutorAlreadyRegisteredError
    ):
        registry.register(
            "fake",
            FakeExecutor(),
        )


def test_executor_registry_rejects_unknown_executor() -> None:
    registry = ExecutorRegistry()

    with pytest.raises(
        ExecutorNotRegisteredError
    ):
        registry.get("missing")


def test_executor_registry_rejects_blank_name() -> None:
    registry = ExecutorRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "   ",
            FakeExecutor(),
        )


def test_executor_receives_governed_context() -> None:
    executor = FakeExecutor()
    context = _context()

    result = executor.execute(
        context=context,
    )

    assert result.succeeded is True
    assert result.output == {
        "resource_id": "ORDER-001",
    }
    assert (
        context.trace_context.action_id
        == context.action_id
    )