"""Blockworks RSS Fetcher"""

from .base_fetcher import BaseFetcher


class BlockworksFetcher(BaseFetcher):
    """Blockworks RSS Fetcher"""

    source_name = "blockworks"
    source_ref = "Blockworks"
    feed_url = "https://blockworks.co/feed/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
