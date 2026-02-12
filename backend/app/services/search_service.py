"""키워드 기사 검색 서비스 - Google News RSS"""

import asyncio
import logging
import re
from typing import List, Optional
from urllib.parse import quote

import feedparser
from sqlalchemy.orm import Session

from app.schemas.feed import SearchArticleItem
from app.services.dedup_service import DedupService
from app.services.sources.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US"


class SearchService:
    """Google News RSS 키워드 검색"""

    def __init__(self, db: Session):
        self.db = db

    async def search(self, query: str, max_results: int = 20) -> List[SearchArticleItem]:
        """키워드로 Google News RSS 검색"""
        encoded_query = quote(query)
        feed_url = GOOGLE_NEWS_RSS_URL.format(query=encoded_query)

        logger.info(f"[SearchService] Searching: query={query}, url={feed_url}")

        feed = await asyncio.to_thread(feedparser.parse, feed_url)

        if feed.bozo and feed.bozo_exception:
            logger.warning(f"[SearchService] Feed parsing warning: {feed.bozo_exception}")

        items: List[SearchArticleItem] = []
        for entry in feed.entries[:max_results]:
            try:
                item = self._parse_entry(entry)
                if item:
                    items.append(item)
            except Exception as e:
                logger.error(f"[SearchService] Error parsing entry: {e}", exc_info=True)

        logger.info(f"[SearchService] Found {len(items)} results for query={query}")
        return items

    def _parse_entry(self, entry: dict) -> Optional[SearchArticleItem]:
        """RSS 엔트리를 SearchArticleItem으로 변환"""
        title = entry.get("title", "")
        link = entry.get("link", "")

        if not title or not link:
            return None

        source_ref = self._extract_source(title)
        clean_title = self._clean_title(title)

        published = entry.get("published", "")
        published_at = BaseFetcher.parse_datetime(published) if published else None

        raw_summary = entry.get("summary", "")
        clean_summary = self._strip_html(raw_summary)

        url_hash = DedupService.create_hash(link)
        is_duplicate = DedupService.is_duplicate(self.db, url_hash)

        return SearchArticleItem(
            title=clean_title,
            url=link,
            summary=clean_summary or None,
            source_ref=source_ref,
            published_at=published_at,
            is_duplicate=is_duplicate,
        )

    @staticmethod
    def _extract_source(title: str) -> Optional[str]:
        """제목에서 소스 추출 (마지막 ' - ' 이후)"""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                return parts[1].strip()
        return None

    @staticmethod
    def _clean_title(title: str) -> str:
        """제목에서 소스 제거"""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                return parts[0].strip()
        return title

    @staticmethod
    def _strip_html(text: str) -> str:
        """HTML 태그 제거"""
        if not text:
            return ""
        clean = re.sub(r"<[^>]+>", "", text)
        clean = clean.replace("&nbsp;", " ")
        clean = clean.replace("&amp;", "&")
        clean = clean.replace("&lt;", "<")
        clean = clean.replace("&gt;", ">")
        clean = clean.replace("&quot;", '"')
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()
