"""학원 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AcademyBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    code: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    keywords: Optional[list[str]] = None
    is_active: bool = True


class AcademyCreate(AcademyBase):
    pass


class AcademyUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    keywords: Optional[list[str]] = None
    is_active: Optional[bool] = None


class AcademyResponse(AcademyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
