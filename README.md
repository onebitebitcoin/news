# AI Coding Template

> **Claude Code와 함께 사용하는 풀스택 웹 애플리케이션 템플릿**

이 템플릿은 비개발자도 Claude Code를 통해 웹 애플리케이션을 쉽게 구축할 수 있도록 설계되었습니다.

---

## Quick Start

**5단계로 나만의 웹 앱을 만들고 배포하세요!**

### 가장 쉬운 방법: easystart.sh

```bash
git clone https://github.com/your-repo/aicoding-template.git
cd aicoding-template
./easystart.sh
```

대화형 인터페이스가 모든 과정을 단계별로 안내합니다:

```
┌─────────────────────────────────────────────┐
│     AI Coding Template - Easy Start         │
├─────────────────────────────────────────────┤
│                                             │
│  Step 1/7: 환경 설치                        │
│  환경 설치를 진행할까요? (y/n): _           │
│                                             │
└─────────────────────────────────────────────┘
```

---

### 수동으로 진행하기

### 1. 템플릿 다운로드

```bash
git clone https://github.com/your-repo/aicoding-template.git
cd aicoding-template
```

### 2. 내 프로젝트로 수정

`SPEC.md` 파일을 열어서 원하는 프로젝트로 수정하세요.
(또는 기본 예시 프로젝트로 먼저 테스트해도 됩니다)

### 3. 환경 설치 및 개발

```bash
# 모든 도구 자동 설치 (Node.js, Python, Git 등)
./install.sh

# Claude Code 실행
claude

# Claude Code에게 요청
"프로젝트 구현해줘"
```

### 4. 개발 서버 확인

```bash
./dev.sh
```

브라우저에서 확인:
- http://localhost:3000 (Frontend)
- http://localhost:8000/docs (API 문서)

### 5. 테스트 및 배포

```bash
# 테스트 실행
./test.sh

# Git 커밋 & 푸시
git add .
git commit -m "My first app"
git push

# Railway 배포
railway login
railway up
```

**끝! 나만의 웹 앱이 인터넷에 배포되었습니다.**

---

## 전체 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. git clone          템플릿 다운로드                          │
│         ↓                                                       │
│   2. SPEC.md 수정       원하는 프로젝트 정의                      │
│         ↓                                                       │
│   3. ./install.sh       Node.js, Python 등 자동 설치            │
│         ↓                                                       │
│   4. claude             Claude Code로 프로젝트 구현              │
│         ↓                                                       │
│   5. ./dev.sh           개발 서버 실행 및 확인                    │
│         ↓                                                       │
│   6. ./test.sh          린트 체크 및 테스트                       │
│         ↓                                                       │
│   7. git push           코드 저장                                │
│         ↓                                                       │
│   8. railway up         인터넷에 배포 완료!                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 이 템플릿의 특징

### 1. SPEC.md 기반 개발
- `SPEC.md` 파일에 원하는 프로젝트의 요구사항을 정의합니다
- Claude Code가 SPEC.md를 읽고 자동으로 프로젝트를 구현합니다
- 현재 예시: **Stock Portfolio Tracker** (주식 포트폴리오 관리 앱)

### 2. 체계적인 개발 규칙
- `.claude/CLAUDE.md`에 정의된 규칙을 Claude Code가 자동으로 따릅니다
- Plan Mode로 계획 수립 후 구현
- 린트 체크, 테스트, Git 커밋까지 자동화

### 3. 풀스택 구조
- **Frontend**: React + Vite + TailwindCSS
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: SQLite3 (설치 불필요)
- **배포**: Railway (Docker 기반)

---

## 사용 방법

### Step 1: 템플릿 다운로드

```bash
git clone https://github.com/your-repo/aicoding-template.git
cd aicoding-template
```

### Step 2: Claude Code 실행

터미널에서 Claude Code를 실행합니다:

```bash
claude
```

### Step 3: 프로젝트 구현 요청

Claude Code에게 다음과 같이 요청합니다:

```
"프로젝트 구현해줘"
```

또는 더 구체적으로:

```
"SPEC.md를 기반으로 프로젝트를 생성해줘"
```

### Step 4: Claude Code가 자동으로 수행하는 작업

1. **SPEC.md 검토** - 요구사항 파악
2. **질문** - 불명확한 부분 확인
3. **Plan Mode** - 구현 계획 수립 및 승인 요청
4. **구현** - 단계별 코드 작성
5. **테스트** - 린트 체크 및 테스트 실행
6. **커밋** - Git 자동 커밋

---

## 프로젝트 구조

```
aicoding-template/
├── .claude/
│   ├── CLAUDE.md          # Claude Code 규칙 (핵심!)
│   └── settings.local.json
│
├── design/
│   └── reference/         # 디자인 레퍼런스 이미지
│       └── sample.png
│
├── samples/               # 기능 테스트용 샘플 코드
│
├── SPEC.md                # 프로젝트 명세서 (수정하여 사용)
├── QUICKSTART.md          # 빠른 시작 가이드
├── AGENTS.md              # AI Agent 개발 규칙
│
├── install.sh             # 의존성 설치 스크립트
├── dev.sh                 # 개발 서버 실행 스크립트
├── test.sh                # 테스트 실행 스크립트
│
├── Dockerfile             # Docker 빌드 설정
├── railway.toml           # Railway 배포 설정
└── .env.example           # 환경 변수 예시
```

### 구현 후 생성되는 구조

```
aicoding-template/
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── pages/         # 페이지
│   │   └── api/           # API 클라이언트
│   └── package.json
│
├── backend/               # FastAPI 백엔드
│   ├── app/
│   │   ├── api/           # API 라우터
│   │   ├── models/        # DB 모델
│   │   └── services/      # 비즈니스 로직
│   └── requirements.txt
│
└── ... (기존 파일들)
```

---

## 예시 프로젝트: Stock Portfolio Tracker

현재 SPEC.md에 정의된 예시 프로젝트입니다.

### 주요 기능
- 보유 종목 및 거래 내역 관리
- 실시간 포트폴리오 가치 및 수익률 계산
- 종목별/전체 수익률 시각화
- 포트폴리오 비중 분석

### 기술 스택
| 구분 | 기술 |
|------|------|
| Frontend | React, Vite, TailwindCSS, Recharts |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite3 |
| 외부 API | Yahoo Finance (yfinance) |
| 배포 | Railway, Docker |

### 데이터 흐름

```
사용자 입력 → Frontend (React) → Backend (FastAPI) → Yahoo Finance API
                  ↓                    ↓
              대시보드 출력 ←── Database (SQLite3) ←── 시세 캐싱
```

---

## 나만의 프로젝트 만들기

### 1. SPEC.md 수정

`SPEC.md` 파일을 열어 원하는 프로젝트로 수정합니다:

```markdown
# My Project - Technical Specification

## 1. Project Overview
### 1.1 Purpose
[프로젝트 설명]

## 5. API Design
[API 엔드포인트 정의]

## 6. Database Schema
[데이터베이스 스키마 정의]
```

### 2. 디자인 레퍼런스 추가 (선택)

`design/reference/` 폴더에 원하는 디자인 이미지를 추가하면 Claude Code가 해당 스타일을 참고합니다.

### 3. Claude Code에게 요청

```
"SPEC.md를 기반으로 프로젝트를 생성해줘"
```

---

## 환경 설치 (install.sh)

**비개발자도 새 컴퓨터에서 바로 실행할 수 있습니다.**

```bash
./install.sh
```

### 지원 OS

| OS | 패키지 매니저 | 자동 설치 |
|----|-------------|----------|
| macOS | Homebrew (없으면 자동 설치) | O |
| Ubuntu/Debian | apt | O |
| Windows (WSL) | apt | O |
| RedHat/CentOS | dnf | O |

### 자동 설치 항목

| 도구 | 설명 |
|------|------|
| Node.js | v20 LTS (Frontend 빌드) |
| Python | 3.x + pip + venv (Backend 실행) |
| Git | 버전 관리 |

### 설치 흐름

```
./install.sh 실행
    │
    ├── 1. OS 감지 (macOS/Ubuntu/Windows 등)
    ├── 2. 패키지 매니저 확인/설치
    ├── 3. Node.js 설치 (없으면)
    ├── 4. Python 설치 (없으면)
    ├── 5. Git 설치 (없으면)
    ├── 6. Python 가상환경 생성
    ├── 7. Backend 의존성 설치 (pip)
    ├── 8. Frontend 의존성 설치 (npm)
    └── 9. .env 파일 생성
```

---

## 개발 서버 실행 (dev.sh)

환경 설치 후:

```bash
./dev.sh
```

Frontend와 Backend가 동시에 실행됩니다:

| 서비스 | 주소 |
|--------|------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |

종료: `Ctrl + C`

---

## 배포 (Railway)

### 사전 준비

1. [Railway](https://railway.app) 계정 생성
2. Railway CLI 설치: `npm install -g @railway/cli`
3. 로그인: `railway login`

### 배포 요청

Claude Code에게 요청:

```
"Railway에 배포해줘"
```

또는 직접 실행:

```bash
railway up
```

---

## CLAUDE.md 핵심 규칙

Claude Code가 따르는 주요 규칙입니다:

| 규칙 | 설명 |
|------|------|
| 한국어 답변 | 모든 설명은 한국어로 작성 |
| SPEC.md 검토 필수 | 구현 전 명세서 확인 및 질문 |
| Plan Mode 필수 | 계획 수립 후 사용자 승인 |
| 테스트 필수 | 코드 수정 후 린트/테스트 실행 |
| Git 커밋 필수 | 테스트 통과 시 자동 커밋 |
| 이모지 금지 | 아이콘 컴포넌트 사용 |
| 반응형 디자인 | 모바일 + PC 양쪽 지원 |
| 12-Factor App | 환경변수 기반 설정 |

---

## 문제 해결

### 에러 발생 시

Claude Code에게 요청:

```
"에러 로그 확인해줘"
"문제 원인 분석해줘"
```

### 로그 확인

```bash
# Backend 로그
tail -f backend/debug.log

# Frontend 로그
# 브라우저 개발자 도구 Console 확인
```

### 배포 상태 확인

```bash
railway status
railway logs
```

---

## 참고 자료

- [SPEC.md](./SPEC.md) - 프로젝트 상세 명세서
- [QUICKSTART.md](./QUICKSTART.md) - 빠른 시작 가이드
- [.claude/CLAUDE.md](./.claude/CLAUDE.md) - Claude Code 규칙
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)

---

## 라이선스

MIT License - 자유롭게 사용하세요.

---

**이 템플릿은 AI와 함께하는 새로운 개발 경험을 제공합니다.**

Claude Code에게 "프로젝트 구현해줘"라고 말해보세요!
