"""Cointelegraph RSS Fetcher"""

from .base_fetcher import BaseFetcher


class CointelegraphFetcher(BaseFetcher):
    """Cointelegraph RSS Fetcher"""

    source_name = "cointelegraph"
    source_ref = "Cointelegraph"
    feed_url = "https://cointelegraph.com/rss"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
