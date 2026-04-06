"""
Naver News Search API Service
네이버 뉴스 검색 API 클라이언트
"""
import html
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """뉴스 기사 데이터"""
    title: str
    url: str
    original_url: str
    description: str
    source_name: str  # 'naver' or 'google'
    published_at: Optional[datetime] = None
    search_keyword: str = ""


@dataclass
class NewsSearchResult:
    """뉴스 검색 결과"""
    articles: List[NewsArticle] = field(default_factory=list)
    total_count: int = 0
    source: str = "naver"


class NaverNewsService:
    """네이버 뉴스 검색 API 서비스"""

    API_URL = "https://openapi.naver.com/v1/search/news.json"

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
    ):
        self.client_id = client_id or os.getenv("NAVER_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET", "")

        self.session = requests.Session()
        self.session.headers.update({
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "EduFit/1.0",
        })

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    @staticmethod
    def _strip_html(text: str) -> str:
        """HTML 태그 및 엔티티 제거"""
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        return text.strip()

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """RFC 822 날짜 파싱 (네이버 API 응답 형식)"""
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def search(
        self,
        query: str,
        display: int = 20,
        start: int = 1,
        sort: str = "date",
    ) -> NewsSearchResult:
        """네이버 뉴스 검색

        Args:
            query: 검색어
            display: 결과 수 (최대 100)
            start: 시작 위치 (최대 1000)
            sort: 정렬 (date: 날짜순, sim: 유사도순)
        """
        if not self.is_configured:
            logger.warning("Naver API credentials not configured")
            return NewsSearchResult()

        try:
            resp = self.session.get(
                self.API_URL,
                params={
                    "query": query,
                    "display": min(display, 100),
                    "start": min(start, 1000),
                    "sort": sort,
                },
                timeout=10,
            )

            if resp.status_code != 200:
                logger.error(f"Naver API error: {resp.status_code} - {resp.text[:200]}")
                return NewsSearchResult()

            data = resp.json()
            articles = []

            for item in data.get("items", []):
                articles.append(NewsArticle(
                    title=self._strip_html(item.get("title", "")),
                    url=item.get("link", ""),
                    original_url=item.get("originallink", ""),
                    description=self._strip_html(item.get("description", "")),
                    source_name="naver",
                    published_at=self._parse_date(item.get("pubDate")),
                    search_keyword=query,
                ))

            return NewsSearchResult(
                articles=articles,
                total_count=data.get("total", 0),
                source="naver",
            )

        except requests.RequestException as e:
            logger.error(f"Naver API request failed: {e}")
            return NewsSearchResult()
