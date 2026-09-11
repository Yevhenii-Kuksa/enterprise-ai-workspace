"""enable pgvector extension

Revision ID: e1c929919150
Revises: 0fe03e1ec830
Create Date: 2026-09-11

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1c929919150"
down_revision: str | Sequence[str] | None = "0fe03e1ec830"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable the pgvector PostgreSQL extension."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Keep pgvector installed during downgrade."""
    pass