"""학원 서비스"""
from typing import Optional
from sqlalchemy.orm import Session

from ..models.academy import Academy
from ..schemas.academy import AcademyCreate, AcademyUpdate


def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> list[Academy]:
    query = db.query(Academy)
    if is_active is not None:
        query = query.filter(Academy.is_active == is_active)
    return query.order_by(Academy.id).offset(skip).limit(limit).all()


def get_by_id(db: Session, academy_id: int) -> Optional[Academy]:
    return db.query(Academy).filter(Academy.id == academy_id).first()


def get_by_code(db: Session, code: str) -> Optional[Academy]:
    return db.query(Academy).filter(Academy.code == code).first()


def count(db: Session, is_active: Optional[bool] = None) -> int:
    query = db.query(Academy)
    if is_active is not None:
        query = query.filter(Academy.is_active == is_active)
    return query.count()


def create(db: Session, data: AcademyCreate) -> Academy:
    academy = Academy(**data.model_dump())
    db.add(academy)
    db.commit()
    db.refresh(academy)
    return academy


def update(db: Session, academy_id: int, data: AcademyUpdate) -> Optional[Academy]:
    academy = get_by_id(db, academy_id)
    if not academy:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(academy, field, value)
    db.commit()
    db.refresh(academy)
    return academy


def delete(db: Session, academy_id: int) -> bool:
    academy = get_by_id(db, academy_id)
    if not academy:
        return False
    db.delete(academy)
    db.commit()
    return True
