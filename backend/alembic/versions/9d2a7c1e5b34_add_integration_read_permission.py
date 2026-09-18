import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9d2a7c1e5b34"
down_revision: str | None = "4c8e7b2a1d11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.Uuid()),
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.String()),
    )

    op.bulk_insert(
        permissions,
        [
            {
                "id": uuid.uuid4(),
                "code": "integration.read",
                "name": "Read enterprise integrations",
                "description": (
                    "Read configured enterprise integrations "
                    "and normalized integration data."
                ),
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM permissions "
            "WHERE code = 'integration.read'"
        )
    )