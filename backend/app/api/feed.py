import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.response import ok
from app.config import settings
from app.database import get_db
from app.models.feed_item import FeedItem
from app.schemas.common import ApiResponse
from app.schemas.feed import (
    BatchManualCreate,
    BatchManualResponse,
    BatchManualResult,
    FeedItemDetail,
    FeedItemResponse,
    FeedListResponse,
    ManualArticleCreate,
    SearchArticlesRequest,
    SearchArticlesResponse,
    UrlPreviewRequest,
    UrlPreviewResponse,
)
from app.services.dedup_service import DedupService
from app.services.feed_service import FeedService
from app.services.search_service import SearchService
from app.services.sources.base_fetcher import BaseFetcher
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)

router = APIRouter()


def _to_translation_http_error(message: str, error: str, status: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "message": message,
            "error": error,
            "type": "TranslationRequiredError",
            "translation_status": status,
        },
    )


def _translate_manual_article_or_raise(
    title: str,
    summary: Optional[str],
    translator: Optional[TranslateService] = None,
) -> tuple[str, Optional[str], str]:
    if TranslateService.is_korean_text(title):
        return title, summary, "skipped"

    active_translator = translator or TranslateService()
    if settings.TRANSLATION_REQUIRED and not active_translator.client:
        raise _to_translation_http_error(
            message="영문 기사는 번역이 필수이지만 OPENAI_API_KEY가 설정되지 않았습니다.",
            error="OPENAI_API_KEY is missing",
            status="failed",
        )

    translated_title, translated_summary = active_translator.translate_to_korean(
        title=title,
        summary=summary or "",
    )
    if not TranslateService.is_korean_text(translated_title):
        raise _to_translation_http_error(
            message="영문 기사 번역에 실패했습니다. 한글 제목이 필요합니다.",
            error="translated title does not contain Korean text",
            status="failed",
        )

    return translated_title, translated_summary, "ok"


@router.get("/feed", response_model=ApiResponse[FeedListResponse])
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
        result = service.get_feed_list(
            page=page,
            page_size=page_size,
            category=category,
            source=source,
            search=search,
        )
        return ok(result)
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


@router.get("/feed/trending", response_model=ApiResponse[List[FeedItemResponse]])
async def get_trending(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """트렌딩 피드 조회"""
    logger.info(f"GET /feed/trending limit={limit}")
    try:
        service = FeedService(db)
        return ok(service.get_trending(limit))
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


@router.get("/feed/categories", response_model=ApiResponse[List[str]])
async def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록"""
    logger.info("GET /feed/categories")
    try:
        service = FeedService(db)
        return ok(service.get_categories())
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


@router.get("/feed/sources", response_model=ApiResponse[List[str]])
async def get_sources(db: Session = Depends(get_db)):
    """소스 목록"""
    logger.info("GET /feed/sources")
    try:
        service = FeedService(db)
        return ok(service.get_sources())
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


@router.post("/feed/preview", response_model=ApiResponse[UrlPreviewResponse])
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

        # 발행 시간 메타태그 추출
        published_at = None
        pub_meta_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"property": "og:article:published_time"}),
            ("meta", {"attrs": {"name": "pubdate"}}),
            ("meta", {"attrs": {"name": "publishdate"}}),
        ]
        for tag_name, kwargs in pub_meta_selectors:
            if "attrs" in kwargs:
                tag = soup.find(tag_name, **kwargs)
            else:
                tag = soup.find(tag_name, **kwargs)
            if tag and tag.get("content"):
                published_at = BaseFetcher.parse_datetime(tag["content"])
                if published_at:
                    break

        # Fallback: <time datetime="..."> 태그
        if not published_at:
            time_tag = soup.find("time", attrs={"datetime": True})
            if time_tag:
                published_at = BaseFetcher.parse_datetime(time_tag["datetime"])

        return ok(UrlPreviewResponse(
            title=title, summary=summary, image_url=image_url, url=url,
            published_at=published_at,
        ))
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


@router.post("/feed/search", response_model=ApiResponse[SearchArticlesResponse])
async def search_articles(
    body: SearchArticlesRequest,
    db: Session = Depends(get_db),
):
    """키워드로 기사 검색 (Google News RSS)"""
    logger.info(f"POST /feed/search query={body.query} max_results={body.max_results}")
    try:
        service = SearchService(db)
        items = await service.search(body.query, body.max_results)
        return ok(SearchArticlesResponse(
            query=body.query,
            items=items,
            total=len(items),
        ))
    except Exception as e:
        logger.error(f"기사 검색 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "기사 검색 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )


@router.post("/feed/manual/batch", response_model=ApiResponse[BatchManualResponse])
async def create_manual_batch(
    body: BatchManualCreate,
    db: Session = Depends(get_db),
):
    """기사 일괄 추가"""
    logger.info(f"POST /feed/manual/batch count={len(body.articles)}")
    results: List[BatchManualResult] = []
    added = 0
    skipped = 0
    translator: Optional[TranslateService] = None

    for article in body.articles:
        url = str(article.url)
        try:
            url_hash = DedupService.create_hash(url)

            if DedupService.is_duplicate(db, url_hash):
                results.append(BatchManualResult(
                    url=url, success=False, error="이미 등록된 URL",
                ))
                skipped += 1
                continue

            if translator is None and not TranslateService.is_korean_text(article.title):
                translator = TranslateService()

            translated_title, translated_summary, translation_status = _translate_manual_article_or_raise(
                title=article.title,
                summary=article.summary,
                translator=translator,
            )

            now = datetime.now(timezone.utc)
            published_at = article.published_at or now
            item = FeedItem(
                id=str(uuid.uuid4()),
                source="manual",
                title=translated_title,
                summary=translated_summary,
                url=url,
                image_url=str(article.image_url) if article.image_url else None,
                published_at=published_at,
                fetched_at=now,
                url_hash=url_hash,
                score=0,
                translation_status=translation_status,
            )
            db.add(item)
            db.flush()
            results.append(BatchManualResult(url=url, success=True, id=item.id))
            added += 1
        except HTTPException as e:
            detail = e.detail if isinstance(e.detail, dict) else {"message": str(e.detail)}
            logger.warning(f"일괄 추가 번역 실패: url={url}, detail={detail}")
            results.append(BatchManualResult(
                url=url, success=False, error=detail.get("message", "번역 실패"),
            ))
            skipped += 1
        except Exception as e:
            logger.error(f"일괄 추가 개별 실패: url={url}, error={e}")
            results.append(BatchManualResult(
                url=url, success=False, error=str(e),
            ))
            skipped += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"일괄 추가 커밋 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "기사 일괄 추가 커밋 중 오류가 발생했습니다",
                "error": str(e),
                "type": type(e).__name__,
            },
        )

    logger.info(f"일괄 추가 완료: added={added}, skipped={skipped}")
    return ok(BatchManualResponse(
        total=len(body.articles),
        added=added,
        skipped=skipped,
        results=results,
    ))


@router.post("/feed/manual", response_model=ApiResponse[FeedItemResponse])
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
        published_at = body.published_at or now
        translator = None
        if not TranslateService.is_korean_text(body.title):
            translator = TranslateService()
        translated_title, translated_summary, translation_status = _translate_manual_article_or_raise(
            title=body.title,
            summary=body.summary,
            translator=translator,
        )
        item = FeedItem(
            id=str(uuid.uuid4()),
            source="manual",
            title=translated_title,
            summary=translated_summary,
            url=url,
            image_url=str(body.image_url) if body.image_url else None,
            published_at=published_at,
            fetched_at=now,
            url_hash=url_hash,
            score=0,
            translation_status=translation_status,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(f"수동 기사 추가 완료: id={item.id} published_at={published_at}")
        return ok(FeedItemResponse.model_validate(item))
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


@router.get("/feed/{item_id}", response_model=ApiResponse[FeedItemDetail])
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
        return ok(item)
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
