# AI Simulation Focus Group MVP

멀티 에이전트 기반 AI 소비자 반응 시뮬레이션 프로토타입입니다.
단순 프로토타입이 아닌 향후 실서비스(SaaS)로 확장하는 것을 목표로 하며,
그에 맞춰 계층형(Layered) 아키텍처로 구성되어 있습니다.

## 목표

사용자가 제품명, 제품 설명, 타겟 고객, 광고 카피를 입력하면 FastAPI 백엔드가 AI API를 호출하여:

1. 가상 소비자 페르소나 10명 생성
2. 각 페르소나별 반응 생성
3. Moderator 요약 리포트 생성
4. React 웹페이지에서 결과 표시

## 프로젝트 구조

```text
ai-simulation-focus-group/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                      # FastAPI 앱 생성, 미들웨어/라우터 등록
│  │  ├─ config.py                    # 환경변수 로드 (.env)
│  │  ├─ api/                         # 라우팅 계층 (HTTP 요청/응답)
│  │  │  └─ simulation.py
│  │  ├─ services/                    # 오케스트레이션 (비즈니스 로직)
│  │  │  └─ simulation_service.py
│  │  ├─ agents/                      # LLM 호출 계층 (AI 에이전트)
│  │  │  └─ simulation_agent.py
│  │  ├─ prompts/                     # 프롬프트 템플릿
│  │  │  └─ simulation_prompts.py
│  │  ├─ schemas/                     # API 요청/응답 검증 (Pydantic)
│  │  │  └─ simulation.py
│  │  ├─ models/                      # DB ORM 모델 (향후 SQLAlchemy, 현재 비어있음)
│  │  ├─ repositories/                # DB 접근 계층 (향후 구현, 현재 비어있음)
│  │  └─ utils/                       # 공통 유틸리티
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ src/
│  │  ├─ main.tsx
│  │  ├─ App.tsx                      # 최상위 진입점 (페이지 라우팅 준비)
│  │  ├─ pages/                       # 화면 단위 컴포넌트
│  │  │  └─ SimulationPage.tsx
│  │  ├─ components/                  # 재사용 가능한 UI 조각
│  │  │  ├─ SimulationForm.tsx
│  │  │  ├─ SummaryReportCard.tsx
│  │  │  └─ PersonaCard.tsx
│  │  ├─ hooks/                       # 상태/부수효과 로직
│  │  │  └─ useSimulation.ts
│  │  ├─ services/                    # 백엔드 API 호출
│  │  │  └─ simulationApi.ts
│  │  ├─ types/                       # 공용 타입 정의
│  │  │  └─ simulation.ts
│  │  └─ styles/
│  │     └─ style.css
│  ├─ index.html
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  └─ .env.example
└─ README.md
```

## 1. Backend 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

`.env` 파일에 OpenAI API 키를 넣어주세요.

```env
OPENAI_API_KEY=your_api_key_here
```

## 2. Frontend 실행

```bash
cd frontend
npm install
cp .env.example .env   # 필요 시 VITE_API_BASE_URL 수정
npm run dev
```

기본 주소:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## 3. MVP API

### POST `/simulate`

요청 예시:

```json
{
  "product_name": "AI 영어 회화 앱",
  "product_description": "매일 10분씩 AI와 영어 회화를 할 수 있는 앱입니다.",
  "target_audience": "20~30대 직장인",
  "ad_copy": "퇴근길 10분, 영어가 습관이 됩니다."
}
```

응답:

```json
{
  "personas": [],
  "responses": [],
  "summary_report": {}
}
```

## 4. 아키텍처 원칙

- **계층 분리**: `api` (라우팅) → `services` (오케스트레이션) → `agents` (LLM 호출) 순으로 의존하며,
  각 계층은 자신의 바로 아래 계층만 알면 됩니다.
- **schemas vs models**: `schemas`는 API 입출력 검증(Pydantic)을, `models`는 향후 DB 테이블(ORM)을
  담당하도록 역할을 분리했습니다. 이름은 비슷하지만 책임이 다릅니다.
- **prompts 분리**: 프롬프트 문구는 로직과 분리하여, AI 응답 품질을 튜닝할 때 서비스 코드를
  건드리지 않도록 했습니다.
- **frontend 계층 분리**: `pages`는 화면 조합, `components`는 순수 UI, `hooks`는 상태/부수효과,
  `services`는 API 통신을 담당합니다.

## 개발 우선순위

1. 로컬에서 입력 → AI 리포트 출력
2. 프론트 UI 정리
3. 결과 저장 기능 추가 (`repositories` + `models` 구현, SQLite)
4. PDF 다운로드
5. 배포 (Docker, AWS EC2)
6. 로그인/구독/결제
