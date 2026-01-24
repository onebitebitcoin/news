# Agent Rules

## Language
- 모든 답변은 한국어로 작성한다.
- 코드/로그/에러 메시지는 원문을 유지하되, 설명은 한국어로 한다.

## SPEC.md 검토 및 스펙 구체화 (CRITICAL)

**프로젝트 작업 전 SPEC.md를 반드시 검토하고, 불명확한 부분은 사용자에게 질문하여 스펙을 구체화해야 한다.**

### 원칙
- SPEC.md 파일을 먼저 읽고 요구사항을 파악한다.
- 모호하거나 불명확한 부분이 있으면 **반드시 사용자에게 질문**한다.
- 가정을 세우기 전에 확인을 먼저 받는다.
- 스펙이 구체화된 후에 구현을 시작한다.

### 질문해야 할 사항

1. **기능 요구사항**
   - 기능의 세부 동작이 불명확할 때
   - 엣지 케이스 처리 방법이 정의되지 않았을 때
   - 여러 가지 해석이 가능할 때

2. **UI/UX 요구사항**
   - 디자인 스펙이 없거나 불명확할 때
   - 사용자 플로우가 정의되지 않았을 때
   - 에러/로딩/빈 상태 처리가 명시되지 않았을 때

3. **데이터 요구사항**
   - 스키마 필드의 타입이나 제약조건이 불명확할 때
   - 데이터 관계(1:N, N:M 등)가 정의되지 않았을 때
   - 초기 데이터/시드 데이터 필요 여부

4. **기술 요구사항**
   - 기술 스택 선택이 필요할 때
   - 성능/보안 요구사항이 불명확할 때
   - 외부 API/서비스 연동 방식이 정의되지 않았을 때

5. **비즈니스 로직**
   - 계산 공식이나 규칙이 불명확할 때
   - 권한/접근 제어가 정의되지 않았을 때
   - 유효성 검증 규칙이 명시되지 않았을 때

### 질문 예시
```
"SPEC.md에서 [기능명]의 동작이 불명확합니다.
다음 중 어떤 방식으로 구현할까요?
1. [옵션 A] - 설명
2. [옵션 B] - 설명
3. 다른 방식이 있으면 설명해주세요."
```

### 체크리스트
- [ ] SPEC.md를 처음부터 끝까지 읽었는가?
- [ ] 불명확한 요구사항을 모두 파악했는가?
- [ ] 사용자에게 질문하여 명확히 했는가?
- [ ] 답변을 바탕으로 구현 방향을 확정했는가?

**주의**: 불명확한 상태로 구현을 시작하면 나중에 대규모 수정이 필요할 수 있다. 먼저 질문하고 확인받는 것이 효율적이다.

## Frontend 개발 규칙 (CRITICAL)

### 새 페이지는 새 URL로 생성

**새로운 페이지를 만들 때는 반드시 새로운 URL(라우트)을 생성해야 한다.**

모달이나 조건부 렌더링으로 페이지를 대체하면 안 된다.

| 상황 | 올바른 방법 | 잘못된 방법 |
|------|------------|------------|
| 상세 페이지 | `/users/:id` 라우트 생성 | 모달로 상세 정보 표시 |
| 생성 페이지 | `/users/new` 라우트 생성 | 같은 페이지에서 폼 토글 |
| 수정 페이지 | `/users/:id/edit` 라우트 생성 | 모달로 수정 폼 표시 |
| 설정 페이지 | `/settings` 라우트 생성 | 드로어로 설정 표시 |

**이유:**
- 브라우저 뒤로가기/앞으로가기 지원
- URL 공유 및 북마크 가능
- SEO 최적화
- 페이지 상태 관리 용이

**React Router 예시:**

```jsx
// ✅ 올바른 예시 - 라우트로 페이지 분리
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/users" element={<UserListPage />} />
        <Route path="/users/new" element={<UserCreatePage />} />
        <Route path="/users/:id" element={<UserDetailPage />} />
        <Route path="/users/:id/edit" element={<UserEditPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

```jsx
// ❌ 잘못된 예시 - 모달로 페이지 대체
function UserListPage() {
  const [showDetail, setShowDetail] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  return (
    <div>
      <UserList onSelect={(user) => {
        setSelectedUser(user);
        setShowDetail(true);  // 모달로 표시 - 잘못됨!
      }} />

      {showDetail && (
        <Modal>
          <UserDetail user={selectedUser} />
        </Modal>
      )}
    </div>
  );
}
```

**예외 (모달 사용 가능한 경우):**
- 삭제 확인 다이얼로그
- 간단한 알림/경고
- 빠른 미리보기 (상세 페이지로 이동 링크 포함)

---

## Writing / UI Guidelines
1) 이모지를 사용하지 말고 아이콘을 사용할 것
   - 문서/설명에서 🎉 같은 이모지 금지
   - UI 구현에서는 아이콘 컴포넌트(예: lucide-react) 사용을 우선한다.

2) **중첩된 카드뷰는 사용하지 말 것 (CRITICAL)**
   - Card 안에 또 Card를 넣는 구조 금지
   - 필요하면 섹션 구분은 Divider, Header, Subsection, Background, Border 등으로 처리한다.
   - 레이아웃 깊이는 최대 2단계까지만 허용

3) **심플한 디자인 유지 (CRITICAL)**
   - 웹 UI에서 너무 많은 텍스트 설명을 표시하지 말 것
   - 긴 설명문, 상세 가이드, 도움말 텍스트는 최소화
   - 필요한 정보만 간결하게 표시
   - 상세 정보는 툴팁, 모달, 드롭다운 등으로 숨김 처리
   - "Less is more" 원칙 준수

   **좋은 예시**:
   ```jsx
   // ✅ 간결한 UI
   <div>
     <h2>주소 검색</h2>
     <Input placeholder="비트코인 주소 입력" />
     <Button>검색</Button>
   </div>

   // ❌ 너무 많은 설명
   <div>
     <h2>비트코인 주소 검색 기능</h2>
     <p>이 기능을 사용하면 비트코인 주소를 검색할 수 있습니다...</p>
     <p>검색 방법: 아래 입력란에 비트코인 주소를 입력하세요...</p>
     <p>주의사항: 올바른 형식의 주소를 입력해야 합니다...</p>
     <Input placeholder="비트코인 주소 입력" />
     <Button>검색</Button>
     <p>검색 버튼을 클릭하면 결과가 표시됩니다...</p>
   </div>
   ```

4) **모바일 친화적인 레이아웃으로 적용할 것 (CRITICAL)**
   - 기본을 모바일 우선(Mobile-first)로 설계한다.
   - 작은 화면에서 가독성(폰트/여백/줄바꿈)과 터치 타깃(버튼/링크)을 우선한다.
   - **모바일 좌우 padding은 최소한으로 설정** (예: `px-2`, `px-4`)
   - 항상 UI 업데이트 시 모바일에서 어떻게 보일지 고려

   **Tailwind CSS 예시**:
   ```jsx
   // ✅ 모바일 친화적인 padding
   <div className="px-2 sm:px-4 md:px-6 lg:px-8">
     {/* 모바일: px-2, 태블릿 이상: px-4+ */}
   </div>

   // ❌ 모바일에서 공간 낭비
   <div className="px-8 md:px-12 lg:px-16">
     {/* 모바일에서 너무 큰 padding */}
   </div>
   ```

   **사용자 요청 확인 (CRITICAL)**:
   - 사용자의 UI 요청이 **웹에만 한정되어 너무 디테일**하면 반드시 되물을 것
   - 예시 질문: **"이렇게 업데이트하면 모바일에서 레이아웃이 깨질 수 있는데 괜찮나요?"**
   - 모바일 호환성을 사용자에게 확인받고 진행
   - 웹 전용 디자인 요청 시 모바일 대안을 함께 제시

   **체크리스트**:
   - [ ] 모바일 화면에서 UI 깨지지 않는지 확인
   - [ ] 터치 타깃 크기 44x44px 이상
   - [ ] 가로 스크롤 발생하지 않는지 확인
   - [ ] 텍스트 크기 최소 14px 이상 (가독성)
   - [ ] 버튼/링크 간격 충분한지 확인

5) 시간/날짜는 항상 한국 시간(Asia/Seoul)을 기준으로 판단한다.

6) fallback 더미 값 주입으로 흐름을 숨기지 말 것
   - 디버깅을 어렵게 하므로 기본/더미 값으로 덮어쓰지 않는다.
   - 문제가 발생하면 에러 메시지를 명확히 노출한다.

7) 사용자 작업에는 성공/실패 메시지를 항상 노출할 것
   - 저장/추가/삭제/새로고침 등 주요 액션의 결과를 명확히 표시한다.

## 의존성 관리 및 환경 구축 (CRITICAL)

**개발 시작 전 반드시 `install.sh`를 실행하여 환경을 구축해야 한다.**

### 개발 환경 구축 순서

1. **install.sh 실행** (최초 1회 또는 의존성 변경 시)
   ```bash
   ./install.sh
   ```
2. **dev.sh 실행** (개발 서버 시작)
   ```bash
   ./dev.sh
   ```

### 새 패키지 설치 워크플로우 (CRITICAL)

**새 패키지가 필요한 기능 구현 시 반드시 아래 순서를 따라야 한다.**

코드에 import만 추가하고 패키지를 설치하지 않으면 **런타임 에러가 발생**한다.

| 단계 | Backend (Python) | Frontend (Node.js) |
|------|------------------|-------------------|
| 1. 패키지 설치 | `pip install 패키지명` | `npm install 패키지명` |
| 2. 의존성 파일 추가 | `backend/requirements.txt`에 추가 | 자동 반영 (`package.json`) |
| 3. 코드 작성 | `import` 또는 `from ... import` | `import ... from '...'` |

**예시: requests 패키지 사용**

```bash
# 1. 패키지 설치
cd backend
pip install requests

# 2. requirements.txt에 추가
echo "requests==2.31.0" >> requirements.txt
```

```python
# 3. 코드에서 사용
import requests

response = requests.get("https://api.example.com")
```

**잘못된 예시**:
```python
# ❌ 패키지 설치 없이 import만 추가
import pandas  # ModuleNotFoundError 발생!

df = pandas.DataFrame()
```

**올바른 예시**:
```bash
# ✅ 먼저 설치
pip install pandas
# requirements.txt에 추가
```
```python
# 그 다음 import
import pandas

df = pandas.DataFrame()
```

### 새 패키지 설치 시 규칙

**패키지를 설치하면 반드시 의존성 파일에 추가해야 한다.**

| 환경 | 설치 명령 | 반영 파일 |
|------|----------|----------|
| Backend (Python) | `pip install 패키지명` | `backend/requirements.txt` |
| Frontend (Node.js) | `npm install 패키지명` | `frontend/package.json` |

### install.sh 유지 규칙

install.sh는 다음을 수행해야 한다:
- Python 가상환경 생성 및 활성화
- `backend/requirements.txt` 패키지 설치
- `frontend/package.json` 패키지 설치
- 환경 변수 파일 생성 (`.env` 없을 경우)

**install.sh 예시 구조**:
```bash
#!/bin/bash

# Backend 설정
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend 설정
cd ../frontend
npm install

# 환경 변수 파일 생성
cd ..
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env 파일이 생성되었습니다. 필요한 값을 설정하세요."
fi

echo "설치 완료!"
```

### 체크리스트

```
[ ] 개발 시작 전 install.sh를 실행했는가?
[ ] 새 패키지 설치 시 requirements.txt 또는 package.json에 추가했는가?
[ ] install.sh 실행 시 모든 의존성이 설치되는가?
[ ] 다른 개발자도 install.sh만 실행하면 환경 구축이 되는가?
```

### Dockerfile과 패키지 관리

**새 패키지 설치 시 Dockerfile 수정이 필요한가?**

| 패키지 종류 | 수정 파일 | Dockerfile 수정 |
|------------|----------|----------------|
| Python (pip) | `backend/requirements.txt` | 불필요 |
| Node.js (npm) | `frontend/package.json` | 불필요 |
| 시스템 (apt) | `Dockerfile` | **필요** |

**원리**:
- Dockerfile은 `requirements.txt`와 `package.json`을 읽어서 패키지 설치
- 따라서 의존성 파일만 업데이트하면 Docker 빌드 시 자동 반영

**Dockerfile 수정이 필요한 경우** (시스템 레벨 의존성):
```dockerfile
# 예: 이미지 처리, DB 드라이버 등 시스템 라이브러리가 필요할 때
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \      # PostgreSQL 드라이버
    libmagic1 \      # python-magic 라이브러리
    ffmpeg \         # 영상 처리
    && rm -rf /var/lib/apt/lists/*
```

**주의**: 시스템 패키지 추가 시 반드시 사용자에게 확인:
```
"이 기능을 위해 시스템 패키지 [패키지명]이 필요합니다.
Dockerfile에 추가해도 될까요?"
```

---

## Workflow (필수)
- 변경 사항이 생기면 아래 순서로 마무리한다.
  1) **Lint 체크 (테스트 전 필수)**
     - Frontend (React): `npm run lint` (ESLint)
     - Backend (FastAPI): `ruff check .` 또는 `flake8`
     - 에러가 있으면 수정 후 다시 체크
  2) 테스트 실행(프로젝트 표준 커맨드 사용)
  3) **테스트 결과를 테이블 형태로 출력 (필수)**
  4) PASS/FAIL 확인 후, FAIL이면 수정 → 재테스트 반복
  5) **PASS면 반드시 `git add` → `git commit` 수행 (절대 누락 금지)**
  6) `git push`는 사용자가 명시적으로 요청할 때만 수행한다.

### Commit 필수 (CRITICAL)
**테스트 통과 후 commit을 절대 잊지 말 것!**
- 작업 완료 + 테스트 PASS → 반드시 commit
- commit 없이 다음 작업으로 넘어가지 말 것
- 사용자가 commit 하지 말라고 명시적으로 요청한 경우에만 생략

### 테스트 결과 출력 형식 (필수)
테스트 수행 후 반드시 아래 형식으로 결과를 출력한다:

```
| 구분 | 결과 | 상세 |
|------|------|------|
| Frontend Lint | PASS/FAIL | 에러 수 또는 "OK" |
| Backend Lint | PASS/FAIL | 에러 수 또는 "OK" |
| Frontend Test | PASS/FAIL | 통과/전체 (예: 10/10) |
| Backend Test | PASS/FAIL | 통과/전체 (예: 15/15) |
| **최종 결과** | **PASS/FAIL** | - |
```

### Lint 설정

**Frontend (React) - ESLint**:
```bash
# 린트 체크
npm run lint

# 자동 수정
npm run lint -- --fix
```

**Backend (FastAPI) - Ruff**:
```bash
# 린트 체크
ruff check .

# 자동 수정
ruff check . --fix

# 포맷팅
ruff format .
```

## 테스트 구조 및 실행 (CRITICAL)

**모든 테스트 코드는 `tests/` 디렉토리 아래에 모아서 관리한다.**

### 디렉토리 구조

```
tests/
├── test.sh                    # 통합 테스트 실행 스크립트
├── backend/                   # Backend 테스트 (pytest)
│   ├── conftest.py            # 공통 fixtures (DB 세션, 테스트 클라이언트 등)
│   ├── test_api.py            # API 엔드포인트 테스트
│   ├── test_services.py       # 서비스 로직 테스트
│   └── test_models.py         # 모델/스키마 테스트
└── frontend/                  # Frontend 테스트 (Vitest)
    ├── setup.ts               # 테스트 환경 설정
    ├── components/            # 컴포넌트 테스트
    │   └── Button.test.tsx
    └── hooks/                 # 커스텀 훅 테스트
        └── useApi.test.ts
```

### 테스트 실행

**통합 실행** (권장):
```bash
./tests/test.sh
```

**개별 실행**:
```bash
# Backend만
./tests/test.sh --backend

# Frontend만
./tests/test.sh --frontend

# Watch 모드 (개발 중)
./tests/test.sh --watch

# 커버리지 리포트
./tests/test.sh --coverage
```

### test.sh 스크립트 구조

```bash
#!/bin/bash
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 결과 변수
BACKEND_RESULT="SKIP"
FRONTEND_RESULT="SKIP"

# 옵션 파싱
RUN_BACKEND=true
RUN_FRONTEND=true
WATCH_MODE=false
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend) RUN_FRONTEND=false; shift ;;
        --frontend) RUN_BACKEND=false; shift ;;
        --watch) WATCH_MODE=true; shift ;;
        --coverage) COVERAGE=true; shift ;;
        *) shift ;;
    esac
done

# Backend 테스트
if [ "$RUN_BACKEND" = true ]; then
    echo "Running Backend tests..."
    cd backend
    if [ "$COVERAGE" = true ]; then
        pytest ../tests/backend -v --cov=app --cov-report=html && BACKEND_RESULT="PASS" || BACKEND_RESULT="FAIL"
    else
        pytest ../tests/backend -v && BACKEND_RESULT="PASS" || BACKEND_RESULT="FAIL"
    fi
    cd ..
fi

# Frontend 테스트
if [ "$RUN_FRONTEND" = true ]; then
    echo "Running Frontend tests..."
    cd frontend
    if [ "$WATCH_MODE" = true ]; then
        npm run test -- --watch
    elif [ "$COVERAGE" = true ]; then
        npm run test -- --coverage && FRONTEND_RESULT="PASS" || FRONTEND_RESULT="FAIL"
    else
        npm run test && FRONTEND_RESULT="PASS" || FRONTEND_RESULT="FAIL"
    fi
    cd ..
fi

# 결과 출력
echo ""
echo "================================"
echo "        테스트 결과"
echo "================================"
echo "| 구분 | 결과 |"
echo "|------|------|"
echo "| Backend  | $BACKEND_RESULT |"
echo "| Frontend | $FRONTEND_RESULT |"
echo "================================"

# 최종 결과
if [ "$BACKEND_RESULT" = "FAIL" ] || [ "$FRONTEND_RESULT" = "FAIL" ]; then
    echo -e "${RED}최종 결과: FAIL${NC}"
    exit 1
else
    echo -e "${GREEN}최종 결과: PASS${NC}"
    exit 0
fi
```

### 테스트 설정 파일

**Backend (pyproject.toml)**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests/backend"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

**Frontend (vitest.config.ts)**:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/frontend/setup.ts'],
    include: ['tests/frontend/**/*.test.{ts,tsx}'],
    coverage: {
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'tests/'],
    },
  },
});
```

### 테스트 작성 규칙

1. **파일 명명**: `test_*.py` (Backend), `*.test.ts(x)` (Frontend)
2. **함수 명명**: `test_기능_상황_예상결과` 형식
   ```python
   def test_create_user_with_valid_data_returns_201():
       ...
   ```
3. **AAA 패턴**: Arrange(준비) → Act(실행) → Assert(검증)
4. **독립성**: 각 테스트는 독립적으로 실행 가능해야 함
5. **Fixtures 활용**: 공통 설정은 `conftest.py` 또는 `setup.ts`에 정의

### Backend 테스트 예시 (pytest)

```python
# tests/backend/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# 테스트용 DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

```python
# tests/backend/test_api.py
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user_with_valid_data(client):
    response = client.post("/api/v1/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### Frontend 테스트 예시 (Vitest)

```typescript
// tests/frontend/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

```typescript
// tests/frontend/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from '@/components/Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 체크리스트

```
[ ] 모든 테스트 코드는 tests/ 디렉토리에 위치
[ ] tests/test.sh로 전체 테스트 실행 가능
[ ] Backend: pytest + conftest.py fixtures 설정
[ ] Frontend: Vitest + setup.ts 설정
[ ] 새 기능 추가 시 테스트 코드도 함께 작성
[ ] 테스트 통과 후 커밋 진행
```

---

## Database 개발 규칙 (CRITICAL)

**Backend에서 데이터베이스 접근 시 반드시 ORM(SQLAlchemy)을 사용해야 한다.**

### 원칙
- Raw SQL 직접 작성 금지 (SQL Injection 방지)
- SQLAlchemy ORM으로 모델 정의 및 쿼리 수행
- 복잡한 쿼리도 ORM으로 작성 (필요시 `joinedload`, `subquery` 등 활용)

### 모델 정의

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 정의
    posts = relationship("Post", back_populates="author")
```

### CRUD 작업

```python
# ✅ ORM 사용 (올바른 예시)
from sqlalchemy.orm import Session
from app.models import User

# Create
def create_user(db: Session, email: str, name: str) -> User:
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Read
def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

# Update
def update_user(db: Session, user_id: int, name: str) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        db.commit()
        db.refresh(user)
    return user

# Delete
def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
```

### 잘못된 예시

```python
# ❌ Raw SQL 직접 사용 - SQL Injection 취약점!
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ❌ 문자열 포매팅으로 쿼리 작성
query = f"INSERT INTO users (name) VALUES ('{name}')"
cursor.execute(query)
```

### 복잡한 쿼리

```python
# 조인 쿼리
users_with_posts = (
    db.query(User)
    .options(joinedload(User.posts))
    .filter(User.is_active == True)
    .all()
)

# 집계 쿼리
from sqlalchemy import func

post_counts = (
    db.query(User.id, func.count(Post.id).label("post_count"))
    .join(Post)
    .group_by(User.id)
    .all()
)

# 서브쿼리
subquery = db.query(Post.author_id).filter(Post.published == True).subquery()
active_authors = db.query(User).filter(User.id.in_(subquery)).all()
```

### 체크리스트
- [ ] 모든 DB 접근은 SQLAlchemy ORM을 통해 수행
- [ ] Raw SQL 문자열 직접 작성하지 않음
- [ ] 모델 클래스에 적절한 인덱스 설정
- [ ] 관계(relationship)가 필요한 경우 명시적으로 정의

---

## Database 마이그레이션 (CRITICAL)

**DB 스키마 변경 시 반드시 마이그레이션을 수행해야 한다.**

### 원칙
- 모델(스키마) 변경 후 **반드시 마이그레이션 생성 및 적용**
- 마이그레이션 없이 서버 실행 시 스키마 불일치로 에러 발생
- Alembic 사용 권장

### 마이그레이션 워크플로우

| 단계 | 명령어 | 설명 |
|------|--------|------|
| 1. 모델 수정 | - | SQLAlchemy 모델 파일 수정 |
| 2. 마이그레이션 생성 | `alembic revision --autogenerate -m "설명"` | 변경사항 감지하여 마이그레이션 파일 생성 |
| 3. 마이그레이션 적용 | `alembic upgrade head` | DB에 변경사항 적용 |
| 4. 확인 | `alembic current` | 현재 마이그레이션 상태 확인 |

### 예시

```bash
# 1. 모델 수정 후 마이그레이션 생성
cd backend
alembic revision --autogenerate -m "add email column to users"

# 2. 생성된 마이그레이션 파일 확인 (backend/alembic/versions/)
# 자동 생성된 내용이 올바른지 검토

# 3. 마이그레이션 적용
alembic upgrade head

# 4. 상태 확인
alembic current
```

### Alembic 초기 설정 (최초 1회)

```bash
cd backend
pip install alembic
alembic init alembic

# alembic.ini 수정: sqlalchemy.url 설정
# alembic/env.py 수정: target_metadata 설정
```

### 주의사항
- 마이그레이션 파일은 **반드시 Git에 커밋**
- 프로덕션 배포 전 마이그레이션 테스트 필수
- 롤백이 필요한 경우: `alembic downgrade -1`

### 체크리스트
- [ ] 모델 변경 후 마이그레이션 파일 생성했는가?
- [ ] 마이그레이션 파일 내용을 검토했는가?
- [ ] 로컬에서 마이그레이션 적용 및 테스트했는가?
- [ ] 마이그레이션 파일을 Git에 커밋했는가?

---

## Database & API Synchronization (CRITICAL)
**스키마와 API는 항상 함께 업데이트되어야 한다.**

처음에 만든 스키마와 API가 다른 상태에서 스키마가 업데이트되면 API는 업데이트되지 않기 때문에, 반드시 CRUD 기능에서는 스키마 업데이트와 API 업데이트를 같이 취급해야 한다.

### 원칙
- 데이터베이스 스키마가 변경되면 반드시 관련 API도 함께 업데이트해야 함
- CRUD 기능 개발/수정 시 스키마와 API를 항상 같이 취급할 것
- 스키마만 업데이트하고 API를 업데이트하지 않으면 불일치가 발생하여 런타임 에러 발생

### 예시
- **스키마에 새 필드 추가** → API response model (Pydantic)에도 필드 추가
- **스키마에서 필드 제거** → API request/response model에서도 해당 필드 제거
- **스키마 필드 타입 변경** → API validation/serialization 로직도 변경
- **필드명 변경** → API 모델, 쿼리 로직, 문서 모두 변경

### 체크리스트
스키마 변경 시 반드시 확인할 항목:
1. [ ] 영향받는 모든 API 엔드포인트 확인
2. [ ] Pydantic 모델 (request/response schemas) 업데이트
3. [ ] SQLAlchemy 모델과 Pydantic 모델 일치 확인
4. [ ] API 문서 (Swagger/OpenAPI) 자동 반영 확인
5. [ ] 관련 테스트 코드 업데이트
6. [ ] 마이그레이션 스크립트 작성 (필요시)

### 나쁜 예시
```python
# ❌ 스키마만 변경하고 API는 업데이트하지 않음
# models.py
class Address(Base):
    address = Column(String)
    balance = Column(Float)
    cluster_id = Column(String)
    tx_count = Column(Integer)  # 새로 추가

# schemas.py (업데이트 안 함!)
class AddressResponse(BaseModel):
    address: str
    balance: float
    cluster_id: str
    # tx_count 누락! → API 응답에 포함되지 않음
```

### 좋은 예시
```python
# ✅ 스키마와 API를 함께 업데이트
# models.py
class Address(Base):
    address = Column(String)
    balance = Column(Float)
    cluster_id = Column(String)
    tx_count = Column(Integer)  # 새로 추가

# schemas.py (함께 업데이트!)
class AddressResponse(BaseModel):
    address: str
    balance: float
    cluster_id: str
    tx_count: int  # 추가됨 ✓
```

---

## Backend Development - 12-Factor App (CRITICAL)

**Backend 개발 시 반드시 12-Factor App 방법론을 따라야 한다.**

12-Factor App은 확장 가능하고 유지보수가 쉬운 SaaS 애플리케이션을 구축하기 위한 방법론이다.
참고: https://12factor.net/

### 12가지 원칙

| # | 원칙 | 설명 | 적용 예시 |
|---|------|------|----------|
| 1 | **Codebase** | 버전 관리되는 하나의 코드베이스, 여러 배포 | Git으로 관리, dev/staging/prod 환경 분리 |
| 2 | **Dependencies** | 의존성을 명시적으로 선언하고 격리 | `requirements.txt`, `pyproject.toml` 사용 |
| 3 | **Config** | 설정을 환경 변수로 분리 | `.env` 파일, `os.getenv()` 사용 |
| 4 | **Backing Services** | 백엔드 서비스를 연결된 리소스로 취급 | DB, Redis, S3를 URL로 연결 |
| 5 | **Build, Release, Run** | 빌드/릴리스/실행 단계 엄격히 분리 | Docker 빌드 → 이미지 태깅 → 컨테이너 실행 |
| 6 | **Processes** | 무상태(Stateless) 프로세스로 실행 | 세션은 Redis/DB에 저장, 로컬 파일 의존 금지 |
| 7 | **Port Binding** | 포트 바인딩으로 서비스 노출 | `uvicorn app:app --port $PORT` |
| 8 | **Concurrency** | 프로세스 모델로 수평 확장 | 워커 수 조절, 로드밸런서 사용 |
| 9 | **Disposability** | 빠른 시작/종료로 견고성 확보 | graceful shutdown, 시그널 핸들링 |
| 10 | **Dev/Prod Parity** | 개발/스테이징/프로덕션 환경 동일하게 유지 | Docker로 환경 통일, 같은 DB 종류 사용 |
| 11 | **Logs** | 로그를 이벤트 스트림으로 취급 | stdout 출력, 로그 수집기가 처리 |
| 12 | **Admin Processes** | 관리 작업을 일회성 프로세스로 실행 | 마이그레이션, 스크립트를 별도 명령으로 |

### 필수 체크리스트

```
[ ] 모든 설정은 환경 변수로 관리 (하드코딩 금지)
[ ] 의존성은 requirements.txt 또는 pyproject.toml에 명시
[ ] 프로세스는 무상태로 유지 (로컬 파일 시스템 의존 금지)
[ ] 로그는 stdout으로 출력 (파일 직접 쓰기는 개발 환경만)
[ ] graceful shutdown 구현
[ ] 개발/프로덕션 환경 차이 최소화
```

### FastAPI 적용 예시

```python
import os
from fastapi import FastAPI

# Config: 환경 변수로 설정 관리
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# Port Binding: 환경 변수로 포트 설정
PORT = int(os.getenv("PORT", 8000))

# Processes: 무상태 유지
# ❌ 잘못된 예시 - 로컬 파일에 상태 저장
# user_sessions = {}  # 메모리에 세션 저장

# ✅ 올바른 예시 - 외부 서비스 사용
# from redis import Redis
# redis_client = Redis.from_url(REDIS_URL)
```

---

## Backend Refactoring - Unix Philosophy (CRITICAL)

**백엔드 리팩토링 시 반드시 Unix Philosophy를 따라야 한다.**

Unix Philosophy는 1969년 Ken Thompson이 제시한 소프트웨어 개발 철학으로, 50년이 지난 현재에도 유효한 원칙이다.
참고: [Unix philosophy - Wikipedia](https://en.wikipedia.org/wiki/Unix_philosophy)

### 핵심 원칙 (Peter H. Salus의 3가지 원칙)

| # | 원칙 | 설명 |
|---|------|------|
| 1 | **Do One Thing Well** | 프로그램은 한 가지 일만 하고, 그것을 잘 해야 한다 |
| 2 | **Work Together** | 프로그램들이 함께 동작하도록 설계한다 |
| 3 | **Universal Interface** | 텍스트 스트림을 범용 인터페이스로 사용한다 |

**DOTADIW (Do One Thing And Do It Well)** - Unix 커뮤니티에서 가장 널리 받아들여지는 원칙

### Eric Raymond의 17가지 설계 규칙

| 규칙 | 설명 | 적용 예시 |
|------|------|----------|
| **Modularity** | 깔끔한 인터페이스로 연결된 단순한 부품을 작성 | 함수/클래스를 작고 독립적으로 유지 |
| **Clarity** | 명확함이 영리함보다 낫다 | 트릭보다 읽기 쉬운 코드 선호 |
| **Composition** | 다른 프로그램과 연결될 수 있도록 설계 | API는 조합 가능하게 설계 |
| **Separation** | 정책(policy)과 메커니즘(mechanism)을 분리 | 비즈니스 로직과 인프라 코드 분리 |
| **Simplicity** | 단순하게 설계하고, 필요한 경우에만 복잡성 추가 | YAGNI 원칙 준수 |
| **Parsimony** | 큰 프로그램은 다른 방법이 없을 때만 작성 | 작은 유틸리티 함수 선호 |
| **Transparency** | 검사와 디버깅이 쉽도록 가시성 있게 설계 | 로깅, 상태 노출 |
| **Robustness** | 견고함은 단순함과 투명함에서 나온다 | 예외 처리보다 예방적 설계 |
| **Representation** | 지식을 데이터에 담아 로직을 단순하게 유지 | 설정 파일, 테이블 기반 로직 |
| **Least Surprise** | 사용자가 예상하는 대로 동작 | 일관된 네이밍, 표준 패턴 사용 |
| **Silence** | 할 말이 없으면 아무것도 출력하지 않음 | 성공 시 불필요한 메시지 제거 |
| **Repair** | 실패할 때는 빠르고 시끄럽게 실패 | 조용한 실패 금지, 명확한 에러 |
| **Economy** | 프로그래머의 시간은 비싸다, 기계 시간으로 절약 | 자동화, 코드 생성 활용 |
| **Generation** | 손으로 코드 작성을 피하고 생성 프로그램 사용 | ORM, 코드 제너레이터 활용 |
| **Optimization** | 작동하게 만든 후 최적화하라 | 조기 최적화 금지 |
| **Diversity** | 모든 좋은 방법을 불신하라 | 단일 솔루션 강요 금지 |
| **Extensibility** | 미래를 위해 설계하라 | 확장 가능한 인터페이스 |

### 백엔드 리팩토링 적용 가이드

#### 1. 함수/클래스 분리 (Do One Thing Well)
```python
# ❌ 잘못된 예시 - 여러 가지 일을 하는 함수
def process_order(order_data):
    # 유효성 검사
    if not order_data.get('items'):
        raise ValueError("No items")
    # 가격 계산
    total = sum(item['price'] * item['qty'] for item in order_data['items'])
    # 할인 적용
    if order_data.get('coupon'):
        total *= 0.9
    # DB 저장
    db.save(order_data)
    # 이메일 발송
    send_email(order_data['email'], f"주문 완료: {total}원")
    return total

# ✅ 올바른 예시 - 각각 한 가지 일만 하는 함수들
def validate_order(order_data: dict) -> None:
    if not order_data.get('items'):
        raise ValueError("No items")

def calculate_total(items: list) -> int:
    return sum(item['price'] * item['qty'] for item in items)

def apply_discount(total: int, coupon: str | None) -> int:
    if coupon:
        return int(total * 0.9)
    return total

def save_order(order_data: dict) -> Order:
    return db.save(order_data)

def notify_customer(email: str, total: int) -> None:
    send_email(email, f"주문 완료: {total}원")
```

#### 2. 모듈 분리 (Separation)
```
backend/
├── app/
│   ├── api/           # API 라우터 (정책)
│   ├── services/      # 비즈니스 로직 (정책)
│   ├── repositories/  # 데이터 접근 (메커니즘)
│   ├── models/        # 데이터 모델 (표현)
│   └── utils/         # 유틸리티 (메커니즘)
```

#### 3. 인터페이스 설계 (Composition)
```python
# ✅ 조합 가능한 인터페이스
class OrderService:
    def __init__(
        self,
        validator: OrderValidator,
        calculator: PriceCalculator,
        repository: OrderRepository,
        notifier: Notifier
    ):
        self.validator = validator
        self.calculator = calculator
        self.repository = repository
        self.notifier = notifier
```

### 리팩토링 체크리스트

```
[ ] 각 함수/클래스가 한 가지 일만 하는가? (Do One Thing Well)
[ ] 함수 이름만 보고 무슨 일을 하는지 알 수 있는가? (Clarity)
[ ] 비즈니스 로직과 인프라 코드가 분리되어 있는가? (Separation)
[ ] 다른 모듈과 쉽게 조합할 수 있는가? (Composition)
[ ] 불필요한 복잡성이 없는가? (Simplicity)
[ ] 에러 발생 시 명확하게 실패하는가? (Repair)
[ ] 테스트하기 쉬운 구조인가? (Transparency)
```

### 마이크로서비스와 Unix Philosophy

Unix Philosophy의 "작고, 집중된 컴포넌트" 원칙은 현대의 **마이크로서비스 아키텍처**에 직접적인 영향을 주었다.

| Unix Philosophy | 마이크로서비스 적용 |
|-----------------|-------------------|
| Do One Thing Well | 각 서비스는 하나의 비즈니스 기능만 담당 |
| Work Together | API를 통한 서비스 간 통신 |
| Text Streams | JSON/REST API를 범용 인터페이스로 사용 |

**참고 자료**:
- [Unix philosophy - Wikipedia](https://en.wikipedia.org/wiki/Unix_philosophy)
- [The Art of Unix Programming - Eric Raymond](https://cscie28.dce.harvard.edu/reference/programming/unix-esr.html)
- [17 Principles of Unix Software Design](https://paulvanderlaken.com/2019/09/17/17-principles-of-unix-software-design/)

---

## Backend Configuration (CRITICAL)

백엔드 개발 시 반드시 적용해야 할 설정들입니다.

### Allowed Hosts & CORS

**필수 설정**:
1. **Allowed Hosts**: 모든 호스트 허용 (`*`)
2. **CORS Origin**: CORS origin 에러가 발생하지 않도록 설정

이는 개발 환경에서 프론트엔드와 백엔드 간의 통신 문제를 방지하기 위함입니다.

### FastAPI 설정 방법

**main.py 또는 app/__init__.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Coding Template API",
    description="Bitcoin 블록체인 분석 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 origin 허용 (개발 환경)
    allow_credentials=True,     # 쿠키 포함 요청 허용
    allow_methods=["*"],        # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],        # 모든 헤더 허용
)
```

### 환경별 설정 예시

더 나은 방법은 환경 변수를 사용하여 개발/프로덕션 환경을 구분하는 것입니다:

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 환경 설정
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI()

# 환경에 따른 CORS 설정
if ENVIRONMENT == "development":
    # 개발 환경: 모든 origin 허용
    origins = ["*"]
else:
    # 프로덕션: 특정 origin만 허용
    origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 확인 방법

CORS가 올바르게 설정되었는지 확인:
```bash
# 브라우저 개발자 도구 콘솔에서 확인
# CORS 에러가 없어야 함:
# ❌ "Access to fetch at '...' from origin '...' has been blocked by CORS policy"
# ✅ 정상적으로 API 요청이 성공함
```

### 주의사항

- **개발 환경**: 편의를 위해 모든 origin 허용 (`allow_origins=["*"]`)
- **프로덕션 환경**: 보안을 위해 특정 origin만 허용 (도메인 명시)
- **allow_credentials=True** 사용 시 `allow_origins=["*"]`는 보안상 권장되지 않으나, 개발 환경에서는 편의성을 우선

---

## Git Rules
4) git commit message는 알아서 만들 것
   - 변경 내용 기반으로 명확하고 간결한 메시지를 자동 생성한다.
   - 커밋 메시지는 한국어로 작성한다.
   - 가능하면 Conventional Commits 형식(예: `fix: ...`, `feat: ...`, `refactor: ...`)을 따른다.
- 단, 실행 환경 제약(샌드박스 등)으로 git이 실패하면:
  - 실패 원인을 사용자에게 알리고, 사용자가 로컬 터미널에서 실행할 수 있도록 필요한 명령을 제시한다.

---

## Debugging & Logging (중요)

### 로그 파일 위치
- **Backend**: `backend/debug.log`
- **Frontend**: `frontend/debug.log`

### 로깅 원칙
1) **상세한 로그 기록 필수**
   - 모든 주요 동작에 대해 상세한 로그를 남긴다.
   - 디버깅이 쉽도록 충분한 컨텍스트 정보를 포함한다.

2) **로그 레벨**
   - `DEBUG`: 상세한 디버깅 정보 (개발 단계)
   - `INFO`: 일반적인 정보 (주요 동작 시작/완료)
   - `WARNING`: 경고 (잠재적 문제)
   - `ERROR`: 에러 (예외 발생, 실패)
   - `CRITICAL`: 치명적 오류 (서비스 중단 수준)

3) **로그 포맷**
   ```
   [YYYY-MM-DD HH:MM:SS] [LEVEL] [파일명:라인] 메시지
   ```

### Backend 로깅 (Python)

**설정 예시** (`backend/app/logger.py`):
```python
import logging
from datetime import datetime

# 로거 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)

logger = logging.getLogger(__name__)
```

**로깅해야 할 항목**:
- API 요청/응답 (엔드포인트, 파라미터, 상태 코드)
- 데이터베이스 쿼리 (SQL, 실행 시간)
- Bitcoin RPC 호출 (메서드, 파라미터, 응답)
- 클러스터링 작업 (시작/종료, 처리된 데이터 수)
- 예외 및 에러 (스택 트레이스 포함)
- 성능 메트릭 (처리 시간, 메모리 사용량)

**예시**:
```python
# API 요청 로깅
logger.info(f"API Request: GET /api/v1/addresses/{address}")

# 데이터베이스 쿼리
logger.debug(f"DB Query: SELECT * FROM addresses WHERE cluster_id = {cluster_id}")

# 에러 로깅
try:
    result = some_function()
except Exception as e:
    logger.error(f"Error in some_function: {str(e)}", exc_info=True)

# 성능 로깅
import time
start = time.time()
process_data()
logger.info(f"process_data completed in {time.time() - start:.2f}s")
```

### Frontend 로깅 (JavaScript/TypeScript)

**설정 예시** (`frontend/src/utils/logger.js`):
```javascript
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARNING: 2,
  ERROR: 3,
  CRITICAL: 4
};

class Logger {
  constructor() {
    this.logFile = 'debug.log';
    this.minLevel = LOG_LEVELS.DEBUG;
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const caller = new Error().stack.split('\n')[3].trim();
    let log = `[${timestamp}] [${level}] ${message}`;
    if (data) {
      log += ` | Data: ${JSON.stringify(data)}`;
    }
    return log;
  }

  async writeLog(level, message, data = null) {
    const logMessage = this.formatMessage(level, message, data);

    // 콘솔 출력
    console.log(logMessage);

    // 파일에 저장 (개발 환경)
    if (import.meta.env.DEV) {
      // Node.js fs 또는 브라우저 localStorage 사용
      const logs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
      logs.push(logMessage);
      localStorage.setItem('debug_logs', JSON.stringify(logs));
    }
  }

  debug(message, data) { this.writeLog('DEBUG', message, data); }
  info(message, data) { this.writeLog('INFO', message, data); }
  warning(message, data) { this.writeLog('WARNING', message, data); }
  error(message, data) { this.writeLog('ERROR', message, data); }
  critical(message, data) { this.writeLog('CRITICAL', message, data); }
}

export const logger = new Logger();
```

**로깅해야 할 항목**:
- 페이지 로드 및 컴포넌트 마운트
- API 호출 (URL, 파라미터, 응답 시간, 상태)
- 사용자 인터랙션 (버튼 클릭, 입력, 검색)
- 상태 변경 (Redux/Context 상태 업데이트)
- 렌더링 성능 (컴포넌트 렌더링 시간)
- 에러 및 예외 (네트워크 오류, 파싱 오류)
- 브라우저 정보 (User Agent, 화면 크기)

**예시**:
```javascript
import { logger } from '@/utils/logger';

// API 호출 로깅
const fetchAddress = async (address) => {
  logger.info(`Fetching address data: ${address}`);

  try {
    const start = performance.now();
    const response = await fetch(`/api/v1/addresses/${address}`);
    const duration = performance.now() - start;

    logger.info(`API response received in ${duration.toFixed(2)}ms`, {
      status: response.status,
      address
    });

    return await response.json();
  } catch (error) {
    logger.error(`Failed to fetch address: ${address}`, { error: error.message });
    throw error;
  }
};

// 사용자 인터랙션 로깅
const handleSearchClick = () => {
  logger.debug('Search button clicked', { query: searchQuery });
  performSearch(searchQuery);
};

// 상태 변경 로깅
useEffect(() => {
  logger.debug('Cluster data updated', {
    clusterCount: clusters.length,
    totalAddresses: clusters.reduce((sum, c) => sum + c.addressCount, 0)
  });
}, [clusters]);
```

### 로그 파일 관리

1) **로그 로테이션**
   - 로그 파일이 너무 커지지 않도록 주기적으로 순환
   - 예: `debug.log`, `debug.log.1`, `debug.log.2`

2) **.gitignore에 추가**
   ```
   backend/debug.log
   backend/debug.log.*
   frontend/debug.log
   frontend/debug.log.*
   ```

3) **개발 시 로그 확인**
   ```bash
   # 실시간 로그 확인
   tail -f backend/debug.log
   tail -f frontend/debug.log

   # 에러만 필터링
   grep ERROR backend/debug.log
   ```

### 프로덕션 환경

- 프로덕션에서는 `INFO` 레벨 이상만 로깅
- 민감한 정보 (비밀번호, 토큰) 로깅 금지
- 로그 집계 시스템 사용 (Sentry, LogRocket 등)

---

## 사용자에게 에러 표시 (CRITICAL)

### 기본 원칙
**에러 발생 시 사용자에게 자세한 에러 메시지를 웹 UI에 표시해야 합니다.**

이는 디버깅을 위해 필수적입니다:
- 개발자가 문제를 빠르게 파악할 수 있음
- 사용자가 문제를 정확히 보고할 수 있음
- 로그만으로는 재현하기 어려운 문제를 추적 가능

### Backend에서 에러 응답

**에러 발생 시 상세 정보를 포함한 JSON 응답**:

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """모든 예외를 캐치하여 상세 정보 반환"""

    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # 개발 환경: 상세 에러 정보 포함
    if settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

    # 프로덕션: 일반적인 메시지
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "type": "ServerError",
                "message": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "timestamp": datetime.now().isoformat()
            }
        }
    )

# 특정 엔드포인트에서 에러 처리
@app.get("/api/v1/addresses/{address}")
async def get_address(address: str):
    try:
        result = fetch_address_from_db(address)
        if not result:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"주소를 찾을 수 없습니다: {address}",
                    "address": address,
                    "suggestion": "주소가 올바른지 확인해주세요."
                }
            )
        return result

    except ValueError as e:
        logger.error(f"Invalid address format: {address}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "message": "잘못된 주소 형식입니다.",
                "address": address,
                "error": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Error fetching address: {address}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "주소 조회 중 오류가 발생했습니다.",
                "error": str(e),
                "type": type(e).__name__
            }
        )
```

### Frontend에서 에러 표시

**1. 에러 토스트/알림 표시**:

```javascript
import { toast } from 'react-hot-toast';  // 또는 다른 알림 라이브러리

const fetchAddress = async (address) => {
  try {
    const response = await fetch(`/api/v1/addresses/${address}`);

    if (!response.ok) {
      const errorData = await response.json();

      // 사용자에게 에러 표시
      showErrorToUser(errorData);

      throw new Error(errorData.error?.message || 'API 요청 실패');
    }

    return await response.json();

  } catch (error) {
    logger.error('Failed to fetch address', { address, error: error.message });

    // 네트워크 에러 등
    showErrorToUser({
      error: {
        message: '네트워크 오류가 발생했습니다.',
        details: error.message
      }
    });

    throw error;
  }
};

// 에러를 사용자에게 표시하는 함수
const showErrorToUser = (errorData) => {
  const { error } = errorData;

  // Toast 알림으로 표시
  toast.error(
    <div>
      <div className="font-bold">{error.message}</div>
      {error.details && (
        <div className="text-sm mt-1 opacity-80">{error.details}</div>
      )}
      {error.type && (
        <div className="text-xs mt-1 opacity-60">타입: {error.type}</div>
      )}
    </div>,
    {
      duration: 5000,
      position: 'top-right'
    }
  );

  // 또는 모달로 표시
  // openErrorModal(error);
};
```

**2. 전역 에러 바운더리**:

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    logger.error('React Error Boundary caught error', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack
    });

    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50">
          <div className="max-w-2xl p-8 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-red-600 mb-4">
              오류가 발생했습니다
            </h2>

            <div className="mb-4">
              <p className="text-gray-700 mb-2">
                {this.state.error?.message || '알 수 없는 오류'}
              </p>
            </div>

            {/* 개발 환경에서만 상세 정보 표시 */}
            {import.meta.env.DEV && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-gray-600">
                  상세 정보 보기
                </summary>
                <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
                  {this.state.error?.stack}
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              페이지 새로고침
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// App.jsx에서 사용
function App() {
  return (
    <ErrorBoundary>
      <YourApp />
    </ErrorBoundary>
  );
}
```

**3. 에러 표시 컴포넌트**:

```javascript
// ErrorAlert.jsx
export const ErrorAlert = ({ error, onClose }) => {
  if (!error) return null;

  return (
    <div className="fixed top-4 right-4 max-w-md bg-red-50 border-l-4 border-red-500 p-4 shadow-lg rounded">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {/* Lucide React 아이콘 사용 */}
          <AlertCircle className="h-5 w-5 text-red-500" />
        </div>

        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            {error.message || '오류 발생'}
          </h3>

          {error.details && (
            <p className="mt-2 text-sm text-red-700">
              {error.details}
            </p>
          )}

          {import.meta.env.DEV && error.type && (
            <p className="mt-1 text-xs text-red-600">
              타입: {error.type}
            </p>
          )}

          {import.meta.env.DEV && error.traceback && (
            <details className="mt-2">
              <summary className="text-xs text-red-600 cursor-pointer">
                스택 트레이스
              </summary>
              <pre className="mt-1 text-xs bg-red-100 p-2 rounded overflow-auto max-h-40">
                {error.traceback}
              </pre>
            </details>
          )}
        </div>

        <button
          onClick={onClose}
          className="ml-3 flex-shrink-0 text-red-500 hover:text-red-700"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

// 사용 예시
function MyComponent() {
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    try {
      await apiCall();
    } catch (err) {
      setError(err.response?.data?.error || { message: err.message });
    }
  };

  return (
    <>
      <ErrorAlert error={error} onClose={() => setError(null)} />
      {/* 나머지 UI */}
    </>
  );
}
```

### 에러 메시지 가이드라인

1. **명확성**: 무엇이 잘못되었는지 명확히 표시
   ```
   ✅ "주소 형식이 올바르지 않습니다: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
   ❌ "오류 발생"
   ```

2. **해결 방법 제시**: 사용자가 어떻게 해야 하는지 안내
   ```
   ✅ "비트코인 주소를 찾을 수 없습니다. 주소를 다시 확인하거나 데이터 동기화를 기다려주세요."
   ❌ "404 Not Found"
   ```

3. **개발 환경에서만 상세 정보**:
   - 개발: 스택 트레이스, 에러 타입, 원본 메시지
   - 프로덕션: 일반적인 메시지만

4. **다국어 지원 고려**:
   ```javascript
   const errorMessages = {
     NETWORK_ERROR: "네트워크 연결을 확인해주세요.",
     NOT_FOUND: "요청한 리소스를 찾을 수 없습니다.",
     // ...
   };
   ```

### 체크리스트

- [ ] Backend에서 모든 예외에 대해 상세한 에러 응답 반환
- [ ] Frontend에서 API 에러를 사용자에게 표시
- [ ] 전역 에러 바운더리 구현
- [ ] 개발 환경에서 스택 트레이스 표시
- [ ] 프로덕션에서 민감 정보 숨김
- [ ] 에러 로그와 UI 표시 모두 수행

---

**중요**: 디버깅을 위해 충분히 상세한 로그를 남기는 것은 필수입니다. 로그가 부족하면 문제 해결이 어려우므로 항상 주요 동작에 대한 로그를 기록하세요. **또한 에러 발생 시 사용자에게도 명확한 에러 메시지를 보여주어야 합니다.**

---

## Railway 배포 전 체크리스트 (CRITICAL)

**`git push` 또는 Railway 배포 요청 전에 반드시 아래 항목을 확인해야 한다.**

확인되지 않은 항목이 있으면 **배포를 진행하지 말고 사용자에게 질문**하여 확인받아야 한다.

### 필수 확인 항목

#### 1. Backend 필수 구현 사항

| 항목 | 설명 | 확인 방법 |
|------|------|----------|
| `/health` 엔드포인트 | Railway 헬스체크용 | `GET /health` 응답 확인 |
| Static 파일 서빙 | Frontend 빌드 파일 서빙 | FastAPI StaticFiles 설정 |
| PORT 환경변수 사용 | Railway가 주입하는 포트 | `os.getenv("PORT", 8000)` |
| CORS 설정 | 프로덕션 origin 허용 | CORSMiddleware 설정 |

**필수 코드 예시**:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Health check 엔드포인트 (필수)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Static 파일 서빙 (Frontend 빌드 결과물)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 경로가 아닌 경우 index.html 반환 (SPA 지원)
        if not full_path.startswith("api/"):
            return FileResponse("static/index.html")
```

#### 2. Frontend 빌드 설정

| 항목 | 설명 | 확인 방법 |
|------|------|----------|
| `npm run build` 성공 | 빌드 에러 없음 | dist/ 폴더 생성 확인 |
| API URL 설정 | 프로덕션 API 경로 | 상대경로 또는 환경변수 |
| 환경변수 | VITE_* 변수 설정 | .env.production 확인 |

**프로덕션 API URL 설정**:
```javascript
// 상대 경로 사용 (권장)
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

// 또는 환경별 분기
const API_URL = import.meta.env.PROD
  ? '/api/v1'  // 프로덕션: 같은 도메인
  : 'http://localhost:8000/api/v1';  // 개발: 로컬 백엔드
```

#### 3. Dockerfile 확인

| 항목 | 설명 |
|------|------|
| Multi-stage 빌드 | Frontend 빌드 → Backend 실행 |
| static/ 복사 | Frontend 빌드 결과물 복사 |
| PORT 환경변수 | `${PORT:-8000}` 사용 |
| HEALTHCHECK | `/health` 엔드포인트 호출 |

#### 4. 환경변수 확인

**Railway 대시보드에서 설정해야 할 변수**:
```
DATABASE_URL=postgresql://...  (Railway PostgreSQL 연결 시 자동)
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

### 체크리스트

배포 전 아래 항목을 모두 확인:

```
[ ] Backend에 /health 엔드포인트가 구현되어 있는가?
[ ] Backend에서 static/ 폴더의 Frontend 파일을 서빙하는가?
[ ] Backend가 PORT 환경변수를 사용하는가?
[ ] Frontend 빌드가 성공하는가? (npm run build)
[ ] Frontend API URL이 프로덕션에 맞게 설정되어 있는가?
[ ] Dockerfile이 올바르게 설정되어 있는가?
[ ] railway.toml이 존재하는가?
[ ] 필수 환경변수 목록이 문서화되어 있는가?
```

### 확인되지 않은 경우 질문 예시

```
"Railway 배포 전 확인이 필요합니다:

1. Backend에 /health 엔드포인트가 구현되어 있지 않습니다.
   → 구현해도 될까요?

2. Frontend 빌드 파일을 서빙하는 코드가 없습니다.
   → Backend에 static 파일 서빙 코드를 추가해도 될까요?

3. 환경변수 SECRET_KEY가 설정되지 않았습니다.
   → Railway 대시보드에서 설정하셨나요?"
```

### 배포 실패 시 확인 사항

1. **빌드 실패**: `railway logs` 확인
2. **헬스체크 실패**: `/health` 엔드포인트 응답 확인
3. **502 에러**: Backend 시작 로그 확인, PORT 환경변수 사용 확인
4. **404 에러**: Static 파일 서빙 설정 확인

---

## samples 디렉토리 활용 (기능 테스트)

**새로운 기능 추가 시 먼저 samples 디렉토리에서 독립적으로 테스트한다.**

### 목적
- 새 기능을 바로 코드에 적용하기 전에 독립적으로 테스트
- 문제 발생 시 롤백 용이
- 사용자가 기능 동작을 확인 후 통합 여부 결정

### 워크플로우
1. **테스트 파일 생성**: 새 기능 추가 요청 시 `samples/` 디렉토리에 테스트 파일 생성
2. **독립 실행**: 테스트 파일을 단독으로 실행하여 기능 동작 확인
3. **사용자 확인**: 테스트 완료 후 사용자에게 질문
   ```
   "테스트가 완료되었습니다. 이 기능을 코드에 반영하시겠습니까?"
   ```
4. **통합**: 승인 후 실제 코드에 통합

### 예시
```
samples/
├── gpt5_mini_example.py      # GPT-5-mini API 테스트
├── redis_cache_example.py    # Redis 캐싱 테스트
└── websocket_example.py      # WebSocket 연결 테스트
```

### 체크리스트
- [ ] 새 기능 요청 시 samples 디렉토리에 테스트 파일 생성
- [ ] 테스트 파일 단독 실행으로 기능 확인
- [ ] 사용자에게 통합 여부 질문
- [ ] 승인 후 실제 코드에 반영
