"""
SENTRA – Backend Foundation Test Suite
Verifies application initialization, root endpoint, health checks,
Swagger/OpenAPI documentation endpoints, and configuration security.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    """
    Verify GET / returns 200 OK with correct application metadata and status.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app_name"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["environment"] == settings.ENVIRONMENT
    assert data["docs_url"] == "/docs"
    assert data["redoc_url"] == "/redoc"
    assert "message" in data


def test_health_endpoint():
    """
    Verify GET /health returns 200 OK with service name and healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["environment"] == settings.ENVIRONMENT


def test_api_health_endpoint():
    """
    Verify GET /api/health returns 200 OK.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == f"{settings.APP_NAME} REST API"


def test_docs_endpoint():
    """
    Verify GET /docs returns 200 OK and serves Swagger UI HTML.
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_redoc_endpoint():
    """
    Verify GET /redoc returns 200 OK and serves ReDoc HTML.
    """
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_openapi_json_endpoint():
    """
    Verify GET /openapi.json returns 200 OK and valid OpenAPI schema specification.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == settings.APP_NAME
    assert schema["info"]["version"] == settings.APP_VERSION
    assert "/" in schema["paths"]
    assert "/health" in schema["paths"]
    assert "/api/health" in schema["paths"]


def test_configuration_loading():
    """
    Verify Settings configuration loads correctly without exposing secrets.
    """
    assert settings.APP_NAME == "SENTRA"
    assert settings.ENVIRONMENT in ["development", "testing", "production"]
    assert isinstance(settings.cors_origins_list, list)
    assert len(settings.cors_origins_list) > 0


def test_no_secrets_exposed_in_public_endpoints():
    """
    Security check: Ensure secret keys, database credentials, or passwords
    are never returned by root or health endpoints.
    """
    root_data = client.get("/").json()
    health_data = client.get("/health").json()
    api_health_data = client.get("/api/health").json()

    for data in [root_data, health_data, api_health_data]:
        payload_str = str(data)
        assert settings.SECRET_KEY not in payload_str
        assert settings.DATABASE_URL not in payload_str
        assert "password" not in payload_str.lower()
