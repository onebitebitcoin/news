"""비트코인 필터 규칙 테스트"""

from app.services.pipeline.bitcoin_filter_stage import is_bitcoin_related


def test_allows_bitcoin_focused_article():
    assert is_bitcoin_related(
        title="Bitcoin hashrate reaches all-time high",
        summary="Miners continue expanding capacity.",
        source_name="googlenews",
    )


def test_filters_altcoin_only_article():
    assert not is_bitcoin_related(
        title="Ethereum price surges after ETF rumors",
        summary="ETH leads the altcoin rally.",
        source_name="googlenews",
    )


def test_filters_gambling_article():
    assert not is_bitcoin_related(
        title="Top Bitcoin casino bonus for 2026",
        summary="Best betting sites with promo code",
        source_name="googlenews",
    )


def test_filters_mixed_article_when_altcoin_signal_is_strong():
    assert not is_bitcoin_related(
        title="Better crypto buy: Bitcoin vs XRP",
        summary="Investors compare bitcoin, xrp, and ripple upside.",
        source_name="googlenews",
    )


def test_bitcoin_only_source_is_allowed():
    assert is_bitcoin_related(
        title="Weekly digest",
        summary="General market recap",
        source_name="bitcoinmagazine",
    )
