"""공통 스키마"""
from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    success: bool
    data: list[Any]
    total: int
    skip: int
    limit: int
