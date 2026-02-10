"""비트코인 전용 필터링 스테이지 - 알트코인 전용 기사 제외"""

import logging

from app.services.pipeline.base_stage import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)

# 비트코인 전용 소스 (필터링 스킵)
BITCOIN_ONLY_SOURCES = {
    "bitcoinmagazine",
    "optech",
    "theminermag",
}

# 비트코인 관련 키워드 (소문자)
BITCOIN_KEYWORDS = {
    "bitcoin",
    "btc",
    "satoshi",
    "lightning network",
    "halving",
    "halvening",
    "비트코인",
    "사토시",
    "라이트닝 네트워크",
    "반감기",
    "block reward",
    "mining",
    "miner",
    "hash rate",
    "hashrate",
    "difficulty adjustment",
    "mempool",
    "utxo",
    "segwit",
    "taproot",
    "ordinals",
    "inscriptions",
    "brc-20",
    "nostr",
    "sats",
}

# 알트코인 전용 키워드 (소문자)
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
    "token launch",
    "ico",
    "ido",
    "meme coin",
    "memecoin",
    "밈코인",
}


def _contains_keyword(text: str, keywords: set) -> bool:
    """텍스트에 키워드가 포함되어 있는지 확인"""
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            return True
    return False


def is_bitcoin_related(title: str, summary: str, source_name: str) -> bool:
    """비트코인 관련 기사인지 판별

    Args:
        title: 기사 제목
        summary: 기사 요약
        source_name: 소스 이름

    Returns:
        True이면 비트코인 관련 (통과), False이면 제외
    """
    # 비트코인 전용 소스는 무조건 통과
    if source_name in BITCOIN_ONLY_SOURCES:
        return True

    combined = f"{title} {summary}"

    # 비트코인 키워드가 있으면 통과
    if _contains_keyword(combined, BITCOIN_KEYWORDS):
        return True

    # 비트코인 키워드 없이 알트코인 키워드만 있으면 제외
    if _contains_keyword(combined, ALTCOIN_KEYWORDS):
        return False

    # 둘 다 없으면 일반 크립토/시장 뉴스로 통과 (crypto market, regulation 등)
    return True


class BitcoinFilterStage(PipelineStage):
    """알트코인 전용 기사 필터링 (Do One Thing)"""

    def process(self, context: PipelineContext) -> PipelineContext:
        """비트코인 관련 기사만 통과"""
        # 비트코인 전용 소스는 필터링 스킵
        if context.source_name in BITCOIN_ONLY_SOURCES:
            return context

        new_items = []

        for item_data in context.items:
            title = item_data.get("title", "")
            summary = item_data.get("summary", "")

            if is_bitcoin_related(title, summary, context.source_name):
                new_items.append(item_data)
            else:
                context.filtered += 1
                logger.debug(
                    f"[{context.source_name}] Filtered (altcoin): {title[:80]}"
                )

        if context.filtered > 0:
            logger.info(
                f"[{context.source_name}] {len(new_items)} items passed "
                f"(filtered {context.filtered} altcoin articles)"
            )

        context.items = new_items
        return context
