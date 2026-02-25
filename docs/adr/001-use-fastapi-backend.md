# 001. FastAPI를 백엔드 프레임워크로 선택

## 상태

Accepted

## 날짜

2026-02

## 컨텍스트

EduFit은 AcademyInsight(Node.js)와 TeacherHub(Spring Boot+Python)를 통합하는 프로젝트이다.

- TeacherHub의 Python 크롤러/분석 모듈이 핵심 기능
- 향후 NLP/ML 기반 감성 분석이 주요 기능으로 예정
- 기존 두 프로젝트의 기술 부채를 줄이면서 통합 필요

## 고려한 대안

### 대안 1: Spring Boot (Java/Kotlin)

- 장점: TeacherHub에서 검증됨, 엔터프라이즈 안정성
- 단점: Python 분석 모듈과 별도 프로세스 필요, 개발 속도 느림

### 대안 2: Express.js (Node.js)

- 장점: AcademyInsight에서 검증됨, 빠른 프로토타이핑
- 단점: ML/NLP 라이브러리 생태계 부족, Python 브릿지 필요

### 대안 3: FastAPI (Python) - 선택

- 장점: Python 단일 언어로 API+크롤링+분석 통합, 자동 OpenAPI 문서, async 지원, 타입 안전성(Pydantic)
- 단점: 상대적으로 작은 커뮤니티 (Django 대비)

## 결정

FastAPI를 선택한다.

### 구체적인 결정 내용

- Python 3.10+ 기반 FastAPI
- SQLAlchemy 2.0 ORM + Alembic 마이그레이션
- pydantic-settings로 환경 설정 관리
- AllergyInsight 프로젝트의 검증된 패턴 재활용

## 결과

### 긍정적 결과

- Python 단일 언어로 전체 백엔드 통합 (API + 크롤러 + 분석)
- Swagger UI 자동 생성으로 API 문서화 부담 제거
- scikit-learn, transformers 등 ML 라이브러리 직접 통합 가능

### 부정적 결과 (Trade-offs)

- GIL로 인한 CPU 바운드 작업 제한 (필요시 Celery로 해결)
- Spring Boot 대비 상대적으로 적은 엔터프라이즈 레퍼런스

### 향후 고려사항

- 대량 크롤링 시 Celery + Redis 워커 구조 도입
- 분석 파이프라인 성능 이슈 시 비동기 처리 확대
