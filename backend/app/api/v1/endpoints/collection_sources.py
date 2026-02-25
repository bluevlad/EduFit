"""수집 소스 API 엔드포인트"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....models.collection_source import CollectionSource
from ....schemas.collection_source import CollectionSourceResponse

router = APIRouter(prefix="/collection-sources", tags=["Collection Sources"])


@router.get("", response_model=list[CollectionSourceResponse])
def list_collection_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """수집 소스 목록 조회"""
    return (
        db.query(CollectionSource)
        .order_by(CollectionSource.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{source_id}", response_model=CollectionSourceResponse)
def get_collection_source(source_id: int, db: Session = Depends(get_db)):
    """수집 소스 상세 조회"""
    source = db.query(CollectionSource).filter(CollectionSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="수집 소스를 찾을 수 없습니다.")
    return source
