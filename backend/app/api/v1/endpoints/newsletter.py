"""월간 뉴스레터 API

뉴스레터 플랫폼 연동용 엔드포인트:
- GET /newsletter/preview : HTML 미리보기 (브라우저 렌더링)
- GET /newsletter/html    : Raw HTML 반환 (뉴스레터 플랫폼 연동)
- GET /newsletter/data    : 뉴스레터 데이터 JSON 반환
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....auth.dependencies import require_admin
from ....services.newsletter_service import render_newsletter_html, generate_newsletter_data

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.get("/preview", response_class=HTMLResponse)
def newsletter_preview(
    year: int = Query(default=None, description="연도 (기본: 현재 연도)"),
    month: int = Query(default=None, ge=1, le=12, description="월 (기본: 현재 월)"),
    days: int = Query(default=30, ge=7, le=90, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """뉴스레터 HTML 미리보기 (관리자 전용)"""
    html = render_newsletter_html(db, year=year, month=month, days=days)
    return HTMLResponse(content=html)


@router.get("/html")
def newsletter_raw_html(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """뉴스레터 Raw HTML 반환 (뉴스레터 플랫폼 연동용)"""
    html = render_newsletter_html(db, year=year, month=month, days=days)
    return {"html": html}


@router.get("/data")
def newsletter_data(
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """뉴스레터 원본 데이터 JSON 반환"""
    data = generate_newsletter_data(db, days=days)
    return data
