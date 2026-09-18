import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalProposalCreate(BaseModel):
    action_type: str = Field(min_length=1, max_length=100)
    resource_type: str = Field(min_length=1, max_length=100)
    resource_id: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)
    justification: str = Field(min_length=1, max_length=2000)
    expires_at: datetime | None = None


class ApprovalProposalSnapshot(BaseModel):
    action_type: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any]
    justification: str


class ApprovalProposal(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: uuid.UUID
    status: ApprovalStatus
    action_type: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any]
    justification: str
    snapshot: ApprovalProposalSnapshot
    fingerprint: str
    created_at: datetime
    expires_at: datetime | None = None
    decided_by_user_id: uuid.UUID | None = None
    decided_at: datetime | None = None
    decision_comment: str | None = None


class ApprovalDecisionRequest(BaseModel):
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ApprovalCancelRequest(BaseModel):
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )