"""학원 API 엔드포인트"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....schemas.academy import AcademyCreate, AcademyUpdate, AcademyResponse
from ....schemas.teacher import TeacherResponse
from ....services import academy_service, teacher_service

router = APIRouter(prefix="/academies", tags=["Academies"])


@router.get("", response_model=list[AcademyResponse])
def list_academies(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """학원 목록 조회"""
    return academy_service.get_all(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{academy_id}", response_model=AcademyResponse)
def get_academy(academy_id: int, db: Session = Depends(get_db)):
    """학원 상세 조회"""
    academy = academy_service.get_by_id(db, academy_id)
    if not academy:
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    return academy


@router.get("/{academy_id}/teachers", response_model=list[TeacherResponse])
def get_academy_teachers(
    academy_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """학원별 강사 목록 조회"""
    academy = academy_service.get_by_id(db, academy_id)
    if not academy:
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    teachers = teacher_service.get_all(db, skip=skip, limit=limit, academy_id=academy_id)
    return [
        TeacherResponse(
            **{
                **t.__dict__,
                "academy_name": t.academy.name if t.academy else None,
                "subject_name": t.subject.name if t.subject else None,
            }
        )
        for t in teachers
    ]


@router.post("", response_model=AcademyResponse, status_code=201)
def create_academy(data: AcademyCreate, db: Session = Depends(get_db)):
    """학원 생성"""
    existing = academy_service.get_by_code(db, data.code)
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 학원 코드입니다.")
    return academy_service.create(db, data)


@router.put("/{academy_id}", response_model=AcademyResponse)
def update_academy(academy_id: int, data: AcademyUpdate, db: Session = Depends(get_db)):
    """학원 수정"""
    academy = academy_service.update(db, academy_id, data)
    if not academy:
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    return academy


@router.delete("/{academy_id}")
def delete_academy(academy_id: int, db: Session = Depends(get_db)):
    """학원 삭제"""
    if not academy_service.delete(db, academy_id):
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    return {"success": True, "message": "학원이 삭제되었습니다."}
