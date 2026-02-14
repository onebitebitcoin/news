from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiError(BaseModel):
    """표준 에러 응답"""
    code: str = Field(default="INTERNAL_ERROR")
    message: str
    details: Optional[Any] = None


class ApiResponse(BaseModel, Generic[T]):
    """표준 API envelope"""
    success: bool = True
    data: Optional[T] = None
    error: Optional[ApiError] = None
    metadata: Optional[dict[str, Any]] = None
