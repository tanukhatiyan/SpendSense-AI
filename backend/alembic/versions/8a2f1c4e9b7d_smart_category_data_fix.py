"""smart_category_data_fix

Revision ID: 8a2f1c4e9b7d
Revises: 77a877cdc72e
Create Date: 2026-10-13 00:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a2f1c4e9b7d'
down_revision: Union[str, Sequence[str], None] = '77a877cdc72e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix historical miscategorized transactions (e.g., uber/ola mistakenly saved as Food)
    op.execute(
        "UPDATE expenses SET category = 'Transport' "
        "WHERE (LOWER(title) LIKE '%uber%' OR LOWER(title) LIKE '%ola%' OR LOWER(title) LIKE '%rapido%') "
        "AND category = 'Food'"
    )


def downgrade() -> None:
    pass
