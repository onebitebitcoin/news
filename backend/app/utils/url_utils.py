"""URL 정규화 및 해시 유틸리티"""

import hashlib
from urllib.parse import parse_qs, urlencode, urlparse

# 제거할 트래킹 파라미터 (DedupService + BaseFetcher 통합 목록)
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content",
    "utm_term", "ref", "source", "fbclid", "gclid", "mc_cid",
    "mc_eid", "__s", "s_kwcid",
}


def normalize_url(url: str) -> str:
    """URL 정규화 - 트래킹 파라미터 제거"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    filtered_params = {
        k: v for k, v in query_params.items()
        if k.lower() not in TRACKING_PARAMS
    }

    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if filtered_params:
        new_query = urlencode(filtered_params, doseq=True)
        if new_query:
            normalized += f"?{new_query}"

    return normalized.rstrip("/")


def create_url_hash(url: str) -> str:
    """URL의 SHA256 해시 생성 (앞 16자리)"""
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
