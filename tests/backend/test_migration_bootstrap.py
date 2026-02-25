import pytest

from app.deploy.migration_bootstrap import (
    REV_BASELINE,
    REV_V2,
    REV_V3,
    infer_legacy_revision,
)


def test_infer_legacy_revision_returns_none_for_fresh_db():
    result = infer_legacy_revision(set())
    assert result is None


def test_infer_legacy_revision_returns_none_when_alembic_version_exists():
    result = infer_legacy_revision({"alembic_version", "api_keys"})
    assert result is None


def test_infer_legacy_revision_raises_on_partial_legacy_schema():
    with pytest.raises(ValueError):
        infer_legacy_revision({"api_keys", "feed_items"})


def test_infer_legacy_revision_detects_baseline():
    result = infer_legacy_revision(
        {"api_keys", "feed_items", "source_statuses", "market_data_snapshots", "bookmarks"},
        api_key_columns={"id", "name", "created_at", "is_active"},
        feed_item_columns={"id", "source", "title"},
    )
    assert result == REV_BASELINE


def test_infer_legacy_revision_detects_v2():
    result = infer_legacy_revision(
        {"api_keys", "feed_items", "source_statuses", "market_data_snapshots", "bookmarks"},
        api_key_columns={"id", "key_prefix", "key_hash", "name", "created_at", "is_active"},
        feed_item_columns={"id", "title", "translation_status"},
    )
    assert result == REV_V2


def test_infer_legacy_revision_detects_v3_when_custom_sources_exists():
    result = infer_legacy_revision(
        {
            "api_keys",
            "feed_items",
            "source_statuses",
            "market_data_snapshots",
            "bookmarks",
            "custom_sources",
        },
        api_key_columns={"id", "key_prefix", "key_hash", "name", "created_at", "is_active"},
        feed_item_columns={"id", "title", "translation_status"},
    )
    assert result == REV_V3

