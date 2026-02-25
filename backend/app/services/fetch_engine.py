"""RSS 통합 수집 엔진"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Callable, Dict, List, Optional, Type

from sqlalchemy.orm import Session

from app.config import settings
from app.models.source_status import SourceStatus
from app.repositories.custom_source_repository import CustomSourceRepository
from app.services.pipeline import (
    BitcoinFilterStage,
    DedupStage,
    GroupingStage,
    PersistStage,
    PipelineContext,
    TranslateStage,
)
from app.services.sources.base_fetcher import BaseFetcher
from app.services.sources.bitcoincom import BitcoinComFetcher
from app.services.sources.bitcoinmagazine import BitcoinMagazineFetcher
from app.services.sources.blockmedia import BlockmediaFetcher
from app.services.sources.blockworks import BlockworksFetcher
from app.services.sources.coindesk import CoinDeskFetcher
from app.services.sources.coindeskkorea import CoinDeskKoreaFetcher
from app.services.sources.cointelegraph import CointelegraphFetcher
from app.services.sources.cryptoslate import CryptoSlateFetcher
from app.services.sources.custom_scrape_runtime import CustomScrapeRuntime
from app.services.sources.decrypt import DecryptFetcher
from app.services.sources.googlenews import GoogleNewsFetcher
from app.services.sources.optech import OptechFetcher
from app.services.sources.theblock import TheBlockFetcher
from app.services.sources.theminermag import TheMinerMagFetcher
from app.services.sources.tokenpost import TokenpostFetcher
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)


class FetchEngine:
    """RSS 통합 수집 엔진 - Pipeline 오케스트레이션"""

    # 등록된 Fetcher 클래스들
    FETCHERS: List[Type[BaseFetcher]] = [
        GoogleNewsFetcher,
        BitcoinMagazineFetcher,
        OptechFetcher,
        CoinDeskFetcher,
        CointelegraphFetcher,
        TheBlockFetcher,
        TheMinerMagFetcher,
        DecryptFetcher,
        BitcoinComFetcher,
        BlockworksFetcher,
        CryptoSlateFetcher,
        # 한국어 소스
        CoinDeskKoreaFetcher,
        BlockmediaFetcher,
        TokenpostFetcher,
    ]

    CUSTOM_RUNTIME_CLASS = CustomScrapeRuntime

    def __init__(self, db: Session, hours_limit: int = 24, translate: bool = True):
        """
        Args:
            db: 데이터베이스 세션
            hours_limit: 수집할 뉴스 시간 제한 (기본 24시간)
            translate: 한국어 번역 여부 (기본 True)
        """
        self.db = db
        self.hours_limit = hours_limit
        self.translate = translate
        self.translation_required = settings.TRANSLATION_REQUIRED
        self.is_testing = os.getenv("TESTING", "").lower() == "true"

        # Pipeline stages 초기화
        translator = TranslateService() if translate else None
        if (
            translate
            and self.translation_required
            and not self.is_testing
            and (not translator or not translator.client)
        ):
            raise ValueError(
                "OPENAI_API_KEY is required when TRANSLATION_REQUIRED is enabled"
            )

        self.stages = [
            DedupStage(),
            BitcoinFilterStage(),
            TranslateStage(translator),
            GroupingStage(),
            PersistStage(),
        ]

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
            "total_filtered": 0,
            "total_translation_failed": 0,
            "total_translation_dropped": 0,
            "sources": {},
            "started_at": datetime.utcnow().isoformat(),
            "finished_at": None,
        }

        custom_sources = self._get_active_custom_sources()
        sources_total = len(self.FETCHERS) + len(custom_sources)

        if progress_callback:
            await progress_callback({"sources_total": sources_total})

        # 1단계: 모든 소스에서 병렬로 fetch (네트워크 I/O)
        logger.info(f"[FetchEngine] Starting parallel fetch for {sources_total} sources")

        async def fetch_only(FetcherClass: Type[BaseFetcher]):
            """Fetch만 수행 (DB 작업 없음)"""
            try:
                fetcher = FetcherClass(hours_limit=self.hours_limit)
                items = await fetcher.fetch()
                return {"source": FetcherClass.source_name, "items": items, "error": None}
            except Exception as e:
                logger.error(f"[{FetcherClass.source_name}] Fetch failed: {e}")
                return {"source": FetcherClass.source_name, "items": [], "error": str(e)}

        async def fetch_custom_only(custom_config: dict):
            source_name = custom_config["slug"]
            try:
                runtime = self.CUSTOM_RUNTIME_CLASS(custom_config, hours_limit=self.hours_limit)
                items = await runtime.fetch()
                return {"source": source_name, "items": items, "error": None}
            except Exception as e:
                logger.error(f"[{source_name}] Custom fetch failed: {e}")
                return {"source": source_name, "items": [], "error": str(e)}

        fetch_tasks = [fetch_only(FetcherClass) for FetcherClass in self.FETCHERS]
        fetch_tasks.extend(fetch_custom_only(config) for config in custom_sources)
        fetch_results = await asyncio.gather(*fetch_tasks)

        # 2단계: Pipeline 처리 (DB 작업) - 순차 처리
        logger.info("[FetchEngine] Processing fetched items sequentially...")

        for i, fetch_result in enumerate(fetch_results):
            source_name = fetch_result["source"]

            if progress_callback:
                await progress_callback({
                    "current_source": source_name,
                    "sources_completed": i,
                })

            source_result = await self._process_fetched_items(
                source_name,
                fetch_result["items"],
                fetch_result["error"]
            )
            results["sources"][source_name] = source_result

            results["total_fetched"] += source_result["fetched"]
            results["total_saved"] += source_result["saved"]
            results["total_duplicates"] += source_result["duplicates"]
            results["total_filtered"] += source_result.get("filtered", 0)
            results["total_translation_failed"] += source_result.get("translation_failed", 0)
            results["total_translation_dropped"] += source_result.get("translation_dropped", 0)

            if not source_result["success"]:
                results["success"] = False

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
            f"Filtered: {results['total_filtered']}, "
            f"TranslationFailed: {results['total_translation_failed']}, "
            f"TranslationDropped: {results['total_translation_dropped']} ==="
        )

        return results

    async def _process_fetched_items(
        self,
        source_name: str,
        items: List,
        fetch_error: Optional[str]
    ) -> Dict:
        """Fetch된 아이템들을 Pipeline으로 처리 (DB 작업)"""
        result = {
            "success": False,
            "fetched": len(items),
            "saved": 0,
            "duplicates": 0,
            "filtered": 0,
            "translation_failed": 0,
            "translation_dropped": 0,
            "error": fetch_error,
        }

        # Fetch 단계에서 이미 에러가 발생한 경우
        if fetch_error:
            self._update_source_status(source_name, success=False, error=fetch_error)
            return result

        try:
            # Pipeline 처리
            context = PipelineContext(
                db=self.db,
                source_name=source_name,
                items=items,
                fetched=len(items),
                translation_required=self.translation_required,
            )

            for stage in self.stages:
                stage_result = stage.process(context)
                if asyncio.iscoroutine(stage_result):
                    context = await stage_result
                else:
                    context = stage_result

            # 결과 수집
            result["duplicates"] = context.duplicates
            result["filtered"] = context.filtered
            result["translation_failed"] = context.translation_failed
            result["translation_dropped"] = context.translation_dropped
            result["saved"] = context.saved

            # 상태 업데이트
            self._update_source_status(source_name, success=True)
            result["success"] = True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{source_name}] Pipeline failed: {error_msg}", exc_info=True)
            result["error"] = error_msg
            self._update_source_status(source_name, success=False, error=error_msg)

        return result

    async def _run_source(self, FetcherClass: Type[BaseFetcher]) -> Dict:
        """단일 소스에서 수집 실행 - Fetch + Pipeline 처리"""
        source_name = FetcherClass.source_name

        try:
            # 1. Fetch
            fetcher = FetcherClass(hours_limit=self.hours_limit)
            items = await fetcher.fetch()

            # 2. Pipeline 처리
            return await self._process_fetched_items(source_name, items, None)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{source_name}] Fetch failed: {error_msg}", exc_info=True)
            self._update_source_status(source_name, success=False, error=error_msg)
            return {
                "success": False,
                "fetched": 0,
                "saved": 0,
                "duplicates": 0,
                "translation_failed": 0,
                "translation_dropped": 0,
                "error": error_msg,
            }

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

        custom_config = self._get_custom_source_by_slug(source_name)
        if custom_config:
            try:
                runtime = self.CUSTOM_RUNTIME_CLASS(custom_config, hours_limit=self.hours_limit)
                items = await runtime.fetch()
                return await self._process_fetched_items(source_name, items, None)
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[{source_name}] Custom fetch failed: {error_msg}", exc_info=True)
                self._update_source_status(source_name, success=False, error=error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "fetched": 0,
                    "saved": 0,
                    "duplicates": 0,
                    "filtered": 0,
                    "translation_failed": 0,
                    "translation_dropped": 0,
                }

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

    def _get_active_custom_sources(self) -> List[dict]:
        repo = CustomSourceRepository(self.db)
        return [repo.to_dict(source) for source in repo.get_active()]

    def _get_custom_source_by_slug(self, slug: str) -> Optional[dict]:
        repo = CustomSourceRepository(self.db)
        source = repo.get_by_slug(slug)
        if not source or not source.is_active:
            return None
        return repo.to_dict(source)
