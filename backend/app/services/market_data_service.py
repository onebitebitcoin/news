"""시장 데이터 외부 API 호출 + 캐시 갱신 서비스"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
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


# ─── 과거 날짜 데이터 수집 함수들 ───────────────────────────────────────────────

async def fetch_btc_krw_for_date(client: httpx.AsyncClient, target_date: date) -> float | None:
    """업비트 특정 날짜 BTC/KRW 종가 조회"""
    # to = 다음날 KST 자정 = 다음날 UTC 15:00
    to_str = (target_date + timedelta(days=1)).strftime("%Y-%m-%dT15:00:00Z")
    resp = await client.get(
        "https://api.upbit.com/v1/candles/days",
        params={"market": "KRW-BTC", "to": to_str, "count": 1},
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    return float(data[0]["trade_price"])


async def fetch_btc_usd_for_date(client: httpx.AsyncClient, target_date: date) -> float | None:
    """Kraken 특정 날짜 BTC/USD 종가 조회 (일별 OHLC)"""
    since = int(datetime(target_date.year, target_date.month, target_date.day,
                         tzinfo=timezone.utc).timestamp())
    resp = await client.get(
        "https://api.kraken.com/0/public/OHLC",
        params={"pair": "XBTUSD", "interval": 1440, "since": since},
    )
    resp.raise_for_status()
    data = resp.json()
    ohlc = data.get("result", {}).get("XXBTZUSD", [])
    if not ohlc:
        return None
    # [time, open, high, low, close, vwap, volume, count]
    return float(ohlc[0][4])


async def fetch_usd_krw_for_date(client: httpx.AsyncClient, target_date: date) -> float | None:
    """Frankfurter 특정 날짜 USD/KRW 환율 조회"""
    date_str = target_date.strftime("%Y-%m-%d")
    resp = await client.get(
        f"https://api.frankfurter.app/{date_str}",
        params={"from": "USD", "to": "KRW"},
    )
    resp.raise_for_status()
    data = resp.json()
    return float(data["rates"]["KRW"])


async def fetch_fear_greed_for_date(client: httpx.AsyncClient, target_date: date) -> dict | None:
    """alternative.me 특정 날짜 Fear & Greed 지수 조회"""
    resp = await client.get(
        "https://api.alternative.me/fng/",
        params={"limit": 14},
    )
    resp.raise_for_status()
    items = resp.json().get("data", [])
    # timestamp는 UTC 자정 unix timestamp
    target_ts = int(datetime(target_date.year, target_date.month, target_date.day,
                             tzinfo=timezone.utc).timestamp())
    for item in items:
        if int(item.get("timestamp", 0)) == target_ts:
            return {
                "value": int(item["value"]),
                "classification": item["value_classification"],
            }
    return None


async def fetch_mvrv_z_score_for_date(client: httpx.AsyncClient, target_date: date) -> float | None:
    """ResearchBitcoin 특정 날짜 MVRV Z-Score 조회"""
    token = settings.RESEARCHBITCOIN_API_TOKEN.strip()
    if not token:
        return None
    from_str = target_date.strftime("%Y-%m-%d")
    to_str = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
    resp = await client.get(
        "https://api.researchbitcoin.net/v2/market_value_to_realized_value/mvrv_z",
        params={"resolution": "d1", "from_time": from_str, "to_time": to_str, "output_format": "json"},
        headers={"X-API-Token": token},
    )
    resp.raise_for_status()
    rows = resp.json().get("data") or []
    if not rows:
        return None
    return float(rows[0]["mvrv_z"])


async def backfill_missing_snapshots(days: int = 7) -> None:
    """최근 N일간 누락된 스냅샷을 과거 API 데이터로 채움 (1시간 크롤링 후 호출)"""
    today_kst = datetime.now(KST).date()
    dates_to_check = [today_kst - timedelta(days=i) for i in range(days)]

    db = SessionLocal()
    try:
        existing_dates = {
            row.date
            for row in db.query(MarketDataSnapshot.date)
            .filter(MarketDataSnapshot.date.in_(dates_to_check))
            .all()
        }
        missing = sorted(d for d in dates_to_check if d not in existing_dates)

        if not missing:
            logger.debug("[Backfill] 누락된 스냅샷 없음")
            return

        logger.info(f"[Backfill] 누락 날짜 {len(missing)}개 보충 시작: {missing}")

        async with httpx.AsyncClient(timeout=15.0) as client:
            for target_date in missing:
                await _backfill_one_day(db, client, target_date, today_kst)
    finally:
        db.close()


async def _backfill_one_day(db, client: httpx.AsyncClient, target_date: date, today_kst: date) -> None:
    """단일 날짜 스냅샷 수집 및 저장"""
    try:
        if target_date == today_kst:
            # 오늘: 인메모리 캐시 사용
            current = market_data_state.get_all()
            btc_krw_data = current.get("bitcoin_price_krw")
            btc_usd_data = current.get("bitcoin_price_usd")
            fng_data = current.get("fear_greed_index")
            halving_data = current.get("halving")
            snapshot = MarketDataSnapshot(
                date=target_date,
                bitcoin_price_krw=btc_krw_data["price"] if btc_krw_data else None,
                bitcoin_price_usd=btc_usd_data["price"] if btc_usd_data else None,
                usd_krw_rate=current.get("usd_krw_rate"),
                kimchi_premium=current.get("kimchi_premium"),
                fee_rates=current.get("fee_rates"),
                fear_greed_value=fng_data["value"] if fng_data else None,
                fear_greed_classification=fng_data["classification"] if fng_data else None,
                mvrv_z_score=current.get("mvrv_z_score"),
                difficulty_adjustment=current.get("difficulty_adjustment"),
                hashrate_data=current.get("hashrate"),
                mempool_stats=current.get("mempool_stats"),
                block_height=halving_data["current_block_height"] if halving_data else None,
            )
        else:
            # 과거 날짜: 외부 API에서 수집
            btc_krw, btc_usd, usd_krw, fng, mvrv = None, None, None, None, None

            try:
                btc_krw = await fetch_btc_krw_for_date(client, target_date)
            except Exception as e:
                logger.warning(f"[Backfill] {target_date} BTC KRW 실패: {e}")
            try:
                btc_usd = await fetch_btc_usd_for_date(client, target_date)
            except Exception as e:
                logger.warning(f"[Backfill] {target_date} BTC USD 실패: {e}")
            try:
                usd_krw = await fetch_usd_krw_for_date(client, target_date)
            except Exception as e:
                logger.warning(f"[Backfill] {target_date} USD/KRW 실패: {e}")
            try:
                fng = await fetch_fear_greed_for_date(client, target_date)
            except Exception as e:
                logger.warning(f"[Backfill] {target_date} Fear&Greed 실패: {e}")
            try:
                mvrv = await fetch_mvrv_z_score_for_date(client, target_date)
            except Exception as e:
                logger.warning(f"[Backfill] {target_date} MVRV 실패: {e}")

            kimchi = calculate_kimchi_premium(btc_krw, btc_usd, usd_krw) if (btc_krw and btc_usd and usd_krw) else None
            snapshot = MarketDataSnapshot(
                date=target_date,
                bitcoin_price_krw=btc_krw,
                bitcoin_price_usd=btc_usd,
                usd_krw_rate=usd_krw,
                kimchi_premium=kimchi,
                fear_greed_value=fng["value"] if fng else None,
                fear_greed_classification=fng["classification"] if fng else None,
                mvrv_z_score=mvrv,
            )

        db.add(snapshot)
        db.commit()
        logger.info(f"[Backfill] {target_date} 스냅샷 저장 완료")
    except Exception as e:
        db.rollback()
        logger.error(f"[Backfill] {target_date} 저장 실패: {e}")
