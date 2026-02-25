# EduFit 개발 환경 설정 가이드

## 사전 요구사항

- Python 3.10+
- Node.js 20+
- Docker / Docker Compose
- PostgreSQL 클라이언트 (psql, optional)

## 방법 1: 공유 DB 사용 (권장)

공유 PostgreSQL 서버(***REMOVED***:5432)에 접속하여 개발합니다.

### 1. 백엔드 설정

```bash
cd C:\GIT\EduFit\backend

# 가상환경 생성
py -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
copy .env.example .env
# .env 파일에서 DATABASE_URL을 공유 DB로 설정:
# DATABASE_URL=postgresql://dev_writer:password@***REMOVED***:5432/edufit_dev
```

### 2. 백엔드 실행

```bash
py -m uvicorn app.main:app --port 9070 --reload
```

- Swagger UI: http://localhost:9070/docs
- API 루트: http://localhost:9070/

### 3. 프론트엔드 설정

```bash
cd C:\GIT\EduFit\frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

- 접속: http://localhost:4070
- API 프록시가 자동으로 localhost:9070으로 전달됩니다.

## 방법 2: 로컬 DB 사용 (Docker)

로컬에 PostgreSQL 컨테이너를 실행하여 독립적으로 개발합니다.

### 1. 로컬 DB 실행

```bash
cd C:\GIT\EduFit
docker compose -f docker-compose.local.yml up -d
```

- 포트: localhost:5433
- DB: edufit_dev
- User: postgres / Password: postgres
- 스키마와 시드 데이터가 자동으로 초기화됩니다.

### 2. 백엔드 .env 설정

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/edufit_dev
CORS_ORIGINS=http://localhost:4070
DEBUG=true
```

### 3. DB 확인

```bash
psql -h localhost -p 5433 -U postgres -d edufit_dev

# 테이블 확인
\dt

# 데이터 확인
SELECT count(*) FROM teachers;
SELECT a.name, count(t.id) FROM academies a LEFT JOIN teachers t ON a.id = t.academy_id GROUP BY a.name;
```

## 포트 정리

| 서비스 | 포트 | 비고 |
|--------|------|------|
| Frontend (Vite) | 4070 | 개발 서버 |
| Backend (FastAPI) | 9070 | API 서버 |
| PostgreSQL (로컬) | 5433 | Docker 로컬 DB |
| PostgreSQL (공유) | 5432 | ***REMOVED*** |

## Alembic 마이그레이션

```bash
cd C:\GIT\EduFit\backend

# 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 문제 해결

### DB 연결 오류

- `.env` 파일의 `DATABASE_URL` 확인
- 공유 DB 사용 시 VPN 연결 상태 확인
- 로컬 DB 사용 시 Docker 컨테이너 실행 상태 확인: `docker ps`

### 포트 충돌

- 4070/9070 포트가 이미 사용 중인지 확인
- Windows: `netstat -ano | findstr :4070`
