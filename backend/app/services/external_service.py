import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem
from app.repositories.feed_repository import FeedRepository
from app.schemas.external import ExternalArticle, ExternalArticleDetail
from app.utils.json_utils import safe_parse_json

logger = logging.getLogger(__name__)


class ExternalService:
    """External API용 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.feed_repo = FeedRepository(db)

    def get_articles(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[ExternalArticle], int]:
        """기사 목록 조회"""
        items, total = self.feed_repo.get_all(
            page=page,
            page_size=page_size,
            category=category,
            source=source,
            search=search,
        )
        articles = [self._to_article(item) for item in items]
        return articles, total

    def get_article_detail(self, article_id: str) -> Optional[ExternalArticleDetail]:
        """기사 상세 조회"""
        item = self.feed_repo.get_by_id(article_id)
        if not item:
            return None
        return self._to_article_detail(item)

    def get_sources(self) -> List[str]:
        """소스 목록"""
        return self.feed_repo.get_sources()

    def get_categories(self) -> List[str]:
        """카테고리 목록"""
        return self.feed_repo.get_categories()

    def _to_article(self, item: FeedItem) -> ExternalArticle:
        """FeedItem → ExternalArticle 변환"""
        return ExternalArticle(
            id=item.id,
            title=item.title,
            url=item.url,
            summary=item.summary,
            source=item.source,
            category=item.category,
            published_at=item.published_at,
        )

    def _to_article_detail(self, item: FeedItem) -> ExternalArticleDetail:
        """FeedItem → ExternalArticleDetail 변환"""
        tags = safe_parse_json(item.tags, default=None) if item.tags else None

        return ExternalArticleDetail(
            id=item.id,
            title=item.title,
            url=item.url,
            summary=item.summary,
            source=item.source,
            category=item.category,
            published_at=item.published_at,
            author=item.author,
            tags=tags,
            image_url=item.image_url,
        )
