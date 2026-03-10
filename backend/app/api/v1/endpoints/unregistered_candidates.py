"""미등록 인물 후보 API 엔드포인트"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....models.unregistered_candidate import UnregisteredCandidate
from ....models.teacher import Teacher
from ....schemas.unregistered_candidate import (
    UnregisteredCandidateResponse,
    UnregisteredCandidateAction,
)
from ....auth.dependencies import require_admin

router = APIRouter(prefix="/unregistered-candidates", tags=["Unregistered Candidates"])


@router.get("", response_model=list[UnregisteredCandidateResponse])
def list_candidates(
    status: str = Query("pending", description="필터: pending, registered, ignored, all"),
    min_mentions: int = Query(1, ge=1, description="최소 언급 횟수"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """미등록 후보 목록 조회 (관리자 전용)"""
    query = db.query(UnregisteredCandidate)

    if status != "all":
        query = query.filter(UnregisteredCandidate.status == status)

    query = query.filter(UnregisteredCandidate.mention_count >= min_mentions)
    query = query.order_by(UnregisteredCandidate.mention_count.desc())

    return query.offset(skip).limit(limit).all()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """미등록 후보 통계"""
    pending = db.query(UnregisteredCandidate).filter(
        UnregisteredCandidate.status == "pending"
    ).count()
    registered = db.query(UnregisteredCandidate).filter(
        UnregisteredCandidate.status == "registered"
    ).count()
    ignored = db.query(UnregisteredCandidate).filter(
        UnregisteredCandidate.status == "ignored"
    ).count()

    return {
        "pending": pending,
        "registered": registered,
        "ignored": ignored,
        "total": pending + registered + ignored,
    }


@router.post("/{candidate_id}/resolve")
def resolve_candidate(
    candidate_id: int,
    action: UnregisteredCandidateAction,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """후보 처리: 강사 등록 또는 무시 (관리자 전용)"""
    candidate = db.query(UnregisteredCandidate).filter(
        UnregisteredCandidate.id == candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="후보를 찾을 수 없습니다.")

    if action.action == "register":
        # 강사로 등록
        teacher = Teacher(
            name=candidate.name,
            academy_id=action.academy_id,
            subject_id=action.subject_id,
            aliases=action.aliases or [],
            is_active=True,
        )
        db.add(teacher)
        db.flush()

        candidate.status = "registered"
        candidate.resolved_at = datetime.utcnow()
        candidate.resolved_teacher_id = teacher.id
        db.commit()

        return {
            "success": True,
            "message": f"'{candidate.name}'이(가) 강사로 등록되었습니다.",
            "teacher_id": teacher.id,
        }

    elif action.action == "ignore":
        candidate.status = "ignored"
        candidate.resolved_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "message": f"'{candidate.name}' 후보가 무시 처리되었습니다.",
        }

    else:
        raise HTTPException(status_code=400, detail="action은 'register' 또는 'ignore'이어야 합니다.")
