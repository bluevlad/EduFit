"""강사 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TeacherBase(BaseModel):
    academy_id: Optional[int] = None
    subject_id: Optional[int] = None
    name: str
    aliases: Optional[list[str]] = None
    profile_url: Optional[str] = None
    is_active: bool = True


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    academy_id: Optional[int] = None
    subject_id: Optional[int] = None
    name: Optional[str] = None
    aliases: Optional[list[str]] = None
    profile_url: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherResponse(TeacherBase):
    id: int
    academy_name: Optional[str] = None
    subject_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
