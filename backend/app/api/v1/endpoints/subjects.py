"""과목 API 엔드포인트"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from ....services import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectResponse])
def list_subjects(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """과목 목록 조회"""
    return subject_service.get_all(db, skip=skip, limit=limit, category=category)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    """과목 상세 조회"""
    subject = subject_service.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
    return subject


@router.post("", response_model=SubjectResponse, status_code=201)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    """과목 생성"""
    return subject_service.create(db, data)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db)):
    """과목 수정"""
    subject = subject_service.update(db, subject_id, data)
    if not subject:
        raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
    return subject
