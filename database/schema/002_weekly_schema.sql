-- =============================================
-- EduFit 주간 집계 스키마
-- 002_weekly_schema.sql
-- =============================================

-- 1. 강사별 주간 리포트
CREATE TABLE IF NOT EXISTS weekly_reports (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    academy_id INTEGER REFERENCES academies(id) ON DELETE CASCADE,

    -- 기간 정보
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,  -- ISO week (1-53)
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,

    -- 언급 통계
    mention_count INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    recommendation_count INTEGER DEFAULT 0,

    -- 난이도 통계
    difficulty_easy_count INTEGER DEFAULT 0,
    difficulty_medium_count INTEGER DEFAULT 0,
    difficulty_hard_count INTEGER DEFAULT 0,

    -- 계산 지표
    avg_sentiment_score FLOAT,
    sentiment_trend FLOAT,           -- 전주 대비 감성 변화
    mention_change_rate FLOAT,       -- 전주 대비 언급 변화율 (%)
    weekly_rank INTEGER,             -- 해당 주 전체 순위
    academy_rank INTEGER,            -- 학원 내 순위

    -- 분석 데이터 (JSON)
    top_keywords JSONB DEFAULT '[]'::jsonb,
    source_distribution JSONB DEFAULT '{}'::jsonb,
    daily_distribution JSONB DEFAULT '{}'::jsonb,
    mention_types JSONB DEFAULT '{}'::jsonb,

    -- AI 요약
    ai_summary TEXT,
    highlight_positive TEXT,
    highlight_negative TEXT,

    -- 메타데이터
    is_complete BOOLEAN DEFAULT FALSE,
    aggregated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uk_weekly_teacher_year_week UNIQUE (teacher_id, year, week_number)
);

CREATE INDEX IF NOT EXISTS idx_weekly_reports_teacher ON weekly_reports(teacher_id);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_academy ON weekly_reports(academy_id);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_year_week ON weekly_reports(year, week_number);


-- 2. 학원별 주간 통계
CREATE TABLE IF NOT EXISTS academy_weekly_stats (
    id SERIAL PRIMARY KEY,
    academy_id INTEGER REFERENCES academies(id) ON DELETE CASCADE,

    -- 기간 정보
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,

    -- 통계
    total_mentions INTEGER DEFAULT 0,
    total_teachers_mentioned INTEGER DEFAULT 0,
    avg_sentiment_score FLOAT,
    total_positive INTEGER DEFAULT 0,
    total_negative INTEGER DEFAULT 0,
    total_recommendations INTEGER DEFAULT 0,

    -- 랭킹 정보
    top_teacher_id INTEGER REFERENCES teachers(id),
    top_teacher_mentions INTEGER DEFAULT 0,

    -- 분석 데이터
    top_keywords JSONB DEFAULT '[]'::jsonb,
    source_distribution JSONB DEFAULT '{}'::jsonb,

    -- 메타데이터
    aggregated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uk_academy_weekly_year_week UNIQUE (academy_id, year, week_number)
);


-- 3. 집계 작업 로그
CREATE TABLE IF NOT EXISTS aggregation_logs (
    id SERIAL PRIMARY KEY,
    aggregation_type VARCHAR(50) NOT NULL,  -- daily, weekly, monthly
    target_date DATE,
    year INTEGER,
    week_number INTEGER,

    -- 상태
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- 결과
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);


-- 4. 시스템 설정 테이블
CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string',  -- string, int, boolean, json
    description TEXT,
    environment VARCHAR(20) DEFAULT 'all',     -- all, dev, prod
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- =============================================
-- 기존 테이블 확장 (IF NOT EXISTS 안전)
-- =============================================

-- academies 테이블에 EduFit 확장 컬럼 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'academies' AND column_name = 'name_en'
    ) THEN
        ALTER TABLE academies ADD COLUMN name_en VARCHAR(100);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'academies' AND column_name = 'keywords'
    ) THEN
        ALTER TABLE academies ADD COLUMN keywords TEXT[];
    END IF;
END $$;

-- collection_sources 테이블에 last_crawled_at 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'collection_sources' AND column_name = 'last_crawled_at'
    ) THEN
        ALTER TABLE collection_sources ADD COLUMN last_crawled_at TIMESTAMP;
    END IF;
END $$;


-- =============================================
-- 권한 부여
-- =============================================

-- 운영 계정
GRANT SELECT, INSERT, UPDATE, DELETE ON weekly_reports TO edufit_svc;
GRANT SELECT, INSERT, UPDATE, DELETE ON academy_weekly_stats TO edufit_svc;
GRANT SELECT, INSERT, UPDATE, DELETE ON aggregation_logs TO edufit_svc;
GRANT SELECT, INSERT, UPDATE, DELETE ON system_configs TO edufit_svc;
GRANT USAGE, SELECT ON SEQUENCE weekly_reports_id_seq TO edufit_svc;
GRANT USAGE, SELECT ON SEQUENCE academy_weekly_stats_id_seq TO edufit_svc;
GRANT USAGE, SELECT ON SEQUENCE aggregation_logs_id_seq TO edufit_svc;
GRANT USAGE, SELECT ON SEQUENCE system_configs_id_seq TO edufit_svc;

-- 개발 계정
GRANT SELECT, INSERT, UPDATE, DELETE ON weekly_reports TO dev_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON academy_weekly_stats TO dev_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON aggregation_logs TO dev_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON system_configs TO dev_writer;
GRANT USAGE, SELECT ON SEQUENCE weekly_reports_id_seq TO dev_writer;
GRANT USAGE, SELECT ON SEQUENCE academy_weekly_stats_id_seq TO dev_writer;
GRANT USAGE, SELECT ON SEQUENCE aggregation_logs_id_seq TO dev_writer;
GRANT USAGE, SELECT ON SEQUENCE system_configs_id_seq TO dev_writer;

GRANT SELECT ON weekly_reports TO dev_reader;
GRANT SELECT ON academy_weekly_stats TO dev_reader;
GRANT SELECT ON aggregation_logs TO dev_reader;
GRANT SELECT ON system_configs TO dev_reader;
