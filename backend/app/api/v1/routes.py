"""API v1 라우터 통합"""
from fastapi import APIRouter

from .endpoints.academies import router as academies_router
from .endpoints.teachers import router as teachers_router
from .endpoints.subjects import router as subjects_router
from .endpoints.collection_sources import router as collection_sources_router
from .endpoints.reports import router as reports_router
from .endpoints.analysis import router as analysis_router
from .endpoints.weekly import router as weekly_router
from .endpoints.unregistered_candidates import router as unregistered_candidates_router
from .endpoints.subscriptions import router as subscriptions_router
from .endpoints.trends import router as trends_router
from .endpoints.newsletter import router as newsletter_router
from .endpoints.news import router as news_router

api_router = APIRouter()
api_router.include_router(academies_router)
api_router.include_router(teachers_router)
api_router.include_router(subjects_router)
api_router.include_router(collection_sources_router)
api_router.include_router(reports_router)
api_router.include_router(analysis_router)
api_router.include_router(weekly_router)
api_router.include_router(unregistered_candidates_router)
api_router.include_router(subscriptions_router)
api_router.include_router(trends_router)
api_router.include_router(newsletter_router)
api_router.include_router(news_router)
