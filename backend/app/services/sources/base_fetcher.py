"""RSS Fetcher 기본 인터페이스"""

import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import feedparser

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """RSS Fetcher 기본 클래스"""

    source_name: str = ""
    feed_url: str = ""
    category: str = "news"

    def __init__(self, hours_limit: int = 24):
        """
        Args:
            hours_limit: 수집할 뉴스 시간 제한 (기본 24시간)
        """
        self.hours_limit = hours_limit
        self.cutoff_time = datetime.utcnow() - timedelta(hours=hours_limit)

    async def fetch(self) -> List[dict]:
        """RSS 피드에서 아이템 수집"""
        logger.info(f"[{self.source_name}] Fetching RSS from: {self.feed_url}")

        try:
            feed = feedparser.parse(self.feed_url)

            if feed.bozo and feed.bozo_exception:
                logger.warning(
                    f"[{self.source_name}] Feed parsing warning: {feed.bozo_exception}"
                )

            items = []
            for entry in feed.entries:
                try:
                    normalized = await self.normalize(entry)
                    if normalized and self._is_within_time_limit(normalized):
                        items.append(normalized)
                except Exception as e:
                    logger.error(
                        f"[{self.source_name}] Error normalizing entry: {e}",
                        exc_info=True
                    )

            logger.info(
                f"[{self.source_name}] Fetched {len(items)} items "
                f"(within {self.hours_limit}h)"
            )
            return items

        except Exception as e:
            logger.error(f"[{self.source_name}] Fetch error: {e}", exc_info=True)
            raise

    @abstractmethod
    async def normalize(self, entry: dict) -> Optional[dict]:
        """RSS 엔트리를 표준 형식으로 변환

        Returns:
            dict with keys:
                - id: str (고유 ID)
                - source: str
                - title: str
                - summary: str (optional)
                - url: str
                - author: str (optional)
                - published_at: datetime
                - tags: list (optional)
                - url_hash: str
                - raw: dict (원본 데이터)
                - image_url: str (optional)
                - category: str
        """
        pass

    def _is_within_time_limit(self, item: dict) -> bool:
        """시간 제한 내의 아이템인지 확인"""
        published_at = item.get("published_at")
        if not published_at:
            return True  # 날짜 없으면 일단 포함

        return published_at >= self.cutoff_time

    @staticmethod
    def normalize_url(url: str) -> str:
        """URL 정규화 - 트래킹 파라미터 제거"""
        tracking_params = {
            "utm_source", "utm_medium", "utm_campaign", "utm_content",
            "utm_term", "ref", "source", "fbclid", "gclid"
        }

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        # 트래킹 파라미터 제거
        filtered_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in tracking_params
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
    def create_url_hash(url: str) -> str:
        """URL의 SHA256 해시 생성"""
        normalized = BaseFetcher.normalize_url(url)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    @staticmethod
    def parse_datetime(dt_string: str) -> Optional[datetime]:
        """다양한 형식의 날짜 문자열 파싱"""
        import email.utils

        if not dt_string:
            return None

        # RSS 표준 형식 (RFC 2822)
        try:
            parsed = email.utils.parsedate_to_datetime(dt_string)
            return parsed.replace(tzinfo=None)  # UTC로 가정, naive datetime으로 변환
        except (TypeError, ValueError):
            pass

        # ISO 8601 형식
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(dt_string, fmt)
                return parsed.replace(tzinfo=None)
            except ValueError:
                continue

        logger.warning(f"Could not parse datetime: {dt_string}")
        return None

    @staticmethod
    def generate_id(source: str, url_hash: str) -> str:
        """고유 ID 생성"""
        return f"{source}_{url_hash}"
