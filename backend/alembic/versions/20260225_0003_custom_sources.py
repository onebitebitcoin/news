"""add custom sources table

Revision ID: 20260225_0003
Revises: 20260214_0002
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260225_0003"
down_revision: Union[str, None] = "20260214_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "custom_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("list_url", sa.String(), nullable=False),
        sa.Column("fetch_mode", sa.String(), nullable=False, server_default="scrape"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ai_model", sa.String(), nullable=True),
        sa.Column("extraction_rules_json", sa.Text(), nullable=False),
        sa.Column("normalization_rules_json", sa.Text(), nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("last_validation_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_custom_sources_slug", "custom_sources", ["slug"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_custom_sources_slug", table_name="custom_sources")
    op.drop_table("custom_sources")
