# 002. PostgreSQL 단일 데이터베이스로 통합

## 상태

Accepted

## 날짜

2026-02

## 컨텍스트

기존 두 프로젝트가 서로 다른 DB를 사용:
- AcademyInsight: MongoDB (비정형 수집 데이터)
- TeacherHub: PostgreSQL (구조화된 분석 데이터)

데이터 통합 및 관리 효율성을 위해 단일 DB 전략이 필요.

## 고려한 대안

### 대안 1: MongoDB + PostgreSQL 혼합

- 장점: 각 데이터 특성에 최적화
- 단점: 두 DB 운영 부담, 데이터 동기화 복잡성

### 대안 2: MongoDB 단일

- 장점: 유연한 스키마, 수집 데이터에 적합
- 단점: 관계형 쿼리 어려움, 분석 통계 집계 비효율

### 대안 3: PostgreSQL 단일 - 선택

- 장점: TeacherHub 스키마 재활용, JSONB로 비정형 지원, 관계형 분석 쿼리 최적
- 단점: 대량 비정형 데이터 저장 시 MongoDB 대비 유연성 부족

## 결정

PostgreSQL 15 단일 데이터베이스를 사용한다.

### 구체적인 결정 내용

- TeacherHub v2_schema.sql을 기반으로 확장 (name_en, keywords, last_crawled_at)
- 비정형 설정 데이터는 JSONB 컬럼 활용 (collection_sources.config)
- 배열 데이터는 TEXT[] 타입 활용 (keywords, aliases, top_keywords)
- 공유 PostgreSQL 서버(***REMOVED***:5432)에 edufit DB 생성

## 결과

### 긍정적 결과

- 11개 테이블 + 2개 뷰 스키마를 빠르게 설계 (TeacherHub 검증 완료)
- 단일 DB로 운영 복잡도 대폭 감소
- SQL 분석 쿼리 직접 활용 가능

### 부정적 결과 (Trade-offs)

- 수집 데이터 급증 시 파티셔닝 전략 필요
- 전문 검색 시 별도 Elasticsearch 도입 검토 필요

### 향후 고려사항

- posts 테이블 파티셔닝 (post_date 기준 월별)
- 검색 성능 개선 시 pg_trgm 확장 또는 Elasticsearch 도입
