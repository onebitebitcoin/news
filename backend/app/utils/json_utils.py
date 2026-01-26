"""JSON 유틸리티 함수"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def safe_parse_json(raw_value: Optional[str], default: Any = None) -> Any:
    """JSON 문자열을 안전하게 파싱

    Args:
        raw_value: JSON 문자열 또는 None
        default: 파싱 실패 시 반환할 기본값 (기본: None → {})

    Returns:
        파싱된 객체 또는 기본값
    """
    if default is None:
        default = {}

    if not raw_value:
        return default

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_dumps_json(data: Any, default: str = "{}") -> str:
    """객체를 안전하게 JSON 문자열로 변환

    Args:
        data: 변환할 객체
        default: 변환 실패 시 반환할 기본 문자열

    Returns:
        JSON 문자열
    """
    if data is None:
        return default

    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return default
