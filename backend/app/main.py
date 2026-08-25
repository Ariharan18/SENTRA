"""
SENTRA – Intelligent Safety & Threat Detection Platform
FastAPI Application Entrypoint
"""

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.emergency_contacts import router as emergency_contacts_router


def create_application() -> FastAPI:
    """
    Application factory pattern to initialize and configure the FastAPI application.
    Centralizes middleware, exception handlers, metadata, and routing.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure Cross-Origin Resource Sharing (CORS) Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list if settings.cors_origins_list else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Centralized application exception handlers
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "errors": exc.errors()},
        )

    # Root endpoint
    @application.get(
        "/",
        status_code=status.HTTP_200_OK,
        tags=["General"],
        summary="Root Endpoint",
        description="Returns basic system status and links to API documentation."
    )
    async def root():
        """
        Root endpoint confirming that the SENTRA API server is active.
        Does not expose internal secrets or credentials.
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

    # Health check endpoints
    @application.get(
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

    @application.get(
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

    # Register API Routers
    application.include_router(
        auth_router,
        prefix=f"{settings.API_PREFIX}/auth",
        tags=["Authentication"]
    )
    application.include_router(
        users_router,
        prefix=f"{settings.API_PREFIX}/users",
        tags=["Users"]
    )
    # Register Emergency Contacts at both /api/users/emergency-contacts and /api/emergency-contacts
    application.include_router(
        emergency_contacts_router,
        prefix=f"{settings.API_PREFIX}/users/emergency-contacts",
        tags=["Emergency Contacts"]
    )
    application.include_router(
        emergency_contacts_router,
        prefix=f"{settings.API_PREFIX}/emergency-contacts",
        tags=["Emergency Contacts"]
    )

    return application


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
