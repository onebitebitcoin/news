"""RSS Fetcher 테스트"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# backend 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.sources.base_fetcher import BaseFetcher
from app.services.sources.googlenews import GoogleNewsFetcher
from app.services.sources.bitcoinmagazine import BitcoinMagazineFetcher
from app.services.sources.optech import OptechFetcher
from app.services.dedup_service import DedupService
from app.services.fetch_engine import FetchEngine


class TestBaseFetcher:
    """BaseFetcher 테스트"""

    def test_normalize_url_removes_utm_params(self):
        """URL 정규화 - UTM 파라미터 제거"""
        url = "https://example.com/article?id=123&utm_source=twitter&utm_medium=social"
        normalized = BaseFetcher.normalize_url(url)

        assert "utm_source" not in normalized
        assert "utm_medium" not in normalized
        assert "id=123" in normalized

    def test_normalize_url_removes_trailing_slash(self):
        """URL 정규화 - 끝 슬래시 제거"""
        url = "https://example.com/article/"
        normalized = BaseFetcher.normalize_url(url)

        assert not normalized.endswith("/")

    def test_create_url_hash_consistency(self):
        """URL 해시 일관성 테스트"""
        url1 = "https://example.com/article?utm_source=twitter"
        url2 = "https://example.com/article?utm_source=facebook"

        # UTM 파라미터가 다르지만 같은 해시 생성
        hash1 = BaseFetcher.create_url_hash(url1)
        hash2 = BaseFetcher.create_url_hash(url2)

        assert hash1 == hash2

    def test_create_url_hash_different_for_different_urls(self):
        """다른 URL은 다른 해시"""
        url1 = "https://example.com/article1"
        url2 = "https://example.com/article2"

        hash1 = BaseFetcher.create_url_hash(url1)
        hash2 = BaseFetcher.create_url_hash(url2)

        assert hash1 != hash2

    def test_parse_datetime_rfc2822(self):
        """RFC 2822 형식 날짜 파싱"""
        dt_string = "Mon, 20 Jan 2025 10:30:00 GMT"
        parsed = BaseFetcher.parse_datetime(dt_string)

        assert parsed is not None
        assert parsed.year == 2025
        assert parsed.month == 1
        assert parsed.day == 20

    def test_parse_datetime_iso8601(self):
        """ISO 8601 형식 날짜 파싱"""
        dt_string = "2025-01-20T10:30:00Z"
        parsed = BaseFetcher.parse_datetime(dt_string)

        assert parsed is not None
        assert parsed.year == 2025

    def test_parse_datetime_invalid(self):
        """잘못된 날짜 형식"""
        dt_string = "invalid-date"
        parsed = BaseFetcher.parse_datetime(dt_string)

        assert parsed is None

    def test_generate_id(self):
        """ID 생성 테스트"""
        source = "googlenews"
        url_hash = "abc123"

        id = BaseFetcher.generate_id(source, url_hash)

        assert id == "googlenews_abc123"


class TestDedupService:
    """DedupService 테스트"""

    def test_normalize_url(self):
        """URL 정규화 테스트"""
        url = "https://example.com/article?fbclid=abc123"
        normalized = DedupService.normalize_url(url)

        assert "fbclid" not in normalized

    def test_create_hash(self):
        """해시 생성 테스트"""
        url = "https://example.com/article"
        hash1 = DedupService.create_hash(url)

        assert len(hash1) == 16
        assert hash1.isalnum()

    def test_is_duplicate_false(self, db):
        """중복 아닌 경우"""
        is_dup = DedupService.is_duplicate(db, "nonexistent_hash")
        assert is_dup is False

    def test_is_duplicate_true(self, db):
        """중복인 경우"""
        from app.models.feed_item import FeedItem

        item = FeedItem(
            id="test-dup",
            source="test",
            title="Test",
            url="https://example.com",
            url_hash="existing_hash",
            fetched_at=datetime.utcnow(),
        )
        db.add(item)
        db.commit()

        is_dup = DedupService.is_duplicate(db, "existing_hash")
        assert is_dup is True


class TestGoogleNewsFetcher:
    """GoogleNewsFetcher 테스트"""

    def test_source_name(self):
        """소스 이름 확인"""
        fetcher = GoogleNewsFetcher()
        assert fetcher.source_name == "googlenews"

    def test_extract_source_from_title(self):
        """제목에서 소스 추출"""
        fetcher = GoogleNewsFetcher()

        title = "Bitcoin hits new high - Bloomberg"
        source = fetcher._extract_source(title)

        assert source == "Bloomberg"

    def test_clean_title(self):
        """제목 정리"""
        fetcher = GoogleNewsFetcher()

        title = "Bitcoin hits new high - Bloomberg"
        clean = fetcher._clean_title(title)

        assert clean == "Bitcoin hits new high"

    @pytest.mark.asyncio
    async def test_normalize_entry(self):
        """엔트리 정규화 테스트"""
        fetcher = GoogleNewsFetcher()

        entry = {
            "title": "Bitcoin rises 10% - CoinDesk",
            "link": "https://news.google.com/article/123",
            "published": "Mon, 20 Jan 2025 10:00:00 GMT",
            "summary": "Bitcoin price has risen..."
        }

        normalized = await fetcher.normalize(entry)

        assert normalized is not None
        assert normalized["source"] == "googlenews"
        assert normalized["source_ref"] == "CoinDesk"
        assert normalized["title"] == "Bitcoin rises 10%"
        assert "url_hash" in normalized


class TestBitcoinMagazineFetcher:
    """BitcoinMagazineFetcher 테스트"""

    def test_source_name(self):
        """소스 이름 확인"""
        fetcher = BitcoinMagazineFetcher()
        assert fetcher.source_name == "bitcoinmagazine"

    @pytest.mark.asyncio
    async def test_normalize_entry(self):
        """엔트리 정규화 테스트"""
        fetcher = BitcoinMagazineFetcher()

        entry = {
            "title": "Bitcoin Mining Update",
            "link": "https://bitcoinmagazine.com/mining/article",
            "published": "Mon, 20 Jan 2025 10:00:00 GMT",
            "summary": "<p>Mining difficulty...</p>",
            "author": "John Doe"
        }

        normalized = await fetcher.normalize(entry)

        assert normalized is not None
        assert normalized["source"] == "bitcoinmagazine"
        assert normalized["author"] == "John Doe"
        assert "<p>" not in normalized["summary"]  # HTML 제거


class TestOptechFetcher:
    """OptechFetcher 테스트"""

    def test_source_name(self):
        """소스 이름 확인"""
        fetcher = OptechFetcher()
        assert fetcher.source_name == "optech"

    def test_categorize_newsletter(self):
        """뉴스레터 분류"""
        fetcher = OptechFetcher()

        category = fetcher._categorize("Bitcoin Optech Newsletter #289")
        assert category == "newsletter"

    def test_categorize_technical(self):
        """기술 문서 분류"""
        fetcher = OptechFetcher()

        category = fetcher._categorize("BIP-352: Silent Payments")
        assert category == "technical"


class TestFetchEngine:
    """FetchEngine 테스트"""

    def test_get_source_names(self):
        """소스 이름 목록"""
        names = FetchEngine.get_source_names()

        assert "googlenews" in names
        assert "bitcoinmagazine" in names
        assert "optech" in names

    @pytest.mark.asyncio
    async def test_run_source_unknown(self, db):
        """알 수 없는 소스"""
        engine = FetchEngine(db)
        result = await engine.run_source("unknown_source")

        assert result["success"] is False
        assert "Unknown source" in result["error"]


class TestAdminAPI:
    """Admin API 테스트"""

    def test_get_sources(self, client):
        """소스 목록 조회"""
        response = client.get("/api/v1/admin/sources")

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert "sources" in data
        assert "available_sources" in data
        assert "googlenews" in data["available_sources"]

    def test_run_fetch_invalid_source(self, client):
        """잘못된 소스 수집 시도"""
        response = client.post("/api/v1/admin/fetch/run/invalid_source")

        assert response.status_code == 404
