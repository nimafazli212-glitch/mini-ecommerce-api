"""add user role

Revision ID: 6178e1014312
Revises: 322f355f5a67
Create Date: 2026-08-21 16:02:00.861561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6178e1014312'
down_revision: Union[str, Sequence[str], None] = '322f355f5a67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    op.drop_column("users", "role")