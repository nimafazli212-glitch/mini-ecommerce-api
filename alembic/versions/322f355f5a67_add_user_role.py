"""add user role

Revision ID: 322f355f5a67
Revises: 2dc5382d005f
Create Date: 2026-08-21 15:55:37.312628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '322f355f5a67'
down_revision: Union[str, Sequence[str], None] = '2dc5382d005f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="customer"
        )
    )


def downgrade() -> None:
    op.drop_column("users", "role")