from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ExternalArticle(BaseModel):
    """External API 기사 응답"""

    id: str
    title: str
    url: str
    summary: Optional[str] = None
    source: str
    category: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExternalArticleDetail(ExternalArticle):
    """External API 기사 상세 응답"""

    author: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ExternalArticleListResponse(BaseModel):
    """External API 기사 목록 응답"""

    articles: List[ExternalArticle]
    total: int
    page: int
    page_size: int
    has_next: bool
