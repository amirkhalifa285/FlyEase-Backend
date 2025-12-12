"""
Tests for map navigation endpoints.
Tests: get map data, calculate shortest path.
"""
import pytest
from httpx import AsyncClient


class TestMapEndpoints:
    """Tests for map data endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_map_data(self, client: AsyncClient):
        """Test getting map data returns proper structure."""
        response = await client.get("/api/map")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have locations, paths, and walls arrays
        assert "locations" in data
        assert "paths" in data
        assert "walls" in data
        assert isinstance(data["locations"], list)
        assert isinstance(data["paths"], list)
        assert isinstance(data["walls"], list)


class TestMapNavigation:
    """Tests for navigation/pathfinding."""
    
    @pytest.mark.asyncio
    async def test_navigate_with_no_data(self, client: AsyncClient):
        """Test navigation with empty database returns error or empty path."""
        response = await client.post(
            "/api/map/navigate",
            json={
                "source_id": 1,
                "destination_id": 2
            }
        )
        
        # Should return 200 with error message when no path exists
        assert response.status_code == 200
        data = response.json()
        # Either returns error or empty path
        assert "error" in data or "path" in data
    
    @pytest.mark.asyncio
    async def test_navigate_request_validation(self, client: AsyncClient):
        """Test navigation requires source_id and destination_id."""
        response = await client.post(
            "/api/map/navigate",
            json={}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_congestion(self, client: AsyncClient):
        """Test congestion update endpoint."""
        response = await client.post("/api/map/update-congestion")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return congestion level info
        assert "level" in data or "paths" in data
