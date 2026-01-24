"""중복 제거 서비스"""

import hashlib
import logging
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem

logger = logging.getLogger(__name__)


class DedupService:
    """URL 기반 중복 제거 서비스"""

    # 제거할 트래킹 파라미터
    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_content",
        "utm_term", "ref", "source", "fbclid", "gclid", "mc_cid",
        "mc_eid", "__s", "s_kwcid"
    }

    @staticmethod
    def normalize_url(url: str) -> str:
        """URL 정규화 - 트래킹 파라미터 제거"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        # 트래킹 파라미터 제거
        filtered_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in DedupService.TRACKING_PARAMS
        }

        # URL 재구성
        if filtered_params:
            new_query = urlencode(filtered_params, doseq=True)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if new_query:
                normalized += f"?{new_query}"
        else:
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        return normalized.rstrip("/")

    @staticmethod
    def create_hash(url: str) -> str:
        """URL의 SHA256 해시 생성 (앞 16자리)"""
        normalized = DedupService.normalize_url(url)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

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
