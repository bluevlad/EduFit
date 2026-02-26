"""리포트 API 엔드포인트"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/daily")
def get_daily_report(
    date: Optional[str] = Query(None, description="조회 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """일별 리포트"""
    return report_service.get_daily(db, report_date=date)


@router.get("/weekly")
def get_weekly_report(
    year: int = Query(..., description="연도"),
    week: int = Query(..., description="주차"),
    db: Session = Depends(get_db),
):
    """주별 리포트"""
    return report_service.get_weekly(db, year=year, week=week)


@router.get("/monthly")
def get_monthly_report(
    year: int = Query(..., description="연도"),
    month: int = Query(..., ge=1, le=12, description="월"),
    db: Session = Depends(get_db),
):
    """월별 리포트"""
    return report_service.get_monthly(db, year=year, month=month)


@router.get("/periods")
def get_periods(db: Session = Depends(get_db)):
    """선택 가능한 기간 목록"""
    return report_service.get_periods(db)
