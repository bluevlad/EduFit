"""분석 API 엔드포인트"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....services import analysis_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/summary")
def get_summary(
    date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """오늘 요약 통계"""
    return analysis_service.get_summary(db, report_date=date)


@router.get("/ranking")
def get_ranking(
    date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db),
):
    """강사 랭킹"""
    return analysis_service.get_ranking(db, report_date=date, limit=limit)


@router.get("/academy-stats")
def get_academy_stats(
    date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """학원별 통계"""
    return analysis_service.get_academy_stats(db, report_date=date)
