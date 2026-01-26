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
        for item_data in context.items:
            try:
                self._save_item(context.db, item_data)
                context.saved += 1
            except Exception as e:
                logger.error(
                    f"[{context.source_name}] Error saving item: {e}",
                    exc_info=True
                )

        return context

    def _save_item(self, db, item_data: dict) -> None:
        """단일 아이템 저장"""
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
        )

        db.add(feed_item)
        db.commit()

        logger.debug(f"Saved: {feed_item.title[:50]}...")
