# EduFit 프로젝트 설정

> Git-First Workflow는 `C:/GIT/CLAUDE.md`에서 자동 상속됩니다.
> 이 파일에는 프로젝트 고유 설정만 작성합니다.

## 프로젝트 개요

- **프로젝트명**: EduFit
- **설명**: 학원/강사 평판 분석 통합 플랫폼 (AcademyInsight + TeacherHub 통합)
- **GitHub**: https://github.com/bluevlad/EduFit

## 기술 스택

- **Backend**: Python FastAPI + SQLAlchemy 2.0
- **Frontend**: React 18 (Vite) + MUI 5
- **Database**: PostgreSQL 15
- **기타**: Alembic (마이그레이션), Docker Compose

## 개발 환경

### 포트 설정

| 서비스 | 포트 |
|--------|------|
| Frontend | 4070 |
| Backend | 9070 |
| PostgreSQL (로컬) | 5433 |
| PostgreSQL (공유) | 5432 |

### 빌드 및 실행

```bash
# Backend 실행
cd C:\GIT\EduFit\backend
py -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
py -m uvicorn app.main:app --port 9070 --reload

# Frontend 실행
cd C:\GIT\EduFit\frontend
npm install && npm run dev
```

### 테스트

```bash
# Backend 테스트
cd C:\GIT\EduFit\backend
py -m pytest

# Frontend 테스트
cd C:\GIT\EduFit\frontend
npm test
```

### Docker

```bash
# 로컬 DB 실행
docker compose -f docker-compose.local.yml up -d

# 운영 전체 실행
docker compose -f docker-compose.prod.yml up -d
```

## 프로젝트별 규칙

### 브랜치 전략

- 기본 브랜치: `main`
- 작업 시 새 브랜치 생성 필수: `feature/이슈번호-설명`

### 주요 디렉토리

```
EduFit/
├── backend/          # FastAPI 백엔드 (포트 9070)
├── frontend/         # React 프론트엔드 (포트 4070)
├── database/         # SQL 스키마 및 시드 데이터
├── docs/             # 프로젝트 문서 (ADR, API, 로드맵)
└── docker-compose.*  # Docker 설정
```

### API 규칙

- API 버전: `/api/v1`
- 응답 형식: `{ success: bool, data: any, error: str | null }`
- 페이지네이션: `skip` / `limit` 파라미터

## Do NOT

- `.env`, `.env.local`, `.env.production` 파일을 직접 생성하거나 커밋하지 마세요
- `docker-compose.override.yml`을 커밋하지 마세요
- 운영 DB(***REMOVED***:5432/edufit)에 직접 DROP/TRUNCATE 실행하지 마세요
- 포트 번호(Frontend 4070, Backend 9070)를 임의로 변경하지 마세요
- `alembic/versions/` 파일을 수동으로 편집하지 마세요
