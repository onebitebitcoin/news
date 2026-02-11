"""시장 데이터 API 라우터"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.market_data_state import market_data_state
from app.models.market_data_snapshot import MarketDataSnapshot
from app.schemas.market import (
    MarketDataDaily,
    MarketDataResponse,
    MarketHistoryResponse,
)

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

router = APIRouter(
    prefix="/market",
    tags=["market"],
)


@router.get("/data", response_model=MarketDataResponse)
async def get_market_data():
    """캐시된 시장 데이터 반환"""
    data = market_data_state.get_all()
    return data


@router.get("/history", response_model=MarketHistoryResponse)
async def get_market_history(
    days: int = Query(default=7, ge=1, le=90, description="조회 일수 (1~90)"),
    db: Session = Depends(get_db),
):
    """최근 N일간 일별 시장 데이터 히스토리 반환"""
    today_kst = datetime.now(KST).date()
    start_date = today_kst - timedelta(days=days - 1)

    # DB에서 과거 스냅샷 조회
    snapshots = (
        db.query(MarketDataSnapshot)
        .filter(MarketDataSnapshot.date >= start_date)
        .filter(MarketDataSnapshot.date < today_kst)
        .order_by(MarketDataSnapshot.date.asc())
        .all()
    )

    result: list[MarketDataDaily] = []

    for snap in snapshots:
        fee_rates = None
        if snap.fee_rates:
            fee_rates = snap.fee_rates

        fear_greed = None
        if snap.fear_greed_value is not None:
            fear_greed = {
                "value": snap.fear_greed_value,
                "classification": snap.fear_greed_classification or "",
            }

        result.append(
            MarketDataDaily(
                date=snap.date.isoformat(),
                bitcoin_price_krw=snap.bitcoin_price_krw,
                bitcoin_price_usd=snap.bitcoin_price_usd,
                usd_krw_rate=snap.usd_krw_rate,
                kimchi_premium=snap.kimchi_premium,
                fee_rates=fee_rates,
                fear_greed_index=fear_greed,
                difficulty_adjustment=snap.difficulty_adjustment,
                hashrate=snap.hashrate_data,
                mempool_stats=snap.mempool_stats,
                halving=None,
            )
        )

    # 오늘 데이터는 인메모리에서 가져오기
    current = market_data_state.get_all()
    btc_krw_data = current.get("bitcoin_price_krw")
    btc_usd_data = current.get("bitcoin_price_usd")
    fng_data = current.get("fear_greed_index")

    today_entry = MarketDataDaily(
        date=today_kst.isoformat(),
        bitcoin_price_krw=btc_krw_data["price"] if btc_krw_data else None,
        bitcoin_price_usd=btc_usd_data["price"] if btc_usd_data else None,
        usd_krw_rate=current.get("usd_krw_rate"),
        kimchi_premium=current.get("kimchi_premium"),
        fee_rates=current.get("fee_rates"),
        fear_greed_index=fng_data,
        difficulty_adjustment=current.get("difficulty_adjustment"),
        hashrate=current.get("hashrate"),
        mempool_stats=current.get("mempool_stats"),
        halving=current.get("halving"),
    )
    result.append(today_entry)

    return MarketHistoryResponse(days=days, data=result)
