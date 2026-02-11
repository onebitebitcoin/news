"""중복 제거 서비스"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem
from app.utils.url_utils import create_url_hash, normalize_url

logger = logging.getLogger(__name__)


class DedupService:
    """URL 기반 중복 제거 서비스"""

    @staticmethod
    def normalize_url(url: str) -> str:
        """URL 정규화 - 트래킹 파라미터 제거"""
        return normalize_url(url)

    @staticmethod
    def create_hash(url: str) -> str:
        """URL의 SHA256 해시 생성 (앞 16자리)"""
        return create_url_hash(url)

    @staticmethod
    def is_duplicate(db: Session, url_hash: str) -> bool:
        """해시 기준 중복 여부 확인"""
        exists = db.query(FeedItem).filter(
            FeedItem.url_hash == url_hash
        ).first() is not None

        if exists:
            logger.debug(f"Duplicate found: {url_hash}")

        return exists

    @staticmethod
    def find_existing(db: Session, url_hash: str) -> Optional[FeedItem]:
        """해시로 기존 아이템 조회"""
        return db.query(FeedItem).filter(
            FeedItem.url_hash == url_hash
        ).first()
