from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class AudioReferenceLink(Base):
    """오디오 참고 링크 모델"""

    __tablename__ = "audio_reference_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_id = Column(
        Integer,
        ForeignKey("audio_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    audio = relationship("Audio", back_populates="reference_links")

    def __repr__(self):
        return f"<AudioReferenceLink(id={self.id}, audio_id={self.audio_id}, url={self.url})>"
