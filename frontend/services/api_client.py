"""HTTP client for the FastAPI traffic-ingestion API."""

from __future__ import annotations

from typing import Any

import requests


class ApiError(RuntimeError):
    """An API or network request failed with a user-safe message."""


class TrafficApiClient:
    """Small, stateless client that keeps authentication in the caller."""

    def __init__(self, base_url: str, token: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = dict(kwargs.pop("headers", {}))
        headers.update(self.headers)
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(
                "Unable to reach the FastAPI backend. Confirm it is running and try again."
            ) from exc

        if response.ok:
            if not response.content:
                return None
            return response.json()

        try:
            detail = response.json().get("detail", response.reason)
        except ValueError:
            detail = response.reason
        raise ApiError(f"Request failed ({response.status_code}): {detail}")

    def _request_bytes(self, method: str, path: str, **kwargs: Any) -> tuple[bytes, str]:
        headers = dict(kwargs.pop("headers", {}))
        headers.update(self.headers)
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(
                "Unable to reach the FastAPI backend. Confirm it is running and try again."
            ) from exc
        if not response.ok:
            try:
                detail = response.json().get("detail", response.reason)
            except ValueError:
                detail = response.reason
            raise ApiError(f"Request failed ({response.status_code}): {detail}")
        return response.content, response.headers.get("content-type", "application/octet-stream")

    def list_readings(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._request("GET", "/api/v1/traffic-readings", params=params)

    def create_reading(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/traffic-readings", json=payload)

    def upload_readings(self, file_name: str, content: bytes) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/traffic-readings/upload",
            files={"file": (file_name, content, "text/csv")},
        )

    def list_imports(self, page: int, page_size: int = 25) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/traffic-imports",
            params={"page": page, "page_size": page_size},
        )

    def get_import(self, import_id: int) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/traffic-imports/{import_id}")

    def analytics(self, resource: str, params: dict[str, Any]) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/analytics/{resource}", params=params)

    def export_analytics(self, params: dict[str, Any]) -> tuple[bytes, str]:
        return self._request_bytes("GET", "/api/v1/analytics/export", params=params)
