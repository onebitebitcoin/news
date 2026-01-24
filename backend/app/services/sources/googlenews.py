"""Google News RSS Fetcher"""

import logging
import re
from datetime import datetime
from typing import Optional

from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class GoogleNewsFetcher(BaseFetcher):
    """Google News RSS Fetcher"""

    source_name = "googlenews"
    feed_url = "https://news.google.com/rss/search?q=bitcoin&hl=en-US&gl=US"
    category = "news"

    async def normalize(self, entry: dict) -> Optional[dict]:
        """Google News RSS 엔트리 정규화"""
        title = entry.get("title", "")
        link = entry.get("link", "")

        if not title or not link:
            return None

        # Google News는 title에 소스가 포함됨 (예: "Bitcoin rises - Bloomberg")
        source_ref = self._extract_source(title)
        clean_title = self._clean_title(title)

        # 발행일 파싱
        published = entry.get("published", "")
        published_at = self.parse_datetime(published) if published else datetime.utcnow()

        # URL 해시 생성
        url_hash = self.create_url_hash(link)

        # summary에서 HTML 태그 제거
        raw_summary = entry.get("summary", "")
        clean_summary = self._strip_html(raw_summary)

        return {
            "id": self.generate_id(self.source_name, url_hash),
            "source": self.source_name,
            "source_ref": source_ref,
            "title": clean_title,
            "summary": clean_summary,
            "url": link,
            "author": None,
            "published_at": published_at,
            "tags": ["bitcoin"],
            "url_hash": url_hash,
            "raw": dict(entry),
            "image_url": None,
            "category": self.category,
        }

    def _strip_html(self, text: str) -> str:
        """HTML 태그 제거"""
        if not text:
            return ""
        # HTML 태그 제거
        clean = re.sub(r"<[^>]+>", "", text)
        # HTML 엔티티 정리
        clean = clean.replace("&nbsp;", " ")
        clean = clean.replace("&amp;", "&")
        clean = clean.replace("&lt;", "<")
        clean = clean.replace("&gt;", ">")
        clean = clean.replace("&quot;", '"')
        # 연속 공백 정리
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()

    def _extract_source(self, title: str) -> Optional[str]:
        """제목에서 소스 추출 (마지막 ' - ' 이후)"""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                return parts[1].strip()
        return None

    def _clean_title(self, title: str) -> str:
        """제목에서 소스 제거"""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                return parts[0].strip()
        return title
