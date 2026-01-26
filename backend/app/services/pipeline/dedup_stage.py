"""중복 필터링 스테이지"""

import logging

from app.services.dedup_service import DedupService
from app.services.pipeline.base_stage import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class DedupStage(PipelineStage):
    """중복 아이템 필터링 (Do One Thing)"""

    def __init__(self):
        self.dedup = DedupService()

    def process(self, context: PipelineContext) -> PipelineContext:
        """중복 아이템 필터링"""
        new_items = []

        for item_data in context.items:
            url_hash = item_data.get("url_hash")
            if self.dedup.is_duplicate(context.db, url_hash):
                context.duplicates += 1
            else:
                new_items.append(item_data)

        logger.info(
            f"[{context.source_name}] {len(new_items)} new items "
            f"(filtered {context.duplicates} duplicates)"
        )

        context.items = new_items
        return context
