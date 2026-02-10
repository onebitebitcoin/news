from datetime import datetime
from typing import List

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    """API 키 생성 요청"""

    name: str


class ApiKeyResponse(BaseModel):
    """API 키 응답"""

    id: int
    name: str
    key: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    """API 키 목록 응답"""

    keys: List[ApiKeyResponse]
