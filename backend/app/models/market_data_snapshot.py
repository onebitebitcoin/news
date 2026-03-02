from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.types import JSON

from app.database import Base


class MarketDataSnapshot(Base):
    """일별 시장 데이터 스냅샷"""

    __tablename__ = "market_data_snapshots"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    bitcoin_price_krw = Column(Float, nullable=True)
    bitcoin_price_usd = Column(Float, nullable=True)
    usd_krw_rate = Column(Float, nullable=True)
    kimchi_premium = Column(Float, nullable=True)
    bitcoin_dominance = Column(Float, nullable=True)
    fee_rates = Column(JSON, nullable=True)
    fear_greed_value = Column(Integer, nullable=True)
    fear_greed_classification = Column(String, nullable=True)
    mvrv_z_score = Column(Float, nullable=True)
    difficulty_adjustment = Column(JSON, nullable=True)
    hashrate_data = Column(JSON, nullable=True)
    mempool_stats = Column(JSON, nullable=True)
    block_height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MarketDataSnapshot(date={self.date})>"
