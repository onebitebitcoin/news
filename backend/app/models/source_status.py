from sqlalchemy import Column, DateTime, String, Text

from app.database import Base


class SourceStatus(Base):
    """소스 상태 모델"""

    __tablename__ = "source_status"

    source = Column(String, primary_key=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SourceStatus(source={self.source})>"
