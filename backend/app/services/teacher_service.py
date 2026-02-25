"""강사 서비스"""
from typing import Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from ..models.teacher import Teacher
from ..schemas.teacher import TeacherCreate, TeacherUpdate


def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    academy_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> list[Teacher]:
    query = db.query(Teacher)
    if academy_id is not None:
        query = query.filter(Teacher.academy_id == academy_id)
    if subject_id is not None:
        query = query.filter(Teacher.subject_id == subject_id)
    if is_active is not None:
        query = query.filter(Teacher.is_active == is_active)
    return query.order_by(Teacher.id).offset(skip).limit(limit).all()


def get_by_id(db: Session, teacher_id: int) -> Optional[Teacher]:
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()


def search(db: Session, query_str: str, skip: int = 0, limit: int = 50) -> list[Teacher]:
    return (
        db.query(Teacher)
        .filter(
            or_(
                Teacher.name.ilike(f"%{query_str}%"),
                Teacher.aliases.any(query_str),
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def count(
    db: Session,
    academy_id: Optional[int] = None,
    subject_id: Optional[int] = None,
) -> int:
    query = db.query(Teacher)
    if academy_id is not None:
        query = query.filter(Teacher.academy_id == academy_id)
    if subject_id is not None:
        query = query.filter(Teacher.subject_id == subject_id)
    return query.count()


def create(db: Session, data: TeacherCreate) -> Teacher:
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def update(db: Session, teacher_id: int, data: TeacherUpdate) -> Optional[Teacher]:
    teacher = get_by_id(db, teacher_id)
    if not teacher:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher


def delete(db: Session, teacher_id: int) -> bool:
    teacher = get_by_id(db, teacher_id)
    if not teacher:
        return False
    db.delete(teacher)
    db.commit()
    return True
