from typing import Any, Optional, TypeVar

from app.schemas.common import ApiError, ApiResponse

T = TypeVar("T")


def ok(data: Optional[T] = None, metadata: Optional[dict[str, Any]] = None) -> ApiResponse[T]:
    return ApiResponse(success=True, data=data, error=None, metadata=metadata)


def fail(code: str, message: str, details: Any = None) -> ApiResponse[None]:
    return ApiResponse(success=False, data=None, error=ApiError(code=code, message=message, details=details))
