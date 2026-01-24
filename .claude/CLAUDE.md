# Claude Project Rules

## Language
- 모든 답변은 한국어로 작성한다.
- 코드/로그/에러 메시지는 원문 유지, 설명은 한국어로 한다.

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

## Plan Mode 필수 (CRITICAL)

**모든 구현 작업은 반드시 Plan Mode로 시작해야 한다.**

### 원칙
- 코드 작성 전에 **항상 Plan Mode를 사용**하여 계획을 먼저 수립한다.
- 계획 없이 바로 구현하지 않는다.
- 사용자의 승인을 받은 후에 구현을 시작한다.

### Plan Mode 진입 시점
- 새로운 기능 구현 요청을 받았을 때
- 버그 수정이 복잡할 때
- 리팩토링 작업을 수행할 때
- 여러 파일을 수정해야 할 때

### Plan Mode에서 수행할 작업
1. **요구사항 분석**: 사용자 요청을 정확히 이해
2. **영향 범위 파악**: 수정이 필요한 파일/모듈 식별
3. **구현 계획 작성**: 단계별 작업 목록 작성
4. **위험 요소 식별**: 잠재적 문제점 미리 파악
5. **사용자 승인**: 계획을 사용자에게 제시하고 승인 요청

### 예외 사항 (Plan Mode 생략 가능)
- 단순 오타 수정
- 한 줄 변경 수준의 사소한 수정
- 사용자가 명시적으로 "바로 수정해줘"라고 요청한 경우

### 체크리스트
- [ ] Plan Mode로 진입했는가?
- [ ] 구현 계획을 작성했는가?
- [ ] 사용자 승인을 받았는가?
- [ ] 승인 후 구현을 시작했는가?

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
   - 텍스트에서 이모지 금지
   - UI에서는 아이콘 컴포넌트(예: lucide-react) 사용

2) **중첩된 카드뷰는 사용하지 말 것 (CRITICAL)**
   - Card 내부에 Card 중첩 금지
   - 섹션 분리는 divider/heading/spacing/background로 처리
   - 레이아웃 깊이는 최대 2단계까지만 허용

3) **심플한 디자인 유지 (CRITICAL)**
   - 웹 UI에 너무 많은 텍스트 설명 표시 금지
   - 긴 설명문, 상세 가이드는 최소화
   - 필요한 정보만 간결하게 표시
   - 상세 정보는 툴팁/모달로 숨김 처리
   - "Less is more" 원칙

4) **반응형 레이아웃 (모바일 친화적 웹페이지) (CRITICAL)**
   - **모바일 친화적인 웹페이지**를 기본으로 하되, **PC에서도 최적화된 경험 제공**
   - 작은 화면 가독성/터치 타깃 최우선
   - **모바일 좌우 padding은 최소한으로 설정** (예: px-2 또는 px-4)
   - 항상 UI 업데이트 시 모바일과 PC 양쪽에서 어떻게 보일지 고려

   **반응형 디자인 원칙**:
   - 모바일: 단일 컬럼, 터치 친화적, 최소 padding
   - 태블릿: 2컬럼 가능, 적절한 여백
   - PC: 최대 너비 제한 (max-w-screen-xl 등), 넓은 화면 활용

   **Tailwind CSS 반응형 예시**:
   ```jsx
   // 모바일 → 태블릿 → PC 순차 적용
   <div className="px-2 sm:px-4 md:px-6 lg:px-8 max-w-screen-xl mx-auto">
     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
       {/* 모바일: 1열, 태블릿: 2열, PC: 3열 */}
     </div>
   </div>
   ```

   **PC 레이아웃 고려사항**:
   - 넓은 화면에서 콘텐츠가 너무 퍼지지 않도록 max-width 설정
   - 사이드바, 다중 컬럼 레이아웃 활용 가능
   - 호버 상태 스타일 추가 (hover:bg-gray-100 등)
   - 마우스 사용자를 위한 더 작은 클릭 타깃 허용

   **사용자 요청 확인 (CRITICAL)**:
   - 사용자의 UI 요청이 특정 화면에만 한정되면 반드시 되물을 것
   - 질문 예시: "이 레이아웃을 모바일과 PC 양쪽에서 어떻게 보여줄까요?"
   - 반응형 호환성을 사용자에게 확인받고 진행

5) 시간/날짜는 항상 한국 시간(Asia/Seoul)을 기준으로 판단한다.

6) fallback 더미 값 주입으로 흐름을 숨기지 말 것
   - 디버깅을 어렵게 하므로 기본/더미 값으로 덮어쓰지 않는다.
   - 문제가 발생하면 에러 메시지를 명확히 노출한다.

7) 사용자 작업에는 성공/실패 메시지를 항상 노출할 것
   - 저장/추가/삭제/새로고침 등 주요 액션의 결과를 명확히 표시한다.

8) **디자인 레퍼런스 확인 (CRITICAL)**
   - UI 작업 전 `design/reference/` 폴더에 레퍼런스 이미지가 있는지 확인
   - 이미지가 있으면 해당 스타일을 분석하여 적용
   - 이미지가 없으면 사용자에게 디자인 방향을 질문:
     ```
     "design/reference 폴더에 레퍼런스 이미지가 없습니다.
     어떤 스타일로 디자인할까요?
     1. 깔끔한 미니멀 스타일
     2. 금융 앱 스타일 (토스, 뱅크샐러드)
     3. 기본 TailwindCSS 스타일
     4. 직접 설명해주세요"
     ```
   - 레퍼런스 이미지 확인 후 UI 컴포넌트 개발 시작

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

## Workflow
- 코드 수정 후 항상:
  1) **Lint 체크 (테스트 전 필수)**
     - Frontend (React): `npm run lint` (ESLint)
     - Backend (FastAPI): `ruff check .` 또는 `flake8`
     - 에러가 있으면 수정 후 다시 체크
  2) 테스트 실행 → PASS/FAIL 확인
  3) **테스트 결과를 테이블 형태로 출력 (필수)**
  4) FAIL이면 수정 후 재테스트
  5) **PASS면 반드시 `git add` → `git commit` 수행 (절대 누락 금지)**
  6) `git push`는 사용자가 명시적으로 요청할 때만 수행

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

- 데이터베이스 스키마가 변경되면 반드시 관련 API도 함께 업데이트해야 함
- CRUD 기능 개발/수정 시 스키마와 API를 항상 같이 취급할 것
- 스키마만 업데이트하고 API를 업데이트하지 않으면 불일치가 발생함

**예시**:
- 스키마에 새 필드 추가 → API response model에도 필드 추가
- 스키마에서 필드 제거 → API에서도 해당 필드 제거
- 스키마 필드 타입 변경 → API validation/serialization 로직도 변경

**체크리스트**:
1. 스키마 변경 시 영향받는 모든 API 엔드포인트 확인
2. Pydantic 모델 (request/response) 업데이트
3. API 문서 (Swagger) 자동 반영 확인
4. 테스트 코드 업데이트

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

### Allowed Hosts & CORS
백엔드 개발 시 다음 설정을 필수로 적용해야 한다:

1. **Allowed Hosts**: 모든 호스트 허용 (`*`)
2. **CORS Origin**: CORS origin 에러가 발생하지 않도록 설정

**FastAPI 설정 예시**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 - 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
```

**주의사항**:
- 개발 환경에서는 편의를 위해 모든 origin 허용
- 프로덕션 환경에서는 보안을 위해 특정 origin만 허용하도록 변경 필요

### Trailing Slash 통일 (CRITICAL)
**Frontend와 Backend에서 URL trailing slash를 반드시 통일해야 한다.**

`/api/users`와 `/api/users/`는 다른 URL로 처리될 수 있어 404 에러의 원인이 됨.

**규칙: Trailing Slash 없이 통일**

```
✅ 올바른 예시:
/api/v1/portfolio/summary
/api/v1/trades
/api/v1/stocks/AAPL

❌ 잘못된 예시:
/api/v1/portfolio/summary/
/api/v1/trades/
/api/v1/stocks/AAPL/
```

**Backend (FastAPI) 설정:**
```python
from fastapi import FastAPI

app = FastAPI()

# Trailing slash redirect 비활성화
app.router.redirect_slashes = False
```

**Frontend (Axios) 설정:**
```javascript
// API 호출 시 trailing slash 제거
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// URL 정규화 (trailing slash 제거)
api.interceptors.request.use((config) => {
  if (config.url && config.url.endsWith('/')) {
    config.url = config.url.slice(0, -1);
  }
  return config;
});
```

**체크리스트:**
- [ ] Backend API 엔드포인트에 trailing slash 없음
- [ ] Frontend API 호출 URL에 trailing slash 없음
- [ ] SPEC.md API Design 섹션 URL 형식 통일

## Git
4) git commit message는 알아서 만들 것
   - 변경 내용 기반으로 명확한 메시지를 자동 생성
   - 커밋 메시지는 한국어로 작성한다.
   - 가능하면 Conventional Commits 사용
- 단, 환경 제약으로 git이 실패하면 사용자에게 원인/대안 커맨드를 안내한다.

---

## Debugging & Logging

### 로그 파일
- **Backend**: `backend/debug.log` - 모든 백엔드 동작 로그
- **Frontend**: `frontend/debug.log` - 모든 프론트엔드 동작 로그

### 핫리로드 시 로그 초기화 (CRITICAL)
**개발 서버 재시작(핫리로드) 시 기존 로그 파일을 삭제하고 새로 생성한다.**

이유: 분석해야 할 로그 범위를 줄여 디버깅 효율을 높이기 위함

**Backend (Python) - 서버 시작 시:**
```python
import os

# 서버 시작 시 기존 로그 삭제
LOG_FILE = 'debug.log'
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
    print(f"[LOG] 기존 로그 파일 삭제: {LOG_FILE}")
```

**Frontend (JavaScript) - 앱 시작 시:**
```javascript
// App.jsx 또는 main.jsx 최상단
if (import.meta.env.DEV) {
  localStorage.removeItem('debug_logs');
  console.log('[LOG] 기존 로그 초기화');
}
```

**dev.sh 스크립트에서 처리:**
```bash
# 개발 서버 시작 전 로그 파일 삭제
rm -f backend/debug.log frontend/debug.log
echo "[LOG] 로그 파일 초기화 완료"
```

### 로깅 필수 사항
1) **상세한 로그 기록**
   - 모든 API 요청/응답
   - 데이터베이스 쿼리
   - 사용자 인터랙션
   - 에러 및 예외 (스택 트레이스 포함)
   - 성능 메트릭 (처리 시간)

2) **로그 포맷**
   ```
   [타임스탬프] [레벨] [위치] 메시지 [데이터]
   ```

3) **로그 레벨**
   - DEBUG: 상세 디버깅 정보
   - INFO: 일반 정보
   - WARNING: 경고
   - ERROR: 에러
   - CRITICAL: 치명적 오류

### Backend (Python)
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 사용 예시
logger.info(f"API Request: GET /api/v1/addresses/{address}")
logger.error(f"Database error: {str(e)}", exc_info=True)
```

### Frontend (JavaScript)
```javascript
// 로그 유틸리티
const logger = {
  log: (level, message, data) => {
    const timestamp = new Date().toISOString();
    const logMsg = `[${timestamp}] [${level}] ${message}`;
    console.log(logMsg, data || '');

    // localStorage에 저장
    const logs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    logs.push({ timestamp, level, message, data });
    localStorage.setItem('debug_logs', JSON.stringify(logs.slice(-1000)));
  },
  debug: (msg, data) => logger.log('DEBUG', msg, data),
  info: (msg, data) => logger.log('INFO', msg, data),
  error: (msg, data) => logger.log('ERROR', msg, data)
};

// 사용 예시
logger.info('Fetching address data', { address });
logger.error('API request failed', { error: error.message });
```

### 로그 확인
```bash
# 실시간 로그 모니터링
tail -f backend/debug.log
tail -f frontend/debug.log

# 에러만 필터링
grep ERROR backend/debug.log
```

---

## 사용자에게 에러 표시 (필수)

### 원칙
**에러 발생 시 사용자에게 웹 UI에서 자세한 에러 메시지를 보여주어야 합니다.**

### Backend
```python
from fastapi import HTTPException

@app.get("/api/v1/addresses/{address}")
async def get_address(address: str):
    try:
        result = fetch_address(address)
        return result
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

        # 개발: 상세 에러 정보 반환
        raise HTTPException(
            status_code=500,
            detail={
                "message": "주소 조회 중 오류 발생",
                "error": str(e),
                "type": type(e).__name__
            }
        )
```

### Frontend
```javascript
// 에러를 사용자에게 표시
const handleError = (error) => {
  // Toast 알림
  toast.error(
    <div>
      <div className="font-bold">{error.message}</div>
      {import.meta.env.DEV && error.details && (
        <div className="text-sm mt-1">{error.details}</div>
      )}
    </div>
  );

  logger.error('Error occurred', error);
};

// API 호출 시
try {
  const response = await fetch('/api/v1/addresses/...');
  if (!response.ok) {
    const errorData = await response.json();
    handleError(errorData.error);
  }
} catch (error) {
  handleError({ message: '네트워크 오류', details: error.message });
}
```

### 에러 표시 컴포넌트
```javascript
export const ErrorAlert = ({ error }) => (
  <div className="bg-red-50 border-l-4 border-red-500 p-4">
    <div className="font-bold">{error.message}</div>
    {import.meta.env.DEV && error.details && (
      <div className="text-sm mt-2">{error.details}</div>
    )}
  </div>
);
```

### 가이드라인
1. **명확한 메시지**: 무엇이 잘못되었는지 명확히 표시
2. **해결 방법 제시**: 사용자가 어떻게 해야 하는지 안내
3. **개발 환경 상세 정보**: 개발 시 스택 트레이스, 에러 타입 표시
4. **프로덕션 간소화**: 프로덕션에서는 민감 정보 숨김

**중요**: 문제 해결을 위해 충분히 상세한 로그를 남기고, **사용자에게도 명확한 에러 메시지를 표시**하는 것이 필수입니다.

---

## Claude Code 사용 가이드 (비개발자용)

이 템플릿은 비개발자도 Claude Code를 통해 프로젝트를 생성하고 배포할 수 있도록 설계되었습니다.

### 프로젝트 시작하기

**1. 프로젝트 생성**
```
"SPEC.md를 기반으로 프로젝트를 생성해줘"
```
- Claude Code가 frontend/, backend/ 폴더와 필요한 파일들을 자동 생성합니다.

**2. 의존성 설치**
```
"의존성 설치해줘" 또는 "./install.sh 실행해줘"
```

**3. 개발 서버 실행**
```
"개발 서버 실행해줘" 또는 "./dev.sh 실행해줘"
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API 문서: http://localhost:8000/docs

**4. 테스트 실행**
```
"테스트 실행해줘" 또는 "./test.sh 실행해줘"
```

### Railway 배포

**사전 준비** (최초 1회):
1. Railway 계정 생성: https://railway.app
2. Railway CLI 설치: `npm install -g @railway/cli`
3. Railway 로그인: `railway login`

**배포 요청**:
```
"Railway에 배포해줘"
```

Claude Code가 자동으로 수행하는 작업:
1. 테스트 실행 (통과 확인)
2. Git 커밋 (변경사항이 있는 경우)
3. `railway up` 실행 (Docker 빌드 및 배포)
4. 배포 URL 및 상태 확인

### 문제 해결

**배포 로그 확인**:
```
"배포 로그 확인해줘" 또는 "railway logs 실행해줘"
```

**배포 상태 확인**:
```
"배포 상태 확인해줘" 또는 "railway status 실행해줘"
```

**에러 발생 시**:
```
"에러 로그 확인해줘"
"문제 원인 분석해줘"
```

### SPEC.md 커스터마이징

새로운 프로젝트를 만들려면 SPEC.md 파일에서 다음을 수정하세요:

1. **프로젝트 이름/설명**: 1.1 Purpose 섹션
2. **데이터베이스 스키마**: 6. Database Schema 섹션
3. **API 엔드포인트**: 5. API Design 섹션
4. **UI 컴포넌트**: 8. Frontend Components 섹션

수정 후 Claude Code에게 "SPEC.md를 기반으로 프로젝트를 생성해줘"라고 요청하면 됩니다.

---

## 배포 설정

### Docker 기반 배포

이 프로젝트는 Dockerfile을 사용하여 Railway에 배포됩니다:

- **빌드**: Multi-stage Docker build
  - Stage 1: Node.js로 Frontend 빌드
  - Stage 2: Python으로 Backend 실행 + Frontend 정적 파일 서빙
- **헬스체크**: `/health` 엔드포인트
- **포트**: Railway가 자동으로 `PORT` 환경 변수 제공

### 환경 변수 (Railway 대시보드에서 설정)

**필수**:
- `DATABASE_URL`: PostgreSQL 연결 URL (Railway가 자동 제공)
- `SECRET_KEY`: 보안 키 (직접 설정)
- `ENVIRONMENT`: production

**선택**:
- `LOG_LEVEL`: INFO (기본값)
- `REDIS_URL`: Redis 연결 URL (캐싱 사용 시)

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
