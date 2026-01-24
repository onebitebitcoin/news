#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 결과 변수
BACKEND_LINT="SKIP"
BACKEND_TEST="SKIP"
FRONTEND_LINT="SKIP"
FRONTEND_TEST="SKIP"

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

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

echo "========================================"
echo "  Bitcoin News - Test Runner"
echo "========================================"

# Backend Lint & Test
if [ "$RUN_BACKEND" = true ]; then
    echo ""
    echo -e "${YELLOW}[Backend] Running lint...${NC}"
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate 2>/dev/null || true

    if ruff check . 2>/dev/null; then
        BACKEND_LINT="PASS"
        echo -e "${GREEN}Backend lint: PASS${NC}"
    else
        BACKEND_LINT="FAIL"
        echo -e "${RED}Backend lint: FAIL${NC}"
    fi

    echo ""
    echo -e "${YELLOW}[Backend] Running tests...${NC}"
    if [ "$COVERAGE" = true ]; then
        if pytest "$PROJECT_ROOT/tests/backend" -v --cov=app --cov-report=html 2>/dev/null; then
            BACKEND_TEST="PASS"
        else
            BACKEND_TEST="FAIL"
        fi
    else
        if pytest "$PROJECT_ROOT/tests/backend" -v 2>/dev/null; then
            BACKEND_TEST="PASS"
            echo -e "${GREEN}Backend tests: PASS${NC}"
        else
            BACKEND_TEST="FAIL"
            echo -e "${RED}Backend tests: FAIL${NC}"
        fi
    fi
    cd "$PROJECT_ROOT"
fi

# Frontend Lint & Test
if [ "$RUN_FRONTEND" = true ]; then
    echo ""
    echo -e "${YELLOW}[Frontend] Running lint...${NC}"
    cd "$PROJECT_ROOT/frontend"

    if npm run lint 2>/dev/null; then
        FRONTEND_LINT="PASS"
        echo -e "${GREEN}Frontend lint: PASS${NC}"
    else
        FRONTEND_LINT="FAIL"
        echo -e "${RED}Frontend lint: FAIL${NC}"
    fi

    echo ""
    echo -e "${YELLOW}[Frontend] Running tests...${NC}"
    if [ "$WATCH_MODE" = true ]; then
        npm run test -- --watch
        FRONTEND_TEST="SKIP"
    elif [ "$COVERAGE" = true ]; then
        if npm run test -- --coverage 2>/dev/null; then
            FRONTEND_TEST="PASS"
        else
            FRONTEND_TEST="FAIL"
        fi
    else
        if npm run test 2>/dev/null; then
            FRONTEND_TEST="PASS"
            echo -e "${GREEN}Frontend tests: PASS${NC}"
        else
            FRONTEND_TEST="FAIL"
            echo -e "${RED}Frontend tests: FAIL${NC}"
        fi
    fi
    cd "$PROJECT_ROOT"
fi

# 결과 출력
echo ""
echo "========================================"
echo "           테스트 결과"
echo "========================================"
echo ""
echo "| 구분           | 결과       |"
echo "|----------------|------------|"
echo "| Backend Lint   | $BACKEND_LINT |"
echo "| Backend Test   | $BACKEND_TEST |"
echo "| Frontend Lint  | $FRONTEND_LINT |"
echo "| Frontend Test  | $FRONTEND_TEST |"
echo ""

# 최종 결과
if [ "$BACKEND_LINT" = "FAIL" ] || [ "$BACKEND_TEST" = "FAIL" ] || \
   [ "$FRONTEND_LINT" = "FAIL" ] || [ "$FRONTEND_TEST" = "FAIL" ]; then
    echo -e "${RED}========================================"
    echo "  최종 결과: FAIL"
    echo "========================================${NC}"
    exit 1
else
    echo -e "${GREEN}========================================"
    echo "  최종 결과: PASS"
    echo "========================================${NC}"
    exit 0
fi
