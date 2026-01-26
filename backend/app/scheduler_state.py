"""스케줄러 상태 관리 (싱글톤)"""

from datetime import datetime, timedelta, timezone
from typing import Optional


class SchedulerState:
    """스케줄러 상태를 캡슐화하는 싱글톤 클래스"""

    _instance: Optional["SchedulerState"] = None

    def __new__(cls) -> "SchedulerState":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._last_fetch_at: Optional[datetime] = None
        self._next_fetch_at: Optional[datetime] = None
        self._fetch_progress: dict = self._default_progress()
        self._initialized = True

    @staticmethod
    def _default_progress() -> dict:
        return {
            "status": "idle",
            "started_at": None,
            "current_source": None,
            "sources_completed": 0,
            "sources_total": 0,
            "items_fetched": 0,
            "items_saved": 0,
            "items_duplicates": 0,
        }

    @property
    def last_fetch_at(self) -> Optional[datetime]:
        return self._last_fetch_at

    @property
    def next_fetch_at(self) -> Optional[datetime]:
        return self._next_fetch_at

    def get_status(self, interval_hours: int, is_running: bool) -> dict:
        """스케줄러 상태 조회"""
        return {
            "last_fetch_at": self._last_fetch_at.isoformat() if self._last_fetch_at else None,
            "next_fetch_at": self._next_fetch_at.isoformat() if self._next_fetch_at else None,
            "interval_hours": interval_hours,
            "is_running": is_running,
        }

    def get_progress(self) -> dict:
        """수집 진행 상황 조회 (복사본 반환)"""
        return self._fetch_progress.copy()

    def update_progress(self, data: dict) -> None:
        """수집 진행 상황 업데이트"""
        self._fetch_progress.update(data)

    def reset_progress(self) -> None:
        """수집 진행 상황 초기화"""
        self._fetch_progress = self._default_progress()
        self._fetch_progress["status"] = "running"
        self._fetch_progress["started_at"] = datetime.now(timezone.utc).isoformat()

    def update_scheduler_times(self, interval_hours: int) -> None:
        """스케줄러 시간 상태 업데이트"""
        self._last_fetch_at = datetime.now(timezone.utc)
        self._next_fetch_at = self._last_fetch_at + timedelta(hours=interval_hours)

    def mark_completed(self, fetched: int, saved: int, duplicates: int) -> None:
        """수집 완료 상태로 변경"""
        self._fetch_progress.update({
            "status": "completed",
            "items_fetched": fetched,
            "items_saved": saved,
            "items_duplicates": duplicates,
        })

    def mark_idle(self) -> None:
        """유휴 상태로 변경"""
        self._fetch_progress["status"] = "idle"


# 싱글톤 인스턴스
scheduler_state = SchedulerState()
