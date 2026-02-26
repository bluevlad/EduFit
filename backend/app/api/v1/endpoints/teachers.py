"""강사 API 엔드포인트"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from ....services import teacher_service, analysis_service

router = APIRouter(prefix="/teachers", tags=["Teachers"])


def _to_response(t) -> TeacherResponse:
    return TeacherResponse(
        **{
            **t.__dict__,
            "academy_name": t.academy.name if t.academy else None,
            "subject_name": t.subject.name if t.subject else None,
        }
    )


@router.get("/search", response_model=list[TeacherResponse])
def search_teachers(
    q: str = Query(..., min_length=1, description="검색어 (이름 또는 별칭)"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """강사 검색 (이름+별칭)"""
    teachers = teacher_service.search(db, q, skip=skip, limit=limit)
    return [_to_response(t) for t in teachers]


@router.get("", response_model=list[TeacherResponse])
def list_teachers(
    skip: int = 0,
    limit: int = 100,
    academy_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """강사 목록 조회"""
    teachers = teacher_service.get_all(
        db, skip=skip, limit=limit,
        academy_id=academy_id, subject_id=subject_id, is_active=is_active,
    )
    return [_to_response(t) for t in teachers]


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """강사 상세 조회"""
    teacher = teacher_service.get_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다.")
    return _to_response(teacher)


@router.get("/{teacher_id}/mentions")
def get_teacher_mentions(
    teacher_id: int,
    limit: int = Query(10, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db),
):
    """강사별 최근 멘션"""
    teacher = teacher_service.get_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다.")
    return analysis_service.get_teacher_mentions(db, teacher_id=teacher_id, limit=limit)


@router.get("/{teacher_id}/reports")
def get_teacher_reports(
    teacher_id: int,
    days: int = Query(7, ge=1, le=90, description="최근 N일"),
    db: Session = Depends(get_db),
):
    """강사별 리포트 이력"""
    teacher = teacher_service.get_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다.")
    return analysis_service.get_teacher_reports(db, teacher_id=teacher_id, days=days)


@router.post("", response_model=TeacherResponse, status_code=201)
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db)):
    """강사 생성"""
    teacher = teacher_service.create(db, data)
    return _to_response(teacher)


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: int, data: TeacherUpdate, db: Session = Depends(get_db)):
    """강사 수정"""
    teacher = teacher_service.update(db, teacher_id, data)
    if not teacher:
        raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다.")
    return _to_response(teacher)


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """강사 삭제"""
    if not teacher_service.delete(db, teacher_id):
        raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다.")
    return {"success": True, "message": "강사가 삭제되었습니다."}
