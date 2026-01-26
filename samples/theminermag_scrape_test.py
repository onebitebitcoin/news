"""The Miner Mag 뉴스 스크래핑 샘플"""

import asyncio
import os

from app.services.sources.theminermag import TheMinerMagFetcher


async def main() -> None:
    os.environ.setdefault("THEMINERMAG_MAX_PAGES", "2")

    fetcher = TheMinerMagFetcher(hours_limit=72)
    items = await fetcher.fetch()

    print(f"Fetched items: {len(items)}")
    for item in items[:5]:
        print(
            "-",
            item["title"],
            "|",
            item["published_at"],
            "|",
            item["url"],
        )


if __name__ == "__main__":
    asyncio.run(main())
