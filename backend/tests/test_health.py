"""
Tests for /health and /ready endpoints.
These are the first thing deployment orchestration checks.
"""
import pytest
from httpx import AsyncClient


class TestHealthEndpoint:

    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_returns_healthy_status(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    async def test_health_returns_version(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] is not None


class TestReadinessEndpoint:

    async def test_ready_returns_200_or_503(self, client: AsyncClient):
        """Readiness may return 200 (DB up) or 503 (DB unavailable in test)."""
        response = await client.get("/ready")
        assert response.status_code in [200, 503]

    async def test_ready_returns_checks_object(self, client: AsyncClient):
        response = await client.get("/ready")
        data = response.json()
        assert "checks" in data
        assert "api" in data["checks"]

    async def test_ready_api_check_is_ok(self, client: AsyncClient):
        response = await client.get("/ready")
        data = response.json()
        assert data["checks"]["api"] == "ok"
