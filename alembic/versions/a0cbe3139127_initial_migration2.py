"""Initial migration2

Revision ID: a0cbe3139127
Revises: 3ae06d72513f
Create Date: 2025-01-12 02:01:14.155021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0cbe3139127'
down_revision: Union[str, None] = '3ae06d72513f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
