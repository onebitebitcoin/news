#!/bin/bash

# AI Coding Template - Easy Start
# 대화형 인터페이스로 프로젝트 생성부터 배포까지 안내합니다

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 함수 정의
print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║            AI Coding Template - Easy Start                ║"
    echo "║                                                           ║"
    echo "║     비개발자도 쉽게 웹 앱을 만들고 배포할 수 있습니다      ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_step() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  Step $1: $2${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

press_enter() {
    echo ""
    echo -e "${YELLOW}계속하려면 Enter를 누르세요...${NC}"
    read
}

ask_yes_no() {
    while true; do
        echo -e "${CYAN}$1 (y/n): ${NC}"
        read -r answer
        case $answer in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "y 또는 n을 입력하세요.";;
        esac
    done
}

# ============================================
# 메인 시작
# ============================================
print_header

echo -e "${BOLD}안녕하세요! AI Coding Template에 오신 것을 환영합니다.${NC}"
echo ""
echo "이 스크립트는 다음 과정을 단계별로 안내합니다:"
echo ""
echo "  1. 환경 설치 (Node.js, Python 등)"
echo "  2. 프로젝트 설정 (SPEC.md)"
echo "  3. Claude Code로 프로젝트 구현"
echo "  4. 개발 서버 실행 및 확인"
echo "  5. 테스트 실행"
echo "  6. Git 저장"
echo "  7. Railway 배포"
echo ""

if ! ask_yes_no "시작할까요?"; then
    echo "다음에 다시 만나요!"
    exit 0
fi

# ============================================
# Step 1: 환경 설치
# ============================================
print_step "1/7" "환경 설치"

echo "Node.js, Python, Git 등 필요한 도구를 설치합니다."
echo "이미 설치된 도구는 건너뜁니다."
echo ""

if ask_yes_no "환경 설치를 진행할까요?"; then
    echo ""
    info "install.sh 실행 중..."
    echo ""

    if [ -f "./install.sh" ]; then
        chmod +x ./install.sh
        ./install.sh

        if [ $? -eq 0 ]; then
            success "환경 설치 완료!"
        else
            error "환경 설치 중 오류가 발생했습니다."
            echo "문제를 해결한 후 다시 시도하세요."
            exit 1
        fi
    else
        error "install.sh 파일을 찾을 수 없습니다."
        exit 1
    fi
else
    warning "환경 설치를 건너뜁니다. (이미 설치되어 있다면 OK)"
fi

press_enter

# ============================================
# Step 2: SPEC.md 설정
# ============================================
print_step "2/7" "프로젝트 설정 (SPEC.md)"

echo "SPEC.md 파일에 만들고 싶은 프로젝트를 정의합니다."
echo ""
echo "현재 SPEC.md에는 예시 프로젝트(Stock Portfolio Tracker)가 있습니다."
echo ""

echo -e "${CYAN}어떻게 하시겠습니까?${NC}"
echo "  1) 예시 프로젝트로 먼저 테스트하기"
echo "  2) SPEC.md를 직접 수정하기 (에디터 열기)"
echo "  3) 나중에 수정하기"
echo ""
echo -e "${CYAN}선택 (1/2/3): ${NC}"
read -r spec_choice

case $spec_choice in
    1)
        success "예시 프로젝트(Stock Portfolio Tracker)로 진행합니다."
        ;;
    2)
        info "SPEC.md 파일을 엽니다..."

        # 에디터 선택
        if command -v code &> /dev/null; then
            code SPEC.md
        elif command -v nano &> /dev/null; then
            nano SPEC.md
        elif command -v vim &> /dev/null; then
            vim SPEC.md
        else
            echo "SPEC.md 파일을 직접 열어서 수정하세요."
        fi

        echo ""
        echo -e "${YELLOW}SPEC.md 수정이 끝나면 Enter를 누르세요...${NC}"
        read
        success "SPEC.md 설정 완료!"
        ;;
    3)
        warning "SPEC.md 수정을 나중에 진행합니다."
        ;;
esac

press_enter

# ============================================
# Step 3: Claude Code로 프로젝트 구현
# ============================================
print_step "3/7" "Claude Code로 프로젝트 구현"

echo "이제 Claude Code를 실행하여 프로젝트를 구현합니다."
echo ""
echo -e "${BOLD}Claude Code에게 이렇게 말하세요:${NC}"
echo ""
echo -e "  ${GREEN}\"프로젝트 구현해줘\"${NC}"
echo ""
echo "또는:"
echo ""
echo -e "  ${GREEN}\"SPEC.md를 기반으로 프로젝트를 생성해줘\"${NC}"
echo ""

if ask_yes_no "Claude Code를 실행할까요?"; then
    if command -v claude &> /dev/null; then
        info "Claude Code를 실행합니다..."
        info "프로젝트 구현이 완료되면 Claude Code를 종료하고 돌아오세요."
        echo ""

        # Claude Code 실행
        claude

        success "Claude Code 세션 종료"
    else
        warning "Claude Code가 설치되어 있지 않습니다."
        echo ""
        echo "설치 방법:"
        echo "  npm install -g @anthropic-ai/claude-code"
        echo ""
        echo "설치 후 터미널에서 'claude'를 실행하세요."
    fi
else
    warning "Claude Code 실행을 건너뜁니다."
    echo "나중에 터미널에서 'claude'를 실행하세요."
fi

press_enter

# ============================================
# Step 4: 개발 서버 실행
# ============================================
print_step "4/7" "개발 서버 실행"

echo "Frontend와 Backend 개발 서버를 실행합니다."
echo ""
echo "실행 후 브라우저에서 확인할 수 있습니다:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo ""

if ask_yes_no "개발 서버를 실행할까요?"; then
    if [ -f "./dev.sh" ]; then
        chmod +x ./dev.sh

        info "개발 서버 실행 중... (종료: Ctrl+C)"
        echo ""

        ./dev.sh

        success "개발 서버 종료"
    else
        error "dev.sh 파일을 찾을 수 없습니다."
    fi
else
    warning "개발 서버 실행을 건너뜁니다."
fi

press_enter

# ============================================
# Step 5: 테스트 실행
# ============================================
print_step "5/7" "테스트 실행"

echo "린트 체크와 테스트를 실행하여 코드 품질을 확인합니다."
echo ""

if ask_yes_no "테스트를 실행할까요?"; then
    if [ -f "./test.sh" ]; then
        chmod +x ./test.sh

        info "테스트 실행 중..."
        echo ""

        ./test.sh

        if [ $? -eq 0 ]; then
            success "모든 테스트 통과!"
        else
            warning "일부 테스트가 실패했습니다."
            echo "Claude Code에게 \"테스트 실패 해결해줘\"라고 요청하세요."
        fi
    else
        error "test.sh 파일을 찾을 수 없습니다."
    fi
else
    warning "테스트 실행을 건너뜁니다."
fi

press_enter

# ============================================
# Step 6: Git 저장
# ============================================
print_step "6/7" "Git 저장"

echo "변경사항을 Git에 저장합니다."
echo ""

# Git 상태 확인
if [ -d ".git" ]; then
    echo "현재 Git 상태:"
    git status --short
    echo ""

    if ask_yes_no "변경사항을 커밋할까요?"; then
        echo ""
        echo -e "${CYAN}커밋 메시지를 입력하세요 (기본: 'Update project'):${NC}"
        read -r commit_msg

        if [ -z "$commit_msg" ]; then
            commit_msg="Update project"
        fi

        git add .
        git commit -m "$commit_msg"

        success "커밋 완료: $commit_msg"

        echo ""
        if ask_yes_no "원격 저장소에 Push할까요?"; then
            git push

            if [ $? -eq 0 ]; then
                success "Push 완료!"
            else
                warning "Push 실패. 원격 저장소 설정을 확인하세요."
            fi
        fi
    fi
else
    warning "Git 저장소가 초기화되어 있지 않습니다."

    if ask_yes_no "Git 저장소를 초기화할까요?"; then
        git init
        git add .
        git commit -m "Initial commit"
        success "Git 저장소 초기화 완료!"
    fi
fi

press_enter

# ============================================
# Step 7: Railway 배포
# ============================================
print_step "7/7" "Railway 배포"

echo "프로젝트를 Railway에 배포하여 인터넷에 공개합니다."
echo ""

# Railway CLI 확인
if ! command -v railway &> /dev/null; then
    warning "Railway CLI가 설치되어 있지 않습니다."
    echo ""

    if ask_yes_no "Railway CLI를 설치할까요?"; then
        npm install -g @railway/cli
        success "Railway CLI 설치 완료!"
    else
        echo "나중에 설치하려면: npm install -g @railway/cli"
        press_enter

        # 완료 화면으로 이동
        print_header
        echo -e "${GREEN}${BOLD}축하합니다! 프로젝트 설정이 완료되었습니다.${NC}"
        echo ""
        echo "Railway 배포는 나중에 다음 명령어로 진행하세요:"
        echo "  railway login"
        echo "  railway up"
        exit 0
    fi
fi

echo ""
if ask_yes_no "Railway에 배포할까요?"; then
    # 로그인 확인
    info "Railway 로그인 상태 확인 중..."

    if ! railway whoami &> /dev/null; then
        info "Railway 로그인이 필요합니다."
        railway login
    fi

    echo ""
    info "Railway 배포 중..."
    railway up

    if [ $? -eq 0 ]; then
        success "배포 완료!"
        echo ""
        info "배포된 URL을 확인하세요:"
        railway open
    else
        error "배포 중 오류가 발생했습니다."
        echo "railway logs 명령어로 로그를 확인하세요."
    fi
else
    warning "Railway 배포를 건너뜁니다."
fi

# ============================================
# 완료
# ============================================
echo ""
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║               축하합니다! 모든 과정 완료!                  ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "다음에 할 수 있는 것들:"
echo ""
echo "  - 기능 추가: Claude Code에게 \"새 기능 추가해줘\"라고 요청"
echo "  - 버그 수정: Claude Code에게 \"버그 수정해줘\"라고 요청"
echo "  - 재배포: railway up"
echo ""
echo "도움이 필요하면 Claude Code에게 물어보세요!"
echo ""
