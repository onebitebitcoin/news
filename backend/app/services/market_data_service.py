"""시장 데이터 외부 API 호출 + 캐시 갱신 서비스"""

import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.database import SessionLocal
from app.market_data_state import market_data_state
from app.models.market_data_snapshot import MarketDataSnapshot

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


async def fetch_usd_krw_rate() -> float:
    """USD/KRW 실제 환율 조회 (Primary: ExchangeRate-API, Fallback: Frankfurter)"""
    # Primary: ExchangeRate-API
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/USD")
            resp.raise_for_status()
            data = resp.json()
            rate = data["rates"]["KRW"]
            logger.info(f"[MarketData] USD/KRW rate from ExchangeRate-API: {rate}")
            return float(rate)
    except Exception as e:
        logger.warning(f"[MarketData] ExchangeRate-API failed, trying fallback: {e}")

    # Fallback: Frankfurter
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://api.frankfurter.app/latest",
            params={"from": "USD", "to": "KRW"},
        )
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"]["KRW"]
        logger.info(f"[MarketData] USD/KRW rate from Frankfurter: {rate}")
        return float(rate)


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
            "https://mempool.space/api/v1/fees/precise"
        )
        resp.raise_for_status()
        data = resp.json()
        return {k: round(v, 1) for k, v in data.items()}


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
    upbit_krw: float, binance_usd: float, usd_krw: float
) -> float:
    """김치 프리미엄 퍼센트 계산"""
    binance_krw = binance_usd * usd_krw
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

    # USD/KRW 실제 환율
    usd_krw = None
    try:
        usd_krw = await fetch_usd_krw_rate()
        market_data_state.update("usd_krw_rate", usd_krw)
    except Exception as e:
        logger.error(f"[MarketData] USD/KRW rate fetch failed: {e}")
        market_data_state.add_error("usd_krw", str(e))

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
    if btc_krw_data and btc_usd and usd_krw:
        premium = calculate_kimchi_premium(
            btc_krw_data["price"], btc_usd, usd_krw
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

    # 일별 스냅샷 저장
    try:
        save_daily_snapshot(market_data_state.get_all())
    except Exception as e:
        logger.error(f"[MarketData] Daily snapshot save failed: {e}")


KST = timezone(timedelta(hours=9))


def save_daily_snapshot(data: dict) -> None:
    """KST 기준 오늘 날짜의 스냅샷이 없으면 저장"""
    today_kst = datetime.now(KST).date()

    db = SessionLocal()
    try:
        existing = (
            db.query(MarketDataSnapshot)
            .filter(MarketDataSnapshot.date == today_kst)
            .first()
        )
        if existing:
            return

        btc_krw_data = data.get("bitcoin_price_krw")
        btc_usd_data = data.get("bitcoin_price_usd")
        fng_data = data.get("fear_greed_index")

        snapshot = MarketDataSnapshot(
            date=today_kst,
            bitcoin_price_krw=btc_krw_data["price"] if btc_krw_data else None,
            bitcoin_price_usd=btc_usd_data["price"] if btc_usd_data else None,
            usd_krw_rate=data.get("usd_krw_rate"),
            kimchi_premium=data.get("kimchi_premium"),
            fee_rates=data.get("fee_rates"),
            fear_greed_value=fng_data["value"] if fng_data else None,
            fear_greed_classification=fng_data["classification"] if fng_data else None,
        )
        db.add(snapshot)
        db.commit()
        logger.info(f"[MarketData] Daily snapshot saved for {today_kst}")
    finally:
        db.close()
