"""api key hash and translation status

Revision ID: 20260214_0002
Revises: 20260214_0001
Create Date: 2026-02-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260214_0002"
down_revision: Union[str, None] = "20260214_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = inspect(bind)
    return {col["name"] for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    feed_cols = _column_names("feed_items")
    if "translation_status" not in feed_cols:
        with op.batch_alter_table("feed_items") as batch_op:
            batch_op.add_column(sa.Column("translation_status", sa.String(), nullable=True))
            batch_op.create_index("ix_feed_items_translation_status", ["translation_status"], unique=False)

    key_cols = _column_names("api_keys")
    if "key_prefix" not in key_cols:
        with op.batch_alter_table("api_keys") as batch_op:
            batch_op.add_column(sa.Column("key_prefix", sa.String(), nullable=True))
    if "key_hash" not in key_cols:
        with op.batch_alter_table("api_keys") as batch_op:
            batch_op.add_column(sa.Column("key_hash", sa.String(), nullable=True))

    bind = op.get_bind()
    bind.execute(sa.text("UPDATE api_keys SET is_active = 0"))
    bind.execute(sa.text("UPDATE api_keys SET key_prefix = 'invalid' WHERE key_prefix IS NULL"))
    bind.execute(sa.text("UPDATE api_keys SET key_hash = id || '_invalidated' WHERE key_hash IS NULL"))

    with op.batch_alter_table("api_keys") as batch_op:
        batch_op.alter_column("key_prefix", existing_type=sa.String(), nullable=False)
        batch_op.alter_column("key_hash", existing_type=sa.String(), nullable=False)
        batch_op.create_index("ix_api_keys_key_prefix", ["key_prefix"], unique=False)
        batch_op.create_index("ix_api_keys_key_hash", ["key_hash"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("api_keys") as batch_op:
        batch_op.drop_index("ix_api_keys_key_hash")
        batch_op.drop_index("ix_api_keys_key_prefix")
    with op.batch_alter_table("feed_items") as batch_op:
        batch_op.drop_index("ix_feed_items_translation_status")
