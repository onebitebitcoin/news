"""ResearchBitcoin MVRV Z-Score 조회 샘플

사용법:
  RESEARCHBITCOIN_API_TOKEN=... python samples/researchbitcoin_mvrv_zscore_example.py

개발 환경에서는 루트 .env에 토큰을 넣고 실행 전에 export 해주세요.
운영 환경에서는 Railway 환경변수에 동일 키를 설정합니다.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


API_URL = "https://api.researchbitcoin.net/api/v1/metrics/timeseries"


def main() -> int:
    token = os.getenv("RESEARCHBITCOIN_API_TOKEN", "").strip()
    if not token:
        print("RESEARCHBITCOIN_API_TOKEN 환경변수가 필요합니다.", file=sys.stderr)
        return 1

    params = urllib.parse.urlencode(
        {
            "metric_category": "onchain_valuation",
            "metrics": "market_value_to_realized_value",
            "data_fields": "mvrv_z_score",
            "interval": "10m",
            "limit": 1,
        }
    )
    req = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-API-Key": token,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            payload = json.loads(body)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}", file=sys.stderr)
        try:
            print(e.read().decode("utf-8"), file=sys.stderr)
        except Exception:
            pass
        return 2
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 3

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    rows = payload.get("data") or []
    if not rows:
        print("응답 data가 비어 있습니다.", file=sys.stderr)
        return 4

    values = rows[0].get("values") or []
    for item in values:
        if item.get("data_field") == "mvrv_z_score":
            print(f"\nMVRV Z-Score: {item.get('value')}")
            return 0

    print("mvrv_z_score 필드를 찾지 못했습니다.", file=sys.stderr)
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
