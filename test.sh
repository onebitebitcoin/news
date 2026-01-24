#!/bin/bash

# AI Coding Template - Test Runner
# 유닛 테스트, 통합 테스트, E2E 테스트를 실행합니다

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
else
    error "가상환경이 없습니다. 먼저 ./install.sh를 실행하세요."
    exit 1
fi

# .env 파일 로드
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 함수: 백엔드 유닛 테스트
run_backend_unit_tests() {
    info "백엔드 유닛 테스트 실행 중..."

    if [ ! -d "backend/tests" ]; then
        error "backend/tests/ 디렉토리가 없습니다."
        return 1
    fi

    cd backend

    if [ "$COVERAGE" = "true" ]; then
        pytest tests/unit/ -v --cov=app --cov-report=html --cov-report=term
    else
        pytest tests/unit/ -v
    fi

    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "백엔드 유닛 테스트 통과"
    else
        error "백엔드 유닛 테스트 실패"
        return 1
    fi
}

# 함수: 백엔드 통합 테스트
run_backend_integration_tests() {
    info "백엔드 통합 테스트 실행 중..."

    if [ ! -d "backend/tests/integration" ]; then
        error "backend/tests/integration/ 디렉토리가 없습니다."
        return 1
    fi

    cd backend
    pytest tests/integration/ -v
    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "백엔드 통합 테스트 통과"
    else
        error "백엔드 통합 테스트 실패"
        return 1
    fi
}

# 함수: 프론트엔드 테스트
run_frontend_tests() {
    info "프론트엔드 테스트 실행 중..."

    if [ ! -d "frontend" ]; then
        error "frontend/ 디렉토리가 없습니다."
        return 1
    fi

    cd frontend

    if [ "$COVERAGE" = "true" ]; then
        npm run test:coverage
    else
        npm run test
    fi

    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "프론트엔드 테스트 통과"
    else
        error "프론트엔드 테스트 실패"
        return 1
    fi
}

# 함수: E2E 테스트
run_e2e_tests() {
    info "E2E 테스트 실행 중..."

    # 백엔드 서버 시작
    info "테스트용 백엔드 서버 시작 중..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    cd ..

    # 서버 시작 대기
    sleep 3

    # Playwright E2E 테스트 실행
    if [ -d "frontend/e2e" ]; then
        cd frontend
        npm run test:e2e
        local EXIT_CODE=$?
        cd ..
    else
        error "E2E 테스트가 설정되지 않았습니다."
        EXIT_CODE=1
    fi

    # 테스트용 서버 종료
    kill $BACKEND_PID 2>/dev/null || true

    if [ $EXIT_CODE -eq 0 ]; then
        success "E2E 테스트 통과"
    else
        error "E2E 테스트 실패"
        return 1
    fi
}

# 함수: Lint 검사
run_lint() {
    info "코드 린트 검사 중..."

    # Backend: Ruff/Flake8
    if [ -d "backend" ]; then
        cd backend
        if command -v ruff &> /dev/null; then
            ruff check .
        elif command -v flake8 &> /dev/null; then
            flake8 app tests
        fi
        cd ..
    fi

    # Frontend: ESLint
    if [ -d "frontend" ]; then
        cd frontend
        npm run lint
        cd ..
    fi

    success "린트 검사 완료"
}

# 메인 로직
echo "=========================================="
echo "AI Coding Template - Test Runner"
echo "=========================================="
echo ""

# 옵션 파싱
MODE=${1:-"all"}
COVERAGE=false

for arg in "$@"; do
    if [ "$arg" = "--coverage" ]; then
        COVERAGE=true
    fi
done

FAILED=false

case $MODE in
    "unit")
        run_backend_unit_tests || FAILED=true
        ;;
    "integration")
        run_backend_integration_tests || FAILED=true
        ;;
    "frontend")
        run_frontend_tests || FAILED=true
        ;;
    "e2e")
        run_e2e_tests || FAILED=true
        ;;
    "lint")
        run_lint || FAILED=true
        ;;
    "all"|*)
        run_lint || FAILED=true
        echo ""
        run_backend_unit_tests || FAILED=true
        echo ""
        run_backend_integration_tests || FAILED=true
        echo ""
        run_frontend_tests || FAILED=true
        ;;
esac

echo ""
echo "=========================================="

if [ "$FAILED" = false ]; then
    success "모든 테스트가 통과했습니다!"

    if [ "$COVERAGE" = "true" ]; then
        echo ""
        info "커버리지 리포트: backend/htmlcov/index.html"
    fi

    exit 0
else
    error "일부 테스트가 실패했습니다."
    exit 1
fi
