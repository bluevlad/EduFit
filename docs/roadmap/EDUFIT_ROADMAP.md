# EduFit 로드맵

## Phase 1: 기반 구축 (현재)

- [x] 프로젝트 초기화 + Git 설정
- [x] PostgreSQL 통합 스키마 설계 (11테이블 + 2뷰)
- [x] FastAPI 백엔드 (CRUD API)
- [x] React 프론트엔드 (MUI 5 레이아웃 + 페이지)
- [x] Docker Compose (로컬/운영)
- [x] 문서화 (ADR, API changelog, 설정 가이드)

## Phase 2: 데이터 수집 엔진

- [ ] 네이버 카페 크롤러 (공스타그램, 공드림)
- [ ] 디시인사이드 갤러리 크롤러
- [ ] 크롤링 스케줄러 (APScheduler / Celery Beat)
- [ ] 수집 모니터링 대시보드
- [ ] 중복 게시글 필터링

## Phase 3: 분석 엔진

- [ ] 강사 멘션 탐지 (이름 + 별칭 매칭)
- [ ] 감성 분석 (키워드 기반 → ML 기반)
- [ ] 난이도 분류
- [ ] 추천 여부 판별
- [ ] 데일리 리포트 자동 생성

## Phase 4: 대시보드 고도화

- [ ] 강사별 트렌드 차트 (Chart.js)
- [ ] 학원별 비교 분석
- [ ] 실시간 알림 (WebSocket)
- [ ] 키워드 클라우드
- [ ] 기간별 필터링

## Phase 5: 고급 기능

- [ ] LLM 기반 요약 리포트 (Claude API)
- [ ] 강사 비교 기능
- [ ] 사용자 인증 (JWT)
- [ ] 관리자 대시보드
- [ ] API Rate Limiting
- [ ] 성능 최적화 (캐싱, 인덱스 튜닝)
