"""add bitcoin_dominance column to market_data_snapshots

Revision ID: 20260302_0008
Revises: 20260227_0007
Create Date: 2026-03-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260302_0008"
down_revision: Union[str, None] = "20260227_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("market_data_snapshots")}

    if "bitcoin_dominance" not in columns:
        op.add_column(
            "market_data_snapshots",
            sa.Column("bitcoin_dominance", sa.Float(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("market_data_snapshots")}

    if "bitcoin_dominance" in columns:
        with op.batch_alter_table("market_data_snapshots") as batch_op:
            batch_op.drop_column("bitcoin_dominance")
