"""Cointelegraph RSS Fetcher"""

import logging
import re
from datetime import datetime
from typing import Optional

from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class CointelegraphFetcher(BaseFetcher):
    """Cointelegraph RSS Fetcher"""

    source_name = "cointelegraph"
    feed_url = "https://cointelegraph.com/rss"
    category = "news"

    async def normalize(self, entry: dict) -> Optional[dict]:
        """Cointelegraph RSS 엔트리 정규화"""
        title = entry.get("title", "")
        link = entry.get("link", "")

        if not title or not link:
            return None

        # 발행일 파싱
        published = entry.get("published", entry.get("pubDate", ""))
        published_at = self.parse_datetime(published) if published else datetime.utcnow()

        # URL 해시 생성
        url_hash = self.create_url_hash(link)

        # 요약 추출
        summary = self._extract_summary(entry)

        # 이미지 URL 추출
        image_url = self._extract_image(entry)

        # 태그 추출
        tags = self._extract_tags(entry)

        return {
            "id": self.generate_id(self.source_name, url_hash),
            "source": self.source_name,
            "source_ref": "Cointelegraph",
            "title": title,
            "summary": summary,
            "url": link,
            "author": entry.get("author", entry.get("dc:creator")),
            "published_at": published_at,
            "tags": tags or ["bitcoin", "crypto"],
            "url_hash": url_hash,
            "raw": dict(entry),
            "image_url": image_url,
            "category": self.category,
        }

    def _extract_summary(self, entry: dict) -> str:
        """요약 추출"""
        summary = entry.get("summary", entry.get("description", ""))

        # HTML 태그 제거
        if summary:
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary.strip()
            # 300자로 제한
            if len(summary) > 300:
                summary = summary[:297] + "..."

        return summary

    def _extract_image(self, entry: dict) -> Optional[str]:
        """이미지 URL 추출"""
        # media:content 또는 media:thumbnail
        if "media_content" in entry:
            media = entry["media_content"]
            if media and len(media) > 0:
                return media[0].get("url")

        if "media_thumbnail" in entry:
            thumb = entry["media_thumbnail"]
            if thumb and len(thumb) > 0:
                return thumb[0].get("url")

        # enclosure
        if "enclosures" in entry:
            for enc in entry["enclosures"]:
                if enc.get("type", "").startswith("image/"):
                    return enc.get("href")

        return None

    def _extract_tags(self, entry: dict) -> list:
        """태그 추출"""
        tags = ["bitcoin", "crypto"]

        # 카테고리/태그
        if "tags" in entry:
            for tag in entry["tags"]:
                term = tag.get("term", "")
                if term and term.lower() not in tags:
                    tags.append(term.lower())

        return tags[:5]  # 최대 5개
