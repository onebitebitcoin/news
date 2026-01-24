import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.bookmark import BookmarkListResponse, BookmarkResponse
from app.schemas.common import SuccessResponse
from app.services.bookmark_service import BookmarkService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/bookmarks", response_model=BookmarkListResponse)
async def get_bookmarks(db: Session = Depends(get_db)):
    """북마크 목록 조회"""
    logger.info("GET /bookmarks")
    service = BookmarkService(db)
    return service.get_bookmarks()


@router.post("/bookmarks/{item_id}", response_model=BookmarkResponse)
async def add_bookmark(
    item_id: str,
    db: Session = Depends(get_db),
):
    """북마크 추가"""
    logger.info(f"POST /bookmarks/{item_id}")
    service = BookmarkService(db)
    bookmark = service.add_bookmark(item_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return bookmark


@router.delete("/bookmarks/{item_id}", response_model=SuccessResponse)
async def remove_bookmark(
    item_id: str,
    db: Session = Depends(get_db),
):
    """북마크 삭제"""
    logger.info(f"DELETE /bookmarks/{item_id}")
    service = BookmarkService(db)
    deleted = service.remove_bookmark(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return SuccessResponse(message="Bookmark removed")
