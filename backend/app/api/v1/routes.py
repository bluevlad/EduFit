"""API v1 라우터 통합"""
from fastapi import APIRouter

from .endpoints.academies import router as academies_router
from .endpoints.teachers import router as teachers_router
from .endpoints.subjects import router as subjects_router
from .endpoints.collection_sources import router as collection_sources_router

api_router = APIRouter()
api_router.include_router(academies_router)
api_router.include_router(teachers_router)
api_router.include_router(subjects_router)
api_router.include_router(collection_sources_router)
