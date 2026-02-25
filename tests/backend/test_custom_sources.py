from datetime import datetime

import pytest

from app.services.custom_source_service import validate_public_http_url


def test_validate_public_http_url_blocks_localhost():
    with pytest.raises(ValueError):
        validate_public_http_url("http://localhost:8000/news")


def test_validate_public_http_url_allows_public_https():
    assert validate_public_http_url("https://example.com/news") == "https://example.com/news"


def test_analyze_custom_source_success(client, monkeypatch):
    from app.services.custom_source_service import CustomSourceScrapeService

    async def fake_analyze(self, *, name, list_url):  # noqa: ARG001
        return {
            "draft": {
                "slug_suggestion": "custom-optech",
                "name": name,
                "list_url": list_url,
                "fetch_mode": "scrape",
                "extraction_rules": {"strategy": "hybrid_link_discovery", "max_items": 5},
                "normalization_rules": {},
                "ai_model": "gpt-5-mini",
            },
            "preview_items": [
                {
                    "title": "Article 1",
                    "url": "https://example.com/a1",
                    "published_at": "2026-02-25T00:00:00Z",
                    "summary": "summary",
                    "image_url": None,
                }
            ],
            "warnings": [],
            "validation_errors": [],
            "is_valid": True,
        }

    monkeypatch.setattr(CustomSourceScrapeService, "analyze", fake_analyze)

    response = client.post(
        "/api/v1/admin/custom-sources/analyze",
        json={"name": "Custom Optech", "list_url": "https://example.com/news"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["draft"]["slug_suggestion"] == "custom-optech"


def test_custom_source_crud_and_feed_sources_merge(client, monkeypatch):
    from app.services.custom_source_service import CustomSourceScrapeService

    async def fake_validate_saved_config(self, *, name, list_url, extraction_rules, max_items=5):  # noqa: ARG001
        return (
            [
                {
                    "title": "Article 1",
                    "url": "https://example.com/a1",
                    "published_at": datetime.utcnow(),
                    "summary": "summary",
                    "image_url": None,
                }
            ],
            [],
        )

    monkeypatch.setattr(CustomSourceScrapeService, "validate_saved_config", fake_validate_saved_config)

    create_resp = client.post(
        "/api/v1/admin/custom-sources",
        json={
            "name": "Custom Optech",
            "slug": "custom-optech",
            "list_url": "https://example.com/news",
            "extraction_rules": {"strategy": "hybrid_link_discovery", "max_items": 5},
            "normalization_rules": {},
            "is_active": True,
            "ai_model": "gpt-5-mini",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    create_payload = create_resp.json()
    assert create_payload["success"] is True
    source_id = create_payload["data"]["id"]

    list_resp = client.get("/api/v1/admin/custom-sources")
    assert list_resp.status_code == 200
    list_payload = list_resp.json()["data"]["sources"]
    assert len(list_payload) == 1
    assert list_payload[0]["slug"] == "custom-optech"

    feed_sources_resp = client.get("/api/v1/feed/sources")
    assert feed_sources_resp.status_code == 200
    assert "custom-optech" in feed_sources_resp.json()["data"]

    toggle_resp = client.patch(f"/api/v1/admin/custom-sources/{source_id}", json={"is_active": False})
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["data"]["is_active"] is False

    feed_sources_resp = client.get("/api/v1/feed/sources")
    assert "custom-optech" not in feed_sources_resp.json()["data"]

    delete_resp = client.delete(f"/api/v1/admin/custom-sources/{source_id}")
    assert delete_resp.status_code == 200
