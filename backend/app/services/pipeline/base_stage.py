"""파이프라인 스테이지 추상 클래스"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

from sqlalchemy.orm import Session


@dataclass
class PipelineContext:
    """파이프라인 컨텍스트 - 단계 간 데이터 전달"""

    db: Session
    source_name: str
    items: List[Dict] = field(default_factory=list)

    # 통계
    fetched: int = 0
    duplicates: int = 0
    filtered: int = 0
    translation_failed: int = 0
    saved: int = 0


class PipelineStage(ABC):
    """파이프라인 스테이지 추상 클래스 (Do One Thing)"""

    @abstractmethod
    def process(self, context: PipelineContext) -> PipelineContext:
        """단계 처리

        Args:
            context: 파이프라인 컨텍스트

        Returns:
            처리된 컨텍스트
        """
        pass
