import logging
from datetime import datetime
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
    ) -> Tuple[List[Dict], int, Optional[datetime]]:
        """
        DB 레벨에서 그룹화된 피드 목록 조회 (최적화)

        group_id 컬럼을 직접 사용 (COALESCE 제거 → 인덱스 활용).
        N+1 루프를 IN clause 1회 쿼리로 교체.
        last_updated_at도 함께 반환 (별도 쿼리 제거).

        Returns: (grouped_data, total_groups, last_updated_at)
        """
        # 1) 그룹별 집계: count, max(published_at), 대표 아이템 id (가장 최신)
        base = self._apply_filters(
            self.db.query(FeedItem), category, source, search
        )

        group_agg = (
            base.with_entities(
                FeedItem.group_id,
                func.count(FeedItem.id).label("cnt"),
                func.max(FeedItem.published_at).label("max_pub"),
            )
            .group_by(FeedItem.group_id)
            .subquery()
        )

        # 전체 그룹 수 + 전체 최신 published_at
        stats = self.db.query(
            func.count(),
            func.max(group_agg.c.max_pub),
        ).select_from(group_agg).one()
        total_groups = stats[0] or 0
        last_updated_at = stats[1]

        # 2) 대표 아이템 선택 (ROW_NUMBER로 그룹 내 최신 1개)
        rn_sub = (
            base.with_entities(
                FeedItem.id,
                FeedItem.group_id,
                func.row_number().over(
                    partition_by=FeedItem.group_id,
                    order_by=desc(FeedItem.published_at),
                ).label("rn"),
            )
            .subquery()
        )
        rep_ids_sub = (
            self.db.query(rn_sub.c.id, rn_sub.c.group_id)
            .filter(rn_sub.c.rn == 1)
            .subquery()
        )

        # 3) 대표 아이템 조회 (페이지네이션)
        representative_items = (
            self.db.query(FeedItem)
            .filter(FeedItem.id.in_(select(rep_ids_sub.c.id)))
            .order_by(desc(FeedItem.published_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        if not representative_items:
            return [], total_groups, last_updated_at

        # 4) 그룹별 카운트 매핑 (대표 아이템의 group_id에 해당하는 것만)
        rep_group_ids = [item.group_id for item in representative_items]
        count_rows = (
            base.with_entities(
                FeedItem.group_id,
                func.count(FeedItem.id).label("cnt"),
            )
            .filter(FeedItem.group_id.in_(rep_group_ids))
            .group_by(FeedItem.group_id)
            .all()
        )
        count_map = {row[0]: row[1] for row in count_rows}

        # 5) 중복 아이템 일괄 조회 (대표 제외, IN clause 1회)
        rep_ids = {item.id for item in representative_items}
        dup_items = (
            base.filter(
                FeedItem.group_id.in_(rep_group_ids),
                FeedItem.id.notin_(rep_ids),
            )
            .order_by(desc(FeedItem.published_at))
            .all()
        )

        # group_id별 중복 아이템 매핑
        dup_map: Dict[str, List[FeedItem]] = {}
        for dup in dup_items:
            dup_map.setdefault(dup.group_id, []).append(dup)

        # 6) 결과 조립
        result = []
        for item in representative_items:
            gid = item.group_id
            duplicates = dup_map.get(gid, [])
            result.append({
                "representative": item,
                "duplicates": duplicates,
                "duplicate_count": count_map.get(gid, 1) - 1,
            })

        logger.debug(f"Grouped feed: {len(result)} groups / {total_groups} total")
        return result, total_groups, last_updated_at
