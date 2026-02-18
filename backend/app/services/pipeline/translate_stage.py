"""번역 스테이지"""

import asyncio
import logging
from typing import Optional

from app.services.pipeline.base_stage import PipelineContext, PipelineStage
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)

# 한국어 소스 목록 (번역 불필요)
KOREAN_SOURCES = {"coindeskkorea", "blockmedia", "tokenpost"}


class TranslateStage(PipelineStage):
    """배치 번역 처리 (Do One Thing)"""

    def __init__(self, translator: Optional[TranslateService] = None):
        self.translator = translator

    async def process(self, context: PipelineContext) -> PipelineContext:
        """배치 번역 실행"""
        if not self.translator or not context.items:
            return context

        # 한국어 소스는 번역 스킵 (이미 한국어)
        if context.source_name in KOREAN_SOURCES:
            logger.info(f"[{context.source_name}] 한국어 소스 - 번역 스킵")
            for item in context.items:
                item["title_ko"] = item["title"]
                item["summary_ko"] = item.get("summary", "")
                item["_translated"] = True
                item["translation_status"] = "skipped"
            return context

        try:
            context.items = await asyncio.to_thread(
                self.translator.translate_batch_sync, context.items
            )
        except Exception as e:
            logger.error(f"[{context.source_name}] Batch translation error: {e}")
            context.translation_failed = len(context.items)
            for item in context.items:
                item["_translated"] = False
                item["translation_status"] = "failed"
            return context

        # 실패 아이템 개별 재시도
        failed_items = [
            item for item in context.items
            if not item.get("_translated", False)
        ]

        if failed_items:
            logger.info(
                f"[{context.source_name}] {len(failed_items)} items failed batch translation, "
                f"retrying individually..."
            )
            for item_data in failed_items:
                try:
                    self.translator.translate_single_item(item_data)
                    if item_data.get("_translated", False):
                        logger.info(
                            f"[{context.source_name}] Individual retry succeeded: "
                            f"{item_data.get('id', 'unknown')}"
                        )
                except Exception as e:
                    logger.error(
                        f"[{context.source_name}] Individual retry failed for "
                        f"{item_data.get('id', 'unknown')}: {e}"
                    )
                    item_data["_translated"] = False

        # 번역 상태 반영 (실패 시 fail-open으로 원문 유지)
        for item_data in context.items:
            if not item_data.get("_translated", False):
                context.translation_failed += 1
                item_data["translation_status"] = "failed"
                logger.debug(
                    f"[{context.source_name}] Keeping untranslated item: "
                    f"{item_data.get('id', 'unknown')}"
                )
            else:
                item_data["translation_status"] = "ok"

        if context.translation_failed > 0:
            logger.warning(
                f"[{context.source_name}] {context.translation_failed} items kept in original language "
                f"due to translation failure"
            )
        return context
