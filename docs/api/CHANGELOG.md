# API Changelog

## v1.0.0 (2026-02-25)

Phase 1 기반 구축 - 초기 API 릴리스

### Academies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/academies` | 학원 목록 조회 |
| GET | `/api/v1/academies/{id}` | 학원 상세 조회 |
| GET | `/api/v1/academies/{id}/teachers` | 학원별 강사 목록 |
| POST | `/api/v1/academies` | 학원 생성 |
| PUT | `/api/v1/academies/{id}` | 학원 수정 |
| DELETE | `/api/v1/academies/{id}` | 학원 삭제 |

### Teachers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teachers` | 강사 목록 조회 |
| GET | `/api/v1/teachers/{id}` | 강사 상세 조회 |
| GET | `/api/v1/teachers/search?q=` | 강사 검색 |
| POST | `/api/v1/teachers` | 강사 생성 |
| PUT | `/api/v1/teachers/{id}` | 강사 수정 |
| DELETE | `/api/v1/teachers/{id}` | 강사 삭제 |

### Subjects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/subjects` | 과목 목록 조회 |
| GET | `/api/v1/subjects/{id}` | 과목 상세 조회 |
| POST | `/api/v1/subjects` | 과목 생성 |
| PUT | `/api/v1/subjects/{id}` | 과목 수정 |

### Collection Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/collection-sources` | 수집 소스 목록 |
| GET | `/api/v1/collection-sources/{id}` | 수집 소스 상세 |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API 루트 정보 |
| GET | `/api/health` | 헬스 체크 |
