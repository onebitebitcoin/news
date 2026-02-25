"""커스텀 스크래핑 소스 분석/수집 서비스"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from openai import OpenAI

from app.services.sources.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

_TIME_META_CANDIDATES: list[tuple[str, dict[str, str]]] = [
    ("meta", {"property": "article:published_time"}),
    ("meta", {"name": "article:published_time"}),
    ("meta", {"property": "og:published_time"}),
    ("meta", {"name": "pubdate"}),
    ("meta", {"name": "publishdate"}),
    ("meta", {"name": "date"}),
    ("meta", {"itemprop": "datePublished"}),
]


def slugify_source_name(name: str) -> str:
    value = name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if not value:
        raise ValueError("유효한 소스 이름을 입력해주세요.")
    return value[:120]


def validate_public_http_url(raw_url: str) -> str:
    """공용 http/https URL만 허용 (기본 SSRF 방어)"""
    try:
        parsed = urlparse(raw_url.strip())
    except Exception as exc:  # pragma: no cover
        raise ValueError("유효하지 않은 URL입니다.") from exc

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("http/https URL만 허용됩니다.")

    if not parsed.netloc or not parsed.hostname:
        raise ValueError("호스트가 없는 URL입니다.")

    host = parsed.hostname.lower()
    blocked_hosts = {"localhost", "0.0.0.0", "::1"}
    if host in blocked_hosts or host.endswith(".local"):
        raise ValueError("localhost/내부망 주소는 허용되지 않습니다.")

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip and any([ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_reserved, ip.is_multicast]):
        raise ValueError("사설망/로컬 IP 주소는 허용되지 않습니다.")

    return raw_url.strip()


def _strip_html(text: Optional[str]) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class CustomSourceScrapeService:
    """커스텀 스크래핑 소스 분석 및 실행"""

    AI_MODEL = "gpt-5-mini"
    USER_AGENT = "Mozilla/5.0 (compatible; BitcoinNewsBot/1.0)"
    MAX_HTML_CHARS = 80_000
    MAX_PREVIEW_ITEMS = 5
    MAX_FETCH_ITEMS = 20

    async def analyze(self, *, name: str, list_url: str) -> dict[str, Any]:
        source_name = name.strip()
        safe_url = validate_public_http_url(list_url)
        html, final_url = await self._fetch_html(safe_url)
        validate_public_http_url(final_url)

        warnings: list[str] = []
        ai_rules = await self._build_ai_rules(source_name, final_url, html)
        if ai_rules.get("_warning"):
            warnings.append(ai_rules["_warning"])

        rules = self._merge_rules(
            self._build_heuristic_rules(source_name, final_url, html),
            ai_rules,
        )
        preview_items, validation_errors = await self._preview_from_rules(
            name=source_name,
            list_url=final_url,
            html=html,
            rules=rules,
            max_items=self.MAX_PREVIEW_ITEMS,
        )

        return {
            "draft": {
                "slug_suggestion": slugify_source_name(source_name),
                "name": source_name,
                "list_url": final_url,
                "fetch_mode": "scrape",
                "extraction_rules": rules,
                "normalization_rules": {},
                "ai_model": self.AI_MODEL if ai_rules.get("_used_ai") else None,
            },
            "preview_items": [
                {
                    "title": item["title"],
                    "url": item["url"],
                    "published_at": item["published_at"].isoformat() + "Z",
                    "summary": item.get("summary"),
                    "image_url": item.get("image_url"),
                }
                for item in preview_items
            ],
            "warnings": warnings,
            "validation_errors": validation_errors,
            "is_valid": len(validation_errors) == 0 and len(preview_items) > 0,
        }

    async def validate_saved_config(
        self,
        *,
        name: str,
        list_url: str,
        extraction_rules: dict[str, Any],
        max_items: int = 5,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        safe_url = validate_public_http_url(list_url)
        html, final_url = await self._fetch_html(safe_url)
        validate_public_http_url(final_url)
        rules = self._merge_rules(self._build_heuristic_rules(name, final_url, html), extraction_rules or {})
        return await self._preview_from_rules(
            name=name,
            list_url=final_url,
            html=html,
            rules=rules,
            max_items=max_items,
        )

    async def fetch_items(
        self,
        *,
        source_slug: str,
        source_name: str,
        list_url: str,
        extraction_rules: dict[str, Any],
        hours_limit: int = 24,
    ) -> list[dict[str, Any]]:
        preview_items, errors = await self.validate_saved_config(
            name=source_name,
            list_url=list_url,
            extraction_rules=extraction_rules,
            max_items=int(extraction_rules.get("max_items", self.MAX_FETCH_ITEMS)),
        )
        if errors:
            logger.warning(f"[{source_slug}] Custom source validation warnings: {errors}")

        cutoff = datetime.utcnow() - timedelta(hours=hours_limit)
        items: list[dict[str, Any]] = []
        for item in preview_items:
            published_at = item["published_at"]
            if not published_at or published_at < cutoff:
                continue
            url_hash = BaseFetcher.create_url_hash(item["url"])
            items.append(
                {
                    "id": BaseFetcher.generate_id(source_slug, url_hash),
                    "source": source_slug,
                    "source_ref": source_name,
                    "title": item["title"],
                    "summary": item.get("summary") or "",
                    "url": item["url"],
                    "author": source_name,
                    "published_at": published_at,
                    "tags": ["bitcoin", "custom-source"],
                    "url_hash": url_hash,
                    "raw": {
                        "custom_source": True,
                        "custom_source_name": source_name,
                        "custom_source_slug": source_slug,
                        "list_url": list_url,
                    },
                    "image_url": item.get("image_url"),
                    "category": "news",
                }
            )
        return items

    async def _fetch_html(self, url: str) -> tuple[str, str]:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={"User-Agent": self.USER_AGENT},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text[: self.MAX_HTML_CHARS]
            return html, str(resp.url)

    async def _build_ai_rules(self, name: str, list_url: str, html: str) -> dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return {"_warning": "OPENAI_API_KEY가 없어 휴리스틱 분석으로 진행했습니다."}

        prompt = (
            "You are extracting article list parsing rules from an HTML page.\n"
            "Return ONLY JSON with keys:\n"
            "{\n"
            '  "item_selector": string|null,\n'
            '  "link_selector": string|null,\n'
            '  "title_selector": string|null,\n'
            '  "summary_selector": string|null,\n'
            '  "published_selector": string|null,\n'
            '  "published_attr": string|null,\n'
            '  "max_items": number\n'
            "}\n"
            "Prefer broad/stable selectors. If not sure, use null values.\n\n"
            f"Page URL: {list_url}\n"
            f"Source name: {name}\n"
            "HTML snippet:\n"
            f"{html[:20000]}"
        )

        def _call() -> str:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.AI_MODEL,
                messages=[
                    {"role": "system", "content": "Return strict JSON only."},
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=500,
            )
            return response.choices[0].message.content or ""

        try:
            raw = await asyncio.to_thread(_call)
            parsed = self._parse_json_response(raw)
            if not isinstance(parsed, dict):
                raise ValueError("AI 응답이 JSON 객체가 아닙니다.")
            parsed["_used_ai"] = True
            return parsed
        except Exception as exc:
            logger.warning(f"AI rule generation failed: {exc}")
            return {"_warning": f"AI 분석 실패로 휴리스틱 분석으로 진행했습니다. ({exc})"}

    @staticmethod
    def _parse_json_response(raw: str) -> Any:
        cleaned = (raw or "").strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 3:
                cleaned = "\n".join(lines[1:-1]).strip()
        return json.loads(cleaned)

    def _build_heuristic_rules(self, name: str, list_url: str, html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        has_article = bool(soup.select("article"))
        return {
            "strategy": "hybrid_link_discovery",
            "item_selector": "article" if has_article else None,
            "link_selector": "a[href]",
            "title_selector": None,
            "summary_selector": None,
            "published_selector": "time",
            "published_attr": "datetime",
            "max_items": self.MAX_FETCH_ITEMS,
            "source_hint": slugify_source_name(name),
            "base_url": list_url,
        }

    @staticmethod
    def _merge_rules(base_rules: dict[str, Any], override_rules: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base_rules or {})
        for key, value in (override_rules or {}).items():
            if key.startswith("_"):
                continue
            if value is None and key in merged:
                continue
            merged[key] = value
        return merged

    async def _preview_from_rules(
        self,
        *,
        name: str,
        list_url: str,
        html: str,
        rules: dict[str, Any],
        max_items: int,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        validation_errors: list[str] = []
        candidates = self._extract_candidate_links(list_url=list_url, html=html, rules=rules)
        if not candidates:
            return [], ["기사 링크를 추출하지 못했습니다. 다른 URL을 입력하거나 재분석하세요."]

        preview_targets = candidates[: max(1, min(max_items, self.MAX_FETCH_ITEMS))]
        previews = await self._fetch_article_previews(preview_targets)

        valid_previews: list[dict[str, Any]] = []
        for preview in previews:
            if not preview:
                continue
            if not preview.get("published_at"):
                continue
            valid_previews.append(preview)

        if not valid_previews:
            validation_errors.append("게시시간을 추출하지 못해 저장할 수 없습니다.")

        if len(valid_previews) < min(1, len(preview_targets)):
            validation_errors.append("유효한 기사 미리보기 수가 부족합니다.")

        return valid_previews, list(dict.fromkeys(validation_errors))

    def _extract_candidate_links(self, *, list_url: str, html: str, rules: dict[str, Any]) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        anchors: list[tuple[str, str]] = []
        seen: set[str] = set()

        item_selector = rules.get("item_selector")
        link_selector = rules.get("link_selector") or "a[href]"
        title_selector = rules.get("title_selector")

        containers = soup.select(item_selector) if item_selector else [soup]
        for container in containers:
            link_nodes = container.select(link_selector)
            for link_node in link_nodes:
                href = link_node.get("href")
                if not href:
                    continue
                absolute = urljoin(list_url, href)
                if not absolute.startswith(("http://", "https://")):
                    continue
                try:
                    validate_public_http_url(absolute)
                except ValueError:
                    continue
                if absolute in seen:
                    continue

                title_text = ""
                if title_selector:
                    title_node = container.select_one(title_selector)
                    if title_node:
                        title_text = _strip_html(title_node.get_text(" ", strip=True))
                if not title_text:
                    title_text = _strip_html(link_node.get_text(" ", strip=True))

                if len(title_text) < 10:
                    continue

                parsed_abs = urlparse(absolute)
                parsed_list = urlparse(list_url)
                if parsed_abs.netloc != parsed_list.netloc and rules.get("strategy") == "hybrid_link_discovery":
                    # 외부 도메인은 기본적으로 제외
                    continue

                seen.add(absolute)
                anchors.append((absolute, title_text))

        if anchors:
            return [{"url": url, "title": title} for url, title in anchors]

        # 최종 fallback: 전체 페이지 anchor 탐색
        for a in soup.find_all("a", href=True):
            href = urljoin(list_url, a["href"])
            title = _strip_html(a.get_text(" ", strip=True))
            if href in seen or len(title) < 10 or not href.startswith(("http://", "https://")):
                continue
            try:
                validate_public_http_url(href)
            except ValueError:
                continue
            seen.add(href)
            anchors.append((href, title))

        return [{"url": url, "title": title} for url, title in anchors]

    async def _fetch_article_previews(self, candidates: list[dict[str, str]]) -> list[Optional[dict[str, Any]]]:
        sem = asyncio.Semaphore(4)

        async def _worker(candidate: dict[str, str]) -> Optional[dict[str, Any]]:
            async with sem:
                return await self._fetch_single_article_preview(candidate["url"], candidate["title"])

        tasks = [_worker(candidate) for candidate in candidates]
        return await asyncio.gather(*tasks)

    async def _fetch_single_article_preview(self, url: str, title_hint: str) -> Optional[dict[str, Any]]:
        try:
            html, final_url = await self._fetch_html(url)
            validate_public_http_url(final_url)
            soup = BeautifulSoup(html, "html.parser")

            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            og_image = soup.find("meta", property="og:image")

            title = (
                (og_title.get("content") if og_title else None)
                or (soup.title.string.strip() if soup.title and soup.title.string else None)
                or title_hint
            )
            summary = (
                (og_desc.get("content") if og_desc else None)
                or self._extract_meta_description(soup)
                or ""
            )
            image_url = og_image.get("content") if og_image else None

            published_at = self._extract_published_at(soup)
            return {
                "title": _strip_html(title)[:300],
                "url": str(final_url),
                "published_at": published_at,
                "summary": _strip_html(summary)[:500] if summary else "",
                "image_url": image_url,
            }
        except Exception as exc:
            logger.debug(f"Custom source article preview failed for {url}: {exc}")
            return None

    @staticmethod
    def _extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            return desc["content"]
        return None

    def _extract_published_at(self, soup: BeautifulSoup) -> Optional[datetime]:
        for tag_name, attrs in _TIME_META_CANDIDATES:
            node = soup.find(tag_name, attrs=attrs)
            if node and node.get("content"):
                parsed = BaseFetcher.parse_datetime(node["content"])
                if parsed:
                    return parsed

        for time_node in soup.find_all("time"):
            dt_raw = time_node.get("datetime") or time_node.get_text(" ", strip=True)
            parsed = BaseFetcher.parse_datetime(dt_raw)
            if parsed:
                return parsed

        # JSON-LD fallback
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            text = script.string or script.get_text()
            if not text:
                continue
            try:
                data = json.loads(text)
            except Exception:
                continue
            parsed = self._extract_published_from_jsonld(data)
            if parsed:
                return parsed

        return None

    def _extract_published_from_jsonld(self, data: Any) -> Optional[datetime]:
        if isinstance(data, list):
            for item in data:
                parsed = self._extract_published_from_jsonld(item)
                if parsed:
                    return parsed
            return None
        if isinstance(data, dict):
            date_val = data.get("datePublished") or data.get("dateCreated")
            if isinstance(date_val, str):
                parsed = BaseFetcher.parse_datetime(date_val)
                if parsed:
                    return parsed
            for value in data.values():
                parsed = self._extract_published_from_jsonld(value)
                if parsed:
                    return parsed
        return None
