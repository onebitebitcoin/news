"""add long_short_ratio to market_data_snapshots

Revision ID: 98c440bb7f64
Revises: 20260303_0010
Create Date: 2026-03-04 02:51:26.141556
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98c440bb7f64'
down_revision: Union[str, None] = '20260303_0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('market_data_snapshots', sa.Column('long_short_ratio', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('market_data_snapshots', 'long_short_ratio')
