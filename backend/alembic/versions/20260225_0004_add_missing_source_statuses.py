"""add missing source_statuses table for legacy DBs

Revision ID: 20260225_0004
Revises: 20260225_0003
Create Date: 2026-02-25

구버전 레거시 DB에 source_statuses 테이블이 누락된 경우를 위한 보정 마이그레이션.
이미 존재하는 경우 아무 작업도 수행하지 않는다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260225_0004"
down_revision: Union[str, None] = "20260225_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "source_statuses" not in existing_tables:
        op.create_table(
            "source_statuses",
            sa.Column("source", sa.String(), nullable=False),
            sa.Column("last_success_at", sa.DateTime(), nullable=True),
            sa.Column("last_error_at", sa.DateTime(), nullable=True),
            sa.Column("last_error_message", sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint("source"),
        )
        op.create_index(
            op.f("ix_source_statuses_source"), "source_statuses", ["source"], unique=True
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "source_statuses" in existing_tables:
        op.drop_index(op.f("ix_source_statuses_source"), table_name="source_statuses")
        op.drop_table("source_statuses")
