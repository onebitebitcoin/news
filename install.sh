#!/bin/bash

# AI Coding Template - Installation Script
# 비개발자도 사용할 수 있도록 모든 의존성을 자동 설치합니다
# 지원 OS: macOS, Ubuntu/Debian, Windows (WSL)

set -e

echo "=========================================="
echo "AI Coding Template - Installation"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# OS 감지
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
    elif [[ -f /etc/redhat-release ]]; then
        OS="redhat"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    echo $OS
}

OS=$(detect_os)
info "감지된 OS: $OS"
echo ""

# ============================================
# 1. 패키지 매니저 설치/확인
# ============================================
echo "1. 패키지 매니저 확인 중..."

install_homebrew() {
    if ! command -v brew &> /dev/null; then
        info "Homebrew 설치 중... (macOS 패키지 매니저)"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Homebrew PATH 설정
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        success "Homebrew 설치 완료"
    else
        success "Homebrew 이미 설치됨"
    fi
}

update_apt() {
    info "패키지 목록 업데이트 중..."
    sudo apt-get update -y
    success "패키지 목록 업데이트 완료"
}

case $OS in
    "macos")
        install_homebrew
        ;;
    "debian"|"windows")
        update_apt
        ;;
    "redhat")
        info "yum/dnf 사용"
        ;;
    *)
        warning "알 수 없는 OS입니다. 수동 설치가 필요할 수 있습니다."
        ;;
esac

echo ""

# ============================================
# 2. Node.js 설치
# ============================================
echo "2. Node.js 확인 중..."

install_nodejs() {
    case $OS in
        "macos")
            info "Node.js 설치 중 (Homebrew)..."
            brew install node
            ;;
        "debian"|"windows")
            info "Node.js 설치 중 (apt)..."
            # NodeSource 저장소 추가 (Node.js 20.x LTS)
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "redhat")
            info "Node.js 설치 중 (dnf)..."
            sudo dnf install -y nodejs
            ;;
    esac
}

if ! command -v node &> /dev/null; then
    warning "Node.js가 설치되어 있지 않습니다."
    install_nodejs
    success "Node.js 설치 완료"
else
    NODE_VERSION=$(node -v)
    success "Node.js $NODE_VERSION 이미 설치됨"
fi

# npm 확인
if ! command -v npm &> /dev/null; then
    error "npm이 설치되어 있지 않습니다."
    exit 1
fi

echo ""

# ============================================
# 3. Python 설치
# ============================================
echo "3. Python 확인 중..."

install_python() {
    case $OS in
        "macos")
            info "Python 설치 중 (Homebrew)..."
            brew install python@3.11
            ;;
        "debian"|"windows")
            info "Python 설치 중 (apt)..."
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        "redhat")
            info "Python 설치 중 (dnf)..."
            sudo dnf install -y python3 python3-pip
            ;;
    esac
}

if ! command -v python3 &> /dev/null; then
    warning "Python3가 설치되어 있지 않습니다."
    install_python
    success "Python 설치 완료"
else
    PYTHON_VERSION=$(python3 --version)
    success "$PYTHON_VERSION 이미 설치됨"
fi

# pip 확인
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    warning "pip가 없습니다. 설치 중..."
    case $OS in
        "macos")
            python3 -m ensurepip --upgrade
            ;;
        "debian"|"windows")
            sudo apt-get install -y python3-pip
            ;;
    esac
fi

echo ""

# ============================================
# 4. Git 설치 (선택)
# ============================================
echo "4. Git 확인 중..."

install_git() {
    case $OS in
        "macos")
            info "Git 설치 중 (Homebrew)..."
            brew install git
            ;;
        "debian"|"windows")
            info "Git 설치 중 (apt)..."
            sudo apt-get install -y git
            ;;
        "redhat")
            info "Git 설치 중 (dnf)..."
            sudo dnf install -y git
            ;;
    esac
}

if ! command -v git &> /dev/null; then
    warning "Git이 설치되어 있지 않습니다."
    install_git
    success "Git 설치 완료"
else
    GIT_VERSION=$(git --version)
    success "$GIT_VERSION 이미 설치됨"
fi

echo ""

# ============================================
# 5. Python 가상환경 생성
# ============================================
echo "5. Python 가상환경 생성 중..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "가상환경 생성 완료"
else
    warning "가상환경이 이미 존재합니다. 건너뜁니다."
fi

# 가상환경 활성화
source venv/bin/activate
success "가상환경 활성화 완료"

echo ""

# ============================================
# 6. Backend 의존성 설치
# ============================================
echo "6. Backend 의존성 설치 중..."

if [ -f "backend/requirements.txt" ]; then
    cd backend
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    success "Backend 패키지 설치 완료"
else
    warning "backend/requirements.txt가 없습니다."
    info "프로젝트 생성 후 다시 install.sh를 실행하세요."
fi

echo ""

# ============================================
# 7. Frontend 의존성 설치
# ============================================
echo "7. Frontend 의존성 설치 중..."

if [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
    success "Frontend 패키지 설치 완료"
else
    warning "frontend/package.json이 없습니다."
    info "프로젝트 생성 후 다시 install.sh를 실행하세요."
fi

echo ""

# ============================================
# 8. 환경 변수 파일 생성
# ============================================
echo "8. 환경 변수 파일 확인 중..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        success ".env 파일 생성 완료"
        warning ".env 파일을 열어서 필요한 값을 설정하세요!"
    else
        warning ".env.example 파일이 없습니다."
    fi
else
    success ".env 파일이 이미 존재합니다."
fi

echo ""

# ============================================
# 9. 설치 완료
# ============================================
echo "=========================================="
echo -e "${GREEN}설치가 완료되었습니다!${NC}"
echo "=========================================="
echo ""
echo "설치된 도구:"
echo "  - Node.js: $(node -v 2>/dev/null || echo '미설치')"
echo "  - npm: $(npm -v 2>/dev/null || echo '미설치')"
echo "  - Python: $(python3 --version 2>/dev/null || echo '미설치')"
echo "  - pip: $(pip --version 2>/dev/null | cut -d' ' -f2 || echo '미설치')"
echo "  - Git: $(git --version 2>/dev/null | cut -d' ' -f3 || echo '미설치')"
echo ""
echo "다음 단계:"
echo "  1. 개발 서버 실행: ./dev.sh"
echo "  2. 테스트 실행: ./test.sh"
echo ""
echo "문제가 있으면 Claude Code에게 물어보세요:"
echo '  "에러 해결해줘: [에러 메시지]"'
echo ""
