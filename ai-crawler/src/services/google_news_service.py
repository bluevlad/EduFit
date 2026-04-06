"""
Google News RSS Service
구글 뉴스 RSS 피드 기반 검색 서비스
"""
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import quote

import feedparser

from .naver_news_service import NewsArticle, NewsSearchResult

logger = logging.getLogger(__name__)


class GoogleNewsService:
    """구글 뉴스 RSS 서비스"""

    RSS_URL = "https://news.google.com/rss/search"

    @staticmethod
    def _strip_html(text: str) -> str:
        if not text:
            return ""
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def search(
        self,
        query: str,
        lang: str = "ko",
        country: str = "KR",
        when: str = "7d",
        max_results: int = 20,
    ) -> NewsSearchResult:
        """구글 뉴스 RSS 검색

        Args:
            query: 검색어
            lang: 언어
            country: 국가
            when: 기간 (1d, 7d, 30d)
            max_results: 최대 결과 수
        """
        try:
            url = (
                f"{self.RSS_URL}?q={quote(query)}"
                f"&hl={lang}&gl={country}&ceid={country}:{lang}"
            )
            if when:
                url += f"&when={when}"

            feed = feedparser.parse(url)
            articles = []

            for entry in feed.entries[:max_results]:
                # 구글 RSS에서 언론사 정보 추출
                source_info = getattr(entry, "source", None)
                publisher = source_info.get("title", "") if source_info else ""

                description = self._strip_html(
                    getattr(entry, "summary", "")
                )
                if len(description) > 500:
                    description = description[:497] + "..."

                articles.append(NewsArticle(
                    title=self._strip_html(entry.get("title", "")),
                    url=entry.get("link", ""),
                    original_url=entry.get("link", ""),
                    description=description,
                    source_name="google",
                    published_at=self._parse_date(
                        entry.get("published", "")
                    ),
                    search_keyword=query,
                ))

            return NewsSearchResult(
                articles=articles,
                total_count=len(articles),
                source="google",
            )

        except Exception as e:
            logger.error(f"Google News RSS failed: {e}")
            return NewsSearchResult()
