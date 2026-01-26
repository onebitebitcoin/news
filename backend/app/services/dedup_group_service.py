"""유사 기사 그룹화 서비스"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Iterable, Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem
from app.services.dedup_service import DedupService

logger = logging.getLogger(__name__)


class DedupGroupService:
    """제목 유사도 기반 그룹화 서비스"""

    WINDOW_HOURS = 24
    JACCARD_THRESHOLD = 0.85
    JACCARD_NEAR_MIN = 0.80
    LEVENSHTEIN_THRESHOLD = 0.85
    STOPWORDS = {
        "a", "an", "the", "and", "or", "to", "for", "of", "in", "on", "at",
        "with", "by", "from", "as", "is", "are", "be", "this", "that", "will",
    }

    def assign_group_id(self, db: Session, item_data: dict) -> str:
        """유사도 기준 그룹 ID 할당 (그룹 대표와만 비교)

        Transitive Closure 버그 수정:
        - 기존: 모든 그룹 멤버와 비교 → A~B, B~C이면 A,B,C가 같은 그룹
        - 수정: 그룹 대표(가장 오래된 기사)와만 비교 → 눈덩이 효과 방지
        """
        title = item_data.get("title", "")
        url = item_data.get("url", "")
        published_at = item_data.get("published_at") or datetime.utcnow()
        domain = urlparse(url).netloc
        cutoff = published_at - timedelta(hours=self.WINDOW_HOURS)

        if not title or not url:
            group_id = self._create_group_id(item_data)
            self._set_group_id_on_raw(item_data, group_id)
            return group_id

        # 오래된 것 먼저 조회 (그룹 대표 식별용)
        candidates = (
            db.query(FeedItem)
            .filter(FeedItem.published_at >= cutoff)
            .order_by(FeedItem.published_at.asc())
            .all()
        )

        # 그룹별 대표 아이템 수집 (각 그룹의 첫 번째 = 가장 오래된 기사)
        group_representatives: dict[str, FeedItem] = {}
        ungrouped_items: list[FeedItem] = []

        for candidate in candidates:
            if not candidate.title or not candidate.url:
                continue
            if urlparse(candidate.url).netloc != domain:
                continue

            gid = self._get_group_id_from_item(candidate)
            if gid:
                # 그룹이 있으면 대표만 저장 (첫 번째가 가장 오래된 것)
                if gid not in group_representatives:
                    group_representatives[gid] = candidate
            else:
                # 그룹 없는 아이템
                ungrouped_items.append(candidate)

        # 1. 기존 그룹 대표와 비교
        best_score = 0.0
        best_group_id = None
        for gid, representative in group_representatives.items():
            score = self._match_score(title, representative.title)
            if score is not None and score > best_score:
                best_score = score
                best_group_id = gid
                logger.debug(
                    f"그룹 대표 매칭: '{title[:30]}...' ~ "
                    f"'{representative.title[:30]}...' (score={score:.3f}, group={gid})"
                )

        if best_group_id:
            self._set_group_id_on_raw(item_data, best_group_id)
            return best_group_id

        # 2. 그룹 없는 아이템과 비교 (새 그룹 형성)
        for candidate in ungrouped_items:
            score = self._match_score(title, candidate.title)
            if score is not None:
                # 새 그룹 생성하고 둘 다 추가
                new_group_id = self._create_group_id(item_data)
                self._set_group_id_on_raw(item_data, new_group_id)
                self._set_group_id_on_items([candidate], new_group_id)
                logger.info(
                    f"새 그룹 생성: '{title[:30]}...' ~ "
                    f"'{candidate.title[:30]}...' (score={score:.3f}, group={new_group_id})"
                )
                return new_group_id

        # 3. 매칭 없으면 새 그룹 (단독)
        group_id = self._create_group_id(item_data)
        self._set_group_id_on_raw(item_data, group_id)
        return group_id

    def _match_score(self, title_a: str, title_b: str) -> Optional[float]:
        tokens_a = self._normalize_title(title_a)
        tokens_b = self._normalize_title(title_b)
        jaccard = self._jaccard_similarity(tokens_a, tokens_b)

        if jaccard >= self.JACCARD_THRESHOLD:
            return jaccard

        if self.JACCARD_NEAR_MIN <= jaccard < self.JACCARD_THRESHOLD:
            ratio = self._levenshtein_ratio(title_a.lower(), title_b.lower())
            if ratio >= self.LEVENSHTEIN_THRESHOLD:
                return ratio

        return None

    def _normalize_title(self, title: str) -> list[str]:
        tokens = re.split(r"[^a-z0-9]+", title.lower())
        return [
            token for token in tokens
            if token and token not in self.STOPWORDS and len(token) >= 2
        ]

    @staticmethod
    def _jaccard_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0

        set_a = set(tokens_a)
        set_b = set(tokens_b)
        return len(set_a & set_b) / len(set_a | set_b)

    @staticmethod
    def _levenshtein_ratio(text_a: str, text_b: str) -> float:
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

    def _get_group_id_from_item(self, item: FeedItem) -> Optional[str]:
        raw = self._parse_raw(item.raw)
        return raw.get("dedup_group_id") if raw else None

    def _set_group_id_on_items(
        self,
        items: Iterable[FeedItem],
        group_id: str,
    ) -> None:
        for item in items:
            raw = self._parse_raw(item.raw)
            raw["dedup_group_id"] = group_id
            item.raw = json.dumps(raw)

    def _set_group_id_on_raw(self, item_data: dict, group_id: str) -> None:
        raw = item_data.get("raw")
        if isinstance(raw, str):
            raw_dict = self._parse_raw(raw)
        elif isinstance(raw, dict):
            raw_dict = raw.copy()
        else:
            raw_dict = {}

        raw_dict["dedup_group_id"] = group_id
        item_data["raw"] = raw_dict

    def _create_group_id(self, item_data: dict) -> str:
        url_hash = item_data.get("url_hash")
        if not url_hash and item_data.get("url"):
            url_hash = DedupService.create_hash(item_data["url"])
        return f"group_{url_hash or datetime.utcnow().timestamp()}"

    @staticmethod
    def _parse_raw(raw_value: Optional[str]) -> dict:
        if not raw_value:
            return {}
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            logger.warning("Failed to parse raw JSON for group id")
            return {}
