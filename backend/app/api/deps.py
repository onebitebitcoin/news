import logging

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.api_key_repository import ApiKeyRepository

logger = logging.getLogger(__name__)


async def verify_api_key(
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """API Key 인증 dependency"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={"message": "API 키가 필요합니다. X-API-Key 헤더를 포함해주세요."},
        )

    repo = ApiKeyRepository(db)
    api_key = repo.get_by_key(x_api_key)

    if not api_key:
        raise HTTPException(
            status_code=403,
            detail={"message": "유효하지 않은 API 키입니다."},
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=403,
            detail={"message": "비활성화된 API 키입니다."},
        )

    logger.debug(f"API key authenticated: {api_key.name} (id={api_key.id})")
    return api_key
