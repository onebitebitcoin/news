"""RSS 통합 수집 엔진"""

import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Type

from sqlalchemy.orm import Session

from app.models.source_status import SourceStatus
from app.services.pipeline import (
    DedupStage,
    GroupingStage,
    PersistStage,
    PipelineContext,
    TranslateStage,
)
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
        self.translate = translate

        # Pipeline stages 초기화
        translator = TranslateService() if translate else None
        self.stages = [
            DedupStage(),
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
            "total_translation_failed": 0,
            "sources": {},
            "started_at": datetime.utcnow().isoformat(),
            "finished_at": None,
        }

        sources_total = len(self.FETCHERS)

        if progress_callback:
            await progress_callback({"sources_total": sources_total})

        for i, FetcherClass in enumerate(self.FETCHERS):
            source_name = FetcherClass.source_name

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
        """단일 소스에서 수집 실행 - Pipeline 처리"""
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
            # 1. Fetch
            fetcher = FetcherClass(hours_limit=self.hours_limit)
            items = await fetcher.fetch()
            result["fetched"] = len(items)

            # 2. Pipeline 처리
            context = PipelineContext(
                db=self.db,
                source_name=source_name,
                items=items,
                fetched=len(items),
            )

            for stage in self.stages:
                context = stage.process(context)

            # 3. 결과 수집
            result["duplicates"] = context.duplicates
            result["translation_failed"] = context.translation_failed
            result["saved"] = context.saved

            # 4. 상태 업데이트
            self._update_source_status(source_name, success=True)
            result["success"] = True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{source_name}] Fetch failed: {error_msg}", exc_info=True)
            result["error"] = error_msg
            self._update_source_status(source_name, success=False, error=error_msg)

        return result

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
