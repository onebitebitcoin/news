"""DB 저장 커스텀 스크래핑 소스 실행기"""

from __future__ import annotations

import logging
from typing import Any

from app.services.custom_source_service import CustomSourceScrapeService

logger = logging.getLogger(__name__)


class CustomScrapeRuntime:
    """커스텀 소스 설정을 사용해 기사 목록을 수집"""

    def __init__(self, config: dict[str, Any], hours_limit: int = 24):
        self.config = config
        self.hours_limit = hours_limit
        self.service = CustomSourceScrapeService()

    @property
    def source_name(self) -> str:
        return self.config["slug"]

    async def fetch(self) -> list[dict]:
        logger.info(f"[{self.source_name}] Fetching custom source from {self.config['list_url']}")
        return await self.service.fetch_items(
            source_slug=self.config["slug"],
            source_name=self.config["name"],
            list_url=self.config["list_url"],
            extraction_rules=self.config.get("extraction_rules") or {},
            hours_limit=self.hours_limit,
        )
