from app.demo.governance import (
    NEXALVORA_ACTION_PROPOSALS,
    NEXALVORA_APPROVALS,
    NEXALVORA_AUDIT_EVENTS,
    NEXALVORA_EXECUTIONS,
    DemoApprovalStatus,
    DemoExecutionStatus,
)


def test_expected_number_of_action_proposals() -> None:
    assert len(NEXALVORA_ACTION_PROPOSALS) == 3


def test_expected_approval_distribution() -> None:
    approved = [
        approval
        for approval in NEXALVORA_APPROVALS
        if approval.status == DemoApprovalStatus.APPROVED
    ]
    pending = [
        approval
        for approval in NEXALVORA_APPROVALS
        if approval.status == DemoApprovalStatus.PENDING
    ]

    assert len(approved) == 2
    assert len(pending) == 1


def test_only_approved_proposals_are_executed() -> None:
    approved_proposal_ids = {
        approval.proposal_id
        for approval in NEXALVORA_APPROVALS
        if approval.status == DemoApprovalStatus.APPROVED
    }

    executed_proposal_ids = {
        execution.proposal_id
        for execution in NEXALVORA_EXECUTIONS
    }

    assert executed_proposal_ids == approved_proposal_ids


def test_pending_proposal_has_no_execution() -> None:
    pending_proposal_ids = {
        approval.proposal_id
        for approval in NEXALVORA_APPROVALS
        if approval.status == DemoApprovalStatus.PENDING
    }

    executed_proposal_ids = {
        execution.proposal_id
        for execution in NEXALVORA_EXECUTIONS
    }

    assert pending_proposal_ids.isdisjoint(executed_proposal_ids)


def test_all_executions_succeeded() -> None:
    assert all(
        execution.status == DemoExecutionStatus.SUCCEEDED
        for execution in NEXALVORA_EXECUTIONS
    )


def test_execution_approval_links_are_valid() -> None:
    approval_by_id = {
        approval.id: approval
        for approval in NEXALVORA_APPROVALS
    }

    for execution in NEXALVORA_EXECUTIONS:
        approval = approval_by_id[execution.approval_id]

        assert approval.proposal_id == execution.proposal_id
        assert approval.status == DemoApprovalStatus.APPROVED


def test_audit_event_ids_are_unique() -> None:
    audit_ids = [
        event.id
        for event in NEXALVORA_AUDIT_EVENTS
    ]

    assert len(audit_ids) == len(set(audit_ids))


def test_audit_story_contains_required_governance_events() -> None:
    event_types = {
        event.event_type
        for event in NEXALVORA_AUDIT_EVENTS
    }

    assert {
        "AI_INSIGHT_CREATED",
        "ACTION_PROPOSAL_CREATED",
        "APPROVAL_GRANTED",
        "ACTION_EXECUTED",
    }.issubset(event_types)