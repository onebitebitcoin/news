"""Decrypt RSS Fetcher"""

from .base_fetcher import BaseFetcher


class DecryptFetcher(BaseFetcher):
    """Decrypt RSS Fetcher"""

    source_name = "decrypt"
    source_ref = "Decrypt"
    feed_url = "https://decrypt.co/feed"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
