from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta

from app.market_data_state import market_data_state
from app.models.market_data_snapshot import MarketDataSnapshot
from app.utils.timezone import KST


def test_get_market_data_includes_mvrv_and_bitcoin_dominance(client):
    """시장 데이터 응답에 MVRV Z-Score와 BTC 도미넌스 포함"""
    backup = deepcopy(market_data_state._data)  # noqa: SLF001
    try:
        market_data_state.update("mvrv_z_score", 1.23)
        market_data_state.update("bitcoin_dominance", 58.76)
        market_data_state.set_updated_at()

        response = client.get("/api/v1/market/data")

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["mvrv_z_score"] == 1.23
        assert payload["data"]["bitcoin_dominance"] == 58.76
    finally:
        market_data_state._data = backup  # noqa: SLF001


def test_get_market_history_includes_mvrv_and_bitcoin_dominance(client, db):
    """시장 히스토리 응답에 저장/현재 MVRV Z-Score와 BTC 도미넌스 포함"""
    today_kst = datetime.now(KST).date()
    yesterday_kst = today_kst - timedelta(days=1)

    snapshot = MarketDataSnapshot(
        date=yesterday_kst,
        bitcoin_price_krw=100.0,
        bitcoin_price_usd=10.0,
        usd_krw_rate=1300.0,
        kimchi_premium=1.0,
        bitcoin_dominance=57.12,
        mvrv_z_score=2.34,
    )
    db.add(snapshot)
    db.commit()

    backup = deepcopy(market_data_state._data)  # noqa: SLF001
    try:
        market_data_state.update("mvrv_z_score", 3.45)
        market_data_state.update("bitcoin_dominance", 59.01)
        market_data_state.set_updated_at()

        response = client.get("/api/v1/market/history?days=2")

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True

        data = payload["data"]["data"]
        by_date = {row["date"]: row for row in data}

        assert by_date[yesterday_kst.isoformat()]["mvrv_z_score"] == 2.34
        assert by_date[yesterday_kst.isoformat()]["bitcoin_dominance"] == 57.12
        assert by_date[today_kst.isoformat()]["mvrv_z_score"] == 3.45
        assert by_date[today_kst.isoformat()]["bitcoin_dominance"] == 59.01
    finally:
        market_data_state._data = backup  # noqa: SLF001
