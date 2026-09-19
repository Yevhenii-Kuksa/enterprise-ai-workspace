from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.demo.ids import (
    ACT_PROP_001_ID,
    ACT_PROP_002_ID,
    ACT_PROP_003_ID,
    ANNA_KOWALSKA_ID,
    APPROVAL_001_ID,
    APPROVAL_002_ID,
    APPROVAL_003_ID,
    AUDIT_001_ID,
    AUDIT_002_ID,
    AUDIT_003_ID,
    AUDIT_004_ID,
    AUDIT_005_ID,
    AUDIT_006_ID,
    AUDIT_007_ID,
    EXECUTION_001_ID,
    EXECUTION_002_ID,
    ORD_1048_ID,
    PIOTR_NOWAK_ID,
)


class DemoApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DemoExecutionStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class DemoActionProposal:
    id: UUID
    proposal_code: str
    order_id: UUID
    title: str
    action_type: str
    requested_by_user_id: UUID
    created_at: datetime


@dataclass(frozen=True, slots=True)
class DemoApproval:
    id: UUID
    proposal_id: UUID
    status: DemoApprovalStatus
    decided_by_user_id: UUID | None
    decided_at: datetime | None


@dataclass(frozen=True, slots=True)
class DemoExecution:
    id: UUID
    proposal_id: UUID
    approval_id: UUID
    status: DemoExecutionStatus
    executed_at: datetime
    result_summary: str


@dataclass(frozen=True, slots=True)
class DemoAuditEvent:
    id: UUID
    event_type: str
    entity_type: str
    entity_id: UUID
    actor_user_id: UUID | None
    occurred_at: datetime
    summary: str


NEXALVORA_ACTION_PROPOSALS = (
    DemoActionProposal(
        id=ACT_PROP_001_ID,
        proposal_code="ACT-PROP-001",
        order_id=ORD_1048_ID,
        title="Utworzyć pilne zamówienie materiału MAT-204",
        action_type="PROCUREMENT_CREATE_URGENT_ORDER",
        requested_by_user_id=ANNA_KOWALSKA_ID,
        created_at=datetime(2026, 9, 19, 10, 35, tzinfo=UTC),
    ),
    DemoActionProposal(
        id=ACT_PROP_002_ID,
        proposal_code="ACT-PROP-002",
        order_id=ORD_1048_ID,
        title="Zaktualizować harmonogram produkcji ORD-1048",
        action_type="PRODUCTION_UPDATE_SCHEDULE",
        requested_by_user_id=ANNA_KOWALSKA_ID,
        created_at=datetime(2026, 9, 19, 10, 40, tzinfo=UTC),
    ),
    DemoActionProposal(
        id=ACT_PROP_003_ID,
        proposal_code="ACT-PROP-003",
        order_id=ORD_1048_ID,
        title="Przygotować komunikat do klienta o ryzyku terminu",
        action_type="CUSTOMER_PREPARE_RISK_MESSAGE",
        requested_by_user_id=ANNA_KOWALSKA_ID,
        created_at=datetime(2026, 9, 19, 10, 45, tzinfo=UTC),
    ),
)


NEXALVORA_APPROVALS = (
    DemoApproval(
        id=APPROVAL_001_ID,
        proposal_id=ACT_PROP_001_ID,
        status=DemoApprovalStatus.APPROVED,
        decided_by_user_id=PIOTR_NOWAK_ID,
        decided_at=datetime(2026, 9, 19, 10, 50, tzinfo=UTC),
    ),
    DemoApproval(
        id=APPROVAL_002_ID,
        proposal_id=ACT_PROP_002_ID,
        status=DemoApprovalStatus.APPROVED,
        decided_by_user_id=ANNA_KOWALSKA_ID,
        decided_at=datetime(2026, 9, 19, 10, 55, tzinfo=UTC),
    ),
    DemoApproval(
        id=APPROVAL_003_ID,
        proposal_id=ACT_PROP_003_ID,
        status=DemoApprovalStatus.PENDING,
        decided_by_user_id=None,
        decided_at=None,
    ),
)


NEXALVORA_EXECUTIONS = (
    DemoExecution(
        id=EXECUTION_001_ID,
        proposal_id=ACT_PROP_001_ID,
        approval_id=APPROVAL_001_ID,
        status=DemoExecutionStatus.SUCCEEDED,
        executed_at=datetime(2026, 9, 19, 10, 52, tzinfo=UTC),
        result_summary=(
            "Pilne zamówienie MAT-204 zostało przekazane "
            "do dalszej obsługi zakupowej."
        ),
    ),
    DemoExecution(
        id=EXECUTION_002_ID,
        proposal_id=ACT_PROP_002_ID,
        approval_id=APPROVAL_002_ID,
        status=DemoExecutionStatus.SUCCEEDED,
        executed_at=datetime(2026, 9, 19, 10, 57, tzinfo=UTC),
        result_summary=(
            "Harmonogram ORD-1048 został oznaczony do aktualizacji "
            "po potwierdzeniu przyjęcia MAT-204."
        ),
    ),
)


NEXALVORA_AUDIT_EVENTS = (
    DemoAuditEvent(
        id=AUDIT_001_ID,
        event_type="AI_INSIGHT_CREATED",
        entity_type="order",
        entity_id=ORD_1048_ID,
        actor_user_id=None,
        occurred_at=datetime(2026, 9, 19, 10, 30, tzinfo=UTC),
        summary="AI wykrył ryzyko terminu dla ORD-1048.",
    ),
    DemoAuditEvent(
        id=AUDIT_002_ID,
        event_type="ACTION_PROPOSAL_CREATED",
        entity_type="action_proposal",
        entity_id=ACT_PROP_001_ID,
        actor_user_id=ANNA_KOWALSKA_ID,
        occurred_at=datetime(2026, 9, 19, 10, 35, tzinfo=UTC),
        summary="Utworzono propozycję pilnego zamówienia MAT-204.",
    ),
    DemoAuditEvent(
        id=AUDIT_003_ID,
        event_type="APPROVAL_GRANTED",
        entity_type="approval",
        entity_id=APPROVAL_001_ID,
        actor_user_id=PIOTR_NOWAK_ID,
        occurred_at=datetime(2026, 9, 19, 10, 50, tzinfo=UTC),
        summary="Piotr Nowak zatwierdził działanie zakupowe.",
    ),
    DemoAuditEvent(
        id=AUDIT_004_ID,
        event_type="ACTION_EXECUTED",
        entity_type="execution",
        entity_id=EXECUTION_001_ID,
        actor_user_id=None,
        occurred_at=datetime(2026, 9, 19, 10, 52, tzinfo=UTC),
        summary="Wykonano zatwierdzone działanie dotyczące MAT-204.",
    ),
    DemoAuditEvent(
        id=AUDIT_005_ID,
        event_type="ACTION_PROPOSAL_CREATED",
        entity_type="action_proposal",
        entity_id=ACT_PROP_002_ID,
        actor_user_id=ANNA_KOWALSKA_ID,
        occurred_at=datetime(2026, 9, 19, 10, 40, tzinfo=UTC),
        summary="Utworzono propozycję aktualizacji harmonogramu ORD-1048.",
    ),
    DemoAuditEvent(
        id=AUDIT_006_ID,
        event_type="APPROVAL_GRANTED",
        entity_type="approval",
        entity_id=APPROVAL_002_ID,
        actor_user_id=ANNA_KOWALSKA_ID,
        occurred_at=datetime(2026, 9, 19, 10, 55, tzinfo=UTC),
        summary="Anna Kowalska zatwierdziła aktualizację harmonogramu.",
    ),
    DemoAuditEvent(
        id=AUDIT_007_ID,
        event_type="ACTION_EXECUTED",
        entity_type="execution",
        entity_id=EXECUTION_002_ID,
        actor_user_id=None,
        occurred_at=datetime(2026, 9, 19, 10, 57, tzinfo=UTC),
        summary="Wykonano zatwierdzoną aktualizację harmonogramu ORD-1048.",
    ),
)