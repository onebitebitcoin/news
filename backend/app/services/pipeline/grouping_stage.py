"""그룹화 스테이지"""

import logging

from app.services.dedup_group_service import DedupGroupService
from app.services.pipeline.base_stage import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class GroupingStage(PipelineStage):
    """유사 기사 그룹화 (Do One Thing)"""

    def __init__(self):
        self.dedup_group = DedupGroupService()

    def process(self, context: PipelineContext) -> PipelineContext:
        """각 아이템에 그룹 ID 할당"""
        for item_data in context.items:
            self.dedup_group.assign_group_id(context.db, item_data)

        return context
