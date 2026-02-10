"""Bitcoin.com RSS Fetcher"""

from .base_fetcher import BaseFetcher


class BitcoinComFetcher(BaseFetcher):
    """Bitcoin.com RSS Fetcher"""

    source_name = "bitcoincom"
    source_ref = "Bitcoin.com"
    feed_url = "https://news.bitcoin.com/feed/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
