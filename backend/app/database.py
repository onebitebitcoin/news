import logging
import os

from sqlalchemy import create_engine, inspect, text
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
    """데이터베이스 초기화

    운영 환경에서는 Alembic 마이그레이션을 사용해야 하며, 런타임 스키마 변경은 수행하지 않는다.
    테스트 환경에서만 테이블 자동 생성을 허용한다.
    """
    from app.models import (  # noqa: F401
        api_key,
        bookmark,
        custom_source,
        feed_item,
        market_data_snapshot,
        source_status,
    )

    if os.getenv("TESTING", "").lower() == "true":
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created for testing environment")
    else:
        ensure_runtime_compatibility()
        logger.info("Runtime compatibility checks complete. Apply Alembic migrations for full sync.")


def ensure_runtime_compatibility():
    """운영 DB와 코드 스키마 간 치명적 불일치 최소 보정.

    배포 직후 컬럼 누락으로 API가 전면 500이 되는 상황을 방지한다.
    근본 해결은 Alembic migration이며, 이 함수는 임시 호환 레이어다.
    """
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.connect() as conn:
        if "feed_items" in table_names:
            feed_cols = {col["name"] for col in inspector.get_columns("feed_items")}
            if "translation_status" not in feed_cols:
                conn.execute(text("ALTER TABLE feed_items ADD COLUMN translation_status VARCHAR"))
                logger.warning("Added missing column: feed_items.translation_status")

        if "api_keys" in table_names:
            key_cols = {col["name"] for col in inspector.get_columns("api_keys")}
            if "key_prefix" not in key_cols:
                conn.execute(text("ALTER TABLE api_keys ADD COLUMN key_prefix VARCHAR"))
                logger.warning("Added missing column: api_keys.key_prefix")
            if "key_hash" not in key_cols:
                conn.execute(text("ALTER TABLE api_keys ADD COLUMN key_hash VARCHAR"))
                logger.warning("Added missing column: api_keys.key_hash")

            # 레거시 키 행은 즉시 무효화 정책 유지 (누락 컬럼으로 인한 500 방지)
            conn.execute(text("UPDATE api_keys SET is_active = FALSE WHERE key_prefix IS NULL OR key_hash IS NULL"))
            conn.execute(
                text("UPDATE api_keys SET key_prefix = 'legacy_' || CAST(id AS TEXT) WHERE key_prefix IS NULL")
            )
            conn.execute(
                text(
                    "UPDATE api_keys SET key_hash = 'legacy_invalid_' || CAST(id AS TEXT) "
                    "WHERE key_hash IS NULL"
                )
            )

        conn.commit()
