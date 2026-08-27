"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.traffic import router as traffic_router
from app.api.analytics import router as analytics_router

settings = get_settings()
app = FastAPI(
    title="Smart Traffic Analytics API",
    description="Versioned API for the Smart Traffic Analytics system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traffic_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["operations"])
def health_check() -> dict[str, str]:
    """Return liveness status without requiring a database connection."""

    return {"status": "ok"}
