"""
News Collector Service
네이버 뉴스 API + 구글 뉴스 RSS 통합 수집기
기존 Post → MentionExtractor 파이프라인과 연결
"""
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .naver_news_service import NaverNewsService, NewsArticle
from .google_news_service import GoogleNewsService
from .mention_extractor import MentionExtractor
from ..models import (
    Post, CollectionSource, CrawlLog, Academy, Teacher
)

logger = logging.getLogger(__name__)


class NewsCollector:
    """뉴스 수집 서비스

    학원/강사 키워드로 네이버+구글 뉴스를 검색하고,
    기존 Post 테이블에 저장하여 MentionExtractor 파이프라인에 연결합니다.
    """

    def __init__(
        self,
        db: Session,
        naver_client_id: str = None,
        naver_client_secret: str = None,
        max_results_per_keyword: int = 10,
    ):
        self.db = db
        self.naver = NaverNewsService(naver_client_id, naver_client_secret)
        self.google = GoogleNewsService()
        self.extractor = MentionExtractor(db)
        self.max_results = max_results_per_keyword

    def collect_all(self) -> Dict[str, Any]:
        """전체 뉴스 수집 (학원 + 주요 강사 + 업계 키워드)

        Returns:
            수집 통계 dict
        """
        stats = {
            "total_new": 0,
            "total_duplicate": 0,
            "total_mentions": 0,
            "keyword_stats": [],
        }

        keywords = self._build_keywords()
        logger.info(f"News collection: {len(keywords)} keywords")

        # 네이버/구글 소스 조회 (없으면 건너뜀)
        naver_source = self._get_source("naver_news")
        google_source = self._get_source("google_news")

        if not naver_source and not google_source:
            logger.warning("No news sources configured. Skip news collection.")
            return stats

        # 키워드별 수집 (Rate limit 방지를 위한 딜레이 포함)
        for i, kw_info in enumerate(keywords):
            keyword = kw_info["keyword"]
            kw_stat = {"keyword": keyword, "type": kw_info["type"], "new": 0, "dup": 0, "mentions": 0}

            # 네이버 API rate limit 방지 (초당 10건 제한)
            if i > 0:
                time.sleep(0.3)

            articles = self._search_keyword(keyword)
            logger.info(f"  [{kw_info['type']}] '{keyword}': {len(articles)} articles")

            for article in articles:
                source = naver_source if article.source_name == "naver" else google_source
                if not source:
                    continue

                post, created = self._save_article(source, article)
                if created:
                    kw_stat["new"] += 1
                    # 새 기사에 대해서만 멘션 추출
                    mentions = self.extractor.extract_and_save(post)
                    kw_stat["mentions"] += len(mentions)
                else:
                    kw_stat["dup"] += 1

            stats["total_new"] += kw_stat["new"]
            stats["total_duplicate"] += kw_stat["dup"]
            stats["total_mentions"] += kw_stat["mentions"]
            stats["keyword_stats"].append(kw_stat)

        # commit
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing news data: {e}")
            self.db.rollback()

        # 소스별 last_crawled_at 업데이트
        now = datetime.utcnow()
        if naver_source:
            naver_source.last_crawled_at = now
        if google_source:
            google_source.last_crawled_at = now
        self.db.commit()

        logger.info(
            f"News collection done: {stats['total_new']} new, "
            f"{stats['total_duplicate']} dup, {stats['total_mentions']} mentions"
        )
        return stats

    def _build_keywords(self) -> List[Dict[str, str]]:
        """수집 키워드 생성 (학원 + 주요 강사 + 업계)"""
        keywords = []

        # 1. 학원 키워드
        academies = self.db.query(Academy).filter(Academy.is_active == True).all()
        for academy in academies:
            # 학원 이름
            keywords.append({"keyword": academy.name, "type": "academy"})
            # 학원 추가 키워드 (첫 2개만 — 나머지는 노이즈 가능)
            if academy.keywords:
                for kw in academy.keywords[:2]:
                    if kw != academy.name:
                        keywords.append({"keyword": kw, "type": "academy"})

        # 2. 주요 강사 (멘션 빈도 상위 또는 전체 활성 강사)
        teachers = self._get_top_teachers(limit=20)
        for teacher in teachers:
            academy_name = teacher.academy.name if teacher.academy else ""
            # "강사명 학원명" 조합으로 동명이인 방지
            if academy_name:
                keywords.append({
                    "keyword": f"{teacher.name} {academy_name}",
                    "type": "teacher",
                })
            else:
                keywords.append({
                    "keyword": f"{teacher.name} 강사",
                    "type": "teacher",
                })

        # 3. 업계 키워드
        industry_keywords = [
            "공무원 학원",
            "공무원 인강",
            "공시 강사",
        ]
        for kw in industry_keywords:
            keywords.append({"keyword": kw, "type": "industry"})

        # 중복 키워드 제거
        seen = set()
        unique = []
        for item in keywords:
            if item["keyword"] not in seen:
                seen.add(item["keyword"])
                unique.append(item)

        return unique

    def _get_top_teachers(self, limit: int = 20) -> List:
        """멘션 빈도 상위 강사 조회 (없으면 전체 활성 강사)"""
        from sqlalchemy import func
        from ..models import TeacherMention

        # 최근 멘션 빈도 상위
        top_ids = (
            self.db.query(TeacherMention.teacher_id)
            .group_by(TeacherMention.teacher_id)
            .order_by(func.count().desc())
            .limit(limit)
            .all()
        )

        if top_ids:
            ids = [r[0] for r in top_ids]
            return (
                self.db.query(Teacher)
                .filter(Teacher.id.in_(ids), Teacher.is_active == True)
                .all()
            )

        # 멘션 데이터 없으면 활성 강사 상위 N명
        return (
            self.db.query(Teacher)
            .filter(Teacher.is_active == True)
            .limit(limit)
            .all()
        )

    def _search_keyword(self, keyword: str) -> List[NewsArticle]:
        """네이버 + 구글 동시 검색 후 URL 중복 제거"""
        articles = []

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}

            if self.naver.is_configured:
                futures[executor.submit(
                    self.naver.search, keyword, self.max_results
                )] = "naver"

            futures[executor.submit(
                self.google.search, keyword, max_results=self.max_results
            )] = "google"

            for future in as_completed(futures, timeout=15):
                try:
                    result = future.result()
                    articles.extend(result.articles)
                except Exception as e:
                    source = futures[future]
                    logger.warning(f"{source} search failed for '{keyword}': {e}")

        # URL 기반 중복 제거 (네이버 우선)
        seen_urls = set()
        unique = []
        for article in articles:
            # 정규화: 프로토콜, trailing slash 제거
            url_key = article.url.rstrip("/").replace("https://", "").replace("http://", "")
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique.append(article)

        return unique

    def _get_source(self, code: str) -> Optional[CollectionSource]:
        """collection_sources에서 소스 조회"""
        return (
            self.db.query(CollectionSource)
            .filter(CollectionSource.code == code, CollectionSource.is_active == True)
            .first()
        )

    def _save_article(self, source: CollectionSource, article: NewsArticle) -> tuple:
        """뉴스 기사를 Post 테이블에 저장

        Returns:
            (Post, created: bool)
        """
        # external_id: URL 해시 (뉴스는 고유 ID가 없으므로)
        external_id = self._url_hash(article.url)

        existing = self.db.query(Post).filter(
            and_(
                Post.source_id == source.id,
                Post.external_id == external_id,
            )
        ).first()

        if existing:
            return existing, False

        # 추가 중복 체크: 제목+URL 해시로 다른 소스에서 같은 기사 확인
        content_hash = self._content_hash(article.title, article.url)
        dup_by_hash = self.db.query(Post).filter(
            Post.url == article.original_url
        ).first()

        if dup_by_hash:
            return dup_by_hash, False

        post = Post(
            source_id=source.id,
            external_id=external_id,
            title=article.title,
            content=article.description,
            url=article.original_url or article.url,
            author=article.search_keyword,  # 뉴스: 검색 키워드를 author에 저장
            post_date=article.published_at,
            view_count=0,
            like_count=0,
            comment_count=0,
        )

        self.db.add(post)
        self.db.flush()

        return post, True

    @staticmethod
    def _url_hash(url: str) -> str:
        """URL을 짧은 해시로 변환 (external_id용)"""
        normalized = url.strip().lower().rstrip("/")
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    @staticmethod
    def _content_hash(title: str, url: str) -> str:
        """제목+URL 기반 콘텐츠 해시"""
        content = f"{title.strip().lower()}|{url.strip().lower()}"
        return hashlib.sha256(content.encode()).hexdigest()[:64]
