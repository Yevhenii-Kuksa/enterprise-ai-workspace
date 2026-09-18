from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.execution.executor import ExecutorRegistry
from app.execution.registry import ActionRegistry
from app.execution.service import ExecutionService


def get_action_registry() -> ActionRegistry:
    return ActionRegistry()


def get_executor_registry() -> ExecutorRegistry:
    return ExecutorRegistry()


def get_execution_service(
    db: Annotated[Session, Depends(get_db)],
    action_registry: Annotated[
        ActionRegistry,
        Depends(get_action_registry),
    ],
    executor_registry: Annotated[
        ExecutorRegistry,
        Depends(get_executor_registry),
    ],
) -> ExecutionService:
    return ExecutionService(
        db=db,
        registry=action_registry,
        executors=executor_registry,
    )
