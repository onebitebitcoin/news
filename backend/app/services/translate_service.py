"""GPT-5-mini 기반 번역 서비스"""

import json
import logging
import os
import re
import time

from openai import OpenAI

logger = logging.getLogger(__name__)


class TranslateService:
    """GPT-5-mini를 사용한 번역 서비스"""

    # 배치 번역 시 최대 아이템 수 (토큰 제한 고려)
    BATCH_SIZE = 15

    # 재시도 설정
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 2  # seconds

    # 한글 유니코드 범위 정규식
    KOREAN_PATTERN = re.compile(r"[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]")

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, translation disabled")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5-mini"

    @classmethod
    def is_korean_text(cls, text: str) -> bool:
        """텍스트에 한글이 포함되어 있는지 확인"""
        if not text:
            return False
        return bool(cls.KOREAN_PATTERN.search(text))

    @classmethod
    def is_translated(cls, item: dict) -> bool:
        """아이템이 제대로 번역되었는지 검증

        Args:
            item: {"title": ..., "summary": ..., ...}

        Returns:
            번역 성공 여부
        """
        title = item.get("title", "")
        # 제목에 한글이 포함되어 있으면 번역 성공으로 간주
        return cls.is_korean_text(title)

    def translate_to_korean(
        self,
        title: str,
        summary: str = ""
    ) -> tuple[str, str]:
        """제목과 요약을 한국어로 번역 (단일 아이템용)

        Args:
            title: 원본 제목
            summary: 원본 요약

        Returns:
            (번역된 제목, 번역된 요약) 튜플
        """
        if not self.client:
            logger.debug("Translation skipped - no API key")
            return title, summary

        try:
            prompt = self._build_prompt(title, summary)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional translator specializing in "
                            "cryptocurrency and Bitcoin news. Translate the given "
                            "English text to Korean. Keep technical terms in English "
                            "if commonly used (e.g., Bitcoin, ETF, Lightning Network). "
                            "Be concise and natural."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=500,
            )

            result = response.choices[0].message.content
            return self._parse_response(result, title, summary)

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return title, summary

    def _build_prompt(self, title: str, summary: str) -> str:
        """단일 아이템 번역 프롬프트 생성"""
        payload = {
            "title": title,
            "summary": summary,
        }
        return (
            "Translate the following Bitcoin news to Korean.\n\n"
            "Input (JSON):\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
            "Output (JSON):\n"
            '{ "title": "Korean title", "summary": "Korean summary" }\n\n'
            "IMPORTANT: Return ONLY JSON."
        )

    def _parse_response(
        self,
        response: str,
        original_title: str,
        original_summary: str
    ) -> tuple[str, str]:
        """단일 응답 파싱"""
        translated_title = original_title
        translated_summary = original_summary

        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if len(lines) >= 3:
                cleaned = "\n".join(lines[1:-1]).strip()

        # JSON 응답 우선 파싱
        try:
            data = json.loads(cleaned)
            if isinstance(data, list) and data:
                data = data[0]
            if isinstance(data, dict):
                title_val = data.get("title")
                summary_val = data.get("summary")
                if isinstance(title_val, str) and title_val.strip():
                    translated_title = title_val.strip()
                if isinstance(summary_val, str):
                    translated_summary = summary_val.strip()
                return translated_title, translated_summary
        except json.JSONDecodeError:
            pass

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:") or line.startswith("제목:"):
                translated_title = line.split(":", 1)[1].strip()
            elif line.startswith("SUMMARY:") or line.startswith("요약:"):
                translated_summary = line.split(":", 1)[1].strip()

        # 비정형 응답 fallback: 첫 줄 제목, 나머지 요약
        if translated_title == original_title and lines:
            first_line = lines[0].strip()
            if first_line:
                translated_title = first_line
            if original_summary and len(lines) > 1:
                translated_summary = " ".join(line.strip() for line in lines[1:] if line.strip())

        return translated_title, translated_summary

    def translate_batch_sync(self, items: list[dict]) -> list[dict]:
        """여러 아이템을 한 번의 API 호출로 일괄 번역 (동기)

        Args:
            items: [{"id": ..., "title": ..., "summary": ...}, ...]

        Returns:
            번역된 아이템 리스트 (각 아이템에 _translated 플래그 포함)
        """
        if not self.client or not items:
            # API 키가 없으면 번역 실패로 마킹
            for item in items:
                item["_translated"] = False
            return items

        # 배치 크기로 나누어 처리
        all_translated = []
        for i in range(0, len(items), self.BATCH_SIZE):
            batch = items[i:i + self.BATCH_SIZE]
            translated_batch = self._translate_single_batch(batch)
            all_translated.extend(translated_batch)

        # 번역 성공/실패 통계
        success_count = sum(1 for item in all_translated if item.get("_translated", False))
        fail_count = len(all_translated) - success_count

        logger.info(
            f"Batch translation complete: {success_count} success, {fail_count} failed "
            f"in {(len(items) + self.BATCH_SIZE - 1) // self.BATCH_SIZE} API calls"
        )

        if fail_count > 0:
            failed_items = [item.get("id", "unknown") for item in all_translated if not item.get("_translated", False)]
            logger.warning(f"Translation failed for items: {failed_items[:5]}...")

        return all_translated

    def translate_single_item(self, item: dict) -> dict:
        """단일 아이템 번역 (배치 실패 후 개별 재시도용)

        Args:
            item: {"id": ..., "title": ..., "summary": ...}

        Returns:
            _translated 플래그가 포함된 아이템
        """
        title = item.get("title", "")
        summary = item.get("summary", "")

        translated_title, translated_summary = self.translate_to_korean(title, summary)
        item["title"] = translated_title
        item["summary"] = translated_summary
        item["_translated"] = self.is_korean_text(translated_title)

        return item

    def _translate_single_batch(self, batch: list[dict]) -> list[dict]:
        """단일 배치 번역 (한 번의 API 호출, 최대 3회 재시도)"""
        last_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                prompt = self._build_batch_prompt(batch)

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional translator specializing in "
                                "cryptocurrency and Bitcoin news. Translate the given "
                                "English texts to Korean. Keep technical terms in English "
                                "if commonly used (e.g., Bitcoin, ETF, Lightning Network). "
                                "Be concise and natural. "
                                "IMPORTANT: Return ONLY valid JSON array, no other text."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_completion_tokens=4000,
                )

                result = response.choices[0].message.content
                return self._parse_batch_response(result, batch)

            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        f"Batch translation attempt {attempt}/{self.MAX_RETRIES} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)

        logger.error(f"Batch translation failed after {self.MAX_RETRIES} attempts: {last_error}")
        for item in batch:
            item["_translated"] = False
        return batch

    def _build_batch_prompt(self, items: list[dict]) -> str:
        """배치 번역 프롬프트 생성"""
        # 입력 데이터 구성
        input_items = []
        for item in items:
            input_items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "summary": item.get("summary", "")[:200]  # 요약은 200자로 제한
            })

        prompt = (
            "Translate the following Bitcoin/crypto news items to Korean.\n\n"
            "Input (JSON array):\n"
            f"{json.dumps(input_items, ensure_ascii=False, indent=2)}\n\n"
            "Output format (JSON array with same structure):\n"
            "[\n"
            '  {"id": "same_id", "title": "Korean title", "summary": "Korean summary"},\n'
            "  ...\n"
            "]\n\n"
            "IMPORTANT: Return ONLY the JSON array, no explanation or markdown."
        )
        return prompt

    def _parse_batch_response(
        self,
        response: str,
        original_items: list[dict]
    ) -> list[dict]:
        """배치 응답 파싱 및 번역 검증"""
        try:
            # JSON 파싱 시도
            response = response.strip()
            # 마크다운 코드 블록 제거
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            translated = json.loads(response)

            # ID 기반으로 매핑
            translated_map = {item["id"]: item for item in translated}

            result = []
            for original in original_items:
                item_id = original.get("id", "")
                original_title = original.get("title", "")

                if item_id in translated_map:
                    translated_item = translated_map[item_id]
                    new_title = translated_item.get("title", original_title)
                    new_summary = translated_item.get("summary", original.get("summary", ""))

                    original["title"] = new_title
                    original["summary"] = new_summary

                    # 번역 성공 여부 검증: 한글이 포함되어 있는지 확인
                    original["_translated"] = self.is_korean_text(new_title)

                    if not original["_translated"]:
                        logger.warning(
                            f"Translation validation failed for {item_id}: "
                            f"no Korean in title '{new_title[:50]}...'"
                        )
                else:
                    # 번역 결과에 없는 아이템은 실패로 마킹
                    original["_translated"] = False
                    logger.warning(f"Translation missing for {item_id}")

                result.append(original)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse batch response: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            # 파싱 실패 시 모든 아이템 번역 실패로 마킹
            for item in original_items:
                item["_translated"] = False
            return original_items

    async def translate_batch(self, items: list[dict]) -> list[dict]:
        """여러 아이템 일괄 번역 (비동기 - 동기 메서드 호출)

        Args:
            items: [{"id": ..., "title": ..., "summary": ...}, ...]

        Returns:
            번역된 아이템 리스트
        """
        return self.translate_batch_sync(items)
