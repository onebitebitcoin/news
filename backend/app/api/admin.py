"""Admin API - RSS 수집 관리"""

import json
import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.response import ok
from app.database import get_db
from app.models.feed_item import FeedItem
from app.models.source_status import SourceStatus
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.custom_source_repository import CustomSourceRepository
from app.scheduler import get_fetch_progress, get_scheduler_status
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
)
from app.schemas.common import ApiResponse
from app.schemas.custom_source import (
    CustomSourceAnalyzeRequest,
    CustomSourceAnalyzeResponse,
    CustomSourceCreate,
    CustomSourceListResponse,
    CustomSourceResponse,
    CustomSourceUpdate,
)
from app.services.custom_source_service import (
    CustomSourceScrapeService,
    slugify_source_name,
)
from app.services.fetch_engine import FetchEngine
from app.services.translate_service import TranslateService
from app.utils.cache import cache

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


def _serialize_custom_source(repo: CustomSourceRepository, source) -> CustomSourceResponse:
    return CustomSourceResponse(**repo.to_dict(source))


def _clear_sources_cache() -> None:
    cache.delete("sources")


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
    repo = CustomSourceRepository(db)
    available = sorted(set(FetchEngine.get_source_names() + repo.active_slugs()))
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


# === Custom Sources Management ===

@router.post("/custom-sources/analyze", response_model=ApiResponse[CustomSourceAnalyzeResponse])
async def analyze_custom_source(
    body: CustomSourceAnalyzeRequest,
):
    """커스텀 스크래핑 소스 분석 (AI + 휴리스틱)"""
    service = CustomSourceScrapeService()
    try:
        result = await service.analyze(name=body.name, list_url=body.list_url)
        return ok(CustomSourceAnalyzeResponse(**result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)}) from e
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "소스 페이지를 불러오지 못했습니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e
    except Exception as e:
        logger.error(f"[Admin] Custom source analyze failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "커스텀 소스 분석 중 오류가 발생했습니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e


@router.get("/custom-sources", response_model=ApiResponse[CustomSourceListResponse])
async def list_custom_sources(db: Session = Depends(get_db)):
    """커스텀 소스 목록 조회"""
    repo = CustomSourceRepository(db)
    sources = repo.get_all()
    return ok(CustomSourceListResponse(
        sources=[_serialize_custom_source(repo, source) for source in sources],
    ))


@router.post("/custom-sources", response_model=ApiResponse[CustomSourceResponse], status_code=201)
async def create_custom_source(
    body: CustomSourceCreate,
    db: Session = Depends(get_db),
):
    """커스텀 소스 저장"""
    repo = CustomSourceRepository(db)
    service = CustomSourceScrapeService()

    try:
        slug = slugify_source_name(body.slug)
        preview_items, validation_errors = await service.validate_saved_config(
            name=body.name,
            list_url=body.list_url,
            extraction_rules=body.extraction_rules,
            max_items=3,
        )
        if validation_errors or not preview_items:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "커스텀 소스 저장 전 검증에 실패했습니다.",
                    "error": "; ".join(validation_errors or ["미리보기 결과 없음"]),
                    "type": "ValidationError",
                },
            )

        created = repo.create(
            name=body.name.strip(),
            slug=slug,
            list_url=body.list_url.strip(),
            extraction_rules=body.extraction_rules,
            normalization_rules=body.normalization_rules,
            is_active=body.is_active,
            ai_model=body.ai_model,
            last_validation_error=None,
        )
        _clear_sources_cache()
        return ok(_serialize_custom_source(repo, created))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)}) from e
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "message": "동일한 이름 또는 slug의 커스텀 소스가 이미 존재합니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] Custom source create failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "커스텀 소스 저장 중 오류가 발생했습니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e


@router.patch("/custom-sources/{source_id}", response_model=ApiResponse[CustomSourceResponse])
async def update_custom_source(
    source_id: int,
    body: CustomSourceUpdate,
    db: Session = Depends(get_db),
):
    """커스텀 소스 수정"""
    repo = CustomSourceRepository(db)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail={"message": f"커스텀 소스를 찾을 수 없습니다: {source_id}"})

    payload = body.model_dump(exclude_unset=True)
    if not payload:
        return ok(_serialize_custom_source(repo, source))

    service = CustomSourceScrapeService()
    try:
        next_name = (payload.get("name") or source.name).strip()
        next_slug = slugify_source_name((payload.get("slug") or source.slug).strip())
        next_list_url = (payload.get("list_url") or source.list_url).strip()
        next_rules = payload.get("extraction_rules")

        touch_analyzed_at = False
        last_validation_error = None
        if next_rules is not None or "list_url" in payload or "name" in payload:
            preview_items, validation_errors = await service.validate_saved_config(
                name=next_name,
                list_url=next_list_url,
                extraction_rules=next_rules if next_rules is not None else repo.to_dict(source)["extraction_rules"],
                max_items=3,
            )
            if validation_errors or not preview_items:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "커스텀 소스 검증에 실패했습니다.",
                        "error": "; ".join(validation_errors or ["미리보기 결과 없음"]),
                        "type": "ValidationError",
                    },
                )
            touch_analyzed_at = True

        updated = repo.update(
            source,
            name=next_name if "name" in payload else None,
            slug=next_slug if "slug" in payload else None,
            list_url=next_list_url if "list_url" in payload else None,
            is_active=payload.get("is_active"),
            extraction_rules=next_rules,
            normalization_rules=payload.get("normalization_rules"),
            ai_model=payload.get("ai_model"),
            last_validation_error=last_validation_error,
            touch_analyzed_at=touch_analyzed_at,
        )
        _clear_sources_cache()
        return ok(_serialize_custom_source(repo, updated))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)}) from e
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "message": "동일한 이름 또는 slug의 커스텀 소스가 이미 존재합니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] Custom source update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "커스텀 소스 수정 중 오류가 발생했습니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e


@router.delete("/custom-sources/{source_id}", response_model=ApiResponse[dict])
async def delete_custom_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """커스텀 소스 삭제"""
    repo = CustomSourceRepository(db)
    deleted = repo.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"message": f"커스텀 소스를 찾을 수 없습니다: {source_id}"})
    _clear_sources_cache()
    return ok({"message": "커스텀 소스가 삭제되었습니다."})


@router.post("/custom-sources/{source_id}/reanalyze", response_model=ApiResponse[CustomSourceAnalyzeResponse])
async def reanalyze_custom_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """기존 커스텀 소스 재분석"""
    repo = CustomSourceRepository(db)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail={"message": f"커스텀 소스를 찾을 수 없습니다: {source_id}"})

    service = CustomSourceScrapeService()
    try:
        result = await service.analyze(name=source.name, list_url=source.list_url)
        return ok(CustomSourceAnalyzeResponse(**result))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)}) from e
    except Exception as e:
        logger.error(f"[Admin] Custom source reanalyze failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "커스텀 소스 재분석 중 오류가 발생했습니다.",
                "error": str(e),
                "type": type(e).__name__,
            },
        ) from e


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
