"""스레드 안전 인메모리 TTL 캐시 (표준 라이브러리만 사용)"""

import threading
import time
from typing import Any, Optional


class TTLCache:
    """키-값 TTL 캐시 (스레드 안전)"""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """캐시 조회. 만료되었으면 None 반환."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """캐시 저장. ttl은 초 단위."""
        with self._lock:
            self._store[key] = (value, time.monotonic() + ttl)

    def delete(self, key: str) -> None:
        """캐시 키 삭제."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """모든 캐시 항목 삭제."""
        with self._lock:
            self._store.clear()


# 전역 캐시 인스턴스
cache = TTLCache()
