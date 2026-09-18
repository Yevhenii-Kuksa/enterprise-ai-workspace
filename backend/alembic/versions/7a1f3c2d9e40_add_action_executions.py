"""add action executions

Revision ID: 7a1f3c2d9e40
Revises: 9bb5d137f10b
Create Date: 2026-09-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7a1f3c2d9e40"
down_revision: str | Sequence[str] | None = "9bb5d137f10b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "action_executions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("proposal_id", sa.UUID(), nullable=False),
        sa.Column("requested_by_user_id", sa.UUID(), nullable=False),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "idempotency_key",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "proposal_fingerprint",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "error_code",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column("trace_id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["approval_proposals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "proposal_id",
            name="uq_action_executions_proposal_id",
        ),
        sa.UniqueConstraint(
            "organization_id",
            "idempotency_key",
            name="uq_action_executions_org_idempotency_key",
        ),
    )

    op.create_index(
        op.f("ix_action_executions_organization_id"),
        "action_executions",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_action_executions_proposal_id"),
        "action_executions",
        ["proposal_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_action_executions_requested_by_user_id"),
        "action_executions",
        ["requested_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_action_executions_status"),
        "action_executions",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_action_executions_trace_id"),
        "action_executions",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_action_executions_request_id"),
        "action_executions",
        ["request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_action_executions_request_id"),
        table_name="action_executions",
    )
    op.drop_index(
        op.f("ix_action_executions_trace_id"),
        table_name="action_executions",
    )
    op.drop_index(
        op.f("ix_action_executions_status"),
        table_name="action_executions",
    )
    op.drop_index(
        op.f("ix_action_executions_requested_by_user_id"),
        table_name="action_executions",
    )
    op.drop_index(
        op.f("ix_action_executions_proposal_id"),
        table_name="action_executions",
    )
    op.drop_index(
        op.f("ix_action_executions_organization_id"),
        table_name="action_executions",
    )
    op.drop_table("action_executions")