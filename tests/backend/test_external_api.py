from datetime import datetime

from app.models.feed_item import FeedItem
from app.repositories.api_key_repository import ApiKeyRepository


def _create_api_key(db) -> str:
    repo = ApiKeyRepository(db)
    _, raw_key = repo.create("external-test-key")
    return raw_key


def _create_feed_item(db, item_id: str, source: str, title: str) -> None:
    item = FeedItem(
        id=item_id,
        source=source,
        title=title,
        summary=f"{title} summary",
        url=f"https://example.com/{item_id}",
        category="Market",
        published_at=datetime.utcnow(),
        fetched_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()


def test_external_articles_filter_mode_manual(client, db):
    api_key = _create_api_key(db)
    _create_feed_item(db, "manual-1", "manual", "Manual Article")
    _create_feed_item(db, "auto-1", "coindesk", "Auto Article")

    response = client.get(
        "/api/v1/external/articles?mode=manual",
        headers={"X-API-Key": api_key},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    articles = payload["data"]["articles"]
    assert len(articles) == 1
    assert articles[0]["id"] == "manual-1"
    assert articles[0]["source"] == "manual"


def test_external_articles_filter_mode_auto(client, db):
    api_key = _create_api_key(db)
    _create_feed_item(db, "manual-1", "manual", "Manual Article")
    _create_feed_item(db, "auto-1", "coindesk", "Auto Article")

    response = client.get(
        "/api/v1/external/articles?mode=auto",
        headers={"X-API-Key": api_key},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    articles = payload["data"]["articles"]
    assert len(articles) == 1
    assert articles[0]["id"] == "auto-1"
    assert articles[0]["source"] == "coindesk"


def test_external_articles_filter_mode_invalid(client, db):
    api_key = _create_api_key(db)

    response = client.get(
        "/api/v1/external/articles?mode=invalid",
        headers={"X-API-Key": api_key},
    )

    assert response.status_code == 422
