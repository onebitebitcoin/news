import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.feed import FeedItemDetail, FeedItemResponse, FeedListResponse
from app.services.feed_service import FeedService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/feed", response_model=FeedListResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """피드 목록 조회"""
    logger.info(f"GET /feed page={page} category={category} search={search}")
    service = FeedService(db)
    return service.get_feed_list(
        page=page,
        page_size=page_size,
        category=category,
        source=source,
        search=search,
    )


@router.get("/feed/trending", response_model=List[FeedItemResponse])
async def get_trending(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """트렌딩 피드 조회"""
    logger.info(f"GET /feed/trending limit={limit}")
    service = FeedService(db)
    return service.get_trending(limit)


@router.get("/feed/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록"""
    logger.info("GET /feed/categories")
    service = FeedService(db)
    return service.get_categories()


@router.get("/feed/sources", response_model=List[str])
async def get_sources(db: Session = Depends(get_db)):
    """소스 목록"""
    logger.info("GET /feed/sources")
    service = FeedService(db)
    return service.get_sources()


@router.get("/feed/{item_id}", response_model=FeedItemDetail)
async def get_feed_detail(
    item_id: str,
    db: Session = Depends(get_db),
):
    """피드 상세 조회"""
    logger.info(f"GET /feed/{item_id}")
    service = FeedService(db)
    item = service.get_feed_detail(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return item
