import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.custom_source import CustomSource

logger = logging.getLogger(__name__)


class CustomSourceRepository:
    """커스텀 소스 설정 레포지토리"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _dumps(value: Optional[dict[str, Any]]) -> Optional[str]:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _loads(value: Optional[str]) -> dict[str, Any]:
        if not value:
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def create(
        self,
        *,
        name: str,
        slug: str,
        list_url: str,
        extraction_rules: dict[str, Any],
        normalization_rules: Optional[dict[str, Any]] = None,
        is_active: bool = True,
        ai_model: Optional[str] = None,
        last_validation_error: Optional[str] = None,
    ) -> CustomSource:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        source = CustomSource(
            name=name,
            slug=slug,
            list_url=list_url,
            fetch_mode="scrape",
            is_active=is_active,
            ai_model=ai_model,
            extraction_rules_json=self._dumps(extraction_rules) or "{}",
            normalization_rules_json=self._dumps(normalization_rules),
            last_analyzed_at=now,
            last_validation_error=last_validation_error,
            created_at=now,
            updated_at=now,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        logger.info(f"Custom source created: {source.slug} (id={source.id})")
        return source

    def get_all(self) -> list[CustomSource]:
        return self.db.query(CustomSource).order_by(CustomSource.created_at.desc()).all()

    def get_active(self) -> list[CustomSource]:
        return (
            self.db.query(CustomSource)
            .filter(CustomSource.is_active.is_(True))
            .order_by(CustomSource.created_at.desc())
            .all()
        )

    def get_by_id(self, source_id: int) -> Optional[CustomSource]:
        return self.db.query(CustomSource).filter(CustomSource.id == source_id).first()

    def get_by_slug(self, slug: str) -> Optional[CustomSource]:
        return self.db.query(CustomSource).filter(CustomSource.slug == slug).first()

    def delete(self, source_id: int) -> bool:
        source = self.get_by_id(source_id)
        if not source:
            return False
        self.db.delete(source)
        self.db.commit()
        logger.info(f"Custom source deleted: {source.slug} (id={source.id})")
        return True

    def update(
        self,
        source: CustomSource,
        *,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        list_url: Optional[str] = None,
        is_active: Optional[bool] = None,
        extraction_rules: Optional[dict[str, Any]] = None,
        normalization_rules: Optional[dict[str, Any]] = None,
        ai_model: Optional[str] = None,
        last_validation_error: Optional[str] = None,
        touch_analyzed_at: bool = False,
    ) -> CustomSource:
        if name is not None:
            source.name = name
        if slug is not None:
            source.slug = slug
        if list_url is not None:
            source.list_url = list_url
        if is_active is not None:
            source.is_active = is_active
        if extraction_rules is not None:
            source.extraction_rules_json = self._dumps(extraction_rules) or "{}"
        if normalization_rules is not None:
            source.normalization_rules_json = self._dumps(normalization_rules)
        if ai_model is not None:
            source.ai_model = ai_model
        if last_validation_error is not None:
            source.last_validation_error = last_validation_error
        if touch_analyzed_at:
            source.last_analyzed_at = datetime.now(timezone.utc).replace(tzinfo=None)

        source.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(source)
        logger.info(f"Custom source updated: {source.slug} (id={source.id})")
        return source

    def active_slugs(self) -> list[str]:
        rows = (
            self.db.query(CustomSource.slug)
            .filter(CustomSource.is_active.is_(True))
            .order_by(CustomSource.slug.asc())
            .all()
        )
        return [r[0] for r in rows if r and r[0]]

    def to_dict(self, source: CustomSource) -> dict[str, Any]:
        return {
            "id": source.id,
            "name": source.name,
            "slug": source.slug,
            "list_url": source.list_url,
            "fetch_mode": source.fetch_mode,
            "is_active": source.is_active,
            "ai_model": source.ai_model,
            "extraction_rules": self._loads(source.extraction_rules_json),
            "normalization_rules": self._loads(source.normalization_rules_json),
            "last_analyzed_at": source.last_analyzed_at,
            "last_validation_error": source.last_validation_error,
            "created_at": source.created_at,
            "updated_at": source.updated_at,
        }
