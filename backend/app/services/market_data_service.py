"""시장 데이터 외부 API 호출 + 캐시 갱신 서비스"""

import logging

import httpx

from app.market_data_state import market_data_state

logger = logging.getLogger(__name__)

_TIMEOUT = 10.0


async def fetch_upbit_btc_price() -> dict:
    """업비트 BTC/KRW 가격 조회"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://api.upbit.com/v1/ticker",
            params={"markets": "KRW-BTC"},
        )
        resp.raise_for_status()
        data = resp.json()[0]
        return {
            "price": data["trade_price"],
            "change_rate": data.get("signed_change_rate", 0),
            "high_price": data.get("high_price"),
            "low_price": data.get("low_price"),
            "acc_trade_volume_24h": data.get("acc_trade_volume_24h"),
            "change": data.get("change"),
        }


async def fetch_upbit_usdt_price() -> float:
    """업비트 USDT/KRW 환율 조회"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://api.upbit.com/v1/ticker",
            params={"markets": "KRW-USDT"},
        )
        resp.raise_for_status()
        data = resp.json()[0]
        return data["trade_price"]


async def fetch_btc_usd_price() -> float:
    """Kraken BTC/USD 가격 조회"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://api.kraken.com/0/public/Ticker",
            params={"pair": "XBTUSD"},
        )
        resp.raise_for_status()
        data = resp.json()
        return float(data["result"]["XXBTZUSD"]["c"][0])


async def fetch_mempool_fees() -> dict:
    """mempool.space 수수료율 조회"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://mempool.space/api/v1/fees/recommended"
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_fear_greed_index() -> dict:
    """Fear & Greed 지수 조회"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get("https://api.alternative.me/fng/")
        resp.raise_for_status()
        data = resp.json()["data"][0]
        return {
            "value": int(data["value"]),
            "classification": data["value_classification"],
        }


def calculate_kimchi_premium(
    upbit_krw: float, binance_usd: float, usdt_krw: float
) -> float:
    """김치 프리미엄 퍼센트 계산"""
    binance_krw = binance_usd * usdt_krw
    if binance_krw == 0:
        return 0.0
    return round(((upbit_krw / binance_krw) - 1) * 100, 2)


async def update_market_data() -> None:
    """전체 시장 데이터 갱신 (스케줄러에서 호출)"""
    logger.info("[MarketData] Updating market data...")
    market_data_state.clear_errors()

    # 업비트 BTC/KRW
    try:
        btc_krw = await fetch_upbit_btc_price()
        market_data_state.update("bitcoin_price_krw", btc_krw)
    except Exception as e:
        logger.error(f"[MarketData] Upbit BTC fetch failed: {e}")
        market_data_state.add_error("upbit_btc", str(e))

    # 업비트 USDT/KRW
    usdt_krw = None
    try:
        usdt_krw = await fetch_upbit_usdt_price()
        market_data_state.update("usdt_krw_rate", usdt_krw)
    except Exception as e:
        logger.error(f"[MarketData] Upbit USDT fetch failed: {e}")
        market_data_state.add_error("upbit_usdt", str(e))

    # CoinGecko BTC/USD
    btc_usd = None
    try:
        btc_usd = await fetch_btc_usd_price()
        market_data_state.update("bitcoin_price_usd", {"price": btc_usd})
    except Exception as e:
        logger.error(f"[MarketData] Kraken BTC fetch failed: {e}")
        market_data_state.add_error("kraken_btc", str(e))

    # 김치 프리미엄 계산
    btc_krw_data = market_data_state.get_all().get("bitcoin_price_krw")
    if btc_krw_data and btc_usd and usdt_krw:
        premium = calculate_kimchi_premium(
            btc_krw_data["price"], btc_usd, usdt_krw
        )
        market_data_state.update("kimchi_premium", premium)

    # mempool 수수료
    try:
        fees = await fetch_mempool_fees()
        market_data_state.update("fee_rates", fees)
    except Exception as e:
        logger.error(f"[MarketData] Mempool fees fetch failed: {e}")
        market_data_state.add_error("mempool", str(e))

    # Fear & Greed 지수
    try:
        fng = await fetch_fear_greed_index()
        market_data_state.update("fear_greed_index", fng)
    except Exception as e:
        logger.error(f"[MarketData] Fear & Greed fetch failed: {e}")
        market_data_state.add_error("fear_greed", str(e))

    market_data_state.set_updated_at()
    logger.info("[MarketData] Market data update completed")
