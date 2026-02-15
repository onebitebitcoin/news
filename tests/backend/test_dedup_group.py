"""중복 그룹화 서비스 테스트"""

from datetime import datetime, timedelta
import json

from app.models.feed_item import FeedItem
from app.services.dedup_group_service import DedupGroupService


def test_assign_group_id_updates_matching_items(db):
    """유사 제목 + 동일 도메인인 경우 그룹 ID가 저장된다."""
    now = datetime.utcnow()
    existing = FeedItem(
        id="existing-1",
        source="Test Source",
        title="Bitcoin miners unplug 110 EH/s to ease grid strain",
        url="https://theminermag.com/news/1",
        published_at=now - timedelta(hours=1),
        fetched_at=now - timedelta(hours=1),
        raw=json.dumps({}),
        url_hash="hash1",
    )
    db.add(existing)
    db.commit()

    service = DedupGroupService()
    item_data = {
        "id": "new-1",
        "title": "Bitcoin miners unplug 110+ EH/s to ease grid strain",
        "url": "https://theminermag.com/news/2",
        "published_at": now,
        "url_hash": "hash2",
        "raw": {},
    }

    group_id = service.assign_group_id(db, item_data)
    db.commit()

    assert group_id.startswith("group_")
    db.refresh(existing)
    raw = json.loads(existing.raw)
    assert raw.get("dedup_group_id") == group_id
    assert item_data["raw"]["dedup_group_id"] == group_id


def test_assign_group_id_skips_different_domain(db):
    """도메인이 달라도 제목이 충분히 다르면 그룹 매칭되지 않는다."""
    now = datetime.utcnow()
    existing = FeedItem(
        id="existing-2",
        source="Test Source",
        title="Bitcoin hashrate slides 14 percent from October peak",
        url="https://example.com/news/1",
        published_at=now - timedelta(hours=1),
        fetched_at=now - timedelta(hours=1),
        raw=json.dumps({}),
        url_hash="hash3",
    )
    db.add(existing)
    db.commit()

    service = DedupGroupService()
    item_data = {
        "id": "new-2",
        "title": "Bitcoin hashrate slides 14% from October peak",
        "url": "https://theminermag.com/news/3",
        "published_at": now,
        "url_hash": "hash4",
        "raw": {},
    }

    group_id = service.assign_group_id(db, item_data)
    db.commit()

    assert group_id != "group_hash3"
    raw = json.loads(existing.raw)
    assert raw.get("dedup_group_id") is None


def test_assign_group_id_matches_cross_domain_when_high_similarity(db):
    """도메인이 달라도 매우 유사하면 같은 그룹으로 묶는다."""
    now = datetime.utcnow()
    existing = FeedItem(
        id="existing-3",
        source="source-a",
        title="Bitcoin ETF inflows surge as institutions buy the dip",
        url="https://site-a.com/article/etf-inflows",
        published_at=now - timedelta(hours=2),
        fetched_at=now - timedelta(hours=2),
        raw=json.dumps({}),
        url_hash="hash5",
    )
    db.add(existing)
    db.commit()

    service = DedupGroupService()
    item_data = {
        "id": "new-3",
        "title": "Bitcoin ETF inflows surge as institutions buy dip",
        "url": "https://site-b.com/news/bitcoin-etf-inflows",
        "published_at": now,
        "url_hash": "hash6",
        "raw": {},
    }

    group_id = service.assign_group_id(db, item_data)
    db.commit()

    assert group_id.startswith("group_")
    db.refresh(existing)
    raw = json.loads(existing.raw)
    assert raw.get("dedup_group_id") == group_id
    assert item_data["raw"]["dedup_group_id"] == group_id
