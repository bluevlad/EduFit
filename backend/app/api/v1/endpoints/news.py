"""뉴스 기사 공개 API

네이버/구글 뉴스에서 수집된 강사·학원 관련 기사를 조회합니다.
인증 없이 접근 가능 — 뉴스레터 플랫폼에서 호출합니다.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....services import news_service

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/recent")
def get_recent_news(
    days: int = Query(default=7, ge=1, le=90, description="조회 기간 (일)"),
    limit: int = Query(default=10, ge=1, le=50, description="조회 건수"),
    offset: int = Query(default=0, ge=0, description="오프셋"),
    teacher_id: Optional[int] = Query(default=None, description="특정 강사 필터"),
    db: Session = Depends(get_db),
):
    """최근 뉴스 기사 목록"""
    return news_service.get_recent_articles(
        db, days=days, limit=limit, offset=offset, teacher_id=teacher_id,
    )


@router.get("/source-stats")
def get_source_stats(
    days: int = Query(default=7, ge=1, le=90, description="조회 기간 (일)"),
    db: Session = Depends(get_db),
):
    """소스 유형별 언급 통계 (뉴스/카페/갤러리/포럼)"""
    return news_service.get_source_stats(db, days=days)


@router.get("/{post_id}")
def get_news_detail(
    post_id: int,
    db: Session = Depends(get_db),
):
    """뉴스 기사 상세 (언급된 강사 목록 포함)"""
    result = news_service.get_article_detail(db, post_id)
    if not result:
        raise HTTPException(status_code=404, detail="뉴스 기사를 찾을 수 없습니다")
    return result
