# EduFit (아카이브 — 코드 보존)

> **상태 (2026-06-06): 운영 종료 / 아카이브.**
> 학원/강사 평판 분석 통합 플랫폼(AcademyInsight + TeacherHub 통합). 사용자 화면은
> 2026-05-01, 백그라운드 수집기(ai-crawler)는 2026-06-06 운영 중지·컨테이너 제거되었습니다.
> 본 repo 는 **구현 코드만** 보존하며, docker-compose·nginx·배포 워크플로우 등 운영/배포
> 구성과 아키텍처 기록은 중앙 관제 repo 의 LEGACY 가이드로 이관했습니다.
>
> 📄 **운영/구성/종료 기록**: [Claude-Opus-bluevlad / services/edufit/LEGACY.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/services/edufit/LEGACY.md)

## 무엇이었나

공무원 시험 학원·강사에 대한 온라인 커뮤니티(네이버 카페·디시인사이드) 평판을 수집·분석해
일/주/월간 리포트로 집계하던 서비스. AcademyInsight(Node.js+MongoDB)와 TeacherHub
(Spring Boot+Python)를 Python FastAPI 단일 스택으로 통합.

| 구성요소 | 기술 |
|----------|------|
| Backend | Python FastAPI + SQLAlchemy 2.0 + Alembic |
| Frontend | React 18 (Vite) + MUI 5 |
| Database | PostgreSQL 15 |
| Crawler | Playwright (Chromium headless) + APScheduler |

## 코드 구조

```
EduFit/
├── backend/           # FastAPI 백엔드 (api/v1, core, models, schemas, services, alembic)
├── frontend/          # React 프론트엔드 (components, pages, services)
├── ai-crawler/        # 데이터 수집 엔진 (crawlers, services, scheduler)
└── database/          # SQL 스키마 & 시드 데이터
```

각 컴포넌트의 `Dockerfile` 은 빌드 참조용으로 유지됩니다. 서비스 토폴로지(docker-compose
구성·포트·게이트웨이)는 위 LEGACY 가이드 §4 스냅샷을 참조하세요.

## 참고

- 본 repo 는 더 이상 배포되지 않습니다 (deploy 워크플로우 제거, 컨테이너 제거).
- 공유 PostgreSQL 의 `edufit` DB 는 보존(미 drop) 상태입니다.
