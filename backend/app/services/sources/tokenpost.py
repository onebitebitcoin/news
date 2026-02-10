"""Tokenpost RSS Fetcher"""

from .base_fetcher import BaseFetcher


class TokenpostFetcher(BaseFetcher):
    """토큰포스트 RSS Fetcher (한국어 소스)"""

    source_name = "tokenpost"
    source_ref = "토큰포스트"
    feed_url = "https://www.tokenpost.kr/rss"
    category = "news"
    default_tags = ["bitcoin", "crypto"]
