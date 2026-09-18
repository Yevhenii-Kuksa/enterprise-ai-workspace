import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from app.core.trace_context import TraceContext
from app.execution.schemas import ExecutionResult


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    action_id: uuid.UUID
    organization_id: uuid.UUID
    proposal_id: uuid.UUID
    requested_by_user_id: uuid.UUID

    action_type: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any]

    trace_context: TraceContext


class ActionExecutor(Protocol):
    def execute(
        self,
        *,
        context: ExecutionContext,
    ) -> ExecutionResult:
        ...


class ExecutorRegistryError(Exception):
    pass


class ExecutorAlreadyRegisteredError(ExecutorRegistryError):
    pass


class ExecutorNotRegisteredError(ExecutorRegistryError):
    pass


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[str, ActionExecutor] = {}

    def register(
        self,
        name: str,
        executor: ActionExecutor,
    ) -> None:
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Executor name must not be empty."
            )

        if normalized_name in self._executors:
            raise ExecutorAlreadyRegisteredError(
                f"Executor is already registered: "
                f"{normalized_name}"
            )

        self._executors[normalized_name] = executor

    def get(
        self,
        name: str,
    ) -> ActionExecutor:
        executor = self._executors.get(name)

        if executor is None:
            raise ExecutorNotRegisteredError(
                f"Executor is not registered: {name}"
            )

        return executor