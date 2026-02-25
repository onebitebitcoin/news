"""add mvrv_z_score column to market_data_snapshots

Revision ID: 20260225_0005
Revises: 20260225_0004
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260225_0005"
down_revision: Union[str, None] = "20260225_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("market_data_snapshots")}

    if "mvrv_z_score" not in columns:
        op.add_column("market_data_snapshots", sa.Column("mvrv_z_score", sa.Float(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("market_data_snapshots")}

    if "mvrv_z_score" in columns:
        with op.batch_alter_table("market_data_snapshots") as batch_op:
            batch_op.drop_column("mvrv_z_score")
