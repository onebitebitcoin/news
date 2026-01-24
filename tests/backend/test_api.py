"""Backend API 테스트"""


def test_health_check(client):
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "bitcoin-scanner-api"


def test_get_feed_empty(client):
    """빈 피드 목록 조회"""
    response = client.get("/api/v1/feed")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_feed_with_items(client, sample_feed_item):
    """피드 목록 조회 (데이터 있음)"""
    response = client.get("/api/v1/feed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "test-001"
    assert data["items"][0]["title"] == "Test Bitcoin Article"


def test_get_feed_detail(client, sample_feed_item):
    """피드 상세 조회"""
    response = client.get("/api/v1/feed/test-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-001"
    assert data["source"] == "Test Source"


def test_get_feed_detail_not_found(client):
    """피드 상세 조회 - 없는 ID"""
    response = client.get("/api/v1/feed/nonexistent")
    assert response.status_code == 404


def test_add_bookmark(client, sample_feed_item):
    """북마크 추가"""
    response = client.post("/api/v1/bookmarks/test-001")
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == "test-001"


def test_add_bookmark_not_found(client):
    """북마크 추가 - 없는 피드"""
    response = client.post("/api/v1/bookmarks/nonexistent")
    assert response.status_code == 404


def test_get_bookmarks(client, sample_feed_item):
    """북마크 목록 조회"""
    # 북마크 추가
    client.post("/api/v1/bookmarks/test-001")

    # 목록 조회
    response = client.get("/api/v1/bookmarks")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["item"]["id"] == "test-001"


def test_remove_bookmark(client, sample_feed_item):
    """북마크 삭제"""
    # 북마크 추가
    client.post("/api/v1/bookmarks/test-001")

    # 북마크 삭제
    response = client.delete("/api/v1/bookmarks/test-001")
    assert response.status_code == 200

    # 목록 확인
    response = client.get("/api/v1/bookmarks")
    data = response.json()
    assert len(data["items"]) == 0


def test_get_categories(client, sample_feed_item):
    """카테고리 목록 조회"""
    response = client.get("/api/v1/feed/categories")
    assert response.status_code == 200
    data = response.json()
    assert "Market" in data


def test_get_trending(client, sample_feed_item):
    """트렌딩 피드 조회"""
    response = client.get("/api/v1/feed/trending?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


def test_feed_category_filter(client, sample_feed_item):
    """피드 카테고리 필터"""
    response = client.get("/api/v1/feed?category=Market")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1

    response = client.get("/api/v1/feed?category=Technology")
    data = response.json()
    assert len(data["items"]) == 0


def test_feed_search(client, sample_feed_item):
    """피드 검색"""
    response = client.get("/api/v1/feed?search=Bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1

    response = client.get("/api/v1/feed?search=Ethereum")
    data = response.json()
    assert len(data["items"]) == 0
