"""유사도 서비스 테스트"""

from app.services.similarity_service import SimilarityService


def test_normalize_title_supports_korean_tokens():
    service = SimilarityService()
    tokens = service.normalize_title("비트코인 가격 급등, 채굴 난이도 상승")
    assert "비트코인" in tokens
    assert "채굴" in tokens


def test_jaccard_similarity_empty_tokens_returns_zero():
    assert SimilarityService.jaccard_similarity([], []) == 0.0


def test_token_overlap_count():
    service = SimilarityService()
    overlap = service.token_overlap_count(
        "Bitcoin ETF inflows surge as institutions buy dip",
        "Bitcoin ETF inflows surge after institutions buy the dip",
    )
    assert overlap >= 5
