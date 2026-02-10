"""The Block RSS Fetcher"""

from .base_fetcher import BaseFetcher


class TheBlockFetcher(BaseFetcher):
    """The Block RSS Fetcher"""

    source_name = "theblock"
    source_ref = "The Block"
    feed_url = "https://www.theblock.co/rss.xml"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
