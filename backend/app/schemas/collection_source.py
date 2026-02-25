"""수집 소스 스키마"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class CollectionSourceBase(BaseModel):
    name: str
    code: str
    base_url: Optional[str] = None
    source_type: Optional[str] = None
    is_active: bool = True
    config: Optional[dict[str, Any]] = None


class CollectionSourceCreate(CollectionSourceBase):
    pass


class CollectionSourceResponse(CollectionSourceBase):
    id: int
    last_crawled_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
