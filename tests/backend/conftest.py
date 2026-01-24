from __future__ import annotations

import os
import sys

# 테스트 환경 설정 (스케줄러 비활성화)
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# backend 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.main import app
from app.database import Base, get_db

# 테스트용 SQLite 메모리 DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """테스트용 DB 세션"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """테스트 클라이언트"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_feed_item(db):
    """샘플 피드 아이템"""
    from app.models.feed_item import FeedItem
    from datetime import datetime

    item = FeedItem(
        id="test-001",
        source="Test Source",
        title="Test Bitcoin Article",
        summary="This is a test summary for the article.",
        url="https://example.com/test-article",
        author="Test Author",
        category="Market",
        score=80,
        published_at=datetime.utcnow(),
        fetched_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
