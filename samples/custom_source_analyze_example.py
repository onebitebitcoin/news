"""커스텀 스크래핑 소스 분석 예제 (독립 실행용)

사용 예시:
  python samples/custom_source_analyze_example.py "Bitcoin Optech" "https://bitcoinops.org/en/newsletters/"
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

os.environ.setdefault("TESTING", "true")

from app.services.custom_source_service import CustomSourceScrapeService  # noqa: E402


async def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python samples/custom_source_analyze_example.py <name> <list_url>")
        raise SystemExit(1)

    name = sys.argv[1]
    list_url = sys.argv[2]
    service = CustomSourceScrapeService()
    result = await service.analyze(name=name, list_url=list_url)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
