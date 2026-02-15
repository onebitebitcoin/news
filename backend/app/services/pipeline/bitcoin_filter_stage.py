"""비트코인 전용 필터링 스테이지 - 광고/알트코인/노이즈 제외"""

import logging
import re
from typing import Set

from app.services.pipeline.base_stage import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)

# 비트코인 전용 소스 (필터링 스킵)
BITCOIN_ONLY_SOURCES = {
    "bitcoinmagazine",
    "optech",
    "theminermag",
}

# 통과 필수 키워드 후보
BITCOIN_KEYWORDS = {
    "bitcoin",
    "btc",
    "비트코인",
    "satoshi",
    "사토시",
    "lightning",
    "lightning network",
    "라이트닝",
    "라이트닝 네트워크",
    "halving",
    "halvening",
    "반감기",
    "mempool",
    "hashrate",
    "hash rate",
    "채굴",
    "mining",
    "miner",
    "utxo",
    "taproot",
    "segwit",
    "ordinals",
    "inscriptions",
    "brc-20",
    "bitcoin core",
    "비트코인 코어",
}

# 제외 키워드 (알트코인 중심)
ALTCOIN_KEYWORDS = {
    "ethereum",
    "eth",
    "solana",
    "sol",
    "cardano",
    "ada",
    "xrp",
    "ripple",
    "dogecoin",
    "doge",
    "shiba",
    "polkadot",
    "dot",
    "avalanche",
    "avax",
    "polygon",
    "matic",
    "chainlink",
    "link",
    "litecoin",
    "ltc",
    "tron",
    "trx",
    "cosmos",
    "atom",
    "near",
    "sui",
    "aptos",
    "apt",
    "arbitrum",
    "arb",
    "optimism",
    "op token",
    "altcoin",
    "altcoins",
    "알트코인",
    "이더리움",
    "솔라나",
    "리플",
    "도지코인",
    "defi",
    "nft",
    "nfts",
    "airdrop",
    "ico",
    "ido",
    "meme coin",
    "memecoin",
    "밈코인",
}

# 광고/도박성 키워드
AD_SPAM_KEYWORDS = {
    "casino",
    "casinos",
    "betting",
    "gambling",
    "sportsbook",
    "slot",
    "jackpot",
    "poker",
    "promo code",
    "bonus code",
    "가입코드",
    "추천코드",
    "먹튀",
}

ASCII_WORD_RE = re.compile(r"^[a-z0-9][a-z0-9\s\-]*$")


def _keyword_hits(text: str, keywords: set[str]) -> Set[str]:
    """텍스트 내 매칭된 키워드 집합 반환"""
    normalized = f" {text.lower()} "
    hits: set[str] = set()

    for kw in keywords:
        key = kw.strip().lower()
        if not key:
            continue

        if ASCII_WORD_RE.match(key):
            pattern = rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                hits.add(key)
            continue

        if key in normalized:
            hits.add(key)

    return hits


def is_bitcoin_related(
    title: str,
    summary: str,
    source_name: str,
    source_ref: str = "",
    url: str = "",
) -> bool:
    """규칙 기반 비트코인 기사 여부 판별"""
    if source_name in BITCOIN_ONLY_SOURCES:
        return True

    combined = f"{title} {summary} {source_ref} {url}"

    btc_hits = _keyword_hits(combined, BITCOIN_KEYWORDS)
    alt_hits = _keyword_hits(combined, ALTCOIN_KEYWORDS)
    ad_hits = _keyword_hits(combined, AD_SPAM_KEYWORDS)

    # 광고/도박성 키워드는 즉시 제외
    if ad_hits:
        return False

    # 비트코인 키워드가 없으면 제외
    if not btc_hits:
        return False

    # 알트코인 신호가 비트코인보다 강하면 제외
    if alt_hits and len(alt_hits) >= len(btc_hits):
        return False

    return True


class BitcoinFilterStage(PipelineStage):
    """규칙 기반 비트코인 기사 필터링 (Do One Thing)"""

    def process(self, context: PipelineContext) -> PipelineContext:
        if context.source_name in BITCOIN_ONLY_SOURCES:
            return context

        new_items = []

        for item_data in context.items:
            title = item_data.get("title", "")
            summary = item_data.get("summary", "")
            source_ref = item_data.get("source_ref", "")
            url = item_data.get("url", "")

            if is_bitcoin_related(title, summary, context.source_name, source_ref, url):
                new_items.append(item_data)
            else:
                context.filtered += 1
                logger.debug(
                    f"[{context.source_name}] Filtered (rules): {title[:80]}"
                )

        if context.filtered > 0:
            logger.info(
                f"[{context.source_name}] {len(new_items)} items passed "
                f"(filtered {context.filtered} by rules)"
            )

        context.items = new_items
        return context
