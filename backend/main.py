"""
GreenOps Carbon Engine — FastAPI 진입점
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from utils.logger import setup_logging, get_logger
from api.routes import carbon, schedule, health, regions  # ← regions, health 추가

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)                              # /health
app.include_router(carbon.router, prefix="/api/v1")            # /api/v1/carbon/*
app.include_router(regions.router, prefix="/api/v1")           # /api/v1/regions/*
app.include_router(schedule.router, prefix="/api/v1")          # /api/v1/schedule/*

logger.info(f"{settings.app_name} v{settings.app_version} 시작")
logger.info(f"데이터 소스: {settings.data_source}")


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "data_source": settings.data_source,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/config")
def get_config():
    """ 현재 설정 조회 (디버깅용) """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "data_source": settings.data_source,
        "default_region": settings.default_region,
        "default_instance_type": settings.default_instance_type,
        "scrape_interval_sec": settings.scrape_interval_sec,
        "prometheus_url": settings.prometheus_url,
        "carbon_aware_sdk_url": settings.carbon_aware_sdk_url,
    }