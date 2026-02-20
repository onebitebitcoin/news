"""Admin API - RSS 수집 관리"""

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.response import ok
from app.database import get_db
from app.models.feed_item import FeedItem
from app.models.source_status import SourceStatus
from app.repositories.api_key_repository import ApiKeyRepository
from app.scheduler import get_fetch_progress, get_scheduler_status
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
)
from app.schemas.common import ApiResponse
from app.services.fetch_engine import FetchEngine
from app.services.translate_service import TranslateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _mask_key(prefix: str) -> str:
    return f"{prefix}...****"


def _serialize_api_key(key) -> ApiKeyResponse:
    key_prefix = key.key_prefix or f"legacy_{key.id}"
    return ApiKeyResponse(
        id=key.id,
        name=key.name,
        key_prefix=key_prefix,
        masked_key=_mask_key(key_prefix),
        created_at=key.created_at,
        is_active=key.is_active,
    )


# === Response Schemas ===

class SourceResult(BaseModel):
    """소스별 수집 결과"""
    success: bool
    fetched: int
    saved: int
    duplicates: int
    filtered: int = 0
    translation_failed: int = 0
    translation_dropped: int = 0
    error: Optional[str] = None


class FetchResult(BaseModel):
    """전체 수집 결과"""
    success: bool
    total_fetched: int
    total_saved: int
    total_duplicates: int
    total_filtered: int = 0
    total_translation_failed: int = 0
    total_translation_dropped: int = 0
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

@router.post("/fetch/run", response_model=ApiResponse[FetchResult])
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

        return ok(FetchResult(**result))

    except Exception as e:
        logger.error(f"[Admin] Fetch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "RSS 수집 중 오류 발생",
                "error": str(e),
            }
        )


@router.post("/fetch/run/{source_name}", response_model=ApiResponse[SourceResult])
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

        return ok(SourceResult(**result))

    except Exception as e:
        logger.error(f"[Admin] Fetch failed for {source_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"{source_name} RSS 수집 중 오류 발생",
                "error": str(e),
            }
        )


@router.get("/sources", response_model=ApiResponse[SourcesListResponse])
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

    return ok(SourcesListResponse(
        sources=sources,
        available_sources=available_sources,
    ))


@router.get("/scheduler-status", response_model=ApiResponse[SchedulerStatusResponse])
async def get_scheduler_status_endpoint():
    """
    스케줄러 상태 조회

    마지막 RSS 수집 시간과 다음 예정 시간을 반환합니다.
    """
    return ok(SchedulerStatusResponse(**get_scheduler_status()))


@router.get("/fetch-progress", response_model=ApiResponse[FetchProgressResponse])
async def get_fetch_progress_endpoint():
    """
    수집 진행 상황 조회

    현재 RSS 수집이 진행 중인 경우 진행 상황을 반환합니다.
    - status: idle(대기), running(진행 중), completed(완료)
    - current_source: 현재 처리 중인 소스
    - sources_completed/total: 완료된 소스 수 / 전체 소스 수
    - items_fetched/saved/duplicates: 조회/저장/중복 아이템 수
    """
    return ok(FetchProgressResponse(**get_fetch_progress()))


class ResetGroupsResponse(BaseModel):
    """그룹 초기화 결과"""
    success: bool
    total_items: int
    reset_count: int
    message: str


@router.post("/groups/reset", response_model=ApiResponse[ResetGroupsResponse])
async def reset_dedup_groups(db: Session = Depends(get_db)):
    """
    모든 dedup_group_id 초기화

    Transitive Closure 버그로 잘못 그룹화된 데이터를 정리합니다.
    모든 피드 아이템의 dedup_group_id를 삭제하여 재그룹화를 준비합니다.
    """
    logger.info("[Admin] Starting dedup_group_id reset")

    try:
        items = db.query(FeedItem).all()
        total_items = len(items)
        reset_count = 0

        for item in items:
            if not item.raw:
                continue

            try:
                raw = json.loads(item.raw)
            except json.JSONDecodeError:
                continue

            if "dedup_group_id" in raw:
                del raw["dedup_group_id"]
                item.raw = json.dumps(raw)
                reset_count += 1

        db.commit()

        logger.info(
            f"[Admin] dedup_group_id reset completed - "
            f"Total: {total_items}, Reset: {reset_count}"
        )

        return ok(ResetGroupsResponse(
            success=True,
            total_items=total_items,
            reset_count=reset_count,
            message=f"{reset_count}개 아이템의 그룹 ID가 초기화되었습니다.",
        ))

    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] dedup_group_id reset failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "그룹 ID 초기화 중 오류 발생",
                "error": str(e),
            }
        )


# === API Key Management ===

@router.get("/api-keys", response_model=ApiResponse[ApiKeyListResponse])
async def get_api_keys(db: Session = Depends(get_db)):
    """API 키 목록 조회"""
    repo = ApiKeyRepository(db)
    keys = repo.get_all()
    return ok(ApiKeyListResponse(
        keys=[_serialize_api_key(k) for k in keys],
    ))


@router.post("/api-keys", response_model=ApiResponse[ApiKeyCreatedResponse], status_code=201)
async def create_api_key(
    body: ApiKeyCreate,
    db: Session = Depends(get_db),
):
    """API 키 생성"""
    repo = ApiKeyRepository(db)
    api_key, raw_key = repo.create(name=body.name)
    return ok(ApiKeyCreatedResponse(
        **_serialize_api_key(api_key).model_dump(),
        key=raw_key,
    ))


@router.delete("/api-keys/{key_id}", response_model=ApiResponse[dict])
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
):
    """API 키 삭제"""
    repo = ApiKeyRepository(db)
    deleted = repo.delete(key_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"message": f"API 키를 찾을 수 없습니다: {key_id}"},
        )
    return ok({"message": "API 키가 삭제되었습니다."})


# === Retranslation ===

class RetranslateResponse(BaseModel):
    """재번역 결과"""
    success: bool
    total_failed: int
    retranslated: int
    still_failed: int
    message: str


@router.post("/retranslate", response_model=ApiResponse[RetranslateResponse])
async def retranslate_failed(db: Session = Depends(get_db)):
    """
    번역 실패 항목 수동 재번역

    translation_status가 'failed'인 항목들을 재번역합니다.
    최대 50개씩 처리합니다.
    """
    logger.info("[Admin] Retranslation triggered")

    try:
        failed_items = (
            db.query(FeedItem)
            .filter(FeedItem.translation_status == "failed")
            .limit(50)
            .all()
        )

        if not failed_items:
            return ok(RetranslateResponse(
                success=True,
                total_failed=0,
                retranslated=0,
                still_failed=0,
                message="재번역할 항목이 없습니다.",
            ))

        translator = TranslateService()
        if not translator.client:
            raise HTTPException(
                status_code=500,
                detail={"message": "OPENAI_API_KEY가 설정되지 않았습니다."},
            )

        batch = [
            {"id": item.id, "title": item.title, "summary": item.summary or ""}
            for item in failed_items
        ]

        translated = translator.translate_batch_sync(batch)

        success_count = 0
        for translated_item in translated:
            if translated_item.get("_translated", False):
                db_item = db.query(FeedItem).filter(
                    FeedItem.id == translated_item["id"]
                ).first()
                if db_item:
                    db_item.title = translated_item["title"]
                    db_item.summary = translated_item["summary"]
                    db_item.translation_status = "ok"
                    success_count += 1

        db.commit()

        still_failed = len(failed_items) - success_count
        logger.info(
            f"[Admin] Retranslation complete - "
            f"Success: {success_count}, Still failed: {still_failed}"
        )

        return ok(RetranslateResponse(
            success=True,
            total_failed=len(failed_items),
            retranslated=success_count,
            still_failed=still_failed,
            message=f"{success_count}개 항목이 재번역되었습니다.",
        ))

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] Retranslation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "재번역 중 오류 발생",
                "error": str(e),
            }
        )
