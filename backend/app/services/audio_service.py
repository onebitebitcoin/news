import logging
import os
import uuid
from typing import List, Optional

import aiofiles
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.audio import Audio
from app.repositories.audio_repository import AudioRepository

logger = logging.getLogger(__name__)

# Railway Volume 사용 시 AUDIO_UPLOAD_DIR=/data/audio 환경변수로 덮어쓴다.
# 미설정 시 로컬 개발용 경로 사용.
_DEFAULT_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "audio")
UPLOAD_DIR = settings.AUDIO_UPLOAD_DIR if settings.AUDIO_UPLOAD_DIR else _DEFAULT_UPLOAD_DIR

MAX_UPLOAD_BYTES = settings.AUDIO_MAX_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".webm"}


class AudioService:
    def __init__(self, db: Session):
        self.repo = AudioRepository(db)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def get_all(self, query: Optional[str] = None) -> List[Audio]:
        normalized_query = query.strip() if query else None
        return self.repo.get_all(query=normalized_query or None)

    def get_by_id(self, audio_id: int) -> Optional[Audio]:
        return self.repo.get_by_id(audio_id)

    def upload(
        self,
        title: str,
        file_content: bytes,
        original_filename: str,
        mime_type: Optional[str],
        description: Optional[str] = None,
    ) -> Audio:
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")

        safe_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"Audio uploaded: {original_filename} -> {safe_filename} ({len(file_content)} bytes)")

        return self.repo.create(
            title=title,
            filename=original_filename,
            file_path=file_path,
            file_size=len(file_content),
            mime_type=mime_type,
            description=description,
        )

    async def upload_async(
        self,
        title: str,
        upload_file: UploadFile,
        description: Optional[str] = None,
    ) -> Audio:
        """비동기 파일 저장 — 이벤트 루프 블로킹 없이 대용량/동시 업로드 처리"""
        ext = os.path.splitext(upload_file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")

        safe_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        size = 0

        async with aiofiles.open(file_path, "wb") as out:
            while True:
                chunk = await upload_file.read(256 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    await out.close()
                    os.remove(file_path)
                    raise ValueError(
                        f"파일 크기가 제한을 초과했습니다 (최대 {settings.AUDIO_MAX_SIZE_MB}MB)"
                    )
                await out.write(chunk)

        logger.info(f"Audio uploaded (async): {upload_file.filename} -> {safe_filename} ({size} bytes)")

        return self.repo.create(
            title=title,
            filename=upload_file.filename or "unknown",
            file_path=file_path,
            file_size=size,
            mime_type=upload_file.content_type,
            description=description,
        )

    def delete(self, audio_id: int) -> bool:
        audio = self.repo.get_by_id(audio_id)
        if not audio:
            return False
        if os.path.exists(audio.file_path):
            os.remove(audio.file_path)
            logger.info(f"Audio file deleted: {audio.file_path}")
        return self.repo.delete(audio_id)
