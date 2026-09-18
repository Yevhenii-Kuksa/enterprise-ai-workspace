from app.models.action_execution import ActionExecution
from sqlalchemy import UniqueConstraint


def test_action_execution_table_contract() -> None:
    table = ActionExecution.__table__

    assert table.name == "action_executions"
    assert set(table.columns.keys()) == {
        "id",
        "organization_id",
        "proposal_id",
        "requested_by_user_id",
        "action_type",
        "status",
        "idempotency_key",
        "proposal_fingerprint",
        "snapshot",
        "attempt_count",
        "max_attempts",
        "result",
        "error_code",
        "error_message",
        "trace_id",
        "request_id",
        "created_at",
        "started_at",
        "finished_at",
        "updated_at",
    }


def test_action_execution_has_replay_protection_constraints() -> None:
    constraints = {
        constraint.name
        for constraint in ActionExecution.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert "uq_action_executions_proposal_id" in constraints
    assert "uq_action_executions_org_idempotency_key" in constraints