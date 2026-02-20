"""DB 저장 스테이지"""

import json
import logging
from datetime import datetime

from app.models.feed_item import FeedItem
from app.services.pipeline.base_stage import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class PersistStage(PipelineStage):
    """DB 저장 (Do One Thing)"""

    def process(self, context: PipelineContext) -> PipelineContext:
        """아이템들을 DB에 저장"""
        failed = 0
        for item_data in context.items:
            if context.translation_required and item_data.get("translation_status") == "failed":
                context.translation_dropped += 1
                logger.warning(
                    f"[{context.source_name}] Dropped untranslated item: "
                    f"{item_data.get('id', 'unknown')}"
                )
                continue
            try:
                with context.db.begin_nested():
                    self._save_item(context.db, item_data)
                context.saved += 1
            except Exception as e:
                failed += 1
                logger.error(
                    f"[{context.source_name}] Error saving item: {e}",
                    exc_info=True
                )

        if context.saved > 0:
            context.db.commit()

        if failed > 0:
            logger.warning(f"[{context.source_name}] Save failures: {failed}")
        if context.translation_dropped > 0:
            logger.warning(
                f"[{context.source_name}] Translation policy dropped: "
                f"{context.translation_dropped}"
            )

        return context

    def _save_item(self, db, item_data: dict) -> None:
        """단일 아이템 저장"""
        # raw에서 group_id 추출 (GroupingStage가 설정한 값)
        raw_data = item_data.get("raw", {})
        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data) if raw_data else {}
        group_id = raw_data.get("dedup_group_id") or item_data["id"]

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
            url_hash=item_data.get("url_hash"),
            raw=json.dumps(item_data.get("raw", {})),
            image_url=item_data.get("image_url"),
            category=item_data.get("category", "news"),
            translation_status=item_data.get("translation_status"),
            group_id=group_id,
        )

        db.add(feed_item)

        logger.debug(f"Saved: {feed_item.title[:50]}...")
