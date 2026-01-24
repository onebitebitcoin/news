"""Bitcoin Optech RSS Fetcher"""

import logging
import re
from datetime import datetime
from typing import Optional

from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class OptechFetcher(BaseFetcher):
    """Bitcoin Optech RSS Fetcher"""

    source_name = "optech"
    feed_url = "https://bitcoinops.org/feed.xml"
    category = "technical"

    async def normalize(self, entry: dict) -> Optional[dict]:
        """Bitcoin Optech RSS 엔트리 정규화"""
        title = entry.get("title", "")
        link = entry.get("link", "")

        if not title or not link:
            return None

        # 발행일 파싱 (Atom 형식)
        published = entry.get("published", entry.get("updated", ""))
        published_at = self.parse_datetime(published) if published else datetime.utcnow()

        # URL 해시 생성
        url_hash = self.create_url_hash(link)

        # 요약 추출
        summary = self._extract_summary(entry)

        # 카테고리 분류
        category = self._categorize(title)

        return {
            "id": self.generate_id(self.source_name, url_hash),
            "source": self.source_name,
            "source_ref": "Bitcoin Optech",
            "title": title,
            "summary": summary,
            "url": link,
            "author": entry.get("author", "Bitcoin Optech"),
            "published_at": published_at,
            "tags": ["bitcoin", "technical", "development"],
            "url_hash": url_hash,
            "raw": dict(entry),
            "image_url": None,
            "category": category,
        }

    def _extract_summary(self, entry: dict) -> str:
        """요약 추출"""
        summary = entry.get("summary", entry.get("content", [{}]))

        # content가 리스트인 경우
        if isinstance(summary, list) and summary:
            summary = summary[0].get("value", "")

        # content가 dict인 경우
        if isinstance(summary, dict):
            summary = summary.get("value", "")

        if summary:
            # HTML 태그 제거
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary.strip()
            # 줄바꿈 정리
            summary = re.sub(r"\s+", " ", summary)
            # 300자로 제한
            if len(summary) > 300:
                summary = summary[:297] + "..."

        return summary or ""

    def _categorize(self, title: str) -> str:
        """제목 기반 카테고리 분류"""
        title_lower = title.lower()

        if "newsletter" in title_lower:
            return "newsletter"
        elif "podcast" in title_lower:
            return "podcast"
        elif any(kw in title_lower for kw in ["bip", "proposal", "soft fork"]):
            return "technical"
        elif any(kw in title_lower for kw in ["security", "vulnerability"]):
            return "security"

        return "technical"
