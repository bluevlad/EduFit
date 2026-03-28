"""트렌드 분석 API 엔드포인트"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....services import trend_service

router = APIRouter(prefix="/analytics", tags=["Analytics - Trends"])


@router.get("/dashboard")
def get_dashboard(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """종합 트렌드 대시보드 - 모든 분석 데이터를 한 번에 반환"""
    return trend_service.get_dashboard(db, days=days)


@router.get("/mention-trend")
def get_mention_trend(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """언급량 이동평균 트렌드"""
    return trend_service.get_mention_trend(db, days=days)


@router.get("/sentiment-bollinger")
def get_sentiment_bollinger(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """감성점수 볼린저 밴드 분석"""
    return trend_service.get_sentiment_bollinger(db, days=days)


@router.get("/momentum")
def get_momentum_ranking(
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db),
):
    """모멘텀 기반 강사 랭킹"""
    return trend_service.get_momentum_ranking(db, limit=limit)


@router.get("/pareto")
def get_pareto(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """파레토 분석 (언급 집중도)"""
    return trend_service.get_pareto(db, days=days)


@router.get("/seasonality")
def get_seasonality(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """요일별 계절성 분석"""
    return trend_service.get_seasonality(db, days=days)


@router.get("/correlation")
def get_correlation(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """지표 간 상관관계 분석"""
    return trend_service.get_correlation(db, days=days)


@router.get("/teacher-heatmap")
def get_teacher_heatmap(
    weeks: int = Query(12, ge=4, le=24, description="분석 주수"),
    limit: int = Query(15, ge=5, le=30, description="강사 수"),
    db: Session = Depends(get_db),
):
    """강사별 주간 감성 히트맵"""
    return trend_service.get_teacher_heatmap(db, weeks=weeks, limit=limit)


@router.get("/academy-bubble")
def get_academy_bubble(
    days: int = Query(90, ge=7, le=365, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
):
    """학원별 버블차트 데이터"""
    return trend_service.get_academy_bubble(db, days=days)
