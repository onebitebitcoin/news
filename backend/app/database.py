import json
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# SQLite URL 처리
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 테이블 생성"""
    from app.models import (  # noqa: F401
        api_key,
        bookmark,
        feed_item,
        market_data_snapshot,
        source_status,
    )

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    migrate_market_snapshots()
    backfill_group_ids()


def migrate_market_snapshots():
    """market_data_snapshots 테이블에 새 컬럼 추가 (없으면)"""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "market_data_snapshots" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("market_data_snapshots")}
    new_columns = [
        ("difficulty_adjustment", "TEXT"),
        ("hashrate_data", "TEXT"),
        ("mempool_stats", "TEXT"),
        ("block_height", "INTEGER"),
    ]

    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            if col_name not in existing:
                conn.execute(
                    text(
                        f"ALTER TABLE market_data_snapshots ADD COLUMN {col_name} {col_type}"
                    )
                )
                logger.info(f"Added column {col_name} to market_data_snapshots")
        conn.commit()


def backfill_group_ids():
    """group_id가 NULL인 기존 아이템에 group_id 백필 (멱등)"""
    from app.models.feed_item import FeedItem

    db = SessionLocal()
    try:
        null_items = db.query(FeedItem).filter(FeedItem.group_id.is_(None)).all()
        if not null_items:
            return

        count = 0
        for item in null_items:
            # raw에서 dedup_group_id 추출 시도
            group_id = None
            if item.raw:
                try:
                    raw_data = json.loads(item.raw) if isinstance(item.raw, str) else item.raw
                    group_id = raw_data.get("dedup_group_id")
                except (json.JSONDecodeError, AttributeError):
                    pass

            # fallback: 자기 id를 group_id로 설정
            item.group_id = group_id or item.id
            count += 1

        db.commit()
        logger.info(f"Backfilled group_id for {count} items")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to backfill group_ids: {e}", exc_info=True)
    finally:
        db.close()
