"""시장 데이터 외부 API 호출 + 캐시 갱신 서비스"""

import logging
from datetime import datetime
from typing import Any, Callable, Coroutine

import httpx

from app.config import settings
from app.database import SessionLocal
from app.market_data_state import market_data_state
from app.models.market_data_snapshot import MarketDataSnapshot
from app.utils.timezone import KST

logger = logging.getLogger(__name__)

_TIMEOUT = 10.0


async def fetch_upbit_btc_price(client: httpx.AsyncClient) -> dict:
    """업비트 BTC/KRW 가격 조회"""
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


async def fetch_usd_krw_rate(client: httpx.AsyncClient) -> float:
    """USD/KRW 실제 환율 조회 (Primary: ExchangeRate-API, Fallback: Frankfurter)"""
    # Primary: ExchangeRate-API
    try:
        resp = await client.get("https://open.er-api.com/v6/latest/USD")
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"]["KRW"]
        logger.info(f"[MarketData] USD/KRW rate from ExchangeRate-API: {rate}")
        return float(rate)
    except Exception as e:
        logger.warning(f"[MarketData] ExchangeRate-API failed, trying fallback: {e}")

    # Fallback: Frankfurter
    resp = await client.get(
        "https://api.frankfurter.app/latest",
        params={"from": "USD", "to": "KRW"},
    )
    resp.raise_for_status()
    data = resp.json()
    rate = data["rates"]["KRW"]
    logger.info(f"[MarketData] USD/KRW rate from Frankfurter: {rate}")
    return float(rate)


async def fetch_btc_usd_price(client: httpx.AsyncClient) -> float:
    """Kraken BTC/USD 가격 조회"""
    resp = await client.get(
        "https://api.kraken.com/0/public/Ticker",
        params={"pair": "XBTUSD"},
    )
    resp.raise_for_status()
    data = resp.json()
    return float(data["result"]["XXBTZUSD"]["c"][0])


async def fetch_mempool_fees(client: httpx.AsyncClient) -> dict:
    """mempool.space 수수료율 조회"""
    resp = await client.get(
        "https://mempool.space/api/v1/fees/precise"
    )
    resp.raise_for_status()
    data = resp.json()
    return {k: round(v, 1) for k, v in data.items()}


async def fetch_difficulty_adjustment(client: httpx.AsyncClient) -> dict:
    """mempool.space 난이도 조정 데이터"""
    resp = await client.get(
        "https://mempool.space/api/v1/difficulty-adjustment"
    )
    resp.raise_for_status()
    d = resp.json()
    return {
        "progress_percent": round(d["progressPercent"], 2),
        "difficulty_change": round(d["difficultyChange"], 2),
        "estimated_retarget_date": d["estimatedRetargetDate"],
        "remaining_blocks": d["remainingBlocks"],
        "remaining_time": d["remainingTime"],
        "previous_retarget": round(d["previousRetarget"], 2),
        "next_retarget_height": d["nextRetargetHeight"],
        "time_avg": d["timeAvg"],
    }


async def fetch_hashrate(client: httpx.AsyncClient) -> dict:
    """mempool.space 해시레이트"""
    resp = await client.get(
        "https://mempool.space/api/v1/mining/hashrate/1w"
    )
    resp.raise_for_status()
    d = resp.json()
    return {
        "current_hashrate": d["currentHashrate"],
        "current_difficulty": d["currentDifficulty"],
    }


async def fetch_mempool_stats(client: httpx.AsyncClient) -> dict:
    """mempool.space 멤풀 통계"""
    resp = await client.get("https://mempool.space/api/mempool")
    resp.raise_for_status()
    d = resp.json()
    return {
        "count": d["count"],
        "vsize": d["vsize"],
        "total_fee": d["total_fee"],
    }


async def fetch_block_tip_height(client: httpx.AsyncClient) -> int:
    """현재 블록 높이"""
    resp = await client.get(
        "https://mempool.space/api/blocks/tip/height"
    )
    resp.raise_for_status()
    return int(resp.text.strip())


def calculate_halving_info(block_height: int) -> dict:
    """반감기 카운트다운 계산"""
    HALVING_INTERVAL = 210_000
    current_era = block_height // HALVING_INTERVAL
    next_halving_height = (current_era + 1) * HALVING_INTERVAL
    remaining_blocks = next_halving_height - block_height
    remaining_seconds = remaining_blocks * 10 * 60
    progress = round(
        ((block_height % HALVING_INTERVAL) / HALVING_INTERVAL) * 100, 2
    )
    return {
        "current_block_height": block_height,
        "next_halving_height": next_halving_height,
        "remaining_blocks": remaining_blocks,
        "remaining_time": remaining_seconds,
        "progress_percent": progress,
        "current_era": current_era,
    }


async def fetch_fear_greed_index(client: httpx.AsyncClient) -> dict:
    """Fear & Greed 지수 조회"""
    resp = await client.get("https://api.alternative.me/fng/")
    resp.raise_for_status()
    data = resp.json()["data"][0]
    return {
        "value": int(data["value"]),
        "classification": data["value_classification"],
    }


async def fetch_mvrv_z_score(client: httpx.AsyncClient) -> float:
    """ResearchBitcoin API에서 MVRV Z-Score 조회"""
    token = settings.RESEARCHBITCOIN_API_TOKEN.strip()
    if not token:
        raise RuntimeError("RESEARCHBITCOIN_API_TOKEN is not configured")

    resp = await client.get(
        "https://api.researchbitcoin.net/v2/market_value_to_realized_value/mvrv_z",
        params={
            "resolution": "d1",
            "output_format": "json",
        },
        headers={"X-API-Token": token},
    )
    resp.raise_for_status()
    payload = resp.json()
    rows = payload.get("data") or []
    if not rows:
        raise ValueError("ResearchBitcoin response has no data rows")

    return float(rows[0]["mvrv_z"])


def calculate_kimchi_premium(
    upbit_krw: float, binance_usd: float, usd_krw: float
) -> float:
    """김치 프리미엄 퍼센트 계산"""
    binance_krw = binance_usd * usd_krw
    if binance_krw == 0:
        return 0.0
    return round(((upbit_krw / binance_krw) - 1) * 100, 2)


async def _safe_fetch(
    fetcher: Callable[..., Coroutine[Any, Any, Any]],
    state_key: str,
    error_key: str,
    label: str,
    client: httpx.AsyncClient,
) -> Any:
    """공통 fetch-update-error 패턴"""
    try:
        result = await fetcher(client)
        market_data_state.update(state_key, result)
        return result
    except Exception as e:
        logger.error(f"[MarketData] {label} fetch failed: {e}")
        market_data_state.add_error(error_key, str(e))
        return None


async def update_market_data() -> None:
    """전체 시장 데이터 갱신 (스케줄러에서 호출)"""
    logger.info("[MarketData] Updating market data...")
    market_data_state.clear_errors()

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        await _safe_fetch(
            fetch_upbit_btc_price, "bitcoin_price_krw", "upbit_btc", "Upbit BTC", client
        )

        usd_krw = await _safe_fetch(
            fetch_usd_krw_rate, "usd_krw_rate", "usd_krw", "USD/KRW rate", client
        )

        btc_usd = await _safe_fetch(
            fetch_btc_usd_price, "bitcoin_price_usd", "kraken_btc", "Kraken BTC", client
        )
        # btc_usd는 float이지만 state에는 {"price": value}로 저장
        if btc_usd is not None:
            market_data_state.update("bitcoin_price_usd", {"price": btc_usd})

        # 김치 프리미엄 계산
        btc_krw_data = market_data_state.get_all().get("bitcoin_price_krw")
        if btc_krw_data and btc_usd and usd_krw:
            premium = calculate_kimchi_premium(
                btc_krw_data["price"], btc_usd, usd_krw
            )
            market_data_state.update("kimchi_premium", premium)

        await _safe_fetch(
            fetch_mempool_fees, "fee_rates", "mempool", "Mempool fees", client
        )
        await _safe_fetch(
            fetch_fear_greed_index, "fear_greed_index", "fear_greed", "Fear & Greed", client
        )
        await _safe_fetch(
            fetch_mvrv_z_score,
            "mvrv_z_score",
            "mvrv_z_score",
            "MVRV Z-Score",
            client,
        )
        await _safe_fetch(
            fetch_difficulty_adjustment, "difficulty_adjustment", "difficulty_adjustment",
            "Difficulty adjustment", client
        )
        await _safe_fetch(
            fetch_hashrate, "hashrate", "hashrate", "Hashrate", client
        )
        await _safe_fetch(
            fetch_mempool_stats, "mempool_stats", "mempool_stats", "Mempool stats", client
        )

        # 블록 높이 + 반감기 계산
        block_height = await _safe_fetch(
            fetch_block_tip_height, "block_height", "block_height", "Block height", client
        )
        if block_height is not None:
            halving = calculate_halving_info(block_height)
            market_data_state.update("halving", halving)

    market_data_state.set_updated_at()
    logger.info("[MarketData] Market data update completed")

    # 일별 스냅샷 저장
    try:
        save_daily_snapshot(market_data_state.get_all())
    except Exception as e:
        logger.error(f"[MarketData] Daily snapshot save failed: {e}")


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
        halving_data = data.get("halving")

        snapshot = MarketDataSnapshot(
            date=today_kst,
            bitcoin_price_krw=btc_krw_data["price"] if btc_krw_data else None,
            bitcoin_price_usd=btc_usd_data["price"] if btc_usd_data else None,
            usd_krw_rate=data.get("usd_krw_rate"),
            kimchi_premium=data.get("kimchi_premium"),
            fee_rates=data.get("fee_rates"),
            fear_greed_value=fng_data["value"] if fng_data else None,
            fear_greed_classification=fng_data["classification"] if fng_data else None,
            mvrv_z_score=data.get("mvrv_z_score"),
            difficulty_adjustment=data.get("difficulty_adjustment"),
            hashrate_data=data.get("hashrate"),
            mempool_stats=data.get("mempool_stats"),
            block_height=halving_data["current_block_height"] if halving_data else None,
        )
        db.add(snapshot)
        db.commit()
        logger.info(f"[MarketData] Daily snapshot saved for {today_kst}")
    finally:
        db.close()
