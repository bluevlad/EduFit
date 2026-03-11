"""EduFit API 서버

학원/강사 평판 분석 통합 플랫폼 REST API

실행 방법:
    cd C:\\GIT\\EduFit\\backend
    py -m uvicorn app.main:app --port 9070 --reload
"""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

from .core.config import settings
from .core.database import engine
from .api.v1.routes import api_router
from .auth.google_oauth import router as auth_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 이벤트"""
    # Startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    yield
    # Shutdown
    engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title="EduFit API",
    description="학원/강사 평판 분석 통합 플랫폼",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS 설정
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware (OAuth state 유지용)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change-me"))

# API 라우터 등록
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix="/api")


@app.get("/")
async def root():
    """API 루트"""
    return {
        "name": "EduFit API",
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "docs": "/api/docs",
            "academies": f"{settings.api_v1_prefix}/academies",
            "teachers": f"{settings.api_v1_prefix}/teachers",
            "subjects": f"{settings.api_v1_prefix}/subjects",
            "collection_sources": f"{settings.api_v1_prefix}/collection-sources",
            "reports": f"{settings.api_v1_prefix}/reports",
            "analysis": f"{settings.api_v1_prefix}/analysis",
            "weekly": f"{settings.api_v1_prefix}/weekly",
        },
    }


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "EduFit", "timestamp": datetime.now().isoformat()}
