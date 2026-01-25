"""Admin API - RSS 수집 관리"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.source_status import SourceStatus
from app.scheduler import get_fetch_progress, get_scheduler_status
from app.services.fetch_engine import FetchEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# === Response Schemas ===

class SourceResult(BaseModel):
    """소스별 수집 결과"""
    success: bool
    fetched: int
    saved: int
    duplicates: int
    error: Optional[str] = None


class FetchResult(BaseModel):
    """전체 수집 결과"""
    success: bool
    total_fetched: int
    total_saved: int
    total_duplicates: int
    sources: dict[str, SourceResult]
    started_at: str
    finished_at: Optional[str] = None


class SourceStatusResponse(BaseModel):
    """소스 상태 응답"""
    source: str
    last_success_at: Optional[str] = None
    last_error_at: Optional[str] = None
    last_error_message: Optional[str] = None

    class Config:
        from_attributes = True


class SourcesListResponse(BaseModel):
    """소스 목록 응답"""
    sources: List[SourceStatusResponse]
    available_sources: List[str]


class SchedulerStatusResponse(BaseModel):
    """스케줄러 상태 응답"""
    last_fetch_at: Optional[str] = None
    next_fetch_at: Optional[str] = None
    interval_hours: int
    is_running: bool


class FetchProgressResponse(BaseModel):
    """수집 진행 상황 응답"""
    status: str  # idle, running, completed
    started_at: Optional[str] = None
    current_source: Optional[str] = None
    sources_completed: int = 0
    sources_total: int = 0
    items_fetched: int = 0
    items_saved: int = 0
    items_duplicates: int = 0


# === API Endpoints ===

@router.post("/fetch/run", response_model=FetchResult)
async def run_fetch(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    RSS 수집 실행

    모든 등록된 소스에서 RSS 피드를 수집하여 DB에 저장합니다.

    - **hours**: 수집할 뉴스 시간 제한 (기본 24시간)
    """
    logger.info(f"[Admin] Fetch triggered (hours: {hours})")

    try:
        engine = FetchEngine(db, hours_limit=hours)
        result = await engine.run_all()

        logger.info(
            f"[Admin] Fetch completed - "
            f"Saved: {result['total_saved']}, "
            f"Duplicates: {result['total_duplicates']}"
        )

        return result

    except Exception as e:
        logger.error(f"[Admin] Fetch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "RSS 수집 중 오류 발생",
                "error": str(e),
            }
        )


@router.post("/fetch/run/{source_name}", response_model=SourceResult)
async def run_fetch_source(
    source_name: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    특정 소스만 RSS 수집 실행

    - **source_name**: 소스 이름 (googlenews, bitcoinmagazine, optech)
    - **hours**: 수집할 뉴스 시간 제한 (기본 24시간)
    """
    available = FetchEngine.get_source_names()
    if source_name not in available:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"알 수 없는 소스: {source_name}",
                "available_sources": available,
            }
        )

    logger.info(f"[Admin] Fetch triggered for source: {source_name} (hours: {hours})")

    try:
        engine = FetchEngine(db, hours_limit=hours)
        result = await engine.run_source(source_name)

        logger.info(
            f"[Admin] Fetch completed for {source_name} - "
            f"Saved: {result['saved']}, "
            f"Duplicates: {result['duplicates']}"
        )

        return result

    except Exception as e:
        logger.error(f"[Admin] Fetch failed for {source_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"{source_name} RSS 수집 중 오류 발생",
                "error": str(e),
            }
        )


@router.get("/sources", response_model=SourcesListResponse)
async def get_sources(db: Session = Depends(get_db)):
    """
    소스 상태 목록 조회

    등록된 모든 소스의 마지막 성공/실패 상태를 반환합니다.
    """
    # DB에 저장된 상태 조회
    statuses = db.query(SourceStatus).all()
    status_map = {s.source: s for s in statuses}

    # 등록된 모든 소스에 대한 상태
    available_sources = FetchEngine.get_source_names()
    sources = []

    for source_name in available_sources:
        if source_name in status_map:
            status = status_map[source_name]
            sources.append(SourceStatusResponse(
                source=status.source,
                last_success_at=status.last_success_at.isoformat() if status.last_success_at else None,
                last_error_at=status.last_error_at.isoformat() if status.last_error_at else None,
                last_error_message=status.last_error_message,
            ))
        else:
            sources.append(SourceStatusResponse(
                source=source_name,
            ))

    return SourcesListResponse(
        sources=sources,
        available_sources=available_sources,
    )


@router.get("/scheduler-status", response_model=SchedulerStatusResponse)
async def get_scheduler_status_endpoint():
    """
    스케줄러 상태 조회

    마지막 RSS 수집 시간과 다음 예정 시간을 반환합니다.
    """
    return get_scheduler_status()


@router.get("/fetch-progress", response_model=FetchProgressResponse)
async def get_fetch_progress_endpoint():
    """
    수집 진행 상황 조회

    현재 RSS 수집이 진행 중인 경우 진행 상황을 반환합니다.
    - status: idle(대기), running(진행 중), completed(완료)
    - current_source: 현재 처리 중인 소스
    - sources_completed/total: 완료된 소스 수 / 전체 소스 수
    - items_fetched/saved/duplicates: 조회/저장/중복 아이템 수
    """
    return get_fetch_progress()
