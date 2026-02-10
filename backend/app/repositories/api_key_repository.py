import logging
import secrets
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.api_key import ApiKey

logger = logging.getLogger(__name__)


class ApiKeyRepository:
    """API Key 레포지토리"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> ApiKey:
        """API 키 생성"""
        key = secrets.token_urlsafe(32)
        api_key = ApiKey(key=key, name=name)
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        logger.info(f"API key created: {api_key.name} (id={api_key.id})")
        return api_key

    def get_all(self) -> List[ApiKey]:
        """전체 키 목록 조회"""
        return self.db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()

    def get_by_key(self, key: str) -> Optional[ApiKey]:
        """키 문자열로 조회"""
        return self.db.query(ApiKey).filter(ApiKey.key == key).first()

    def get_by_id(self, key_id: int) -> Optional[ApiKey]:
        """ID로 조회"""
        return self.db.query(ApiKey).filter(ApiKey.id == key_id).first()

    def delete(self, key_id: int) -> bool:
        """키 삭제"""
        api_key = self.get_by_id(key_id)
        if api_key:
            self.db.delete(api_key)
            self.db.commit()
            logger.info(f"API key deleted: {api_key.name} (id={key_id})")
            return True
        return False

    def toggle_active(self, key_id: int) -> Optional[ApiKey]:
        """키 활성/비활성 토글"""
        api_key = self.get_by_id(key_id)
        if api_key:
            api_key.is_active = not api_key.is_active
            self.db.commit()
            self.db.refresh(api_key)
            logger.info(
                f"API key toggled: {api_key.name} "
                f"(id={key_id}, active={api_key.is_active})"
            )
            return api_key
        return None
