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
        hash_to_items: dict[str, list[dict]] = {}
        for item_data in context.items:
            url_hash = item_data.get("url_hash")
            if not url_hash:
                continue
            hash_to_items.setdefault(url_hash, []).append(item_data)

        existing_hashes = self.dedup.get_existing_hashes(context.db, list(hash_to_items.keys()))
        new_items = []
        seen_hashes = set()

        for item_data in context.items:
            url_hash = item_data.get("url_hash")
            if not url_hash:
                new_items.append(item_data)
                continue

            if url_hash in existing_hashes or url_hash in seen_hashes:
                context.duplicates += 1
            else:
                seen_hashes.add(url_hash)
                new_items.append(item_data)

        logger.info(
            f"[{context.source_name}] {len(new_items)} new items "
            f"(filtered {context.duplicates} duplicates)"
        )

        context.items = new_items
        return context
