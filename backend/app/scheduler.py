"""RSS 자동 수집 스케줄러"""

import logging
import os

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


async def scheduled_fetch():
    """스케줄된 RSS 수집 작업"""
    logger.info("[Scheduler] Starting scheduled RSS fetch...")

    db = SessionLocal()
    try:
        engine = FetchEngine(db, hours_limit=24, translate=True)
        result = await engine.run_all()

        logger.info(
            f"[Scheduler] Fetch complete - "
            f"Saved: {result['total_saved']}, "
            f"Duplicates: {result['total_duplicates']}"
        )
    except Exception as e:
        logger.error(f"[Scheduler] Fetch failed: {e}", exc_info=True)
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
