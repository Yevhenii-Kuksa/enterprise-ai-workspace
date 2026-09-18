import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ActionDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    action_type: str = Field(min_length=1, max_length=100)
    executor_name: str = Field(min_length=1, max_length=100)
    required_permission: str = Field(min_length=1, max_length=100)
    enabled: bool = True
    idempotency_required: bool = True
    max_attempts: int = Field(default=3, ge=1, le=10)


class ExecutionResult(BaseModel):
    succeeded: bool
    output: dict[str, Any] = Field(default_factory=dict)
    retryable: bool = False
    error_code: str | None = Field(
        default=None,
        max_length=100,
    )
    error_message: str | None = Field(
        default=None,
        max_length=2000,
    )


class ActionExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    proposal_id: uuid.UUID
    requested_by_user_id: uuid.UUID

    action_type: str
    status: ExecutionStatus

    idempotency_key: str
    proposal_fingerprint: str
    snapshot: dict[str, Any]

    attempt_count: int
    max_attempts: int

    result: dict[str, Any] | None
    error_code: str | None
    error_message: str | None

    trace_id: uuid.UUID
    request_id: uuid.UUID

    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    updated_at: datetime