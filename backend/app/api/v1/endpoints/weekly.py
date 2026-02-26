"""주간 리포트 API 엔드포인트"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....services import weekly_service

router = APIRouter(prefix="/weekly", tags=["Weekly"])


@router.get("/summary")
def get_weekly_summary(
    year: int = Query(..., description="연도"),
    week: int = Query(..., description="주차"),
    db: Session = Depends(get_db),
):
    """주간 요약"""
    return weekly_service.get_summary(db, year=year, week=week)


@router.get("/ranking")
def get_weekly_ranking(
    year: int = Query(..., description="연도"),
    week: int = Query(..., description="주차"),
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db),
):
    """주간 랭킹"""
    return weekly_service.get_ranking(db, year=year, week=week, limit=limit)


@router.get("/teacher/{teacher_id}/trend")
def get_teacher_trend(
    teacher_id: int,
    weeks: int = Query(8, ge=1, le=52, description="최근 N주"),
    db: Session = Depends(get_db),
):
    """강사 트렌드 (최근 N주)"""
    return weekly_service.get_teacher_trend(db, teacher_id=teacher_id, weeks=weeks)
