from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class FeedItemDuplicate(BaseModel):
    """중복 아이템 요약"""
    id: str
    source: str
    title: str
    url: str
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeedItemResponse(BaseModel):
    """피드 아이템 응답"""
    id: str
    source: str
    title: str
    summary: Optional[str] = None
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    score: float = 0
    is_bookmarked: bool = False
    is_new: bool = False
    fetched_at: Optional[datetime] = None
    group_id: Optional[str] = None
    duplicate_count: int = 0
    duplicates: List[FeedItemDuplicate] = []

    class Config:
        from_attributes = True


class FeedItemDetail(FeedItemResponse):
    """피드 상세 응답"""
    tags: Optional[List[str]] = None
    source_ref: Optional[str] = None

    class Config:
        from_attributes = True


class FeedListResponse(BaseModel):
    """피드 목록 응답"""
    items: List[FeedItemResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    last_updated_at: Optional[datetime] = None


class UrlPreviewRequest(BaseModel):
    """URL 미리보기 요청"""
    url: HttpUrl


class UrlPreviewResponse(BaseModel):
    """URL 미리보기 응답"""
    title: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None


class ManualArticleCreate(BaseModel):
    """수동 기사 추가 요청"""
    url: HttpUrl
    title: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None


class SearchArticlesRequest(BaseModel):
    """키워드 기사 검색 요청"""
    query: str
    max_results: int = 20


class SearchArticleItem(BaseModel):
    """검색 결과 개별 아이템"""
    title: str
    url: str
    summary: Optional[str] = None
    source_ref: Optional[str] = None
    published_at: Optional[datetime] = None
    is_duplicate: bool = False


class SearchArticlesResponse(BaseModel):
    """키워드 기사 검색 응답"""
    query: str
    items: List[SearchArticleItem]
    total: int


class BatchManualCreate(BaseModel):
    """기사 일괄 추가 요청"""
    articles: List[ManualArticleCreate]


class BatchManualResult(BaseModel):
    """일괄 추가 개별 결과"""
    url: str
    success: bool
    id: Optional[str] = None
    error: Optional[str] = None


class BatchManualResponse(BaseModel):
    """기사 일괄 추가 응답"""
    total: int
    added: int
    skipped: int
    results: List[BatchManualResult]
