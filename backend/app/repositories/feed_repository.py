import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem

logger = logging.getLogger(__name__)


class FeedRepository:
    """피드 아이템 레포지토리"""

    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(
        self,
        query,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ):
        """공통 필터 적용"""
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
        return query

    def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[FeedItem], int]:
        """피드 목록 조회"""
        query = self._apply_filters(
            self.db.query(FeedItem), category, source, search
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

    def get_grouped_feed(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict], int]:
        """
        DB 레벨에서 그룹화된 피드 목록 조회
        group_id가 같은 아이템을 그룹화하고, 각 그룹의 대표 아이템과 중복 개수 반환
        """
        # 그룹 키: group_id가 있으면 사용, 없으면 id 사용
        group_key = func.coalesce(FeedItem.group_id, FeedItem.id)

        # 필터 적용
        base_query = self._apply_filters(
            self.db.query(FeedItem), category, source, search
        )

        # 그룹별 대표 아이템 선택 (ROW_NUMBER 사용)
        # SQLite와 PostgreSQL 모두 지원
        subquery = (
            base_query
            .with_entities(
                FeedItem.id,
                group_key.label("group_key"),
                func.row_number().over(
                    partition_by=group_key,
                    order_by=desc(func.coalesce(FeedItem.published_at, FeedItem.fetched_at))
                ).label("rn")
            )
            .subquery()
        )

        # 대표 아이템만 선택 (rn = 1)
        representative_ids_query = (
            self.db.query(subquery.c.id)
            .filter(subquery.c.rn == 1)
            .subquery()
        )

        # 그룹별 아이템 수 계산
        count_subquery = (
            base_query
            .with_entities(
                group_key.label("group_key"),
                func.count(FeedItem.id).label("cnt")
            )
            .group_by(group_key)
            .subquery()
        )

        # 전체 그룹 수 (페이지네이션 계산용)
        total_groups = self.db.query(func.count()).select_from(count_subquery).scalar()

        # 대표 아이템 조회 (페이지네이션 적용)
        items_query = (
            self.db.query(FeedItem)
            .filter(FeedItem.id.in_(select(representative_ids_query)))
            .order_by(desc(func.coalesce(FeedItem.published_at, FeedItem.fetched_at)))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        representative_items = items_query.all()

        # 각 대표 아이템의 그룹에 속한 중복 아이템 조회
        result = []
        for item in representative_items:
            gk = item.group_id or item.id

            # 중복 아이템 조회 (대표 아이템 제외)
            duplicates_query = base_query.filter(
                func.coalesce(FeedItem.group_id, FeedItem.id) == gk,
                FeedItem.id != item.id,
            ).order_by(desc(func.coalesce(FeedItem.published_at, FeedItem.fetched_at)))

            duplicates = duplicates_query.all()

            result.append({
                "representative": item,
                "duplicates": duplicates,
                "duplicate_count": len(duplicates),
            })

        logger.debug(f"Grouped feed: {len(result)} groups / {total_groups} total")
        return result, total_groups
