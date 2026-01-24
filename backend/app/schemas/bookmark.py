from datetime import datetime

from pydantic import BaseModel

from app.schemas.feed import FeedItemResponse


class BookmarkResponse(BaseModel):
    """북마크 응답"""
    id: int
    item_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkWithItemResponse(BaseModel):
    """북마크 + 피드 아이템 응답"""
    bookmark: BookmarkResponse
    item: FeedItemResponse


class BookmarkListResponse(BaseModel):
    """북마크 목록 응답"""
    items: list[BookmarkWithItemResponse]
    total: int
