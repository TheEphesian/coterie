"""API tests for root and health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(api_client: AsyncClient):
    """Test the root endpoint returns application info."""
    response = await api_client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_check(api_client: AsyncClient):
    """Test the health check endpoint."""
    response = await api_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_api_docs_accessible(api_client: AsyncClient):
    """Test that API documentation is accessible."""
    response = await api_client.get("/docs")
    assert response.status_code == 200
    
    # Check that it contains Swagger UI
    content = response.text
    assert "swagger" in content.lower() or "openapi" in content.lower()
