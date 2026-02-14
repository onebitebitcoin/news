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
    key_prefix: str
    masked_key: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(ApiKeyResponse):
    """API 키 생성 응답 (평문 키 1회 노출)"""

    key: str


class ApiKeyListResponse(BaseModel):
    """API 키 목록 응답"""

    keys: List[ApiKeyResponse]
