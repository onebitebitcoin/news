"""CryptoSlate RSS Fetcher"""

from .base_fetcher import BaseFetcher


class CryptoSlateFetcher(BaseFetcher):
    """CryptoSlate RSS Fetcher"""

    source_name = "cryptoslate"
    source_ref = "CryptoSlate"
    feed_url = "https://cryptoslate.com/feed/"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
