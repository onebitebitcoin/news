"""번역 스테이지"""

import logging
from typing import Optional

from app.services.pipeline.base_stage import PipelineContext, PipelineStage
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)


class TranslateStage(PipelineStage):
    """배치 번역 처리 (Do One Thing)"""

    def __init__(self, translator: Optional[TranslateService] = None):
        self.translator = translator

    def process(self, context: PipelineContext) -> PipelineContext:
        """배치 번역 실행"""
        if not self.translator or not context.items:
            return context

        try:
            context.items = self.translator.translate_batch_sync(context.items)
        except Exception as e:
            logger.error(f"[{context.source_name}] Batch translation error: {e}")
            context.translation_failed = len(context.items)
            context.items = []
            return context

        # 번역 실패한 아이템 필터링
        translated_items = []
        for item_data in context.items:
            if not item_data.get("_translated", False):
                context.translation_failed += 1
                logger.debug(
                    f"[{context.source_name}] Skipping untranslated item: "
                    f"{item_data.get('id', 'unknown')}"
                )
            else:
                translated_items.append(item_data)

        if context.translation_failed > 0:
            logger.warning(
                f"[{context.source_name}] {context.translation_failed} items skipped "
                f"due to translation failure"
            )

        context.items = translated_items
        return context
