import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feed_item import FeedItem
from app.schemas.feed import (
    FeedItemDetail,
    FeedItemResponse,
    FeedListResponse,
    ManualArticleCreate,
    UrlPreviewRequest,
    UrlPreviewResponse,
)
from app.services.dedup_service import DedupService
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
    try:
        service = FeedService(db)
        return service.get_feed_list(
            page=page,
            page_size=page_size,
            category=category,
            source=source,
            search=search,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"피드 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "피드 목록 조회 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.get("/feed/trending", response_model=List[FeedItemResponse])
async def get_trending(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """트렌딩 피드 조회"""
    logger.info(f"GET /feed/trending limit={limit}")
    try:
        service = FeedService(db)
        return service.get_trending(limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"트렌딩 피드 조회 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "트렌딩 피드 조회 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.get("/feed/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록"""
    logger.info("GET /feed/categories")
    try:
        service = FeedService(db)
        return service.get_categories()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "카테고리 목록 조회 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.get("/feed/sources", response_model=List[str])
async def get_sources(db: Session = Depends(get_db)):
    """소스 목록"""
    logger.info("GET /feed/sources")
    try:
        service = FeedService(db)
        return service.get_sources()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"소스 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "소스 목록 조회 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.post("/feed/preview", response_model=UrlPreviewResponse)
async def preview_url(body: UrlPreviewRequest):
    """URL 미리보기 - Open Graph / meta 태그 파싱"""
    url = str(body.url)
    logger.info(f"POST /feed/preview url={url}")
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0
        ) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; BitcoinNewsBot/1.0)"},
            )
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Open Graph 우선
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")

        title = (og_title["content"] if og_title and og_title.get("content") else None)
        summary = (og_desc["content"] if og_desc and og_desc.get("content") else None)
        image_url = (og_image["content"] if og_image and og_image.get("content") else None)

        # Fallback: <title>, <meta name="description">
        if not title:
            title_tag = soup.find("title")
            title = title_tag.string.strip() if title_tag and title_tag.string else None
        if not summary:
            desc_tag = soup.find("meta", attrs={"name": "description"})
            summary = (desc_tag["content"] if desc_tag and desc_tag.get("content") else None)

        return UrlPreviewResponse(
            title=title, summary=summary, image_url=image_url, url=url
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"URL 미리보기 HTTP 에러: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"URL 접근 실패 (HTTP {e.response.status_code})",
                "error": str(e),
                "type": "HTTPStatusError",
            },
        )
    except httpx.RequestError as e:
        logger.error(f"URL 미리보기 요청 에러: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "message": "URL에 접근할 수 없습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )
    except Exception as e:
        logger.error(f"URL 미리보기 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "URL 미리보기 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.post("/feed/manual", response_model=FeedItemResponse)
async def create_manual_article(
    body: ManualArticleCreate,
    db: Session = Depends(get_db),
):
    """수동 기사 추가"""
    url = str(body.url)
    logger.info(f"POST /feed/manual url={url} title={body.title}")
    try:
        url_hash = DedupService.create_hash(url)

        if DedupService.is_duplicate(db, url_hash):
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "이미 등록된 URL입니다",
                    "error": f"url_hash={url_hash}",
                    "type": "DuplicateError",
                },
            )

        now = datetime.now(timezone.utc)
        item = FeedItem(
            id=str(uuid.uuid4()),
            source="manual",
            title=body.title,
            summary=body.summary,
            url=url,
            image_url=str(body.image_url) if body.image_url else None,
            published_at=now,
            fetched_at=now,
            url_hash=url_hash,
            score=0,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(f"수동 기사 추가 완료: id={item.id}")
        return item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"수동 기사 추가 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "기사 추가 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.get("/feed/{item_id}", response_model=FeedItemDetail)
async def get_feed_detail(
    item_id: str,
    db: Session = Depends(get_db),
):
    """피드 상세 조회"""
    logger.info(f"GET /feed/{item_id}")
    try:
        service = FeedService(db)
        item = service.get_feed_detail(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Feed item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"피드 상세 조회 실패 (id={item_id}): {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "피드 상세 조회 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )
