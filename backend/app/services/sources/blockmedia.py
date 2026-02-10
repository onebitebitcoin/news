"""Blockmedia RSS Fetcher"""

from .base_fetcher import BaseFetcher


class BlockmediaFetcher(BaseFetcher):
    """블록미디어 RSS Fetcher (한국어 소스)"""

    source_name = "blockmedia"
    source_ref = "블록미디어"
    feed_url = "https://www.blockmedia.co.kr/feed/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
