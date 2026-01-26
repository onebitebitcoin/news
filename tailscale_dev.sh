#!/bin/bash

# Tailscale 외부 접속용 개발 서버
# Backend API를 Tailscale IP로 직접 접근하도록 설정

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# PID 파일 경로
BACKEND_PID_FILE=".backend.pid"
FRONTEND_PID_FILE=".frontend.pid"

# Tailscale IP 가져오기
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "")
if [ -z "$TAILSCALE_IP" ]; then
    echo -e "${RED}[ERROR]${NC} Tailscale IP를 가져올 수 없습니다."
    echo "Tailscale이 실행 중인지 확인하세요."
    exit 1
fi

echo "=========================================="
echo "Tailscale Development Server"
echo "=========================================="
echo ""
echo -e "${GREEN}Tailscale IP: $TAILSCALE_IP${NC}"
echo ""

# 함수: 메시지 출력
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# 함수: 서버 종료
cleanup() {
    echo ""
    info "서버를 종료합니다..."

    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat $BACKEND_PID_FILE)
        kill $BACKEND_PID 2>/dev/null || true
        rm $BACKEND_PID_FILE
        success "백엔드 서버 종료"
    fi

    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat $FRONTEND_PID_FILE)
        kill $FRONTEND_PID 2>/dev/null || true
        rm $FRONTEND_PID_FILE
        success "프론트엔드 서버 종료"
    fi

    exit 0
}

# Ctrl+C 처리
trap cleanup INT TERM

# 함수: 포트에서 실행 중인 프로세스 종료
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        info "포트 $port 에서 실행 중인 프로세스 종료됨"
        sleep 1
    fi
}

# 기존 프로세스 정리
info "기존 프로세스 정리 중..."
kill_port 6300
kill_port 6200

# 로그 파일 초기화
rm -f backend/debug.log frontend/debug.log
info "로그 파일 초기화 완료"

# 함수: 백엔드 서버 시작
start_backend() {
    info "백엔드 서버 시작 중..."

    if [ ! -d "backend" ]; then
        error "backend/ 디렉토리가 없습니다."
        exit 1
    fi

    # 가상환경 활성화
    if [ ! -d "venv" ]; then
        error "가상환경이 없습니다. 먼저 ./install.sh를 실행하세요."
        exit 1
    fi

    source venv/bin/activate

    # .env 파일 로드
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    cd backend

    # Uvicorn으로 FastAPI 서버 시작 (0.0.0.0으로 모든 인터페이스에서 접근 가능)
    uvicorn app.main:app --reload --host 0.0.0.0 --port 6300 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../$BACKEND_PID_FILE

    cd ..

    success "백엔드 서버 시작됨 (PID: $BACKEND_PID, Port: 6300)"
}

# 함수: 프론트엔드 서버 시작 (Tailscale IP로 API 접근)
start_frontend() {
    info "프론트엔드 서버 시작 중..."

    if [ ! -d "frontend" ]; then
        error "frontend/ 디렉토리가 없습니다."
        exit 1
    fi

    cd frontend

    # Tailscale IP로 API URL 설정 (Backend API prefix 포함)
    export VITE_API_URL="http://$TAILSCALE_IP:6300/api/v1"

    # Vite 개발 서버 시작 (--host로 외부 접근 허용)
    npm run dev -- --host &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../$FRONTEND_PID_FILE

    cd ..

    success "프론트엔드 서버 시작됨 (PID: $FRONTEND_PID, Port: 6200)"
}

# 메인 로직
start_backend
echo ""
sleep 2  # 백엔드 시작 대기
start_frontend

echo ""
echo "=========================================="
echo -e "${GREEN}[Tailscale 접속 주소]${NC}"
echo "   Frontend: http://$TAILSCALE_IP:6200"
echo "   Backend:  http://$TAILSCALE_IP:6300"
echo "   API 문서: http://$TAILSCALE_IP:6300/docs"
echo "=========================================="
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# 서버 로그 감시
wait
