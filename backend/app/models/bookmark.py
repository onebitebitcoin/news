from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Bookmark(Base):
    """북마크 모델"""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Bookmark(id={self.id}, item_id={self.item_id})>"
