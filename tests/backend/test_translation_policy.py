from __future__ import annotations

import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.models.feed_item import FeedItem
from app.services.pipeline.base_stage import PipelineContext
from app.services.pipeline.persist_stage import PersistStage
from app.services.pipeline.translate_stage import TranslateStage
from app.services.translate_service import TranslateService


class _DummyTranslator:
    def __init__(self):
        self.client = object()

    def translate_batch_sync(self, items):
        for item in items:
            item["title"] = f"한글 {item['title']}"
            item["summary"] = "번역 요약"
            item["_translated"] = True
        return items

    def translate_single_item(self, item):
        item["title"] = f"한글 {item['title']}"
        item["_translated"] = True
        return item


@pytest.mark.asyncio
async def test_translate_stage_marks_non_korean_failed_when_translator_unavailable(db):
    stage = TranslateStage(translator=None)
    context = PipelineContext(
        db=db,
        source_name="googlenews",
        translation_required=True,
        items=[
            {"id": "ko-1", "title": "비트코인 상승", "summary": "요약"},
            {"id": "en-1", "title": "Bitcoin rallies again", "summary": "summary"},
        ],
    )

    result = await stage.process(context)

    ko_item = next(item for item in result.items if item["id"] == "ko-1")
    en_item = next(item for item in result.items if item["id"] == "en-1")
    assert ko_item["translation_status"] == "skipped"
    assert en_item["translation_status"] == "failed"
    assert result.translation_failed == 1


def test_persist_stage_drops_failed_items_when_translation_required(db):
    stage = PersistStage()
    now = datetime.utcnow()
    context = PipelineContext(
        db=db,
        source_name="googlenews",
        translation_required=True,
        items=[
            {
                "id": "drop-1",
                "source": "googlenews",
                "title": "English title",
                "summary": "summary",
                "url": "https://example.com/drop-1",
                "published_at": now,
                "translation_status": "failed",
                "raw": {},
            },
            {
                "id": "save-1",
                "source": "googlenews",
                "title": "비트코인 기사",
                "summary": "요약",
                "url": "https://example.com/save-1",
                "published_at": now,
                "translation_status": "ok",
                "raw": {},
            },
        ],
    )

    stage.process(context)

    saved = db.query(FeedItem).all()
    assert len(saved) == 1
    assert saved[0].id == "save-1"
    assert context.translation_dropped == 1


def test_manual_article_translates_english_title(client, monkeypatch):
    def fake_init(self):
        self.client = object()
        self.model = "gpt-5-mini"

    def fake_translate(self, title, summary=""):
        return "비트코인 급등", "한국어 요약"

    monkeypatch.setattr(TranslateService, "__init__", fake_init)
    monkeypatch.setattr(TranslateService, "translate_to_korean", fake_translate)

    response = client.post(
        "/api/v1/feed/manual",
        json={
            "url": "https://example.com/manual-english",
            "title": "Bitcoin surges",
            "summary": "Bitcoin jumped 5 percent",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "비트코인 급등"
    assert data["translation_status"] == "ok"


def test_manual_article_rejects_english_without_api_key(client, monkeypatch):
    def fake_init(self):
        self.client = None
        self.model = "gpt-5-mini"

    monkeypatch.setattr(TranslateService, "__init__", fake_init)

    response = client.post(
        "/api/v1/feed/manual",
        json={
            "url": "https://example.com/manual-no-key",
            "title": "Bitcoin surges",
            "summary": "Bitcoin jumped 5 percent",
        },
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["type"] == "TranslationRequiredError"
