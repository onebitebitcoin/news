from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import settings
from app.services.market_data_service import fetch_bitcoin_dominance


@pytest.mark.asyncio
async def test_fetch_bitcoin_dominance_returns_btc_percentage(monkeypatch):
    """CoinGecko 응답에서 BTC 도미넌스 값을 파싱한다."""
    monkeypatch.setattr(settings, "COIN_GECKO_API_KEY", "demo-key")

    response = MagicMock()
    response.json.return_value = {
        "data": {
            "market_cap_percentage": {
                "btc": 58.9876,
            }
        }
    }

    client = AsyncMock()
    client.get.return_value = response

    dominance = await fetch_bitcoin_dominance(client)

    assert dominance == 58.99
    client.get.assert_awaited_once_with(
        "https://api.coingecko.com/api/v3/global",
        headers={"x-cg-demo-api-key": "demo-key"},
    )


@pytest.mark.asyncio
async def test_fetch_bitcoin_dominance_raises_when_api_key_missing(monkeypatch):
    """API 키가 없으면 즉시 에러를 발생시킨다."""
    monkeypatch.setattr(settings, "COIN_GECKO_API_KEY", "")

    with pytest.raises(RuntimeError, match="COIN_GECKO_API_KEY is not configured"):
        await fetch_bitcoin_dominance(AsyncMock())
