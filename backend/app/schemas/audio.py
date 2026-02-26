from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AudioResponse(BaseModel):
    """오디오 응답 스키마"""
    id: int
    title: str
    filename: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class AudioListResponse(BaseModel):
    """오디오 목록 응답 스키마"""
    items: List[AudioResponse]
    total: int
