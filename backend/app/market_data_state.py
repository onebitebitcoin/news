"""시장 데이터 인메모리 캐시 (싱글톤)"""

from datetime import datetime, timezone
from typing import Any, Optional


class MarketDataState:
    """시장 데이터를 캡슐화하는 싱글톤 클래스"""

    _instance: Optional["MarketDataState"] = None

    def __new__(cls) -> "MarketDataState":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._data: dict[str, Any] = {
            "bitcoin_price_krw": None,
            "bitcoin_price_usd": None,
            "usd_krw_rate": None,
            "kimchi_premium": None,
            "fee_rates": None,
            "fear_greed_index": None,
            "mvrv_z_score": None,
            "difficulty_adjustment": None,
            "hashrate": None,
            "mempool_stats": None,
            "halving": None,
            "updated_at": None,
            "errors": {},
        }
        self._initialized = True

    def get_all(self) -> dict[str, Any]:
        """전체 데이터 복사본 반환"""
        return self._data.copy()

    def update(self, key: str, value: Any) -> None:
        """개별 필드 갱신"""
        self._data[key] = value

    def set_updated_at(self) -> None:
        """갱신 시각 기록"""
        self._data["updated_at"] = datetime.now(timezone.utc).isoformat()

    def add_error(self, source: str, error: str) -> None:
        """에러 기록"""
        self._data["errors"][source] = error

    def clear_errors(self) -> None:
        """에러 초기화"""
        self._data["errors"] = {}


# 싱글톤 인스턴스
market_data_state = MarketDataState()
