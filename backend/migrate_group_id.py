"""
group_id 컬럼 마이그레이션 스크립트

1. feed_items 테이블에 group_id 컬럼 추가 (없는 경우)
2. 기존 raw 컬럼에서 dedup_group_id 추출하여 group_id에 저장
"""

import json
import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """데이터베이스 파일 경로"""
    return str(Path(__file__).parent / "bitcoin_news.db")


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """컬럼 존재 여부 확인"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def add_group_id_column(cursor: sqlite3.Cursor) -> bool:
    """group_id 컬럼 추가"""
    if column_exists(cursor, "feed_items", "group_id"):
        logger.info("group_id 컬럼이 이미 존재합니다.")
        return False

    logger.info("group_id 컬럼을 추가합니다...")
    cursor.execute("ALTER TABLE feed_items ADD COLUMN group_id TEXT")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_feed_items_group_id ON feed_items(group_id)")
    logger.info("group_id 컬럼 추가 완료")
    return True


def migrate_group_ids(cursor: sqlite3.Cursor) -> int:
    """기존 데이터의 group_id 마이그레이션"""
    logger.info("기존 데이터에서 group_id 추출 중...")

    # raw 컬럼이 있고 group_id가 NULL인 레코드 조회
    cursor.execute("""
        SELECT id, raw FROM feed_items
        WHERE raw IS NOT NULL AND (group_id IS NULL OR group_id = '')
    """)
    rows = cursor.fetchall()

    updated = 0
    for item_id, raw in rows:
        if not raw:
            continue

        try:
            raw_data = json.loads(raw)
            group_id = raw_data.get("dedup_group_id")
            if group_id:
                cursor.execute(
                    "UPDATE feed_items SET group_id = ? WHERE id = ?",
                    (group_id, item_id),
                )
                updated += 1
        except json.JSONDecodeError:
            continue

    logger.info(f"group_id 마이그레이션 완료: {updated}개 업데이트됨")
    return updated


def main():
    db_path = get_db_path()
    logger.info(f"데이터베이스: {db_path}")

    if not Path(db_path).exists():
        logger.error("데이터베이스 파일이 존재하지 않습니다.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        add_group_id_column(cursor)
        migrate_group_ids(cursor)
        conn.commit()
        logger.info("마이그레이션 성공!")
    except Exception as e:
        conn.rollback()
        logger.error(f"마이그레이션 실패: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
