"""시장 데이터 API 라우터"""

import logging

from fastapi import APIRouter

from app.market_data_state import market_data_state
from app.schemas.market import MarketDataResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/market",
    tags=["market"],
)


@router.get("/data", response_model=MarketDataResponse)
async def get_market_data():
    """캐시된 시장 데이터 반환"""
    data = market_data_state.get_all()
    return data
