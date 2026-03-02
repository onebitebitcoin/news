from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AudioReferenceLinkCreate(BaseModel):
    """참고 링크 추가 요청"""
    url: str
    title: Optional[str] = None


class AudioReferenceLinkResponse(BaseModel):
    """참고 링크 응답"""
    id: int
    audio_id: int
    url: str
    title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AudioResponse(BaseModel):
    """오디오 응답 스키마"""
    id: int
    title: str
    filename: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    uploaded_at: datetime
    reference_links: List[AudioReferenceLinkResponse] = []

    class Config:
        from_attributes = True


class AudioListResponse(BaseModel):
    """오디오 목록 응답 스키마"""
    items: List[AudioResponse]
    total: int


class AudioUpdate(BaseModel):
    """오디오 정보 수정 요청"""
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
