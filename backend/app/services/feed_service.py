import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.feed_repository import FeedRepository
from app.schemas.feed import FeedItemDetail, FeedItemDuplicate, FeedItemResponse, FeedListResponse

logger = logging.getLogger(__name__)


class FeedService:
    """피드 서비스"""

    # NEW 태그 표시 기준 시간 (3시간)
    NEW_ITEM_HOURS = 3

    def __init__(self, db: Session):
        self.feed_repo = FeedRepository(db)
        self.bookmark_repo = BookmarkRepository(db)

    def _is_new_item(self, fetched_at: datetime) -> bool:
        """최근 수집된 아이템인지 확인"""
        if not fetched_at:
            return False
        cutoff = datetime.utcnow() - timedelta(hours=self.NEW_ITEM_HOURS)
        return fetched_at > cutoff

    def get_feed_list(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> FeedListResponse:
        """피드 목록 조회 (DB 레벨 그룹화 + 페이지네이션)"""
        # DB에서 그룹화된 결과 조회
        grouped_data, total = self.feed_repo.get_grouped_feed(
            page=page,
            page_size=page_size,
            category=category,
            source=source,
            search=search,
        )

        # 최신 발행 시간 조회
        last_updated_at = self.feed_repo.get_latest_published_at(
            category=category, source=source, search=search,
        )

        # 북마크 상태 확인
        bookmarked_ids = self.bookmark_repo.get_item_ids()

        feed_items = [
            self._to_feed_response_from_grouped(data, bookmarked_ids)
            for data in grouped_data
        ]

        return FeedListResponse(
            items=feed_items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
            last_updated_at=last_updated_at,
        )

    def get_feed_detail(self, item_id: str) -> Optional[FeedItemDetail]:
        """피드 상세 조회"""
        item = self.feed_repo.get_by_id(item_id)
        if not item:
            return None

        is_bookmarked = self.bookmark_repo.exists(item_id)

        # tags JSON 파싱
        tags = None
        if item.tags:
            try:
                tags = json.loads(item.tags)
            except json.JSONDecodeError:
                tags = []

        return FeedItemDetail(
            id=item.id,
            source=item.source,
            source_ref=item.source_ref,
            title=item.title,
            summary=item.summary,
            url=item.url,
            author=item.author,
            published_at=item.published_at,
            fetched_at=item.fetched_at,
            image_url=item.image_url,
            category=item.category,
            score=item.score or 0,
            tags=tags,
            is_bookmarked=is_bookmarked,
            is_new=self._is_new_item(item.fetched_at),
        )

    def get_trending(self, limit: int = 5) -> List[FeedItemResponse]:
        """트렌딩 피드 조회"""
        items = self.feed_repo.get_trending(limit)
        bookmarked_ids = self.bookmark_repo.get_item_ids()
        return [self._build_feed_response(item, bookmarked_ids) for item in items]

    def get_categories(self) -> List[str]:
        """카테고리 목록"""
        return self.feed_repo.get_categories()

    def get_sources(self) -> List[str]:
        """소스 목록"""
        return self.feed_repo.get_sources()

    def _build_feed_response(
        self,
        item,
        bookmarked_ids: set,
        duplicates: Optional[List[FeedItemDuplicate]] = None,
    ) -> FeedItemResponse:
        """FeedItem → FeedItemResponse 변환 (공통 헬퍼)"""
        return FeedItemResponse(
            id=item.id,
            source=item.source,
            title=item.title,
            summary=item.summary,
            url=item.url,
            author=item.author,
            published_at=item.published_at,
            image_url=item.image_url,
            category=item.category,
            score=item.score or 0,
            is_bookmarked=item.id in bookmarked_ids,
            is_new=self._is_new_item(item.fetched_at),
            fetched_at=item.fetched_at,
            group_id=getattr(item, "group_id", None),
            duplicate_count=len(duplicates) if duplicates else 0,
            duplicates=duplicates or [],
        )

    def _to_feed_response_from_grouped(
        self,
        data: dict,
        bookmarked_ids: set,
    ) -> FeedItemResponse:
        """그룹화된 데이터를 응답 모델로 변환"""
        duplicates = [
            FeedItemDuplicate(
                id=item.id,
                source=item.source,
                title=item.title,
                url=item.url,
                published_at=item.published_at,
            )
            for item in data["duplicates"]
        ]
        return self._build_feed_response(data["representative"], bookmarked_ids, duplicates)
