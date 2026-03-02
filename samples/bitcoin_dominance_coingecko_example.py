"""CoinGecko 무료 API로 BTC 도미넌스 조회 샘플"""

from __future__ import annotations

import asyncio
import os

import httpx
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv(".env")
    api_key = os.getenv("COIN_GECKO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("COIN_GECKO_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.coingecko.com/api/v3/global",
            headers={"x-cg-demo-api-key": api_key},
        )
        response.raise_for_status()
        data = response.json().get("data") or {}
        dominance = data.get("market_cap_percentage", {}).get("btc")
        print({"bitcoin_dominance": dominance})


if __name__ == "__main__":
    asyncio.run(main())
