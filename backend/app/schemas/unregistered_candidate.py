"""미등록 인물 후보 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UnregisteredCandidateResponse(BaseModel):
    id: int
    name: str
    mention_count: int
    first_seen_at: datetime
    last_seen_at: datetime
    sample_contexts: list = []
    source_distribution: dict = {}
    status: str
    resolved_at: Optional[datetime] = None
    resolved_teacher_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnregisteredCandidateAction(BaseModel):
    """관리자 처리 액션"""
    action: str  # "register" or "ignore"
    # register 시 사용
    academy_id: Optional[int] = None
    subject_id: Optional[int] = None
    aliases: Optional[list[str]] = None
