"""RSS 자동 수집 스케줄러"""

import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.scheduler_state import scheduler_state
from app.services.fetch_engine import FetchEngine
from app.services.market_data_service import update_market_data
from app.utils.cache import cache

logger = logging.getLogger(__name__)

# 테스트 환경 감지
TESTING = os.getenv("TESTING", "").lower() == "true"

# 스케줄러 인스턴스
scheduler = AsyncIOScheduler()

# 수집 주기 (시간)
FETCH_INTERVAL_HOURS = 3

# 서버 시작 후 초기 fetch 지연 시간 (초)
# 서버가 먼저 응답 가능하도록 지연
INITIAL_DELAY_SECONDS = 30

# 시장 데이터 수집 주기 (초)
MARKET_DATA_INTERVAL_SECONDS = 60

# 시장 데이터 초기 수집 지연 (초)
MARKET_DATA_INITIAL_DELAY_SECONDS = 5


def get_scheduler_status() -> dict:
    """스케줄러 상태 조회"""
    return scheduler_state.get_status(FETCH_INTERVAL_HOURS, scheduler.running)


def get_fetch_progress() -> dict:
    """수집 진행 상황 조회"""
    return scheduler_state.get_progress()


def update_fetch_progress(data: dict):
    """수집 진행 상황 업데이트"""
    scheduler_state.update_progress(data)


async def _progress_callback(data: dict):
    """FetchEngine에서 호출하는 진행 상황 콜백"""
    scheduler_state.update_progress(data)
    logger.debug(f"[Scheduler] Progress update: {data}")


async def scheduled_fetch():
    """스케줄된 RSS 수집 작업"""
    logger.info("[Scheduler] Starting scheduled RSS fetch...")

    # 상태 업데이트 (실행 시점 기록)
    scheduler_state.update_scheduler_times(FETCH_INTERVAL_HOURS)
    logger.info(
        f"[Scheduler] Status updated - Last: {scheduler_state.last_fetch_at}, "
        f"Next: {scheduler_state.next_fetch_at}"
    )

    # 진행 상황 초기화
    scheduler_state.reset_progress()

    db = SessionLocal()
    try:
        engine = FetchEngine(db, hours_limit=24, translate=True)
        result = await engine.run_all(progress_callback=_progress_callback)

        # 완료 상태 업데이트
        scheduler_state.mark_completed(
            fetched=result["total_fetched"],
            saved=result["total_saved"],
            duplicates=result["total_duplicates"],
        )

        # 캐시 무효화 (새 데이터 반영)
        cache.clear()
        logger.info(
            f"[Scheduler] Fetch complete - "
            f"Saved: {result['total_saved']}, "
            f"Duplicates: {result['total_duplicates']}"
        )
    except Exception as e:
        logger.error(f"[Scheduler] Fetch failed: {e}", exc_info=True)
        scheduler_state.mark_idle()
    finally:
        db.close()


def start_scheduler():
    """스케줄러 시작"""
    if TESTING:
        logger.info("[Scheduler] Skipped in testing environment")
        return

    # 서버 시작 후 지연 실행 (서버가 먼저 응답 가능하도록)
    scheduler.add_job(
        scheduled_fetch,
        trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=INITIAL_DELAY_SECONDS)),
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

    # 시장 데이터: 서버 시작 5초 후 초기 수집
    scheduler.add_job(
        update_market_data,
        trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=MARKET_DATA_INITIAL_DELAY_SECONDS)),
        id="market_data_initial",
        name="Market Data Fetch (Initial)",
        replace_existing=True,
    )

    # 시장 데이터: 60초마다 반복 수집
    scheduler.add_job(
        update_market_data,
        trigger=IntervalTrigger(seconds=MARKET_DATA_INTERVAL_SECONDS),
        id="market_data_job",
        name="Market Data Fetch",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"[Scheduler] Started - RSS: initial {INITIAL_DELAY_SECONDS}s then every {FETCH_INTERVAL_HOURS}h, "
        f"Market: initial {MARKET_DATA_INITIAL_DELAY_SECONDS}s then every {MARKET_DATA_INTERVAL_SECONDS}s"
    )


def stop_scheduler():
    """스케줄러 중지"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
