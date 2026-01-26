"""RSS 통합 수집 엔진"""

import json
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Type

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem
from app.models.source_status import SourceStatus
from app.services.dedup_service import DedupService
from app.services.sources.base_fetcher import BaseFetcher
from app.services.sources.bitcoincom import BitcoinComFetcher
from app.services.sources.bitcoinmagazine import BitcoinMagazineFetcher
from app.services.sources.blockworks import BlockworksFetcher
from app.services.sources.coindesk import CoinDeskFetcher
from app.services.sources.cointelegraph import CointelegraphFetcher
from app.services.sources.cryptoslate import CryptoSlateFetcher
from app.services.sources.decrypt import DecryptFetcher
from app.services.sources.googlenews import GoogleNewsFetcher
from app.services.sources.optech import OptechFetcher
from app.services.sources.theblock import TheBlockFetcher
from app.services.sources.theminermag import TheMinerMagFetcher
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)


class FetchEngine:
    """RSS 통합 수집 엔진"""

    # 등록된 Fetcher 클래스들
    FETCHERS: List[Type[BaseFetcher]] = [
        GoogleNewsFetcher,
        BitcoinMagazineFetcher,
        OptechFetcher,
        # 새로 추가된 소스
        CoinDeskFetcher,
        CointelegraphFetcher,
        TheBlockFetcher,
        TheMinerMagFetcher,
        DecryptFetcher,
        BitcoinComFetcher,
        BlockworksFetcher,
        CryptoSlateFetcher,
    ]

    def __init__(self, db: Session, hours_limit: int = 24, translate: bool = True):
        """
        Args:
            db: 데이터베이스 세션
            hours_limit: 수집할 뉴스 시간 제한 (기본 24시간)
            translate: 한국어 번역 여부 (기본 True)
        """
        self.db = db
        self.hours_limit = hours_limit
        self.dedup = DedupService()
        self.translate = translate
        self.translator = TranslateService() if translate else None

    async def run_all(
        self,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ) -> Dict:
        """모든 소스에서 RSS 수집 실행

        Args:
            progress_callback: 진행 상황 콜백 함수 (optional)

        Returns:
            수집 결과 통계
        """
        logger.info(f"=== FetchEngine: Starting fetch (limit: {self.hours_limit}h) ===")

        results = {
            "success": True,
            "total_fetched": 0,
            "total_saved": 0,
            "total_duplicates": 0,
            "total_translation_failed": 0,
            "sources": {},
            "started_at": datetime.utcnow().isoformat(),
            "finished_at": None,
        }

        sources_total = len(self.FETCHERS)

        # 시작 시 콜백
        if progress_callback:
            await progress_callback({
                "sources_total": sources_total,
            })

        for i, FetcherClass in enumerate(self.FETCHERS):
            source_name = FetcherClass.source_name

            # 소스 처리 시작 시 콜백
            if progress_callback:
                await progress_callback({
                    "current_source": source_name,
                    "sources_completed": i,
                })

            source_result = await self._run_source(FetcherClass)
            results["sources"][source_name] = source_result

            results["total_fetched"] += source_result["fetched"]
            results["total_saved"] += source_result["saved"]
            results["total_duplicates"] += source_result["duplicates"]
            results["total_translation_failed"] += source_result.get("translation_failed", 0)

            if not source_result["success"]:
                results["success"] = False

            # 소스 완료 후 콜백
            if progress_callback:
                await progress_callback({
                    "sources_completed": i + 1,
                    "items_fetched": results["total_fetched"],
                    "items_saved": results["total_saved"],
                    "items_duplicates": results["total_duplicates"],
                })

        results["finished_at"] = datetime.utcnow().isoformat()

        logger.info(
            f"=== FetchEngine: Complete - "
            f"Fetched: {results['total_fetched']}, "
            f"Saved: {results['total_saved']}, "
            f"Duplicates: {results['total_duplicates']}, "
            f"TranslationFailed: {results['total_translation_failed']} ==="
        )

        return results

    async def _run_source(self, FetcherClass: Type[BaseFetcher]) -> Dict:
        """단일 소스에서 수집 실행"""
        source_name = FetcherClass.source_name
        result = {
            "success": False,
            "fetched": 0,
            "saved": 0,
            "duplicates": 0,
            "translation_failed": 0,
            "error": None,
        }

        try:
            fetcher = FetcherClass(hours_limit=self.hours_limit)
            items = await fetcher.fetch()
            result["fetched"] = len(items)

            # 중복 필터링
            new_items = []
            for item_data in items:
                url_hash = item_data.get("url_hash")
                if self.dedup.is_duplicate(self.db, url_hash):
                    result["duplicates"] += 1
                else:
                    new_items.append(item_data)

            logger.info(
                f"[{source_name}] {len(new_items)} new items "
                f"(filtered {result['duplicates']} duplicates)"
            )

            # 새 아이템이 있으면 배치 번역 후 저장
            if new_items:
                # 배치 번역 (한 번 또는 최소한의 API 호출)
                if self.translator:
                    try:
                        new_items = self.translator.translate_batch_sync(new_items)
                    except Exception as e:
                        logger.error(f"[{source_name}] Batch translation error: {e}")
                        # 번역 실패 시 모든 아이템 스킵
                        result["translation_failed"] = len(new_items)
                        new_items = []

                # 번역된 아이템만 저장 (번역 실패한 아이템 제외)
                for item_data in new_items:
                    # 번역 성공 여부 확인
                    if not item_data.get("_translated", False):
                        result["translation_failed"] += 1
                        logger.debug(
                            f"[{source_name}] Skipping untranslated item: "
                            f"{item_data.get('id', 'unknown')}"
                        )
                        continue

                    try:
                        self._save_item_no_translate(item_data)
                        result["saved"] += 1
                    except Exception as e:
                        logger.error(
                            f"[{source_name}] Error saving item: {e}",
                            exc_info=True
                        )

            if result["translation_failed"] > 0:
                logger.warning(
                    f"[{source_name}] {result['translation_failed']} items skipped "
                    f"due to translation failure"
                )

            # 성공 상태 업데이트
            self._update_source_status(source_name, success=True)
            result["success"] = True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{source_name}] Fetch failed: {error_msg}", exc_info=True)
            result["error"] = error_msg

            # 실패 상태 업데이트
            self._update_source_status(source_name, success=False, error=error_msg)

        return result

    def _save_item_no_translate(self, item_data: dict) -> bool:
        """아이템 저장 (번역 없이 - 이미 번역된 데이터)"""
        url_hash = item_data.get("url_hash")

        # FeedItem 생성
        feed_item = FeedItem(
            id=item_data["id"],
            source=item_data["source"],
            source_ref=item_data.get("source_ref"),
            title=item_data["title"],
            summary=item_data.get("summary", ""),
            url=item_data["url"],
            author=item_data.get("author"),
            published_at=item_data.get("published_at"),
            fetched_at=datetime.utcnow(),
            tags=json.dumps(item_data.get("tags", [])),
            score=0,
            url_hash=url_hash,
            raw=json.dumps(item_data.get("raw", {})),
            image_url=item_data.get("image_url"),
            category=item_data.get("category", "news"),
        )

        self.db.add(feed_item)
        self.db.commit()

        logger.debug(f"Saved: {feed_item.title[:50]}...")
        return True

    def _save_item(self, item_data: dict) -> bool:
        """아이템 저장 (레거시 - 개별 번역 포함, 중복이면 False 반환)"""
        url_hash = item_data.get("url_hash")

        # 중복 체크
        if self.dedup.is_duplicate(self.db, url_hash):
            return False

        # 한국어 번역
        title = item_data["title"]
        summary = item_data.get("summary", "")

        if self.translator:
            try:
                title, summary = self.translator.translate_to_korean(title, summary)
                logger.debug(f"Translated: {title[:30]}...")
            except Exception as e:
                logger.error(f"Translation error: {e}")
                # 번역 실패 시 원본 사용

        # FeedItem 생성
        feed_item = FeedItem(
            id=item_data["id"],
            source=item_data["source"],
            source_ref=item_data.get("source_ref"),
            title=title,
            summary=summary,
            url=item_data["url"],
            author=item_data.get("author"),
            published_at=item_data.get("published_at"),
            fetched_at=datetime.utcnow(),
            tags=json.dumps(item_data.get("tags", [])),
            score=0,
            url_hash=url_hash,
            raw=json.dumps(item_data.get("raw", {})),
            image_url=item_data.get("image_url"),
            category=item_data.get("category", "news"),
        )

        self.db.add(feed_item)
        self.db.commit()

        logger.debug(f"Saved: {feed_item.title[:50]}...")
        return True

    def _update_source_status(
        self,
        source_name: str,
        success: bool,
        error: str = None
    ):
        """소스 상태 업데이트"""
        status = self.db.query(SourceStatus).filter(
            SourceStatus.source == source_name
        ).first()

        if not status:
            status = SourceStatus(source=source_name)
            self.db.add(status)

        if success:
            status.last_success_at = datetime.utcnow()
        else:
            status.last_error_at = datetime.utcnow()
            status.last_error_message = error

        self.db.commit()

    async def run_source(self, source_name: str) -> Dict:
        """특정 소스만 수집 실행"""
        for FetcherClass in self.FETCHERS:
            if FetcherClass.source_name == source_name:
                return await self._run_source(FetcherClass)

        return {
            "success": False,
            "error": f"Unknown source: {source_name}",
            "fetched": 0,
            "saved": 0,
            "duplicates": 0,
        }

    @classmethod
    def get_source_names(cls) -> List[str]:
        """등록된 소스 이름 목록"""
        return [f.source_name for f in cls.FETCHERS]
