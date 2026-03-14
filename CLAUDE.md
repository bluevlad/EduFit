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

## Deployment

- **CI/CD**: GitHub Actions (Self-hosted Runner, `prod` 브랜치 push 시 자동 배포)
- **Docker**: OrbStack (edufit-db, edufit-backend, edufit-frontend)
- **Secrets**: GitHub Secrets로 관리 (DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, CORS_ORIGINS)

### 배포 프로세스

```bash
# main → prod 머지로 자동 배포
git checkout prod && git merge main && git push origin prod
```

> 로컬 환경 정보는 `CLAUDE.local.md` 참조 (git에 포함되지 않음)

## Help Page 관리

> 작성 표준: [HELP_PAGE_GUIDE.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/documentation/HELP_PAGE_GUIDE.md)
> HTML 템플릿: [help-page-template.html](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/documentation/templates/help-page-template.html)

- **기능 추가/변경/삭제 시 반드시 헬프 페이지도 함께 업데이트**
- 헬프 파일 위치: `frontend/public/help/`
- 서비스 accent-color: `#3b82f6` (Blue)
- 대상 가이드 파일:
  - `user-guide.html` — EduFit 관리자 가이드 (메인)
  - `api-guide.html` — API 문서 가이드
  - `newsletter-guide.html` — 뉴스레터 기능 가이드
  - `analytics-guide.html` — 분석/통계 기능 가이드

## Do NOT

- `.env`, `.env.local`, `.env.production` 파일을 직접 생성하거나 커밋하지 마세요
- `docker-compose.override.yml`을 커밋하지 마세요
- 운영 DB에 직접 DROP/TRUNCATE 실행하지 마세요
- 포트 번호(Frontend 4070, Backend 9070)를 임의로 변경하지 마세요
- `alembic/versions/` 파일을 수동으로 편집하지 마세요

## Fix 커밋 오류 추적

> 상세: [FIX_COMMIT_TRACKING_GUIDE.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/git/FIX_COMMIT_TRACKING_GUIDE.md) | [ERROR_TAXONOMY.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/git/ERROR_TAXONOMY.md)

`fix:` 커밋 시 footer에 오류 추적 메타데이터를 **필수** 포함합니다.

### 이 프로젝트에서 자주 발생하는 Root-Cause

| Root-Cause | 설명 | 예방 |
|-----------|------|------|
| `env-assumption` | Docker 내/외부 경로, 환경변수 가정 | Settings 클래스에서 필수값 검증, 기본값 금지 |
| `import-error` | 패키지 import 경로 오류, 상대/절대 경로 혼동 | `__init__.py` 확인, 절대 import 사용 |
| `null-handling` | Optional 필드 None 미처리 | Pydantic `Optional[T]` + 기본값 명시 |
| `type-mismatch` | SQLAlchemy 모델 ↔ Pydantic 스키마 타입 불일치 | `model_validate()` 사용, from_attributes=True |
| `async-handling` | await 누락, 동기/비동기 혼용 | async def에서 동기 DB 호출 금지, run_in_executor 사용 |
| `db-migration` | Alembic 마이그레이션 누락/충돌 | 스키마 변경 시 반드시 `alembic revision --autogenerate` |

### 예시

```
fix(api): 알레르기 성분 조회 시 None 응답 처리

- ingredient가 Optional인데 None 체크 없이 .name 접근하여 AttributeError 발생
- None일 때 빈 문자열 반환하도록 수정

Root-Cause: null-handling
Error-Category: logic-error
Affected-Layer: backend/api
Recurrence: first
Prevention: Optional 필드 접근 전 반드시 None 체크, or 연산자 활용

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
