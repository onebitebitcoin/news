from typing import Any, Optional

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """성공 응답"""
    success: bool = True
    message: str = "OK"


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    message: str
    error: Optional[str] = None
    details: Optional[Any] = None
