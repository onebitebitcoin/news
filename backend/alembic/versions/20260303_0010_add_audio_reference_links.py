"""add audio_reference_links table

Revision ID: 20260303_0010
Revises: 20260302_0009
Create Date: 2026-03-03
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260303_0010"
down_revision: Union[str, None] = "20260302_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audio_reference_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("audio_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["audio_id"], ["audio_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audio_reference_links_id", "audio_reference_links", ["id"])
    op.create_index("ix_audio_reference_links_audio_id", "audio_reference_links", ["audio_id"])


def downgrade() -> None:
    op.drop_index("ix_audio_reference_links_audio_id", table_name="audio_reference_links")
    op.drop_index("ix_audio_reference_links_id", table_name="audio_reference_links")
    op.drop_table("audio_reference_links")
