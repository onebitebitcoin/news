"""baseline schema

Revision ID: 20260214_0001
Revises:
Create Date: 2026-02-14
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260214_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key_prefix", sa.String(), nullable=False),
        sa.Column("key_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_key_hash"), "api_keys", ["key_hash"], unique=True)
    op.create_index(op.f("ix_api_keys_key_prefix"), "api_keys", ["key_prefix"], unique=False)

    op.create_table(
        "feed_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_ref", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("url_hash", sa.String(), nullable=True),
        sa.Column("group_id", sa.String(), nullable=True),
        sa.Column("translation_status", sa.String(), nullable=True),
        sa.Column("raw", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feed_items_category"), "feed_items", ["category"], unique=False)
    op.create_index(op.f("ix_feed_items_group_id"), "feed_items", ["group_id"], unique=False)
    op.create_index(op.f("ix_feed_items_id"), "feed_items", ["id"], unique=False)
    op.create_index(op.f("ix_feed_items_published_at"), "feed_items", ["published_at"], unique=False)
    op.create_index(op.f("ix_feed_items_source"), "feed_items", ["source"], unique=False)
    op.create_index(
        op.f("ix_feed_items_translation_status"), "feed_items", ["translation_status"], unique=False
    )
    op.create_index(op.f("ix_feed_items_url_hash"), "feed_items", ["url_hash"], unique=False)

    op.create_table(
        "source_statuses",
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("last_success_at", sa.DateTime(), nullable=True),
        sa.Column("last_error_at", sa.DateTime(), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("source"),
    )
    op.create_index(op.f("ix_source_statuses_source"), "source_statuses", ["source"], unique=True)

    op.create_table(
        "market_data_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("bitcoin_price_krw", sa.Float(), nullable=True),
        sa.Column("bitcoin_price_usd", sa.Float(), nullable=True),
        sa.Column("usd_krw_rate", sa.Float(), nullable=True),
        sa.Column("kimchi_premium", sa.Float(), nullable=True),
        sa.Column("fee_rates", sa.JSON(), nullable=True),
        sa.Column("fear_greed_value", sa.Integer(), nullable=True),
        sa.Column("fear_greed_classification", sa.String(), nullable=True),
        sa.Column("difficulty_adjustment", sa.JSON(), nullable=True),
        sa.Column("hashrate_data", sa.JSON(), nullable=True),
        sa.Column("mempool_stats", sa.JSON(), nullable=True),
        sa.Column("block_height", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date"),
    )
    op.create_index(op.f("ix_market_data_snapshots_id"), "market_data_snapshots", ["id"], unique=False)

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["feed_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bookmarks")
    op.drop_index(op.f("ix_market_data_snapshots_id"), table_name="market_data_snapshots")
    op.drop_table("market_data_snapshots")
    op.drop_index(op.f("ix_source_statuses_source"), table_name="source_statuses")
    op.drop_table("source_statuses")
    op.drop_index(op.f("ix_feed_items_url_hash"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_translation_status"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_source"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_published_at"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_id"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_group_id"), table_name="feed_items")
    op.drop_index(op.f("ix_feed_items_category"), table_name="feed_items")
    op.drop_table("feed_items")
    op.drop_index(op.f("ix_api_keys_key_prefix"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key_hash"), table_name="api_keys")
    op.drop_table("api_keys")
