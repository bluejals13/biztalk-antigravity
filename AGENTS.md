# AGENTS.md — 업무 말투 변환기 프로젝트 에이전트 지침서

> 본 문서는 **업무 말투 변환기** 프로젝트 개발 시 에이전트(AI Agent)와 개발자가 준수해야 하는 작업 지침, 프로젝트 룰, 기술 스택 및 검증 절차를 정의합니다.

---

## 1. 프로젝트 개요 & 바이브 코딩 3원칙

### 1.1 프로젝트 목표
- **서비스명**: 업무 말투 변환기 (BizTalk Tone Converter)
- **목적**: 텍스트 원문을 입력받아 수신 대상(상사, 타팀 동료, 고객, 팀 내 동료)에 적합한 격식/어조의 비즈니스 메시지로 변환하는 1-Day 프로젝트.

### 1.2 에이전트 바이브 코딩 3원칙 (필수 준수)
1. **원칙 1: 완료 기준을 먼저 정의하라**
   - 개발 및 코드 수정 시 `PRD_업무말투변환기.md`의 [2. 완료 체크리스트] 항목만을 목표로 지정합니다.
   - 요청받지 않은 과도한 추가 기능(로그인, DB 이력 저장 등)을 임의로 구현하지 않습니다.
2. **원칙 2: 조사 먼저, 구현 나중**
   - 외부 라이브러리 연동(`langchain-upstage`, Upstage Solar-Pro3 API 등) 전 연동 방식 및 최신 패키지 버전을 먼저 확인/설명한 뒤 구현합니다.
3. **원칙 3: 버그는 분석 먼저, 수정 나중**
   - 오류 발생 시 에러의 근본 원인을 먼저 분석하여 설명하고, 확인 후 수정을 진행합니다. 무분별한 땜빵식 패치를 금지합니다.

---

## 2. 기술 스택 및 구성 표준

| 영역 | 기술 스택 | 비고 |
|------|-----------|------|
| **Backend** | Python 3.11+ / FastAPI / Uvicorn | Async 핸들러 기본 사용 |
| **AI LLM** | Upstage `Solar-Pro3` | `langchain-upstage`, `langchain` 사용 |
| **Frontend** | HTML5 / CSS3 / Vanilla JavaScript (ES6+) | 외부 프레임워크(React, Vue 등) 사용 금지 |
| **환경 변수** | `python-dotenv` | `.env` 관리 (절대 Git에 노출 금지) |
| **배포** | Vercel | Frontend 및 Backend 통합 배포 |

---

## 3. 디렉토리 구조 및 역할

```
biztalk_antigravity/
├── backend/
│   ├── main.py                 # FastAPI 앱 생성, CORS 및 Static 라우팅 설정
│   ├── routers/
│   │   └── convert.py          # POST /api/convert 라우터
│   ├── services/
│   │   └── tone_converter.py   # LangChain + Solar-Pro3 LLM 연동 핵심 로직
│   ├── prompts/
│   │   └── templates.py        # 수신 대상별(boss, colleague, client, team) 프롬프트 정의
│   ├── models/
│   │   └── schemas.py          # Pydantic ConvertRequest, ConvertResponse 정의
│   ├── .env                    # UPSTAGE_API_KEY (Git 추적 제외)
│   ├── .env.example            # 환경변수 샘플
│   └── requirements.txt        # 의존성 정의
├── frontend/
│   ├── index.html              # UI 레이아웃
│   ├── css/
│   │   └── style.css           # 스타일시트 (모던, 반응형)
│   └── js/
│       └── app.js              # 이벤트 처리, API 연동, 복사 기능
├── .env                        # 루트 환경변수 (필요 시)
├── .gitignore                  # .env, venv, pycache 필수 포함
├── AGENTS.md                   # 에이전트 지침서 (본 문서)
└── PRD_업무말투변환기.md       # 제품 요구사항 정의서
```

---

## 4. 에이전트 안전 및 파괴 방지 규칙 (Safety Rules)

1. **환경변수 및 API 키 보안 (`.env`)**
   - `.env` 파일의 내용이나 API 키를 콘솔에 출력하거나 코드에 하드코딩하지 않습니다.
   - `.gitignore`에 `.env`, `__pycache__/`, `venv/`가 포함되어 있는지 항상 확인합니다.
2. **파괴적 작업 사전 승인**
   - 기존 코드 대규모 리팩토링, 디렉토리 구조 변경, 패키지 삭제 등의 작업 시 사전에 명시적 확인을 거칩니다.
3. **엄격한 스코프 조절**
   - PRD 범위(F-01 ~ F-06) 내에서만 개발하며, 범위를 벗어난 기능 구현 요청은 사전에 확정 후 진행합니다.

---

## 5. 코딩 스타일 & API 명세 규칙

### 5.1 백엔드 규칙
- **API 규격**:
  - `POST /api/convert`
    - Request: `{"text": "원문 내용", "target_audience": "boss" | "colleague" | "client" | "team"}`
    - Response: `{"converted_text": "변환문", "target_audience": "boss", "original_text": "원문 내용"}`
  - `GET /health` -> `{"status": "ok"}`
- **오류 처리**: Pydantic 검증 오류(422) 및 LLM 호출 예외(500) 처리.
- **CORS 설정**: 개발 및 배포 환경 고려 CORS Middleware 설정.

### 5.2 프론트엔드 규칙
- Vanilla HTML/CSS/JS 구현.
- UI 요소:
  - 4종 수신 대상 선택 버튼 (`active` 클래스 토글)
  - 텍스트 입력창 및 결과 출력창
  - 변환 진행 중 로딩 스피너/상태 표시
  - 클립보드 복사 기능 (`navigator.clipboard.writeText`)
- 디자인: 직관적이고 깔끔한 현대적 UI (Inter font, smooth button state).

---

## 6. 검증 및 완료 기준 (Definition of Done)

작업 완료 선언 전 아래 검증을 반드시 통과해야 합니다:

1. **백엔드 검증**:
   - `uvicorn backend.main:app --reload` 로컬 실행 확인
   - `GET /health` 200 OK 확인
   - Swagger UI (`http://localhost:8000/docs`) 접속 및 `POST /api/convert` 4개 수신 대상별 테스트 정상 작동 확인
2. **프론트엔드 검증**:
   - 수신 대상 선택 버튼 클릭 시 활성화 상태 전환 확인
   - API 연동 후 변환 결과 정상 출력 및 복사 기능 동작 확인
3. **코드 검증**:
   - `.env` 보안 처리 및 Git 추적 제외 확인
