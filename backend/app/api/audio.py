import logging
import os
from typing import Optional

import aiofiles
import aiofiles.os
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.response import ok
from app.database import get_db
from app.schemas.audio import AudioListResponse, AudioResponse
from app.schemas.common import ApiResponse
from app.services.audio_service import AudioService

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 256 * 1024  # 256KB — 동시 접속 시 메모리 압박 최소화


@router.get("/audio", response_model=ApiResponse[AudioListResponse])
async def get_audio_list(
    q: Optional[str] = Query(default=None, description="제목/설명/파일명 부분 검색"),
    db: Session = Depends(get_db),
):
    """오디오 목록 조회"""
    logger.info(f"GET /audio - q={q!r}")
    service = AudioService(db)
    items = service.get_all(query=q)
    return ok(AudioListResponse(
        items=[AudioResponse.model_validate(a) for a in items],
        total=len(items),
    ))


@router.post("/audio/upload", response_model=ApiResponse[AudioResponse])
async def upload_audio(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """오디오 파일 업로드 (비동기 저장)"""
    logger.info(f"POST /audio/upload - title={title}, filename={file.filename}")
    service = AudioService(db)
    try:
        audio = await service.upload_async(
            title=title,
            upload_file=file,
            description=description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ok(AudioResponse.model_validate(audio))


@router.get("/audio/{audio_id}/stream")
async def stream_audio(audio_id: int, request: Request, db: Session = Depends(get_db)):
    """오디오 스트리밍 — aiofiles 비동기 I/O + HTTP Range Request 지원

    동시 N명 스트리밍 시 이벤트 루프를 블로킹하지 않아 Uvicorn 스레드 풀 고갈 없음.
    """
    logger.info(f"GET /audio/{audio_id}/stream")
    service = AudioService(db)
    audio = service.get_by_id(audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="오디오 파일을 찾을 수 없습니다")
    if not os.path.exists(audio.file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

    file_size = os.path.getsize(audio.file_path)
    content_type = audio.mime_type or "audio/mpeg"
    range_header = request.headers.get("Range")

    if range_header:
        range_val = range_header.replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        content_length = end - start + 1

        async def iter_range():
            async with aiofiles.open(audio.file_path, "rb") as f:
                await f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk = await f.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type,
        }
        return StreamingResponse(iter_range(), status_code=206, headers=headers)

    async def iter_full():
        async with aiofiles.open(audio.file_path, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": content_type,
    }
    return StreamingResponse(iter_full(), status_code=200, headers=headers)


@router.delete("/audio/{audio_id}", response_model=ApiResponse[dict])
async def delete_audio(audio_id: int, db: Session = Depends(get_db)):
    """오디오 삭제"""
    logger.info(f"DELETE /audio/{audio_id}")
    service = AudioService(db)
    deleted = service.delete(audio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="오디오 파일을 찾을 수 없습니다")
    return ok({"message": "삭제되었습니다"})
