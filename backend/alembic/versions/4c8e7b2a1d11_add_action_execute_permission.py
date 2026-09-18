"""add action execute permission

Revision ID: 4c8e7b2a1d11
Revises: 7a1f3c2d9e40
Create Date: 2026-09-18
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4c8e7b2a1d11"
down_revision: str | Sequence[str] | None = "7a1f3c2d9e40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    permission_table = sa.table(
        "permissions",
        sa.column("id", sa.UUID()),
        sa.column("code", sa.String(length=100)),
        sa.column("name", sa.String(length=100)),
        sa.column("description", sa.String(length=255)),
    )

    op.bulk_insert(
        permission_table,
        [
            {
                "id": uuid.uuid4(),
                "code": "action.execute",
                "name": "Execute governed actions",
                "description": "Execute approved governed actions",
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM permissions "
            "WHERE code = 'action.execute'"
        )
    )
