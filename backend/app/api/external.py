"""External API - 외부 서버용 기사 조회 API (API Key 인증 필요)"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.database import get_db
from app.schemas.external import (
    ExternalArticleDetail,
    ExternalArticleListResponse,
)
from app.services.external_service import ExternalService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/external",
    tags=["external"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/articles", response_model=ExternalArticleListResponse)
async def get_articles(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    기사 목록 조회

    - **page**: 페이지 번호 (기본 1)
    - **page_size**: 페이지 크기 (기본 20, 최대 100)
    - **category**: 카테고리 필터
    - **source**: 소스 필터
    - **search**: 검색어 (제목, 요약)
    """
    page_size = min(page_size, 100)

    service = ExternalService(db)
    articles, total = service.get_articles(
        page=page,
        page_size=page_size,
        category=category,
        source=source,
        search=search,
    )

    return ExternalArticleListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/articles/{article_id}", response_model=ExternalArticleDetail)
async def get_article_detail(
    article_id: str,
    db: Session = Depends(get_db),
):
    """기사 상세 조회"""
    service = ExternalService(db)
    article = service.get_article_detail(article_id)

    if not article:
        raise HTTPException(
            status_code=404,
            detail={"message": f"기사를 찾을 수 없습니다: {article_id}"},
        )

    return article


@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """소스 목록 조회"""
    service = ExternalService(db)
    return {"sources": service.get_sources()}


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록 조회"""
    service = ExternalService(db)
    return {"categories": service.get_categories()}
