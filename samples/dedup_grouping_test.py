"""중복 그룹화 로직 샘플 테스트"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from typing import List

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


def normalize_title(title: str) -> List[str]:
    tokens = re.split(r"[^a-z0-9]+", title.lower())
    return [t for t in tokens if t and t not in STOPWORDS and len(t) >= 2]


def jaccard_similarity(a: List[str], b: List[str]) -> float:
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


def is_duplicate(candidate: Item, other: Item) -> bool:
    if candidate.url_domain != other.url_domain:
        return False

    time_cutoff = candidate.published_at - timedelta(hours=WINDOW_HOURS)
    if other.published_at < time_cutoff:
        return False

    tokens_a = normalize_title(candidate.title)
    tokens_b = normalize_title(other.title)
    jaccard = jaccard_similarity(tokens_a, tokens_b)
    if jaccard >= JACCARD_THRESHOLD:
        return True

    if JACCARD_NEAR_MIN <= jaccard < JACCARD_THRESHOLD:
        ratio = levenshtein_ratio(candidate.title.lower(), other.title.lower())
        return ratio >= LEVENSHTEIN_THRESHOLD

    return False


def group_items(items: List[Item]) -> List[List[Item]]:
    groups: List[List[Item]] = []

    for item in items:
        matched_group = None
        for group in groups:
            if any(is_duplicate(item, existing) for existing in group):
                matched_group = group
                break

        if matched_group is None:
            groups.append([item])
        else:
            matched_group.append(item)

    return groups


def main() -> None:
    now = datetime.utcnow()
    items = [
        Item("a1", "Bitcoin miners unplug 110 EH/s to ease grid strain", "theminermag.com", now - timedelta(hours=2)),
        Item("a2", "Bitcoin miners unplug 110+ EH/s to ease grid strain", "theminermag.com", now - timedelta(hours=3)),
        Item("a3", "Bitcoin hashrate slides 14% from October peak", "theminermag.com", now - timedelta(hours=4)),
        Item("a4", "Bitcoin hashrate slides 14 percent from October peak", "theminermag.com", now - timedelta(hours=5)),
        Item("b1", "Bitcoin miners unplug 110 EH/s to ease grid strain", "example.com", now - timedelta(hours=2)),
        Item("c1", "Old article beyond window", "theminermag.com", now - timedelta(hours=30)),
    ]

    groups = group_items(items)

    print(f"Total groups: {len(groups)}")
    for idx, group in enumerate(groups, start=1):
        print(f"\nGroup {idx} ({len(group)} items):")
        for item in group:
            print(f"- {item.id}: {item.title}")


if __name__ == "__main__":
    main()
