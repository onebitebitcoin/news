"""RSS 자동 수집 스케줄러"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.services.fetch_engine import FetchEngine

logger = logging.getLogger(__name__)

# 테스트 환경 감지
TESTING = os.getenv("TESTING", "").lower() == "true"

# 스케줄러 인스턴스
scheduler = AsyncIOScheduler()

# 수집 주기 (시간)
FETCH_INTERVAL_HOURS = 3

# 스케줄러 상태 저장 (메모리)
last_fetch_at: Optional[datetime] = None
next_fetch_at: Optional[datetime] = None

# 수집 진행 상황 저장 (메모리)
fetch_progress: dict = {
    "status": "idle",  # idle, running, completed
    "started_at": None,
    "current_source": None,
    "sources_completed": 0,
    "sources_total": 0,
    "items_fetched": 0,
    "items_saved": 0,
    "items_duplicates": 0,
}


def get_scheduler_status() -> dict:
    """스케줄러 상태 조회"""
    return {
        "last_fetch_at": last_fetch_at.isoformat() if last_fetch_at else None,
        "next_fetch_at": next_fetch_at.isoformat() if next_fetch_at else None,
        "interval_hours": FETCH_INTERVAL_HOURS,
        "is_running": scheduler.running,
    }


def get_fetch_progress() -> dict:
    """수집 진행 상황 조회"""
    return fetch_progress.copy()


def update_fetch_progress(data: dict):
    """수집 진행 상황 업데이트"""
    global fetch_progress
    fetch_progress.update(data)


def _update_scheduler_status():
    """스케줄러 상태 업데이트"""
    global last_fetch_at, next_fetch_at
    last_fetch_at = datetime.now(timezone.utc)
    next_fetch_at = last_fetch_at + timedelta(hours=FETCH_INTERVAL_HOURS)
    logger.info(f"[Scheduler] Status updated - Last: {last_fetch_at}, Next: {next_fetch_at}")


async def _progress_callback(data: dict):
    """FetchEngine에서 호출하는 진행 상황 콜백"""
    update_fetch_progress(data)
    logger.debug(f"[Scheduler] Progress update: {data}")


async def scheduled_fetch():
    """스케줄된 RSS 수집 작업"""
    logger.info("[Scheduler] Starting scheduled RSS fetch...")

    # 상태 업데이트 (실행 시점 기록)
    _update_scheduler_status()

    # 진행 상황 초기화
    update_fetch_progress({
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "current_source": None,
        "sources_completed": 0,
        "sources_total": 0,
        "items_fetched": 0,
        "items_saved": 0,
        "items_duplicates": 0,
    })

    db = SessionLocal()
    try:
        engine = FetchEngine(db, hours_limit=24, translate=True)
        result = await engine.run_all(progress_callback=_progress_callback)

        # 완료 상태 업데이트
        update_fetch_progress({
            "status": "completed",
            "items_fetched": result["total_fetched"],
            "items_saved": result["total_saved"],
            "items_duplicates": result["total_duplicates"],
        })

        logger.info(
            f"[Scheduler] Fetch complete - "
            f"Saved: {result['total_saved']}, "
            f"Duplicates: {result['total_duplicates']}"
        )
    except Exception as e:
        logger.error(f"[Scheduler] Fetch failed: {e}", exc_info=True)
        update_fetch_progress({"status": "idle"})
    finally:
        db.close()


def start_scheduler():
    """스케줄러 시작"""
    if TESTING:
        logger.info("[Scheduler] Skipped in testing environment")
        return

    # 서버 시작 시 즉시 1회 실행
    scheduler.add_job(
        scheduled_fetch,
        id="rss_fetch_initial",
        name="RSS Feed Fetch (Initial)",
        replace_existing=True,
    )

    # 이후 3시간마다 실행
    scheduler.add_job(
        scheduled_fetch,
        trigger=IntervalTrigger(hours=FETCH_INTERVAL_HOURS),
        id="rss_fetch_job",
        name="RSS Feed Fetch",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"[Scheduler] Started - Initial fetch + every {FETCH_INTERVAL_HOURS} hours"
    )


def stop_scheduler():
    """스케줄러 중지"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
