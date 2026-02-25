"""배포 시 레거시 DB의 Alembic 상태를 안전하게 보정한다.

기존 운영 DB에 테이블은 존재하지만 `alembic_version` 테이블이 없는 경우,
baseline 마이그레이션(0001)에서 DuplicateTable 에러가 발생할 수 있다.
이 스크립트는 스키마를 읽어 적절한 revision을 `alembic_version`에 기록한 뒤 `upgrade head`가
정상 동작하도록 돕는다.
"""

from __future__ import annotations

import logging

from sqlalchemy import Column, MetaData, String, Table, create_engine, inspect, text

from app.config import settings

logger = logging.getLogger(__name__)

REV_BASELINE = "20260214_0001"
REV_V2 = "20260214_0002"
REV_V3 = "20260225_0003"

BASELINE_TABLES = {
    "api_keys",
    "feed_items",
    "source_statuses",
    "market_data_snapshots",
    "bookmarks",
}

# source_statuses는 구버전 레거시 DB에서 빠져 있을 수 있으므로
# stamp 가능 여부 판단에는 핵심 테이블만 사용한다.
CORE_BASELINE_TABLES = {
    "api_keys",
    "feed_items",
    "market_data_snapshots",
    "bookmarks",
}


def infer_legacy_revision(
    table_names: set[str],
    api_key_columns: set[str] | None = None,
    feed_item_columns: set[str] | None = None,
) -> str | None:
    """기존 스키마 상태를 기반으로 stamp 대상 revision을 추론한다.

    Returns:
        - None: stamp 불필요 (신규 DB 또는 이미 alembic_version 존재)
        - revision string: stamp 필요
    Raises:
        ValueError: 핵심 baseline 테이블 일부만 존재하는 불완전 스키마 (자동 stamp 위험)
    """
    if "alembic_version" in table_names:
        return None

    has_any_baseline = bool(BASELINE_TABLES & table_names)
    if not has_any_baseline:
        return None

    # 핵심 테이블 기준으로 완전성 검사 (source_statuses는 구버전 DB에서 누락 가능)
    if not CORE_BASELINE_TABLES.issubset(table_names):
        missing_tables = sorted(CORE_BASELINE_TABLES - table_names)
        raise ValueError(
            "레거시 DB 스키마가 부분적으로만 존재합니다. 자동 stamp를 중단합니다. "
            f"누락 테이블: {', '.join(missing_tables)}"
        )

    if "custom_sources" in table_names:
        return REV_V3

    api_cols = api_key_columns or set()
    feed_cols = feed_item_columns or set()
    has_v2_columns = {"key_prefix", "key_hash"}.issubset(api_cols) and "translation_status" in feed_cols
    return REV_V2 if has_v2_columns else REV_BASELINE


def _write_alembic_version(connection, revision: str) -> None:
    metadata = MetaData()
    alembic_version = Table(
        "alembic_version",
        metadata,
        Column("version_num", String(32), primary_key=True, nullable=False),
    )
    metadata.create_all(connection, tables=[alembic_version])
    connection.execute(text("DELETE FROM alembic_version"))
    connection.execute(
        text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
        {"revision": revision},
    )


def bootstrap_alembic_state() -> str | None:
    """필요 시 Alembic revision을 stamp한다."""
    engine = create_engine(settings.DATABASE_URL)

    with engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())

        api_key_columns = (
            {col["name"] for col in inspector.get_columns("api_keys")}
            if "api_keys" in table_names
            else set()
        )
        feed_item_columns = (
            {col["name"] for col in inspector.get_columns("feed_items")}
            if "feed_items" in table_names
            else set()
        )

        target_revision = infer_legacy_revision(
            table_names=table_names,
            api_key_columns=api_key_columns,
            feed_item_columns=feed_item_columns,
        )

        if "alembic_version" in table_names:
            current_revision = connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            ).scalar_one_or_none()
            logger.info("Alembic version table exists. current=%s", current_revision)
            if current_revision:
                logger.info("Alembic bootstrap not required.")
                return None

        if not target_revision:
            logger.info("Alembic bootstrap not required.")
            return None

        logger.warning(
            "Legacy DB detected without alembic_version. Writing alembic_version=%s before upgrade.",
            target_revision,
        )
        _write_alembic_version(connection, target_revision)
        return target_revision


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
    stamped_revision = bootstrap_alembic_state()
    if stamped_revision:
        logger.info("Alembic bootstrap completed. stamped=%s", stamped_revision)


if __name__ == "__main__":
    main()
