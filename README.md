# EduFit

학원/강사 평판 분석 통합 플랫폼

## 개요

EduFit은 AcademyInsight(Node.js+MongoDB)와 TeacherHub(Spring Boot+PostgreSQL+Python)의 데이터 수집/분석 기능을 통합한 학원/강사 평판 분석 플랫폼입니다.

공무원 시험 학원 및 강사에 대한 온라인 커뮤니티 평판을 수집, 분석하여 수험생에게 유용한 인사이트를 제공합니다.

## 기술 스택

| 구성요소 | 기술 |
|----------|------|
| Backend | Python FastAPI + SQLAlchemy 2.0 |
| Frontend | React 18 (Vite) + MUI 5 |
| Database | PostgreSQL 15 |
| Migration | Alembic |
| Container | Docker Compose |

## 빠른 시작

### 1. 로컬 DB 실행

```bash
docker compose -f docker-compose.local.yml up -d
```

### 2. 백엔드 실행

```bash
cd backend
py -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
# .env.example을 .env로 복사 후 설정
py -m uvicorn app.main:app --port 9070 --reload
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

### 4. 접속

- Frontend: http://localhost:4070
- Backend API: http://localhost:9070
- Swagger UI: http://localhost:9070/docs

## 프로젝트 구조

```
EduFit/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── api/v1/    # API 엔드포인트
│   │   ├── core/      # 설정, DB 연결
│   │   ├── models/    # SQLAlchemy 모델
│   │   ├── schemas/   # Pydantic 스키마
│   │   └── services/  # 비즈니스 로직
│   └── alembic/       # DB 마이그레이션
├── frontend/          # React 프론트엔드
│   └── src/
│       ├── components/  # UI 컴포넌트
│       ├── pages/       # 페이지
│       └── services/    # API 클라이언트
├── database/          # SQL 스키마 & 시드 데이터
├── docs/              # 프로젝트 문서
└── docker-compose.*   # Docker 설정
```

## 문서

- [개발 환경 설정](docs/dev/SETUP.md)
- [API Changelog](docs/api/CHANGELOG.md)
- [Architecture Decision Records](docs/adr/)
- [로드맵](docs/roadmap/EDUFIT_ROADMAP.md)
