import logging
import os

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
    """데이터베이스 초기화

    운영 환경에서는 Alembic 마이그레이션을 사용해야 하며, 런타임 스키마 변경은 수행하지 않는다.
    테스트 환경에서만 테이블 자동 생성을 허용한다.
    """
    from app.models import (  # noqa: F401
        api_key,
        bookmark,
        feed_item,
        market_data_snapshot,
        source_status,
    )

    if os.getenv("TESTING", "").lower() == "true":
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created for testing environment")
    else:
        logger.info("Skipping runtime schema mutation. Apply migrations with Alembic.")
