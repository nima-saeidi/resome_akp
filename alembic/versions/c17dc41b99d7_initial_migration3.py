"""Initial migration3

Revision ID: c17dc41b99d7
Revises: a0cbe3139127
Create Date: 2025-02-12 00:09:41.875171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c17dc41b99d7'
down_revision: Union[str, None] = 'a0cbe3139127'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
