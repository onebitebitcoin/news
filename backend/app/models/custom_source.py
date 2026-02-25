from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.database import Base


class CustomSource(Base):
    """커스텀 스크래핑 소스 설정"""

    __tablename__ = "custom_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    list_url = Column(String, nullable=False)
    fetch_mode = Column(String, nullable=False, default="scrape")
    is_active = Column(Boolean, nullable=False, default=True)
    ai_model = Column(String, nullable=True)
    extraction_rules_json = Column(Text, nullable=False)
    normalization_rules_json = Column(Text, nullable=True)
    last_analyzed_at = Column(DateTime, nullable=True)
    last_validation_error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CustomSource(id={self.id}, slug={self.slug}, active={self.is_active})>"
