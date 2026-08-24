"""
SENTRA – Intelligent Safety & Threat Detection Platform
FastAPI Application Entrypoint
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Initialize FastAPI application instance with OpenAPI metadata
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.cors_origins_list else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["General"],
    summary="Root Endpoint",
    description="Returns basic system status and links to API documentation."
)
async def root():
    """
    Root endpoint confirming that the SENTRA API server is active.
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "message": "Welcome to SENTRA – Intelligent Safety & Threat Detection Platform API"
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Health Check Endpoint",
    description="Returns the current operational health status of the SENTRA backend service."
)
async def health_check():
    """
    Health check probe endpoint for uptime monitoring and readiness verification.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get(
    "/api/health",
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="API Health Check Endpoint",
    description="API-prefixed health check endpoint."
)
async def api_health_check():
    """
    API-prefixed health check endpoint.
    """
    return {
        "status": "healthy",
        "service": f"{settings.APP_NAME} REST API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
