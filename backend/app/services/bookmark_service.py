import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.feed_repository import FeedRepository
from app.schemas.bookmark import (
    BookmarkListResponse,
    BookmarkResponse,
    BookmarkWithItemResponse,
)
from app.schemas.feed import FeedItemResponse

logger = logging.getLogger(__name__)


class BookmarkService:
    """북마크 서비스"""

    def __init__(self, db: Session):
        self.feed_repo = FeedRepository(db)
        self.bookmark_repo = BookmarkRepository(db)

    def get_bookmarks(self) -> BookmarkListResponse:
        """북마크 목록 조회"""
        bookmarks = self.bookmark_repo.get_all()

        items = []
        for bookmark in bookmarks:
            feed_item = self.feed_repo.get_by_id(bookmark.item_id)
            if feed_item:
                items.append(
                    BookmarkWithItemResponse(
                        bookmark=BookmarkResponse(
                            id=bookmark.id,
                            item_id=bookmark.item_id,
                            created_at=bookmark.created_at,
                        ),
                        item=FeedItemResponse(
                            id=feed_item.id,
                            source=feed_item.source,
                            title=feed_item.title,
                            summary=feed_item.summary,
                            url=feed_item.url,
                            author=feed_item.author,
                            published_at=feed_item.published_at,
                            image_url=feed_item.image_url,
                            category=feed_item.category,
                            score=feed_item.score or 0,
                            is_bookmarked=True,
                        ),
                    )
                )

        return BookmarkListResponse(items=items, total=len(items))

    def add_bookmark(self, item_id: str) -> Optional[BookmarkResponse]:
        """북마크 추가"""
        # 피드 아이템 존재 확인
        feed_item = self.feed_repo.get_by_id(item_id)
        if not feed_item:
            logger.warning(f"Feed item not found: {item_id}")
            return None

        # 이미 북마크된 경우
        existing = self.bookmark_repo.get_by_item_id(item_id)
        if existing:
            return BookmarkResponse(
                id=existing.id,
                item_id=existing.item_id,
                created_at=existing.created_at,
            )

        # 북마크 생성
        bookmark = self.bookmark_repo.create(item_id)
        return BookmarkResponse(
            id=bookmark.id,
            item_id=bookmark.item_id,
            created_at=bookmark.created_at,
        )

    def remove_bookmark(self, item_id: str) -> bool:
        """북마크 삭제"""
        return self.bookmark_repo.delete(item_id)
