import logging
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark

logger = logging.getLogger(__name__)


class BookmarkRepository:
    """북마크 레포지토리"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Bookmark]:
        """전체 북마크 조회"""
        return self.db.query(Bookmark).order_by(Bookmark.created_at.desc()).all()

    def get_by_item_id(self, item_id: str) -> Optional[Bookmark]:
        """아이템 ID로 북마크 조회"""
        return self.db.query(Bookmark).filter(Bookmark.item_id == item_id).first()

    def get_item_ids(self) -> Set[str]:
        """북마크된 아이템 ID 목록"""
        result = self.db.query(Bookmark.item_id).all()
        return {r[0] for r in result}

    def create(self, item_id: str) -> Bookmark:
        """북마크 생성"""
        bookmark = Bookmark(item_id=item_id)
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        logger.info(f"Bookmark created: {item_id}")
        return bookmark

    def delete(self, item_id: str) -> bool:
        """북마크 삭제"""
        bookmark = self.get_by_item_id(item_id)
        if bookmark:
            self.db.delete(bookmark)
            self.db.commit()
            logger.info(f"Bookmark deleted: {item_id}")
            return True
        return False

    def exists(self, item_id: str) -> bool:
        """북마크 존재 여부"""
        return self.get_by_item_id(item_id) is not None
