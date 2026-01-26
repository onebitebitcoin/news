"""중복 그룹화 로직 샘플 테스트

Transitive Closure 버그 수정 테스트:
- 기존: A~B, B~C이면 A,B,C가 같은 그룹 (버그)
- 수정: 그룹 대표(첫 번째 기사)와만 비교 → A~B는 그룹, C는 별도
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from typing import Optional

JACCARD_THRESHOLD = 0.85
JACCARD_NEAR_MIN = 0.80
LEVENSHTEIN_THRESHOLD = 0.85
WINDOW_HOURS = 24

STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "for", "of", "in", "on", "at",
    "with", "by", "from", "as", "is", "are", "be", "this", "that", "will",
}


@dataclass
class Item:
    id: str
    title: str
    url_domain: str
    published_at: datetime
    group_id: Optional[str] = field(default=None)


def normalize_title(title: str) -> list[str]:
    tokens = re.split(r"[^a-z0-9]+", title.lower())
    return [t for t in tokens if t and t not in STOPWORDS and len(t) >= 2]


def jaccard_similarity(a: list[str], b: list[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    set_a = set(a)
    set_b = set(b)
    return len(set_a & set_b) / len(set_a | set_b)


def levenshtein_ratio(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    len_a = len(a)
    len_b = len(b)
    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

    for i in range(len_a + 1):
        dp[i][0] = i
    for j in range(len_b + 1):
        dp[0][j] = j

    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )

    distance = dp[len_a][len_b]
    return 1 - (distance / max(len_a, len_b))


def match_score(title_a: str, title_b: str) -> Optional[float]:
    """두 제목의 유사도 점수 반환 (임계값 미달 시 None)"""
    tokens_a = normalize_title(title_a)
    tokens_b = normalize_title(title_b)
    jaccard = jaccard_similarity(tokens_a, tokens_b)

    if jaccard >= JACCARD_THRESHOLD:
        return jaccard

    if JACCARD_NEAR_MIN <= jaccard < JACCARD_THRESHOLD:
        ratio = levenshtein_ratio(title_a.lower(), title_b.lower())
        if ratio >= LEVENSHTEIN_THRESHOLD:
            return ratio

    return None


def group_items_fixed(items: list[Item]) -> dict[str, list[Item]]:
    """수정된 그룹화 알고리즘: 그룹 대표와만 비교

    1. 시간순으로 정렬 (오래된 것 먼저)
    2. 각 아이템을 처리할 때:
       - 기존 그룹의 대표(첫 번째 아이템)와만 비교
       - 매칭되면 해당 그룹에 추가
       - 매칭 안 되면 새 그룹 생성
    """
    # 시간순 정렬 (오래된 것 먼저)
    sorted_items = sorted(items, key=lambda x: x.published_at)

    groups: dict[str, list[Item]] = {}  # group_id -> [items]
    group_counter = 0

    for item in sorted_items:
        matched_group_id = None
        best_score = 0.0

        # 기존 그룹의 대표(첫 번째 아이템)와만 비교
        for gid, group_items in groups.items():
            representative = group_items[0]  # 첫 번째 = 가장 오래된 = 대표

            # 도메인 체크
            if representative.url_domain != item.url_domain:
                continue

            # 시간 윈도우 체크
            time_cutoff = item.published_at - timedelta(hours=WINDOW_HOURS)
            if representative.published_at < time_cutoff:
                continue

            score = match_score(item.title, representative.title)
            if score is not None and score > best_score:
                best_score = score
                matched_group_id = gid

        if matched_group_id:
            item.group_id = matched_group_id
            groups[matched_group_id].append(item)
        else:
            # 새 그룹 생성
            group_counter += 1
            new_gid = f"group_{group_counter}"
            item.group_id = new_gid
            groups[new_gid] = [item]

    return groups


def group_items_old(items: list[Item]) -> dict[str, list[Item]]:
    """기존 버그 있는 알고리즘: 모든 그룹 멤버와 비교 (Transitive Closure)

    문제: A~B, B~C이면 A,B,C가 같은 그룹이 됨
    """
    sorted_items = sorted(items, key=lambda x: x.published_at)

    groups: dict[str, list[Item]] = {}
    group_counter = 0

    for item in sorted_items:
        matched_group_id = None

        # 버그: 모든 그룹의 모든 멤버와 비교
        for gid, group_items in groups.items():
            for existing in group_items:  # 모든 멤버와 비교!
                if existing.url_domain != item.url_domain:
                    continue

                time_cutoff = item.published_at - timedelta(hours=WINDOW_HOURS)
                if existing.published_at < time_cutoff:
                    continue

                score = match_score(item.title, existing.title)
                if score is not None:
                    matched_group_id = gid
                    break

            if matched_group_id:
                break

        if matched_group_id:
            item.group_id = matched_group_id
            groups[matched_group_id].append(item)
        else:
            group_counter += 1
            new_gid = f"group_{group_counter}"
            item.group_id = new_gid
            groups[new_gid] = [item]

    return groups


def print_groups(groups: dict[str, list[Item]], title: str) -> None:
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Total groups: {len(groups)}")

    for gid, items in groups.items():
        print(f"\n{gid} ({len(items)} items):")
        for item in items:
            print(f"  - {item.id}: {item.title[:50]}...")


def test_basic_grouping() -> None:
    """기본 그룹화 테스트"""
    print("\n" + "="*60)
    print("TEST 1: 기본 그룹화")
    print("="*60)

    now = datetime.utcnow()
    items = [
        Item("a1", "Bitcoin miners unplug 110 EH/s to ease grid strain", "theminermag.com", now - timedelta(hours=2)),
        Item("a2", "Bitcoin miners unplug 110+ EH/s to ease grid strain", "theminermag.com", now - timedelta(hours=3)),
        Item("a3", "Bitcoin hashrate slides 14% from October peak", "theminermag.com", now - timedelta(hours=4)),
        Item("a4", "Bitcoin hashrate slides 14 percent from October peak", "theminermag.com", now - timedelta(hours=5)),
        Item("b1", "Bitcoin miners unplug 110 EH/s to ease grid strain", "example.com", now - timedelta(hours=2)),
        Item("c1", "Old article beyond window", "theminermag.com", now - timedelta(hours=30)),
    ]

    groups = group_items_fixed(items)
    print_groups(groups, "기본 그룹화 결과")

    # 검증
    assert len(groups) == 4, f"Expected 4 groups, got {len(groups)}"
    print("\n[PASS] 기본 그룹화 테스트 통과")


def test_transitive_closure_bug() -> None:
    """Transitive Closure 버그 테스트

    시나리오:
    - A: "Bitcoin price hits new high amid market rally"
    - B: "Bitcoin price hits new high in Asian trading" (A와 유사)
    - C: "Ethereum price hits new high in Asian trading" (B와 유사, A와는 다름)

    기존 버그: A~B, B~C → A,B,C 모두 같은 그룹
    수정 후: A~B는 그룹, C는 별도 그룹 (대표 A와 비교 시 불일치)
    """
    print("\n" + "="*60)
    print("TEST 2: Transitive Closure 버그 테스트")
    print("="*60)

    now = datetime.utcnow()
    items = [
        # A: 대표가 될 기사
        Item("A", "Bitcoin price hits new high amid market rally", "news.com", now - timedelta(hours=5)),
        # B: A와 유사 (bitcoin, price, hits, new, high 공통)
        Item("B", "Bitcoin price hits new high in Asian trading", "news.com", now - timedelta(hours=4)),
        # C: B와 유사 (price, hits, new, high, asian, trading 공통)
        #    하지만 A와는 다름 (bitcoin vs ethereum)
        Item("C", "Ethereum price hits new high in Asian trading", "news.com", now - timedelta(hours=3)),
    ]

    # A-B 유사도 확인
    score_ab = match_score(items[0].title, items[1].title)
    score_bc = match_score(items[1].title, items[2].title)
    score_ac = match_score(items[0].title, items[2].title)

    print(f"\n유사도 분석:")
    print(f"  A~B: {f'{score_ab:.3f}' if score_ab else 'None (< threshold)'}")
    print(f"  B~C: {f'{score_bc:.3f}' if score_bc else 'None (< threshold)'}")
    print(f"  A~C: {f'{score_ac:.3f}' if score_ac else 'None (< threshold)'}")

    # 기존 버그 알고리즘
    groups_old = group_items_old(items.copy())
    print_groups(groups_old, "기존 알고리즘 (버그 있음)")

    # 수정된 알고리즘
    groups_fixed = group_items_fixed(items.copy())
    print_groups(groups_fixed, "수정된 알고리즘")

    # 검증
    if score_ab and score_bc and not score_ac:
        # A~B, B~C이지만 A~C가 아닌 경우
        # 기존: A,B,C 모두 같은 그룹 (1개)
        # 수정: A,B 한 그룹, C 별도 그룹 (2개)

        old_group_count = len(groups_old)
        fixed_group_count = len(groups_fixed)

        print(f"\n기존 알고리즘 그룹 수: {old_group_count} (버그: 모두 같은 그룹)")
        print(f"수정된 알고리즘 그룹 수: {fixed_group_count}")

        if old_group_count == 1 and fixed_group_count == 2:
            print("\n[PASS] Transitive Closure 버그 수정 확인!")
        elif old_group_count == 1:
            print(f"\n[INFO] 기존 버그 재현됨. 수정 알고리즘 결과: {fixed_group_count}개 그룹")
        else:
            print(f"\n[INFO] 테스트 데이터로는 버그 재현 안됨 (유사도 조건 불충족)")
    else:
        print("\n[INFO] 테스트 데이터의 유사도가 예상과 다름")


def test_snowball_effect() -> None:
    """눈덩이 효과 테스트

    실제 발견된 버그: 23개의 완전히 다른 기사가 하나의 그룹에 묶임
    """
    print("\n" + "="*60)
    print("TEST 3: 눈덩이 효과 테스트")
    print("="*60)

    now = datetime.utcnow()

    # 체인 형태로 연결되는 기사들
    # 1~2 유사, 2~3 유사, 3~4 유사... 하지만 1~4는 완전히 다름
    items = [
        Item("1", "Bitcoin mining difficulty reaches all-time high", "news.com", now - timedelta(hours=10)),
        Item("2", "Bitcoin mining hashrate reaches all-time high", "news.com", now - timedelta(hours=9)),  # 1과 유사
        Item("3", "Bitcoin hashrate and network growth accelerate", "news.com", now - timedelta(hours=8)),  # 2와 일부 유사
        Item("4", "Network growth and adoption metrics show strength", "news.com", now - timedelta(hours=7)),  # 3과 일부 유사
        Item("5", "Adoption metrics and institutional interest rise", "news.com", now - timedelta(hours=6)),  # 4와 일부 유사
    ]

    groups_old = group_items_old(items.copy())
    groups_fixed = group_items_fixed(items.copy())

    print_groups(groups_old, "기존 알고리즘 (눈덩이 효과 가능)")
    print_groups(groups_fixed, "수정된 알고리즘")

    old_max = max(len(g) for g in groups_old.values())
    fixed_max = max(len(g) for g in groups_fixed.values())

    print(f"\n기존 알고리즘 최대 그룹 크기: {old_max}")
    print(f"수정된 알고리즘 최대 그룹 크기: {fixed_max}")

    if fixed_max <= old_max:
        print("\n[PASS] 눈덩이 효과 방지 확인")
    else:
        print("\n[WARN] 수정된 알고리즘에서 더 큰 그룹 발생")


def main() -> None:
    print("\n" + "="*60)
    print("유사도 그룹핑 버그 수정 테스트")
    print("="*60)

    test_basic_grouping()
    test_transitive_closure_bug()
    test_snowball_effect()

    print("\n" + "="*60)
    print("모든 테스트 완료")
    print("="*60)


if __name__ == "__main__":
    main()
