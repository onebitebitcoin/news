import logging
from typing import List, Optional, Tuple

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem

logger = logging.getLogger(__name__)


class FeedRepository:
    """피드 아이템 레포지토리"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[FeedItem], int]:
        """피드 목록 조회"""
        query = self.db.query(FeedItem)

        # 필터
        if category:
            query = query.filter(FeedItem.category == category)
        if source:
            query = query.filter(FeedItem.source == source)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    FeedItem.title.ilike(search_term),
                    FeedItem.summary.ilike(search_term),
                )
            )

        # 전체 개수
        total = query.count()

        # 정렬 및 페이지네이션
        items = (
            query.order_by(desc(FeedItem.published_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        logger.debug(f"Feed items fetched: {len(items)} / {total}")
        return items, total

    def get_by_id(self, item_id: str) -> Optional[FeedItem]:
        """ID로 피드 아이템 조회"""
        return self.db.query(FeedItem).filter(FeedItem.id == item_id).first()

    def get_trending(self, limit: int = 5) -> List[FeedItem]:
        """트렌딩 피드 조회 (score 기준)"""
        return (
            self.db.query(FeedItem)
            .order_by(desc(FeedItem.score))
            .limit(limit)
            .all()
        )

    def create(self, feed_item: FeedItem) -> FeedItem:
        """피드 아이템 생성"""
        self.db.add(feed_item)
        self.db.commit()
        self.db.refresh(feed_item)
        return feed_item

    def get_categories(self) -> List[str]:
        """사용 가능한 카테고리 목록"""
        result = (
            self.db.query(FeedItem.category)
            .filter(FeedItem.category.isnot(None))
            .distinct()
            .all()
        )
        return [r[0] for r in result if r[0]]

    def exists_by_url_hash(self, url_hash: str) -> bool:
        """URL 해시로 중복 여부 확인"""
        return (
            self.db.query(FeedItem)
            .filter(FeedItem.url_hash == url_hash)
            .first() is not None
        )

    def get_by_url_hash(self, url_hash: str) -> Optional[FeedItem]:
        """URL 해시로 피드 아이템 조회"""
        return (
            self.db.query(FeedItem)
            .filter(FeedItem.url_hash == url_hash)
            .first()
        )

    def get_sources(self) -> List[str]:
        """사용 가능한 소스 목록"""
        result = (
            self.db.query(FeedItem.source)
            .distinct()
            .all()
        )
        return [r[0] for r in result if r[0]]

    def bulk_create(self, feed_items: List[FeedItem]) -> int:
        """여러 피드 아이템 일괄 생성"""
        count = 0
        for item in feed_items:
            if not self.exists_by_url_hash(item.url_hash):
                self.db.add(item)
                count += 1
        self.db.commit()
        logger.debug(f"Bulk created {count} feed items")
        return count
