"""add product name snapshot to order items

Revision ID: ab45ab76d9da
Revises: d6041898d194
Create Date: 2026-08-21 16:47:53.520875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab45ab76d9da'
down_revision: Union[str, Sequence[str], None] = 'd6041898d194'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "order_items",
        sa.Column(
            "product_name",
            sa.String(length=150),
            nullable=True
        )
    )

    op.execute("""
        UPDATE order_items
        SET product_name = products.name
        FROM products
        WHERE order_items.product_id = products.id
    """)

    op.alter_column(
        "order_items",
        "product_name",
        nullable=False
    )

def downgrade() -> None:
    op.drop_column(
        "order_items",
        "product_name"
    )