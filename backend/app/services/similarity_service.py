"""텍스트 유사도 계산 서비스 (순수 계산 로직)"""

import re
from typing import Optional


class SimilarityService:
    """텍스트 유사도 계산을 위한 순수 함수 모음"""

    STOPWORDS = {
        "a", "an", "the", "and", "or", "to", "for", "of", "in", "on", "at",
        "with", "by", "from", "as", "is", "are", "be", "this", "that", "will",
    }

    def __init__(
        self,
        jaccard_threshold: float = 0.85,
        jaccard_near_min: float = 0.80,
        levenshtein_threshold: float = 0.85,
    ):
        self.jaccard_threshold = jaccard_threshold
        self.jaccard_near_min = jaccard_near_min
        self.levenshtein_threshold = levenshtein_threshold

    def match_score(self, title_a: str, title_b: str) -> Optional[float]:
        """두 제목 간의 매칭 점수 계산

        Returns:
            유사도 점수 (임계값 이상일 때) 또는 None (유사하지 않을 때)
        """
        tokens_a = self.normalize_title(title_a)
        tokens_b = self.normalize_title(title_b)
        jaccard = self.jaccard_similarity(tokens_a, tokens_b)

        if jaccard >= self.jaccard_threshold:
            return jaccard

        if self.jaccard_near_min <= jaccard < self.jaccard_threshold:
            ratio = self.levenshtein_ratio(title_a.lower(), title_b.lower())
            if ratio >= self.levenshtein_threshold:
                return ratio

        return None

    def normalize_title(self, title: str) -> list[str]:
        """제목을 정규화하여 토큰 리스트로 변환"""
        tokens = re.split(r"[^a-z0-9]+", title.lower())
        return [
            token for token in tokens
            if token and token not in self.STOPWORDS and len(token) >= 2
        ]

    @staticmethod
    def jaccard_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
        """Jaccard 유사도 계산"""
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0

        set_a = set(tokens_a)
        set_b = set(tokens_b)
        return len(set_a & set_b) / len(set_a | set_b)

    @staticmethod
    def levenshtein_ratio(text_a: str, text_b: str) -> float:
        """Levenshtein 거리 기반 유사도 비율 계산"""
        if text_a == text_b:
            return 1.0
        if not text_a or not text_b:
            return 0.0

        len_a = len(text_a)
        len_b = len(text_b)
        dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

        for i in range(len_a + 1):
            dp[i][0] = i
        for j in range(len_b + 1):
            dp[0][j] = j

        for i in range(1, len_a + 1):
            for j in range(1, len_b + 1):
                cost = 0 if text_a[i - 1] == text_b[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost,
                )

        distance = dp[len_a][len_b]
        return 1 - (distance / max(len_a, len_b))
