"""유사 기사 그룹화 서비스"""

import json
import logging
from datetime import datetime, timedelta
from typing import Iterable, Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.feed_item import FeedItem
from app.services.dedup_service import DedupService
from app.services.similarity_service import SimilarityService

logger = logging.getLogger(__name__)


class DedupGroupService:
    """제목 유사도 기반 그룹화 서비스"""

    WINDOW_HOURS = 24

    def __init__(self):
        self.similarity = SimilarityService()

    def assign_group_id(self, db: Session, item_data: dict) -> str:
        """유사도 기준 그룹 ID 할당 (그룹 대표와만 비교)

        Transitive Closure 버그 수정:
        - 기존: 모든 그룹 멤버와 비교 → A~B, B~C이면 A,B,C가 같은 그룹
        - 수정: 그룹 대표(가장 오래된 기사)와만 비교 → 눈덩이 효과 방지

        원본 영어 제목 사용:
        - 번역된 한국어 제목은 영문 토큰이 적어 잘못된 매칭 발생
        - raw["title"]에서 원본 영어 제목을 가져와 비교
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

        # 원본 영어 제목 가져오기 (번역된 제목 대신)
        original_title = self._get_original_title(item_data)

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

        # 1. 기존 그룹 대표와 비교 (원본 영어 제목 사용)
        best_score = 0.0
        best_group_id = None
        for gid, representative in group_representatives.items():
            rep_original_title = self._get_original_title_from_item(representative)
            score = self._match_score(original_title, rep_original_title)
            if score is not None and score > best_score:
                best_score = score
                best_group_id = gid
                logger.debug(
                    f"그룹 대표 매칭: '{original_title[:30]}...' ~ "
                    f"'{rep_original_title[:30]}...' (score={score:.3f}, group={gid})"
                )

        if best_group_id:
            self._set_group_id_on_raw(item_data, best_group_id)
            return best_group_id

        # 2. 그룹 없는 아이템과 비교 (새 그룹 형성)
        for candidate in ungrouped_items:
            cand_original_title = self._get_original_title_from_item(candidate)
            score = self._match_score(original_title, cand_original_title)
            if score is not None:
                # 새 그룹 생성하고 둘 다 추가
                new_group_id = self._create_group_id(item_data)
                self._set_group_id_on_raw(item_data, new_group_id)
                self._set_group_id_on_items([candidate], new_group_id)
                logger.info(
                    f"새 그룹 생성: '{original_title[:30]}...' ~ "
                    f"'{cand_original_title[:30]}...' (score={score:.3f}, group={new_group_id})"
                )
                return new_group_id

        # 3. 매칭 없으면 새 그룹 (단독)
        group_id = self._create_group_id(item_data)
        self._set_group_id_on_raw(item_data, group_id)
        return group_id

    def _get_original_title(self, item_data: dict) -> str:
        """item_data에서 원본 영어 제목 가져오기"""
        raw = item_data.get("raw")
        if isinstance(raw, str):
            raw = self._parse_raw(raw)
        elif not isinstance(raw, dict):
            raw = {}

        # raw["title"]에 원본 영어 제목이 있음
        original = raw.get("title", "")
        if original:
            return original
        # fallback: 현재 제목 사용
        return item_data.get("title", "")

    def _get_original_title_from_item(self, item: FeedItem) -> str:
        """FeedItem에서 원본 영어 제목 가져오기"""
        raw = self._parse_raw(item.raw)
        original = raw.get("title", "")
        if original:
            return original
        return item.title or ""

    def _match_score(self, title_a: str, title_b: str) -> Optional[float]:
        """SimilarityService를 사용하여 매칭 점수 계산"""
        return self.similarity.match_score(title_a, title_b)

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
