"""CoinDesk Korea RSS Fetcher"""

from .base_fetcher import BaseFetcher


class CoinDeskKoreaFetcher(BaseFetcher):
    """코인데스크 코리아 RSS Fetcher (한국어 소스)"""

    source_name = "coindeskkorea"
    source_ref = "코인데스크코리아"
    feed_url = "https://www.coindeskkorea.com/feed/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
