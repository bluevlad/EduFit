"""과목 서비스"""
from typing import Optional
from sqlalchemy.orm import Session

from ..models.subject import Subject
from ..schemas.subject import SubjectCreate, SubjectUpdate


def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
) -> list[Subject]:
    query = db.query(Subject)
    if category is not None:
        query = query.filter(Subject.category == category)
    return query.order_by(Subject.display_order).offset(skip).limit(limit).all()


def get_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    return db.query(Subject).filter(Subject.id == subject_id).first()


def count(db: Session, category: Optional[str] = None) -> int:
    query = db.query(Subject)
    if category is not None:
        query = query.filter(Subject.category == category)
    return query.count()


def create(db: Session, data: SubjectCreate) -> Subject:
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update(db: Session, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
    subject = get_by_id(db, subject_id)
    if not subject:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return subject
