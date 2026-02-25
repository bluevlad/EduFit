"""과목 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SubjectBase(BaseModel):
    name: str
    category: str
    display_order: int = 0


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    display_order: Optional[int] = None


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
