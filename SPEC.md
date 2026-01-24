# Bitcoin News Feed Aggregator - Technical Specification (SPEC.md)

> **참고**: 이 프로젝트는 **모바일 뷰 중심의 웹 앱**으로, 비트코인 관련 정보를 “언론 기사”뿐 아니라 **커뮤니티/개발자/GitHub/SNS** 등에서 폭넓게 수집해 하나의 피드로 제공하는 것을 목표로 한다.  
> 기술 스택은 예시와 동일하게 **React + FastAPI + SQLite3** 기반으로 진행한다.

---

## 0. Data Flow Definition (필수 - 프로젝트 시작 전 정의)

> **IMPORTANT**: 이 프로젝트의 핵심은 “뉴스 수집 로직”이다.  
> 데이터 소스별 접근 방식(API/스크래핑/RSS), 레이트리밋, 파싱 규칙, 중복 제거 전략이 먼저 정의되어야 한다.

### 0.1 Data Source (데이터 소스)

| 소스 | 타입 | 접근 방법 | 인증 | 비용 | 비고 |
|---|---|---|---|---|---|
| Reddit (Bitcoin 관련 Subreddit) | Public API / HTML | 우선 API, 불가 시 스크래핑(Playwright) | 경우에 따라 필요 | 무료 | rate limit 주의 |
| X.com (Twitter) | 제한적 / HTML | 스크래핑(Playwright) 중심 | 로그인/세션 필요 가능 | 무료/불안정 | 정책/차단 리스크 큼 |
| Google News (Bitcoin 관련) | RSS/HTML | RSS 우선, 필요 시 스크래핑 | 불필요 | 무료 | 지역/언어 파라미터 관리 |
| Bitcoin Magazine | RSS/HTML | RSS 우선, 필요 시 스크래핑 | 불필요 | 무료 | |
| Bitcoin Optech | RSS/HTML | RSS/HTML 파싱 | 불필요 | 무료 | 주간 이슈 구조 고정 |
| GitHub (Bitcoin Core 등) | Public API | GitHub REST API | 토큰 권장 | 무료 | rate limit 개선 위해 토큰 사용 |
| Mining 관련 종목/기업 뉴스 | RSS/HTML | RSS/스크래핑 | 불필요 | 무료 | 출처 다양, 규칙화 필요 |

#### 소스 타입 가이드

| 타입 | 예시 | 난이도 | 안정성 | 비용 |
|---|---|---:|---:|---:|
| **RSS** | Google News RSS, Optech RSS | 쉬움 | 높음 | 무료 |
| **Public API** | GitHub API, Reddit API(가능 시) | 보통 | 중간~높음 | 무료 |
| **스크래핑** | X.com, 일부 블로그/뉴스 | 보통~어려움 | 낮음(차단/변경) | 무료 |
| **혼합** | RSS + 보완 스크래핑 | 보통 | 중간 | 무료 |

---

### 0.2 Input (사용자 입력)

| 입력 항목 | 타입 | 예시 | 필수 |
|---|---|---|---|
| 키워드/토픽 | String[] | ["bitcoin", "mempool", "mining"] | 선택 |
| 소스 필터 | Enum[] | ["reddit","x","optech","github"] | 선택 |
| 언어/지역 | String | "ko-KR", "en-US" | 선택 |
| 시간 범위 | Enum | "24h", "7d", "30d" | 선택 |
| 정렬 | Enum | "latest", "score", "trending" | 선택 |
| 차단 키워드 | String[] | ["airdrop", "giveaway"] | 선택 |

---

### 0.3 Output (결과 출력)

| 출력 항목 | 형태 | 설명 |
|---|---|---|
| 메인 피드 | 카드 리스트 | 출처/제목/요약/시간/점수/태그 |
| 소스별 탭 | 탭 UI | Reddit/X/GitHub/Optech 등 |
| 상세 뷰 | 상세 페이지 | 원문 링크 + 본문 일부/메타데이터 |
| 북마크 | 로컬/DB | 사용자 즐겨찾기 |
| “트렌딩” | 섹션 | 최근 반응/언급량 기반 |

---

### 0.4 Data Flow Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌───────────────┐
│    User     │      │  Frontend   │      │   Backend   │      │ Data Sources  │
│ (filters)   │────▶ │   (React)   │────▶ │  (FastAPI)  │────▶ │ RSS/API/HTML  │
└─────────────┘      └─────────────┘      └─────────────┘      └───────────────┘
                           │                    │                       │
                           │                    │                       │
                           ▼                    ▼                       │
                    ┌─────────────┐      ┌─────────────┐               │
                    │   Output    │◀─────│  Database   │◀──────────────┘
                    │   (Feed)    │      │  (SQLite3)  │   (캐시/중복제거/메타)
                    └─────────────┘      └─────────────┘
```

---

### 0.5 Data Refresh (데이터 갱신 주기)

| 데이터 | 갱신 주기 | 방법 |
|---|---|---|
| RSS 기반 소스 | 5~15분 | 백엔드 스케줄러(배치) |
| GitHub API | 10~30분 | 배치 + 조건부 요청(ETag 등) |
| Reddit | 5~10분 | API/스크래핑(부하 최소화) |
| X.com 스크래핑 | 10~30분 | 큐 기반, 실패 시 백오프 |
| 사용자 피드 조회 | 요청 시 | DB 캐시 기반 응답 |

---

### 0.6 Data Access Checklist (개발 전 확인사항)

- [ ] 각 소스별 **ToS/robots/정책** 확인 (스크래핑 리스크 관리)
- [ ] RSS/API 우선, 스크래핑은 보조로 사용
- [ ] 스크래핑은 **Playwright** + **백오프/재시도/프록시 옵션** 고려
- [ ] HTML 구조 변경 감지(파서 테스트)
- [ ] 중복 제거 기준 정의(URL, canonical, title+source+time 해시)
- [ ] “삭제/차단/비공개” 컨텐츠 처리 정책
- [ ] 장애 시 대체(마지막 캐시 제공)

---

## 1. Project Overview

### 1.1 Purpose
비트코인 관련 정보를 “한 곳”에서 보기 위한 모바일 웹 피드 앱.  
언론 기사 중심이 아니라 **커뮤니티(레딧), SNS(X), 개발자(GitHub), 전문 리포트(Optech)** 등에서 신호를 수집한다.

### 1.2 Goals
- 여러 소스에서 콘텐츠를 자동 수집 → 단일 피드 제공
- 소스별 파싱/정규화 → 동일한 “피드 아이템 모델”로 통합
- 중복 제거 + 태깅(토픽/카테고리) + 간단 점수화(trending)
- 모바일에서 빠른 UX(캐시 기반, 무한 스크롤)

### 1.3 Target Users
- 비트코인 커뮤니티/개발 흐름을 빠르게 따라가고 싶은 사용자
- “뉴스 기사”보다 **현장 반응/개발 업데이트**를 선호하는 사용자
- 연구/콘텐츠 제작을 위해 출처를 모아보는 사용자

### 1.4 Key Use Cases
- 최신 피드 보기(전체/소스별)
- 토픽 필터(예: mining, lightning, core dev)
- 북마크/읽음 처리
- 특정 출처의 글만 모아보기(예: Optech 주간 이슈)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Main Feed  │  │ Source Tabs  │  │  Item Detail │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Filters UI   │  │ Bookmarks    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Layer   │  │ Fetch Engine │  │ Normalizer   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Dedup/Score  │  │ Scheduler    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
           ↕                    ↕
┌──────────────────┐  ┌─────────────────────────────────────┐
│   SQLite3        │  │ RSS / API / Scraping (Playwright)    │
│ (cache + items)  │  │ Reddit, X, Google News, Optech, ...  │
└──────────────────┘  └─────────────────────────────────────┘
```

---

## 3. Core Features & Functionality

### 3.1 Feed Aggregation (핵심)
- 소스별 Fetcher 모듈
  - RSS Fetcher (feedparser)
  - API Fetcher (GitHub/Reddit 가능 시)
  - Scraper Fetcher (Playwright)
- 모든 결과는 **표준 FeedItem 모델**로 normalize
- DB 저장 시 dedup 수행
- 최신/트렌딩 쿼리로 프론트에 제공

### 3.2 Normalized Feed Item Model (표준 모델)
```json
{
  "id": "uuid",
  "source": "reddit|x|googlenews|optech|bitcoinmagazine|github|...",
  "source_ref": "원본 id(있으면)",
  "title": "string",
  "summary": "string|null",
  "url": "string",
  "author": "string|null",
  "published_at": "ISO8601",
  "fetched_at": "ISO8601",
  "tags": ["mining","core","lightning"],
  "score": 0.0,
  "raw": { "source_specific_payload": "..." }
}
```

### 3.3 Dedup Strategy (중복 제거)
우선순위:
1) canonical URL이 같으면 동일
2) url 정규화(utm 제거 등) 후 동일
3) `(source, source_ref)` 동일
4) `hash(title + domain + published_date_rounded)` 유사도 기반 (옵션)

### 3.4 Scoring / Trending (간단 점수)
- 기본: 최신성 가중치 + 소스별 반응 지표(가능한 경우)
  - Reddit: upvotes/comments(가능 시)
  - X: likes/retweets(스크래핑 가능하면)
  - GitHub: comments/reactions/labels(가능 시)
- “트렌딩”은 단순 합산으로 시작, 추후 개선

---

## 4. API Design (FastAPI)

### 4.1 REST Endpoints

#### Feed
```
GET /api/v1/feed
- Query: sources, tags, q, since, sort, limit, offset
- Response: { items: [...], total, next_offset }

GET /api/v1/feed/{item_id}
- Response: { item }

POST /api/v1/bookmarks/{item_id}
DELETE /api/v1/bookmarks/{item_id}
GET /api/v1/bookmarks
```

#### Admin / Fetch
```
POST /api/v1/admin/fetch/run
- 수동 수집 트리거 (개발용)

GET /api/v1/admin/sources
- 소스 상태(마지막 성공 시간, 에러)
```

### 4.2 Response Format
```json
{
  "status": "success",
  "data": { "items": [] },
  "error": null,
  "metadata": {
    "timestamp": "2026-01-24T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### 4.3 Error Codes
- `400`: 잘못된 필터/파라미터
- `404`: 아이템 없음
- `429`: 소스 rate limit / 내부 보호용 제한
- `500`: 파서/스크래퍼 예외
- `503`: 외부 소스 장애(일시적)

---

## 5. Database Schema (SQLite3)

### 5.1 Tables

#### feed_items
```sql
CREATE TABLE feed_items (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_ref TEXT,
  title TEXT NOT NULL,
  summary TEXT,
  url TEXT NOT NULL,
  author TEXT,
  published_at TEXT,
  fetched_at TEXT NOT NULL,
  tags TEXT,                 -- JSON string
  score REAL DEFAULT 0,
  url_hash TEXT,             -- dedup 용
  raw TEXT                   -- JSON string
);

CREATE INDEX idx_feed_items_source_time ON feed_items(source, published_at DESC);
CREATE INDEX idx_feed_items_url_hash ON feed_items(url_hash);
```

#### bookmarks
```sql
CREATE TABLE bookmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(item_id)
);

CREATE INDEX idx_bookmarks_created ON bookmarks(created_at DESC);
```

#### source_status
```sql
CREATE TABLE source_status (
  source TEXT PRIMARY KEY,
  last_success_at TEXT,
  last_error_at TEXT,
  last_error_message TEXT
);
```

---

## 6. Scraping / Fetch Engine (Playwright 중심 설계)

### 6.1 Fetcher Interface
- `fetch()` → 원본 데이터 수집
- `parse()` → FeedItem 후보 생성
- `normalize()` → 표준 모델 변환
- `persist()` → dedup 후 저장

### 6.2 Playwright 운영 규칙
- headless 기본
- 요청 간 최소 간격 + 랜덤 지터
- 실패 시 exponential backoff
- selector 기반 파싱 + 구조 변경 대비 테스트
- X.com 등 로그인 필요 소스는 “세션 쿠키” 관리(환경변수/파일)

### 6.3 Rate Limiting / Backoff
- 소스별 최소 간격 설정
- 에러율 높으면 자동으로 주기 늘림
- 차단 감지(403/429/캡차) 시 해당 소스 “쿨다운” 기록

---

## 7. Frontend (React) - Mobile Web UX

### 7.1 Pages
- `/` 메인 피드 (무한 스크롤)
- `/sources/:source` 소스 탭
- `/item/:id` 상세
- `/bookmarks` 북마크

### 7.2 UI 컴포넌트(예시)
- FeedCard: 제목/요약/출처/시간/태그
- SourceFilterBar: 토글/칩 UI
- TagChips: 토픽 필터
- Skeleton Loader: 로딩 UX

---

## 8. Project Structure

```
bitcoin-news-feed/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   ├── utils/
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── feed.py
│   │   │   ├── bookmarks.py
│   │   │   └── admin.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── fetch_engine.py
│   │   │   ├── dedup.py
│   │   │   ├── score.py
│   │   │   └── sources/
│   │   │       ├── reddit.py
│   │   │       ├── xcom.py
│   │   │       ├── googlenews.py
│   │   │       ├── optech.py
│   │   │       ├── bitcoinmagazine.py
│   │   │       └── github.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
│
├── .claude/
├── SPEC.md
├── README.md
├── Dockerfile
├── railway.toml
├── install.sh
├── dev.sh
└── test.sh
```

---

## 9. Environment Variables

```bash
# .env.example

# Backend
DATABASE_URL=sqlite:///./feed.db
LOG_LEVEL=INFO
ENVIRONMENT=development

# Optional: GitHub
GITHUB_TOKEN=...

# Optional: X.com session (if needed)
X_SESSION_COOKIES_JSON=...

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Bitcoin News Feed
```

---

## 10. Development Phases

### Phase 1: Foundation
- [ ] 프로젝트 스캐폴딩(React + FastAPI + SQLite)
- [ ] FeedItem 모델/스키마/DB 테이블
- [ ] 기본 /feed API + 더미 데이터 렌더링

### Phase 2: RSS First
- [ ] Google News RSS
- [ ] Bitcoin Magazine RSS
- [ ] Optech RSS/HTML
- [ ] dedup + 최신 피드 완성

### Phase 3: API Sources
- [ ] GitHub API(릴리즈/이슈/PR)
- [ ] Reddit API 가능 여부 검토 후 적용

### Phase 4: Scraping Layer
- [ ] Playwright 기반 스크래퍼 프레임워크
- [ ] Reddit 스크래핑(필요 시)
- [ ] X.com 스크래핑(리스크/쿨다운 포함)

### Phase 5: UX & Quality
- [ ] 필터/북마크/읽음 처리
- [ ] 트렌딩 점수/태그 개선
- [ ] 안정성(스케줄러, 에러 대시보드, 알림)

---

## 11. Success Metrics
- [ ] 피드 최신성: RSS 기준 15분 내 반영
- [ ] 스크래핑 소스 성공률: 주간 평균 95% 이상(변경 시 대응)
- [ ] 중복 제거 정확도: 중복 노출 최소화
- [ ] 피드 API 응답: 캐시 기준 300ms~800ms 내
- [ ] 모바일 UX: 스크롤/전환 지연 최소

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-24  
**Template Type**: Bitcoin News Feed Aggregator
