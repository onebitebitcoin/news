"""CoinDesk RSS Fetcher"""

from .base_fetcher import BaseFetcher


class CoinDeskFetcher(BaseFetcher):
    """CoinDesk RSS Fetcher"""

    source_name = "coindesk"
    source_ref = "CoinDesk"
    feed_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
