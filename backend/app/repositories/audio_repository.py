import logging
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.audio import Audio

logger = logging.getLogger(__name__)


class AudioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, query: Optional[str] = None) -> List[Audio]:
        db_query = self.db.query(Audio)

        if query:
            like_query = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Audio.title.ilike(like_query),
                    Audio.description.ilike(like_query),
                    Audio.filename.ilike(like_query),
                )
            )

        return db_query.order_by(Audio.uploaded_at.desc()).all()

    def get_by_id(self, audio_id: int) -> Optional[Audio]:
        return self.db.query(Audio).filter(Audio.id == audio_id).first()

    def create(
        self,
        title: str,
        filename: str,
        file_path: str,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Audio:
        audio = Audio(
            title=title,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            description=description,
        )
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def delete(self, audio_id: int) -> bool:
        audio = self.get_by_id(audio_id)
        if not audio:
            return False
        self.db.delete(audio)
        self.db.commit()
        return True
