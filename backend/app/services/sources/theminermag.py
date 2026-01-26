"""The Miner Mag Playwright Fetcher"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from playwright.async_api import async_playwright

from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class TheMinerMagFetcher(BaseFetcher):
    """The Miner Mag Playwright Fetcher"""

    source_name = "theminermag"
    feed_url = "https://theminermag.com/news"
    category = "news"

    def __init__(self, hours_limit: int = 24):
        super().__init__(hours_limit=hours_limit)
        self.max_pages = int(os.getenv("THEMINERMAG_MAX_PAGES", "3"))

    async def fetch(self) -> List[dict]:
        """Playwright로 뉴스 목록 수집"""
        logger.info(
            f"[{self.source_name}] Fetching pages via Playwright: {self.feed_url}"
        )

        items: List[dict] = []
        seen_urls: set[str] = set()

        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                page = await browser.new_page()

                for page_num in range(1, self.max_pages + 1):
                    page_url = self._build_page_url(page_num)
                    logger.info(
                        f"[{self.source_name}] Loading page {page_num}: {page_url}"
                    )

                    await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(1500)

                    raw_items = await self._extract_items(page)
                    if not raw_items:
                        raise RuntimeError(
                            f"[{self.source_name}] No items found on page {page_num}"
                        )

                    for entry in raw_items:
                        normalized = await self.normalize(entry)
                        if not normalized:
                            continue
                        if not self._is_within_time_limit(normalized):
                            continue
                        if normalized["url"] in seen_urls:
                            continue
                        items.append(normalized)
                        seen_urls.add(normalized["url"])

                await browser.close()

            logger.info(
                f"[{self.source_name}] Fetched {len(items)} items "
                f"(within {self.hours_limit}h)"
            )
            return items

        except Exception as e:
            logger.error(f"[{self.source_name}] Fetch error: {e}", exc_info=True)
            raise

    async def normalize(self, entry: dict) -> Optional[dict]:
        """스크래핑 결과를 표준 형식으로 변환"""
        title = entry.get("title", "")
        link = entry.get("url", "")

        if not title or not link:
            return None

        published_at = self._parse_date(entry.get("published_text", ""))
        if not published_at:
            published_at = datetime.utcnow()

        url_hash = self.create_url_hash(link)

        return {
            "id": self.generate_id(self.source_name, url_hash),
            "source": self.source_name,
            "source_ref": "The Miner Mag",
            "title": title,
            "summary": entry.get("summary"),
            "url": link,
            "author": entry.get("author"),
            "published_at": published_at,
            "tags": entry.get("tags") or ["bitcoin", "mining"],
            "url_hash": url_hash,
            "raw": entry,
            "image_url": entry.get("image_url"),
            "category": self.category,
        }

    async def _extract_items(self, page) -> List[dict]:
        """페이지에서 뉴스 목록 추출"""
        raw_items = await page.eval_on_selector_all(
            "a[href^='/news/']",
            """
            (els) => els.map((el) => {
                const titleEl = el.querySelector('h2');
                const summaryEl = el.querySelector('p');
                const dateEl = el.querySelector('div.flex.items-center');
                const imgEl = el.querySelector('img');

                const text = (value) => (value || '').replace(/\\s+/g, ' ').trim();

                return {
                    href: el.getAttribute('href') || '',
                    title: text(titleEl ? titleEl.textContent : ''),
                    summary: text(summaryEl ? summaryEl.textContent : ''),
                    publishedText: text(dateEl ? dateEl.textContent : ''),
                    imageSrc: imgEl ? imgEl.getAttribute('src') : '',
                    imageSrcSet: imgEl ? imgEl.getAttribute('srcset') : ''
                };
            })
            """
        )

        items: List[dict] = []
        for item in raw_items:
            href = item.get("href", "")
            title = item.get("title", "")
            if not href or not title:
                continue

            absolute_url = urljoin(self.feed_url, href)
            image_url = self._extract_image_url(
                item.get("imageSrc", ""), item.get("imageSrcSet", "")
            )

            items.append(
                {
                    "url": absolute_url,
                    "title": title,
                    "summary": item.get("summary") or None,
                    "published_text": item.get("publishedText") or "",
                    "image_url": image_url,
                    "author": None,
                    "tags": ["bitcoin", "mining"],
                }
            )

        return items

    def _build_page_url(self, page_num: int) -> str:
        if page_num <= 1:
            return self.feed_url
        return f"{self.feed_url}?page={page_num}"

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        if not date_text:
            return None

        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue

        logger.warning(f"[{self.source_name}] Could not parse date: {date_text}")
        return None

    def _extract_image_url(self, src: str, srcset: str) -> Optional[str]:
        candidate = src or ""
        if not candidate and srcset:
            candidate = srcset.split(",")[-1].strip().split(" ")[0]

        if not candidate:
            return None

        parsed = urlparse(candidate)
        if parsed.path == "/_next/image":
            params = parse_qs(parsed.query)
            if "url" in params and params["url"]:
                return unquote(params["url"][0])

        return candidate
