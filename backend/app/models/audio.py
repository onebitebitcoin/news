from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Audio(Base):
    """오디오 파일 모델"""

    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)   # bytes
    duration = Column(Integer, nullable=True)    # seconds
    mime_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    reference_links = relationship(
        "AudioReferenceLink",
        back_populates="audio",
        cascade="all, delete-orphan",
        order_by="AudioReferenceLink.created_at",
    )

    def __repr__(self):
        return f"<Audio(id={self.id}, title={self.title})>"
