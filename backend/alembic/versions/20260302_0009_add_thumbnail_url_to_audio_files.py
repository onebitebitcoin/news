"""add thumbnail_url column to audio_files

Revision ID: 20260302_0009
Revises: 20260302_0008
Create Date: 2026-03-02
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260302_0009"
down_revision: Union[str, None] = "20260302_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "audio_files",
        sa.Column("thumbnail_url", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("audio_files", "thumbnail_url")
