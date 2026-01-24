from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text

from app.database import Base


class FeedItem(Base):
    """피드 아이템 모델"""

    __tablename__ = "feed_items"

    id = Column(String, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)
    source_ref = Column(String, nullable=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    tags = Column(Text, nullable=True)  # JSON string
    score = Column(Float, default=0)
    url_hash = Column(String, nullable=True, index=True)
    raw = Column(Text, nullable=True)  # JSON string
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)

    def __repr__(self):
        return f"<FeedItem(id={self.id}, title={self.title[:30]}...)>"
