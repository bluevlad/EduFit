#!/usr/bin/env python3
"""
EduFit 데이터 마이그레이션 스크립트
===================================
TeacherHub(PostgreSQL) + AcademyInsight(MongoDB) → EduFit(PostgreSQL)

사용법:
    python database/migration/migrate_data.py              # 전체 마이그레이션
    python database/migration/migrate_data.py --dry-run    # 시뮬레이션 (ROLLBACK)
    python database/migration/migrate_data.py --step sources  # 특정 단계만 실행

의존성:
    pip install psycopg2-binary pymongo
"""

import argparse
import hashlib
import logging
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import psycopg2
import psycopg2.extras
from pymongo import MongoClient

# ============================================
# 접속 정보 (환경변수에서 읽음)
# ============================================
TEACHERHUB_PG = {
    "host": os.environ["TH_PG_HOST"],
    "port": int(os.environ.get("TH_PG_PORT", "5432")),
    "dbname": os.environ.get("TH_PG_DBNAME", "teacherhub"),
    "user": os.environ["TH_PG_USER"],
    "password": os.environ["TH_PG_PASSWORD"],
}

ACADEMYINSIGHT_MONGO = {
    "host": os.environ["AI_MONGO_HOST"],
    "port": int(os.environ.get("AI_MONGO_PORT", "27017")),
    "dbname": os.environ.get("AI_MONGO_DBNAME", "academyinsight"),
    "user": os.environ["AI_MONGO_USER"],
    "password": os.environ["AI_MONGO_PASSWORD"],
}

EDUFIT_PG = {
    "host": os.environ.get("EF_PG_HOST", "localhost"),
    "port": int(os.environ.get("EF_PG_PORT", "5433")),
    "dbname": os.environ.get("EF_PG_DBNAME", "edufit_dev"),
    "user": os.environ["EF_PG_USER"],
    "password": os.environ["EF_PG_PASSWORD"],
}

# ============================================
# 소스 코드 매핑
# ============================================

# TH source code → EF source code (코드가 다른 경우만 명시)
TH_CODE_TO_EF_CODE = {
    "dcinside_government": "dcinside_gongmuwon",
    # 나머지는 코드가 동일 (naver_gongstar, naver_gongdream, naver_9gong,
    # dcinside_gongmuwon_minor, daum_gongmuwon, dcinside_gongsisaeng 등)
}

# AI (sourceType, sourceId) → EF source code
AI_SOURCE_TO_EF_CODE = {
    ("naver_cafe", "m2school"): "naver_gongdream",       # m2school = 공드림 카페
    ("naver_cafe", "gongdream"): "naver_gongdream_real",  # 실제 gongdream 카페
    ("naver_cafe", "9gong"): "naver_9gong",
    ("daum_cafe", "gongmuwon"): "daum_gongmuwon",
    ("dcinside", "gongmuwon"): "dcinside_gongmuwon_minor",
    ("dcinside", "gongsisaeng"): "dcinside_gongsisaeng",
    ("dcinside", "gongsi"): "dcinside_gongsi",
}

# TH academy code → EF academy code (코드가 다른 경우만 명시)
TH_ACADEMY_CODE_TO_EF_CODE = {
    "pmg": "parkmungak",
    # 나머지는 동일 (gongdangi, hackers, willbes, eduwill)
}

# Step 1에서 추가할 새 소스들
NEW_SOURCES = [
    {
        "code": "dcinside_gosi",
        "name": "디시인사이드 - 고시 갤러리",
        "base_url": "https://gall.dcinside.com/board/lists/?id=gosi",
        "source_type": "gallery",
        "config": '{"gallery_id": "gosi", "requires_login": false}',
    },
    {
        "code": "daum_gongmuwon",
        "name": "다음카페 - 공무원시험",
        "base_url": "https://cafe.daum.net/gongmuwon",
        "source_type": "cafe",
        "config": '{"cafe_id": "gongmuwon", "requires_login": false}',
    },
    {
        "code": "dcinside_gongsisaeng",
        "name": "디시인사이드 - 공시생 마이너 갤러리",
        "base_url": "https://gall.dcinside.com/mgallery/board/lists/?id=gongsisaeng",
        "source_type": "gallery",
        "config": '{"gallery_id": "gongsisaeng", "is_minor": true, "requires_login": false}',
    },
    {
        "code": "naver_gongdream_real",
        "name": "네이버 카페 - 공드림 (실제)",
        "base_url": "https://cafe.naver.com/gongdream",
        "source_type": "cafe",
        "config": '{"club_id": "gongdream", "requires_login": true}',
    },
    {
        "code": "dcinside_gongsi",
        "name": "디시인사이드 - 공시 마이너 갤러리",
        "base_url": "https://gall.dcinside.com/mgallery/board/lists/?id=gongsi",
        "source_type": "gallery",
        "config": '{"gallery_id": "gongsi", "is_minor": true, "requires_login": false}',
    },
]

# ============================================
# 로깅 설정
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("EduFitMigrator")

# ============================================
# 마이그레이션 Step 이름 → 메서드 매핑
# ============================================
STEP_NAMES = {
    "sources": "migrate_collection_sources",
    "keywords": "migrate_analysis_keywords",
    "teacher_map": "build_teacher_id_map",
    "posts_th": "migrate_posts_from_teacherhub",
    "posts_ai": "migrate_posts_from_academyinsight",
    "comments": "migrate_comments",
    "mentions": "migrate_teacher_mentions",
    "daily_reports": "migrate_daily_reports",
    "crawl_logs": "migrate_crawl_logs",
    "weekly_schema": "ensure_weekly_schema",
    "weekly_reports": "migrate_weekly_reports",
    "academy_weekly": "migrate_academy_weekly_stats",
}


class EduFitMigrator:
    """TeacherHub + AcademyInsight → EduFit 데이터 마이그레이터"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

        # DB 연결
        self.th_conn = None
        self.ef_conn = None
        self.mongo_client = None
        self.mongo_db = None

        # 매핑 딕셔너리
        self.source_id_map_th = {}   # TH source_id → EF source_id
        self.source_id_map_ai = {}   # AI source ObjectId str → EF source_id
        self.teacher_id_map = {}     # TH teacher_id → EF teacher_id
        self.post_id_map_th = {}     # TH post_id → EF post_id
        self.post_id_map_ai = {}     # AI post ObjectId str → EF post_id
        self.comment_id_map_th = {}  # TH comment_id → EF comment_id

        # 학원 코드 매핑
        self.th_academy_id_to_code = {}
        self.ef_academy_code_to_id = {}

        # 통계
        self.stats = {}

    # ============================================
    # 연결 관리
    # ============================================
    def connect(self):
        """3개 DB 연결"""
        logger.info("=== DB 연결 시작 ===")

        # TeacherHub PostgreSQL
        logger.info(
            "TeacherHub PG 연결: %s:%s/%s",
            TEACHERHUB_PG["host"],
            TEACHERHUB_PG["port"],
            TEACHERHUB_PG["dbname"],
        )
        self.th_conn = psycopg2.connect(**TEACHERHUB_PG)
        self.th_conn.set_session(readonly=True)
        logger.info("  → TeacherHub PG 연결 성공")

        # EduFit PostgreSQL
        logger.info(
            "EduFit PG 연결: %s:%s/%s",
            EDUFIT_PG["host"],
            EDUFIT_PG["port"],
            EDUFIT_PG["dbname"],
        )
        self.ef_conn = psycopg2.connect(**EDUFIT_PG)
        self.ef_conn.autocommit = False  # 트랜잭션 모드
        logger.info("  → EduFit PG 연결 성공")

        # AcademyInsight MongoDB
        mongo_uri = (
            f"mongodb://{ACADEMYINSIGHT_MONGO['user']}:{ACADEMYINSIGHT_MONGO['password']}"
            f"@{ACADEMYINSIGHT_MONGO['host']}:{ACADEMYINSIGHT_MONGO['port']}"
            f"/{ACADEMYINSIGHT_MONGO['dbname']}?authSource=admin"
        )
        logger.info(
            "AcademyInsight Mongo 연결: %s:%s/%s",
            ACADEMYINSIGHT_MONGO["host"],
            ACADEMYINSIGHT_MONGO["port"],
            ACADEMYINSIGHT_MONGO["dbname"],
        )
        self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.mongo_db = self.mongo_client[ACADEMYINSIGHT_MONGO["dbname"]]
        # 연결 테스트
        self.mongo_client.admin.command("ping")
        logger.info("  → AcademyInsight Mongo 연결 성공")

        logger.info("=== 모든 DB 연결 완료 ===\n")

    def disconnect(self):
        """모든 DB 연결 종료"""
        if self.th_conn:
            self.th_conn.close()
            logger.info("TeacherHub PG 연결 종료")
        if self.ef_conn:
            self.ef_conn.close()
            logger.info("EduFit PG 연결 종료")
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("AcademyInsight Mongo 연결 종료")

    # ============================================
    # Step 1: collection_sources 통합
    # ============================================
    def migrate_collection_sources(self):
        """Step 1: collection_sources 통합 (EF 기존 8개 유지 + 신규 5개 추가)"""
        logger.info("=" * 60)
        logger.info("Step 1: collection_sources 통합")
        logger.info("=" * 60)

        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # 1a. EF 기존 소스 로드
        ef_cur.execute("SELECT id, code, name FROM collection_sources ORDER BY id")
        ef_sources = {row["code"]: row["id"] for row in ef_cur.fetchall()}
        logger.info("  EF 기존 소스: %d개 %s", len(ef_sources), list(ef_sources.keys()))

        # 1b. 신규 소스 추가 (ON CONFLICT DO NOTHING)
        added = 0
        for src in NEW_SOURCES:
            ef_cur.execute(
                """
                INSERT INTO collection_sources (name, code, base_url, source_type, config)
                VALUES (%(name)s, %(code)s, %(base_url)s, %(source_type)s, %(config)s::jsonb)
                ON CONFLICT (code) DO NOTHING
                RETURNING id
                """,
                src,
            )
            result = ef_cur.fetchone()
            if result:
                ef_sources[src["code"]] = result["id"]
                added += 1
                logger.info("  [+] 신규 소스 추가: %s (id=%d)", src["code"], result["id"])
            else:
                # 이미 존재 — ID 조회
                ef_cur.execute(
                    "SELECT id FROM collection_sources WHERE code = %s", (src["code"],)
                )
                row = ef_cur.fetchone()
                if row:
                    ef_sources[src["code"]] = row["id"]
                logger.info("  [=] 이미 존재: %s", src["code"])

        logger.info("  신규 추가: %d개, 총: %d개", added, len(ef_sources))

        # 1c. TH source_id → EF source_id 매핑 구축
        th_cur.execute("SELECT id, code FROM collection_sources ORDER BY id")
        th_sources = th_cur.fetchall()
        logger.info("  TH 소스: %d개", len(th_sources))

        for row in th_sources:
            th_id = row["id"]
            th_code = row["code"]
            ef_code = TH_CODE_TO_EF_CODE.get(th_code, th_code)
            ef_id = ef_sources.get(ef_code)
            if ef_id:
                self.source_id_map_th[th_id] = ef_id
                logger.info("  TH(%d:%s) → EF(%d:%s)", th_id, th_code, ef_id, ef_code)
            else:
                logger.warning(
                    "  TH 소스 매핑 실패: %s (id=%d) — EF에 %s 없음",
                    th_code,
                    th_id,
                    ef_code,
                )

        # 1d. AI source ObjectId → EF source_id 매핑 구축
        ai_sources = list(self.mongo_db.crawlsources.find())
        logger.info("  AI 소스: %d개", len(ai_sources))

        for src in ai_sources:
            key = (src["sourceType"], src["sourceId"])
            ef_code = AI_SOURCE_TO_EF_CODE.get(key)
            if ef_code:
                ef_id = ef_sources.get(ef_code)
                if ef_id:
                    self.source_id_map_ai[str(src["_id"])] = ef_id
                    logger.info(
                        "  AI(%s:%s) → EF(%d:%s)",
                        src["sourceType"],
                        src["sourceId"],
                        ef_id,
                        ef_code,
                    )
                else:
                    logger.warning(
                        "  AI 소스 매핑 실패: %s:%s → EF code=%s 없음",
                        src["sourceType"],
                        src["sourceId"],
                        ef_code,
                    )
            else:
                logger.warning(
                    "  AI 소스 매핑 없음: %s:%s", src["sourceType"], src["sourceId"]
                )

        self.stats["sources_added"] = added
        self.stats["sources_total"] = len(ef_sources)
        self.stats["th_source_mapped"] = len(self.source_id_map_th)
        self.stats["ai_source_mapped"] = len(self.source_id_map_ai)

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: TH %d/%d 매핑, AI %d/%d 매핑\n",
            len(self.source_id_map_th),
            len(th_sources),
            len(self.source_id_map_ai),
            len(ai_sources),
        )

    # ============================================
    # Step 2: analysis_keywords UPSERT
    # ============================================
    def migrate_analysis_keywords(self):
        """Step 2: TH analysis_keywords → EF UPSERT"""
        logger.info("=" * 60)
        logger.info("Step 2: analysis_keywords UPSERT")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor()

        th_cur.execute("SELECT category, keyword, weight, is_active FROM analysis_keywords")
        th_keywords = th_cur.fetchall()
        logger.info("  TH 키워드: %d개", len(th_keywords))

        inserted = 0
        skipped = 0
        for kw in th_keywords:
            ef_cur.execute(
                """
                INSERT INTO analysis_keywords (category, keyword, weight, is_active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (category, keyword) DO NOTHING
                """,
                (kw["category"], kw["keyword"], kw["weight"], kw["is_active"]),
            )
            if ef_cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        self.stats["keywords_inserted"] = inserted
        self.stats["keywords_skipped"] = skipped

        th_cur.close()
        ef_cur.close()
        logger.info("  → 완료: 추가 %d, 스킵(기존) %d\n", inserted, skipped)

    # ============================================
    # Step 3: teacher_id 매핑 구축
    # ============================================
    def build_teacher_id_map(self):
        """Step 3: TH teacher_id → EF teacher_id 매핑 (INSERT 없음)"""
        logger.info("=" * 60)
        logger.info("Step 3: teacher_id 매핑 구축")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # TH academy_id → code 매핑
        th_cur.execute("SELECT id, code FROM academies")
        self.th_academy_id_to_code = {row["id"]: row["code"] for row in th_cur.fetchall()}

        # EF academy code → id 매핑
        ef_cur.execute("SELECT id, code FROM academies")
        self.ef_academy_code_to_id = {row["code"]: row["id"] for row in ef_cur.fetchall()}

        # TH 강사 조회
        th_cur.execute(
            "SELECT id, name, academy_id FROM teachers ORDER BY id"
        )
        th_teachers = th_cur.fetchall()
        logger.info("  TH 강사: %d명", len(th_teachers))

        # EF 강사 조회 — (name, academy_id) 인덱스
        ef_cur.execute("SELECT id, name, academy_id FROM teachers")
        ef_teacher_lookup = {}
        for row in ef_cur.fetchall():
            key = (row["name"], row["academy_id"])
            ef_teacher_lookup[key] = row["id"]

        mapped = 0
        skipped_english = 0
        skipped_no_match = 0

        for t in th_teachers:
            th_id = t["id"]
            name = t["name"]
            th_academy_id = t["academy_id"]

            # 영문 이름 강사 스킵 (ASCII만 포함된 이름)
            if name and all(ord(c) < 128 for c in name.replace(" ", "")):
                skipped_english += 1
                logger.debug("  [SKIP] TH id=%d, name='%s' (영문 이름)", th_id, name)
                continue

            # academy_id 변환: TH → EF
            th_academy_code = self.th_academy_id_to_code.get(th_academy_id)
            if not th_academy_code:
                skipped_no_match += 1
                logger.warning(
                    "  [SKIP] TH id=%d '%s' — TH academy_id=%s 코드 없음",
                    th_id,
                    name,
                    th_academy_id,
                )
                continue

            ef_academy_code = TH_ACADEMY_CODE_TO_EF_CODE.get(
                th_academy_code, th_academy_code
            )
            ef_academy_id = self.ef_academy_code_to_id.get(ef_academy_code)
            if not ef_academy_id:
                skipped_no_match += 1
                logger.warning(
                    "  [SKIP] TH id=%d '%s' — EF academy '%s' 없음",
                    th_id,
                    name,
                    ef_academy_code,
                )
                continue

            # EF에서 같은 (name, academy_id) 찾기
            ef_id = ef_teacher_lookup.get((name, ef_academy_id))
            if ef_id:
                self.teacher_id_map[th_id] = ef_id
                mapped += 1
                logger.debug(
                    "  TH(%d:'%s') → EF(%d)", th_id, name, ef_id
                )
            else:
                skipped_no_match += 1
                logger.warning(
                    "  [SKIP] TH id=%d '%s' (academy=%s) — EF 매칭 실패",
                    th_id,
                    name,
                    ef_academy_code,
                )

        self.stats["teacher_mapped"] = mapped
        self.stats["teacher_skipped_english"] = skipped_english
        self.stats["teacher_skipped_no_match"] = skipped_no_match

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 매핑 %d, 스킵(영문) %d, 스킵(미매칭) %d\n",
            mapped,
            skipped_english,
            skipped_no_match,
        )

    # ============================================
    # Step 4: TeacherHub posts 마이그레이션
    # ============================================
    def migrate_posts_from_teacherhub(self):
        """Step 4: TH posts → EF posts (source_id 재매핑)"""
        logger.info("=" * 60)
        logger.info("Step 4: TeacherHub posts 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        th_cur.execute(
            """
            SELECT id, source_id, external_id, title, content, url, author,
                   post_date, view_count, like_count, comment_count, collected_at
            FROM posts
            ORDER BY id
            """
        )
        th_posts = th_cur.fetchall()
        logger.info("  TH posts: %d건", len(th_posts))

        inserted = 0
        skipped_no_source = 0
        skipped_dup = 0

        for p in th_posts:
            ef_source_id = self.source_id_map_th.get(p["source_id"])
            if not ef_source_id:
                skipped_no_source += 1
                continue

            ef_cur.execute(
                """
                INSERT INTO posts
                    (source_id, external_id, title, content, url, author,
                     post_date, view_count, like_count, comment_count, collected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id, external_id) DO NOTHING
                RETURNING id
                """,
                (
                    ef_source_id,
                    p["external_id"],
                    p["title"],
                    p["content"],
                    p["url"],
                    p["author"],
                    p["post_date"],
                    p["view_count"] or 0,
                    p["like_count"] or 0,
                    p["comment_count"] or 0,
                    p["collected_at"],
                ),
            )
            result = ef_cur.fetchone()
            if result:
                self.post_id_map_th[p["id"]] = result["id"]
                inserted += 1
            else:
                # 이미 존재 — 기존 ID 조회
                ef_cur.execute(
                    "SELECT id FROM posts WHERE source_id = %s AND external_id = %s",
                    (ef_source_id, p["external_id"]),
                )
                existing = ef_cur.fetchone()
                if existing:
                    self.post_id_map_th[p["id"]] = existing["id"]
                skipped_dup += 1

        self.stats["posts_th_inserted"] = inserted
        self.stats["posts_th_skipped_source"] = skipped_no_source
        self.stats["posts_th_skipped_dup"] = skipped_dup

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(소스없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_source,
            skipped_dup,
        )

    # ============================================
    # Step 5: AcademyInsight posts 마이그레이션
    # ============================================
    def migrate_posts_from_academyinsight(self):
        """Step 5: AI posts → EF posts (MongoDB → PostgreSQL)"""
        logger.info("=" * 60)
        logger.info("Step 5: AcademyInsight posts 마이그레이션")
        logger.info("=" * 60)

        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        ai_posts = list(
            self.mongo_db.posts.find({"isSample": {"$ne": True}}).sort("_id", 1)
        )
        logger.info("  AI posts: %d건", len(ai_posts))

        inserted = 0
        skipped_no_source = 0
        skipped_dup = 0

        for p in ai_posts:
            source_oid = str(p.get("source", ""))
            ef_source_id = self.source_id_map_ai.get(source_oid)
            if not ef_source_id:
                skipped_no_source += 1
                continue

            # external_id 추출
            post_url = p.get("postUrl", "")
            external_id = self._extract_external_id(post_url)

            title = p.get("title", "")
            if not title:
                skipped_no_source += 1
                continue

            ef_cur.execute(
                """
                INSERT INTO posts
                    (source_id, external_id, title, content, url, author,
                     post_date, view_count, like_count, comment_count, collected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id, external_id) DO NOTHING
                RETURNING id
                """,
                (
                    ef_source_id,
                    external_id,
                    title[:500],
                    p.get("content", ""),
                    post_url[:500] if post_url else None,
                    p.get("author", "알 수 없음"),
                    p.get("postedAt"),
                    p.get("viewCount", 0) or 0,
                    0,  # like_count (AI에 없음)
                    p.get("commentCount", 0) or 0,
                    p.get("collectedAt"),
                ),
            )
            result = ef_cur.fetchone()
            if result:
                self.post_id_map_ai[str(p["_id"])] = result["id"]
                inserted += 1
            else:
                # 이미 존재 — 기존 ID 조회
                ef_cur.execute(
                    "SELECT id FROM posts WHERE source_id = %s AND external_id = %s",
                    (ef_source_id, external_id),
                )
                existing = ef_cur.fetchone()
                if existing:
                    self.post_id_map_ai[str(p["_id"])] = existing["id"]
                skipped_dup += 1

        self.stats["posts_ai_inserted"] = inserted
        self.stats["posts_ai_skipped_source"] = skipped_no_source
        self.stats["posts_ai_skipped_dup"] = skipped_dup

        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(소스없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_source,
            skipped_dup,
        )

    # ============================================
    # Step 6: TeacherHub comments 마이그레이션
    # ============================================
    def migrate_comments(self):
        """Step 6: TH comments → EF (SELECT EXISTS 체크)"""
        logger.info("=" * 60)
        logger.info("Step 6: TeacherHub comments 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        th_cur.execute(
            """
            SELECT id, post_id, external_id, content, author,
                   comment_date, like_count, collected_at
            FROM comments
            ORDER BY id
            """
        )
        th_comments = th_cur.fetchall()
        logger.info("  TH comments: %d건", len(th_comments))

        # Step 7: AI comments (0건) 스킵 안내
        ai_comment_count = self.mongo_db.comments.count_documents({})
        logger.info("  AI comments: %d건 (스킵)", ai_comment_count)

        inserted = 0
        skipped_no_post = 0
        skipped_dup = 0

        for c in th_comments:
            ef_post_id = self.post_id_map_th.get(c["post_id"])
            if not ef_post_id:
                skipped_no_post += 1
                continue

            # 중복 체크 (comments에 UNIQUE 제약 없음)
            ef_cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM comments
                    WHERE post_id = %s AND external_id = %s
                )
                """,
                (ef_post_id, c["external_id"]),
            )
            if ef_cur.fetchone()["exists"]:
                # external_id가 NULL인 경우 content+author로 체크
                if c["external_id"] is not None:
                    skipped_dup += 1
                    continue

            # external_id가 NULL이면 content+author+comment_date로 중복 체크
            if c["external_id"] is None:
                ef_cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM comments
                        WHERE post_id = %s
                          AND content = %s
                          AND author = %s
                          AND comment_date = %s
                    )
                    """,
                    (ef_post_id, c["content"], c["author"], c["comment_date"]),
                )
                if ef_cur.fetchone()["exists"]:
                    skipped_dup += 1
                    continue

            ef_cur.execute(
                """
                INSERT INTO comments
                    (post_id, external_id, content, author, comment_date,
                     like_count, collected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    ef_post_id,
                    c["external_id"],
                    c["content"],
                    c["author"],
                    c["comment_date"],
                    c["like_count"] or 0,
                    c["collected_at"],
                ),
            )
            result = ef_cur.fetchone()
            if result:
                self.comment_id_map_th[c["id"]] = result["id"]
                inserted += 1

        self.stats["comments_inserted"] = inserted
        self.stats["comments_skipped_post"] = skipped_no_post
        self.stats["comments_skipped_dup"] = skipped_dup

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(포스트없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_post,
            skipped_dup,
        )

    # ============================================
    # Step 8: teacher_mentions 마이그레이션
    # ============================================
    def migrate_teacher_mentions(self):
        """Step 8: TH teacher_mentions → EF (teacher/post/comment ID 재매핑)"""
        logger.info("=" * 60)
        logger.info("Step 8: teacher_mentions 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        th_cur.execute(
            """
            SELECT id, teacher_id, post_id, comment_id, mention_type,
                   matched_text, context, sentiment, sentiment_score,
                   difficulty, is_recommended, analyzed_at
            FROM teacher_mentions
            ORDER BY id
            """
        )
        th_mentions = th_cur.fetchall()
        logger.info("  TH teacher_mentions: %d건", len(th_mentions))

        inserted = 0
        skipped_no_teacher = 0
        skipped_no_post = 0
        skipped_dup = 0

        for m in th_mentions:
            ef_teacher_id = self.teacher_id_map.get(m["teacher_id"])
            if not ef_teacher_id:
                skipped_no_teacher += 1
                continue

            ef_post_id = self.post_id_map_th.get(m["post_id"])
            if not ef_post_id:
                skipped_no_post += 1
                continue

            ef_comment_id = None
            if m["comment_id"] is not None:
                ef_comment_id = self.comment_id_map_th.get(m["comment_id"])
                if not ef_comment_id:
                    # comment가 매핑 안 됐으면 스킵
                    skipped_no_post += 1
                    continue

            # 중복 체크 (comment_id IS NULL 시 UNIQUE 작동 안 함)
            if ef_comment_id is None:
                ef_cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM teacher_mentions
                        WHERE teacher_id = %s
                          AND post_id = %s
                          AND comment_id IS NULL
                          AND mention_type = %s
                    )
                    """,
                    (ef_teacher_id, ef_post_id, m["mention_type"]),
                )
            else:
                ef_cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM teacher_mentions
                        WHERE teacher_id = %s
                          AND post_id = %s
                          AND comment_id = %s
                          AND mention_type = %s
                    )
                    """,
                    (ef_teacher_id, ef_post_id, ef_comment_id, m["mention_type"]),
                )

            if ef_cur.fetchone()["exists"]:
                skipped_dup += 1
                continue

            ef_cur.execute(
                """
                INSERT INTO teacher_mentions
                    (teacher_id, post_id, comment_id, mention_type,
                     matched_text, context, sentiment, sentiment_score,
                     difficulty, is_recommended, analyzed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ef_teacher_id,
                    ef_post_id,
                    ef_comment_id,
                    m["mention_type"],
                    m["matched_text"],
                    m["context"],
                    m["sentiment"],
                    m["sentiment_score"],
                    m["difficulty"],
                    m["is_recommended"],
                    m["analyzed_at"],
                ),
            )
            inserted += 1

        self.stats["mentions_inserted"] = inserted
        self.stats["mentions_skipped_teacher"] = skipped_no_teacher
        self.stats["mentions_skipped_post"] = skipped_no_post
        self.stats["mentions_skipped_dup"] = skipped_dup

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(강사없음) %d, 스킵(포스트/댓글없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_teacher,
            skipped_no_post,
            skipped_dup,
        )

    # ============================================
    # Step 9: daily_reports 마이그레이션
    # ============================================
    def migrate_daily_reports(self):
        """Step 9: TH daily_reports → EF (teacher_id 재매핑)"""
        logger.info("=" * 60)
        logger.info("Step 9: daily_reports 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor()

        th_cur.execute(
            """
            SELECT id, report_date, teacher_id,
                   mention_count, post_mention_count, comment_mention_count,
                   positive_count, negative_count, neutral_count, avg_sentiment_score,
                   difficulty_easy_count, difficulty_medium_count, difficulty_hard_count,
                   recommendation_count, mention_change, sentiment_change,
                   summary, top_keywords, created_at
            FROM daily_reports
            ORDER BY id
            """
        )
        th_reports = th_cur.fetchall()
        logger.info("  TH daily_reports: %d건", len(th_reports))

        inserted = 0
        skipped_no_teacher = 0
        skipped_dup = 0

        for r in th_reports:
            ef_teacher_id = self.teacher_id_map.get(r["teacher_id"])
            if not ef_teacher_id:
                skipped_no_teacher += 1
                continue

            ef_cur.execute(
                """
                INSERT INTO daily_reports
                    (report_date, teacher_id,
                     mention_count, post_mention_count, comment_mention_count,
                     positive_count, negative_count, neutral_count, avg_sentiment_score,
                     difficulty_easy_count, difficulty_medium_count, difficulty_hard_count,
                     recommendation_count, mention_change, sentiment_change,
                     summary, top_keywords, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_date, teacher_id) DO NOTHING
                """,
                (
                    r["report_date"],
                    ef_teacher_id,
                    r["mention_count"] or 0,
                    r["post_mention_count"] or 0,
                    r["comment_mention_count"] or 0,
                    r["positive_count"] or 0,
                    r["negative_count"] or 0,
                    r["neutral_count"] or 0,
                    r["avg_sentiment_score"],
                    r["difficulty_easy_count"] or 0,
                    r["difficulty_medium_count"] or 0,
                    r["difficulty_hard_count"] or 0,
                    r["recommendation_count"] or 0,
                    r["mention_change"] or 0,
                    r["sentiment_change"],
                    r["summary"],
                    r["top_keywords"],
                    r["created_at"],
                ),
            )
            if ef_cur.rowcount > 0:
                inserted += 1
            else:
                skipped_dup += 1

        self.stats["daily_reports_inserted"] = inserted
        self.stats["daily_reports_skipped_teacher"] = skipped_no_teacher
        self.stats["daily_reports_skipped_dup"] = skipped_dup

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(강사없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_teacher,
            skipped_dup,
        )

    # ============================================
    # Step 10: crawl_logs 마이그레이션
    # ============================================
    def migrate_crawl_logs(self):
        """Step 10: TH crawl_logs → EF (source_id 재매핑)"""
        logger.info("=" * 60)
        logger.info("Step 10: crawl_logs 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        th_cur.execute(
            """
            SELECT id, source_id, started_at, finished_at, status,
                   posts_collected, comments_collected, mentions_found,
                   error_message, created_at
            FROM crawl_logs
            ORDER BY id
            """
        )
        th_logs = th_cur.fetchall()
        logger.info("  TH crawl_logs: %d건", len(th_logs))

        inserted = 0
        skipped_no_source = 0
        skipped_dup = 0

        for log in th_logs:
            ef_source_id = self.source_id_map_th.get(log["source_id"])
            if not ef_source_id:
                skipped_no_source += 1
                continue

            # (source_id, started_at) 기준 중복 체크
            ef_cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM crawl_logs
                    WHERE source_id = %s AND started_at = %s
                )
                """,
                (ef_source_id, log["started_at"]),
            )
            if ef_cur.fetchone()["exists"]:
                skipped_dup += 1
                continue

            ef_cur.execute(
                """
                INSERT INTO crawl_logs
                    (source_id, started_at, finished_at, status,
                     posts_collected, comments_collected, mentions_found,
                     error_message, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ef_source_id,
                    log["started_at"],
                    log["finished_at"],
                    log["status"],
                    log["posts_collected"] or 0,
                    log["comments_collected"] or 0,
                    log["mentions_found"] or 0,
                    log["error_message"],
                    log["created_at"],
                ),
            )
            inserted += 1

        self.stats["crawl_logs_inserted"] = inserted
        self.stats["crawl_logs_skipped_source"] = skipped_no_source
        self.stats["crawl_logs_skipped_dup"] = skipped_dup

        th_cur.close()
        ef_cur.close()
        logger.info(
            "  → 완료: 추가 %d, 스킵(소스없음) %d, 스킵(중복) %d\n",
            inserted,
            skipped_no_source,
            skipped_dup,
        )

    # ============================================
    # Step 11: weekly_reports DDL + 데이터
    # ============================================
    def ensure_weekly_schema(self):
        """Step 11: weekly_reports, academy_weekly_stats 테이블 생성"""
        logger.info("=" * 60)
        logger.info("Step 11: weekly_reports 스키마 생성")
        logger.info("=" * 60)

        ef_cur = self.ef_conn.cursor()

        # weekly_reports 테이블
        ef_cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weekly_reports (
                id SERIAL PRIMARY KEY,
                teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
                academy_id INTEGER NOT NULL REFERENCES academies(id) ON DELETE CASCADE,

                year INT NOT NULL,
                week_number INT NOT NULL,
                week_start_date DATE NOT NULL,
                week_end_date DATE NOT NULL,

                mention_count INT DEFAULT 0,
                positive_count INT DEFAULT 0,
                negative_count INT DEFAULT 0,
                neutral_count INT DEFAULT 0,
                recommendation_count INT DEFAULT 0,

                difficulty_easy_count INT DEFAULT 0,
                difficulty_medium_count INT DEFAULT 0,
                difficulty_hard_count INT DEFAULT 0,

                avg_sentiment_score DECIMAL(5,4),
                sentiment_trend DECIMAL(5,4),
                mention_change_rate DECIMAL(6,2),
                weekly_rank INT,
                academy_rank INT,

                top_keywords JSONB DEFAULT '[]',
                source_distribution JSONB DEFAULT '{}',
                daily_distribution JSONB DEFAULT '{}',
                mention_types JSONB DEFAULT '{}',

                ai_summary TEXT,
                highlight_positive TEXT,
                highlight_negative TEXT,

                is_complete BOOLEAN DEFAULT FALSE,
                aggregated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uk_weekly_teacher_year_week
                    UNIQUE (teacher_id, year, week_number)
            )
            """
        )

        # academy_weekly_stats 테이블
        ef_cur.execute(
            """
            CREATE TABLE IF NOT EXISTS academy_weekly_stats (
                id SERIAL PRIMARY KEY,
                academy_id INTEGER NOT NULL REFERENCES academies(id) ON DELETE CASCADE,

                year INT NOT NULL,
                week_number INT NOT NULL,
                week_start_date DATE NOT NULL,
                week_end_date DATE NOT NULL,

                total_mentions INT DEFAULT 0,
                total_teachers_mentioned INT DEFAULT 0,
                avg_sentiment_score DECIMAL(5,4),
                total_positive INT DEFAULT 0,
                total_negative INT DEFAULT 0,
                total_recommendations INT DEFAULT 0,

                top_teacher_id INTEGER REFERENCES teachers(id),
                top_teacher_mentions INT DEFAULT 0,

                top_keywords JSONB DEFAULT '[]',
                source_distribution JSONB DEFAULT '{}',

                aggregated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uk_academy_weekly_year_week
                    UNIQUE (academy_id, year, week_number)
            )
            """
        )

        # 인덱스 생성
        ef_cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_weekly_reports_teacher ON weekly_reports(teacher_id)"
        )
        ef_cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_weekly_reports_academy ON weekly_reports(academy_id)"
        )
        ef_cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_weekly_reports_year_week ON weekly_reports(year, week_number)"
        )
        ef_cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_academy_weekly_academy ON academy_weekly_stats(academy_id)"
        )
        ef_cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_academy_weekly_year_week ON academy_weekly_stats(year, week_number)"
        )

        ef_cur.close()
        logger.info("  → weekly_reports, academy_weekly_stats 테이블 생성 완료\n")

    def migrate_weekly_reports(self):
        """Step 11b: TH weekly_reports → EF"""
        logger.info("=" * 60)
        logger.info("Step 11b: weekly_reports 데이터 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor()

        th_cur.execute(
            """
            SELECT id, teacher_id, academy_id,
                   year, week_number, week_start_date, week_end_date,
                   mention_count, positive_count, negative_count, neutral_count,
                   recommendation_count,
                   difficulty_easy_count, difficulty_medium_count, difficulty_hard_count,
                   avg_sentiment_score, sentiment_trend, mention_change_rate,
                   weekly_rank, academy_rank,
                   top_keywords, source_distribution, daily_distribution, mention_types,
                   ai_summary, highlight_positive, highlight_negative,
                   is_complete, aggregated_at, created_at
            FROM weekly_reports
            ORDER BY id
            """
        )
        th_reports = th_cur.fetchall()
        logger.info("  TH weekly_reports: %d건", len(th_reports))

        # TH academy_id → EF academy_id 매핑 구축
        th_academy_to_ef = {}
        for th_id, th_code in self.th_academy_id_to_code.items():
            ef_code = TH_ACADEMY_CODE_TO_EF_CODE.get(th_code, th_code)
            ef_id = self.ef_academy_code_to_id.get(ef_code)
            if ef_id:
                th_academy_to_ef[th_id] = ef_id

        inserted = 0
        skipped = 0

        for r in th_reports:
            ef_teacher_id = self.teacher_id_map.get(r["teacher_id"])
            ef_academy_id = th_academy_to_ef.get(r["academy_id"])

            if not ef_teacher_id or not ef_academy_id:
                skipped += 1
                continue

            # top_keywords 등 JSONB 필드 처리
            top_keywords = r["top_keywords"]
            if isinstance(top_keywords, str):
                top_keywords = psycopg2.extras.Json(top_keywords)
            elif top_keywords is not None:
                top_keywords = psycopg2.extras.Json(top_keywords)

            ef_cur.execute(
                """
                INSERT INTO weekly_reports
                    (teacher_id, academy_id,
                     year, week_number, week_start_date, week_end_date,
                     mention_count, positive_count, negative_count, neutral_count,
                     recommendation_count,
                     difficulty_easy_count, difficulty_medium_count, difficulty_hard_count,
                     avg_sentiment_score, sentiment_trend, mention_change_rate,
                     weekly_rank, academy_rank,
                     top_keywords, source_distribution, daily_distribution, mention_types,
                     ai_summary, highlight_positive, highlight_negative,
                     is_complete, aggregated_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT uk_weekly_teacher_year_week DO NOTHING
                """,
                (
                    ef_teacher_id,
                    ef_academy_id,
                    r["year"],
                    r["week_number"],
                    r["week_start_date"],
                    r["week_end_date"],
                    r["mention_count"] or 0,
                    r["positive_count"] or 0,
                    r["negative_count"] or 0,
                    r["neutral_count"] or 0,
                    r["recommendation_count"] or 0,
                    r["difficulty_easy_count"] or 0,
                    r["difficulty_medium_count"] or 0,
                    r["difficulty_hard_count"] or 0,
                    r["avg_sentiment_score"],
                    r["sentiment_trend"],
                    r["mention_change_rate"],
                    r["weekly_rank"],
                    r["academy_rank"],
                    psycopg2.extras.Json(r["top_keywords"]) if r["top_keywords"] else "[]",
                    psycopg2.extras.Json(r["source_distribution"]) if r["source_distribution"] else "{}",
                    psycopg2.extras.Json(r["daily_distribution"]) if r["daily_distribution"] else "{}",
                    psycopg2.extras.Json(r["mention_types"]) if r["mention_types"] else "{}",
                    r["ai_summary"],
                    r["highlight_positive"],
                    r["highlight_negative"],
                    r["is_complete"],
                    r["aggregated_at"],
                    r["created_at"],
                ),
            )
            if ef_cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        self.stats["weekly_reports_inserted"] = inserted
        self.stats["weekly_reports_skipped"] = skipped

        th_cur.close()
        ef_cur.close()
        logger.info("  → 완료: 추가 %d, 스킵 %d\n", inserted, skipped)

    # ============================================
    # Step 12: academy_weekly_stats 마이그레이션
    # ============================================
    def migrate_academy_weekly_stats(self):
        """Step 12: TH academy_weekly_stats → EF"""
        logger.info("=" * 60)
        logger.info("Step 12: academy_weekly_stats 마이그레이션")
        logger.info("=" * 60)

        th_cur = self.th_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ef_cur = self.ef_conn.cursor()

        th_cur.execute(
            """
            SELECT id, academy_id,
                   year, week_number, week_start_date, week_end_date,
                   total_mentions, total_teachers_mentioned, avg_sentiment_score,
                   total_positive, total_negative, total_recommendations,
                   top_teacher_id, top_teacher_mentions,
                   top_keywords, source_distribution,
                   aggregated_at, created_at
            FROM academy_weekly_stats
            ORDER BY id
            """
        )
        th_stats = th_cur.fetchall()
        logger.info("  TH academy_weekly_stats: %d건", len(th_stats))

        # TH academy_id → EF academy_id 매핑
        th_academy_to_ef = {}
        for th_id, th_code in self.th_academy_id_to_code.items():
            ef_code = TH_ACADEMY_CODE_TO_EF_CODE.get(th_code, th_code)
            ef_id = self.ef_academy_code_to_id.get(ef_code)
            if ef_id:
                th_academy_to_ef[th_id] = ef_id

        inserted = 0
        skipped = 0

        for s in th_stats:
            ef_academy_id = th_academy_to_ef.get(s["academy_id"])
            if not ef_academy_id:
                skipped += 1
                continue

            ef_top_teacher_id = None
            if s["top_teacher_id"]:
                ef_top_teacher_id = self.teacher_id_map.get(s["top_teacher_id"])

            ef_cur.execute(
                """
                INSERT INTO academy_weekly_stats
                    (academy_id,
                     year, week_number, week_start_date, week_end_date,
                     total_mentions, total_teachers_mentioned, avg_sentiment_score,
                     total_positive, total_negative, total_recommendations,
                     top_teacher_id, top_teacher_mentions,
                     top_keywords, source_distribution,
                     aggregated_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT uk_academy_weekly_year_week DO NOTHING
                """,
                (
                    ef_academy_id,
                    s["year"],
                    s["week_number"],
                    s["week_start_date"],
                    s["week_end_date"],
                    s["total_mentions"] or 0,
                    s["total_teachers_mentioned"] or 0,
                    s["avg_sentiment_score"],
                    s["total_positive"] or 0,
                    s["total_negative"] or 0,
                    s["total_recommendations"] or 0,
                    ef_top_teacher_id,
                    s["top_teacher_mentions"] or 0,
                    psycopg2.extras.Json(s["top_keywords"]) if s["top_keywords"] else "[]",
                    psycopg2.extras.Json(s["source_distribution"]) if s["source_distribution"] else "{}",
                    s["aggregated_at"],
                    s["created_at"],
                ),
            )
            if ef_cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        self.stats["academy_weekly_inserted"] = inserted
        self.stats["academy_weekly_skipped"] = skipped

        th_cur.close()
        ef_cur.close()
        logger.info("  → 완료: 추가 %d, 스킵 %d\n", inserted, skipped)

    # ============================================
    # 헬퍼: external_id 추출
    # ============================================
    def _extract_external_id(self, url):
        """AI postUrl에서 external_id 추출

        - DCInside: ?no=12345 → '12345'
        - Naver: articleid 파라미터 또는 path에서 추출
        - Daum: path 마지막 세그먼트
        - Fallback: URL의 SHA256 해시 (앞 16자리)
        """
        if not url:
            return hashlib.sha256(b"unknown").hexdigest()[:16]

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # DCInside: ?no=12345
            if "dcinside.com" in (parsed.hostname or ""):
                if "no" in params:
                    return params["no"][0]

            # Naver Cafe: articleid 파라미터
            if "cafe.naver.com" in (parsed.hostname or ""):
                if "articleid" in params:
                    return params["articleid"][0]
                # m.cafe.naver.com/cafeName/12345 형태
                path_parts = [p for p in parsed.path.split("/") if p]
                if len(path_parts) >= 2 and path_parts[-1].isdigit():
                    return path_parts[-1]

            # Daum Cafe: path 마지막 세그먼트
            if "cafe.daum.net" in (parsed.hostname or ""):
                path_parts = [p for p in parsed.path.split("/") if p]
                if path_parts:
                    return path_parts[-1]

        except Exception:
            pass

        # Fallback: SHA256 해시
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    # ============================================
    # 통계 출력
    # ============================================
    def _print_summary(self):
        """최종 마이그레이션 통계 출력"""
        logger.info("=" * 60)
        logger.info("마이그레이션 결과 요약")
        logger.info("=" * 60)

        sections = [
            ("소스 매핑", [
                ("sources_added", "신규 소스 추가"),
                ("sources_total", "총 소스 수"),
                ("th_source_mapped", "TH 소스 매핑"),
                ("ai_source_mapped", "AI 소스 매핑"),
            ]),
            ("키워드", [
                ("keywords_inserted", "추가"),
                ("keywords_skipped", "스킵(기존)"),
            ]),
            ("강사 매핑", [
                ("teacher_mapped", "매핑 성공"),
                ("teacher_skipped_english", "스킵(영문)"),
                ("teacher_skipped_no_match", "스킵(미매칭)"),
            ]),
            ("게시글", [
                ("posts_th_inserted", "TH 추가"),
                ("posts_th_skipped_source", "TH 스킵(소스)"),
                ("posts_th_skipped_dup", "TH 스킵(중복)"),
                ("posts_ai_inserted", "AI 추가"),
                ("posts_ai_skipped_source", "AI 스킵(소스)"),
                ("posts_ai_skipped_dup", "AI 스킵(중복)"),
            ]),
            ("댓글", [
                ("comments_inserted", "추가"),
                ("comments_skipped_post", "스킵(포스트)"),
                ("comments_skipped_dup", "스킵(중복)"),
            ]),
            ("멘션", [
                ("mentions_inserted", "추가"),
                ("mentions_skipped_teacher", "스킵(강사)"),
                ("mentions_skipped_post", "스킵(포스트)"),
                ("mentions_skipped_dup", "스킵(중복)"),
            ]),
            ("데일리 리포트", [
                ("daily_reports_inserted", "추가"),
                ("daily_reports_skipped_teacher", "스킵(강사)"),
                ("daily_reports_skipped_dup", "스킵(중복)"),
            ]),
            ("크롤 로그", [
                ("crawl_logs_inserted", "추가"),
                ("crawl_logs_skipped_source", "스킵(소스)"),
                ("crawl_logs_skipped_dup", "스킵(중복)"),
            ]),
            ("주간 리포트", [
                ("weekly_reports_inserted", "추가"),
                ("weekly_reports_skipped", "스킵"),
            ]),
            ("학원 주간 통계", [
                ("academy_weekly_inserted", "추가"),
                ("academy_weekly_skipped", "스킵"),
            ]),
        ]

        for section_name, items in sections:
            values = []
            for key, label in items:
                val = self.stats.get(key, "-")
                values.append(f"{label}: {val}")
            logger.info("  %-12s │ %s", section_name, " / ".join(values))

        if self.dry_run:
            logger.info("")
            logger.info("  *** DRY-RUN 모드: 모든 변경이 ROLLBACK 됩니다 ***")

    # ============================================
    # 오케스트레이션
    # ============================================
    def run(self, step=None):
        """전체 마이그레이션 실행 또는 특정 단계만 실행"""
        start_time = datetime.now()

        mode_label = "DRY-RUN" if self.dry_run else "실행"
        logger.info("╔══════════════════════════════════════════════════╗")
        logger.info("║  EduFit 데이터 마이그레이션 (%s)              ║", mode_label)
        logger.info("╚══════════════════════════════════════════════════╝")
        logger.info("")

        try:
            self.connect()

            # 전체 실행 순서
            all_steps = [
                ("sources", self.migrate_collection_sources),
                ("keywords", self.migrate_analysis_keywords),
                ("teacher_map", self.build_teacher_id_map),
                ("posts_th", self.migrate_posts_from_teacherhub),
                ("posts_ai", self.migrate_posts_from_academyinsight),
                ("comments", self.migrate_comments),
                ("mentions", self.migrate_teacher_mentions),
                ("daily_reports", self.migrate_daily_reports),
                ("crawl_logs", self.migrate_crawl_logs),
                ("weekly_schema", self.ensure_weekly_schema),
                ("weekly_reports", self.migrate_weekly_reports),
                ("academy_weekly", self.migrate_academy_weekly_stats),
            ]

            if step:
                # 특정 단계만 실행 (의존성 있는 앞 단계도 함께 실행)
                step_order = [s[0] for s in all_steps]
                if step not in step_order:
                    logger.error(
                        "알 수 없는 step: '%s'. 사용 가능: %s",
                        step,
                        ", ".join(step_order),
                    )
                    return

                # 선택된 step까지의 모든 의존 step 실행
                target_idx = step_order.index(step)
                steps_to_run = all_steps[: target_idx + 1]
                logger.info(
                    "Step '%s'까지 실행 (%d단계)\n", step, len(steps_to_run)
                )
            else:
                steps_to_run = all_steps
                logger.info("전체 12단계 실행\n")

            for step_name, step_func in steps_to_run:
                step_func()

            # 커밋 또는 롤백
            if self.dry_run:
                self.ef_conn.rollback()
                logger.info("\n*** DRY-RUN: ROLLBACK 완료 (데이터 변경 없음) ***\n")
            else:
                self.ef_conn.commit()
                logger.info("\n*** COMMIT 완료 ***\n")

            self._print_summary()

        except Exception as e:
            logger.error("마이그레이션 오류: %s", e, exc_info=True)
            if self.ef_conn:
                self.ef_conn.rollback()
                logger.info("ROLLBACK 실행됨")
            raise

        finally:
            elapsed = datetime.now() - start_time
            logger.info("\n소요 시간: %s", elapsed)
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="EduFit 데이터 마이그레이션 (TeacherHub + AcademyInsight → EduFit)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="시뮬레이션 모드: 트랜잭션 후 ROLLBACK (실제 변경 없음)",
    )
    parser.add_argument(
        "--step",
        type=str,
        default=None,
        choices=list(STEP_NAMES.keys()),
        help="특정 단계까지만 실행 (의존 단계 포함)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="상세 로그 출력 (DEBUG 레벨)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    migrator = EduFitMigrator(dry_run=args.dry_run)
    migrator.run(step=args.step)


if __name__ == "__main__":
    main()
