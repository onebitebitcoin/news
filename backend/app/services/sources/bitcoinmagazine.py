"""Bitcoin Magazine RSS Fetcher"""

from .base_fetcher import BaseFetcher


class BitcoinMagazineFetcher(BaseFetcher):
    """Bitcoin Magazine RSS Fetcher"""

    source_name = "bitcoinmagazine"
    source_ref = "Bitcoin Magazine"
    feed_url = "https://bitcoinmagazine.com/feed"
    category = "news"
    default_tags = ["bitcoin"]
