"""시장 데이터 Pydantic 스키마"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class BitcoinPriceKRW(BaseModel):
    """업비트 BTC/KRW 가격"""
    price: float
    change_rate: float = 0
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    acc_trade_volume_24h: Optional[float] = None
    change: Optional[str] = None


class BitcoinPriceUSD(BaseModel):
    """바이낸스 BTC/USDT 가격"""
    price: float


class FeeRates(BaseModel):
    """mempool 수수료율 (소수점 3자리, sat/vB)"""
    fastestFee: float
    halfHourFee: float
    hourFee: float
    economyFee: float
    minimumFee: Optional[float] = None


class FearGreedIndex(BaseModel):
    """공포/탐욕 지수"""
    value: int
    classification: str


class DifficultyAdjustment(BaseModel):
    """난이도 조정 데이터"""
    progress_percent: float
    difficulty_change: float
    estimated_retarget_date: int
    remaining_blocks: int
    remaining_time: int
    previous_retarget: float
    next_retarget_height: int
    time_avg: int


class HashRate(BaseModel):
    """해시레이트 데이터"""
    current_hashrate: float
    current_difficulty: float


class MempoolStats(BaseModel):
    """멤풀 통계"""
    count: int
    vsize: int
    total_fee: int


class HalvingInfo(BaseModel):
    """반감기 카운트다운"""
    current_block_height: int
    next_halving_height: int
    remaining_blocks: int
    remaining_time: int
    progress_percent: float
    current_era: int


class MarketDataResponse(BaseModel):
    """시장 데이터 전체 응답 (모든 필드 Optional - 부분 실패 허용)"""
    bitcoin_price_krw: Optional[BitcoinPriceKRW] = None
    bitcoin_price_usd: Optional[BitcoinPriceUSD] = None
    usd_krw_rate: Optional[float] = None
    kimchi_premium: Optional[float] = None
    fee_rates: Optional[FeeRates] = None
    fear_greed_index: Optional[FearGreedIndex] = None
    difficulty_adjustment: Optional[DifficultyAdjustment] = None
    hashrate: Optional[HashRate] = None
    mempool_stats: Optional[MempoolStats] = None
    halving: Optional[HalvingInfo] = None
    updated_at: Optional[str] = None
    errors: Optional[dict[str, Any]] = None


class MarketDataDaily(BaseModel):
    """일별 시장 데이터"""
    date: str
    bitcoin_price_krw: Optional[float] = None
    bitcoin_price_usd: Optional[float] = None
    usd_krw_rate: Optional[float] = None
    kimchi_premium: Optional[float] = None
    fee_rates: Optional[FeeRates] = None
    fear_greed_index: Optional[FearGreedIndex] = None
    difficulty_adjustment: Optional[DifficultyAdjustment] = None
    hashrate: Optional[HashRate] = None
    mempool_stats: Optional[MempoolStats] = None
    halving: Optional[HalvingInfo] = None


class MarketHistoryResponse(BaseModel):
    """시장 데이터 히스토리 응답"""
    days: int = Field(description="조회 일수")
    data: list[MarketDataDaily]
