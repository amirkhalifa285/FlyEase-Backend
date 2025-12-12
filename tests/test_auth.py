"""
Tests for authentication endpoints.
Tests: signup, login, token generation, protected routes.
"""
import pytest
from httpx import AsyncClient


class TestAuthSignup:
    """Tests for the signup endpoint."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient):
        """Test successful user signup."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "password": "TestPass123!",
                "email": "test@example.com",
                "role": "user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_username(self, client: AsyncClient):
        """Test signup with duplicate username fails."""
        # First signup
        await client.post(
            "/api/auth/signup",
            json={
                "username": "duplicate",
                "password": "TestPass123!",
                "email": "test1@example.com",
                "role": "user"
            }
        )
        
        # Duplicate signup
        response = await client.post(
            "/api/auth/signup",
            json={
                "username": "duplicate",
                "password": "TestPass123!",
                "email": "test2@example.com",
                "role": "user"
            }
        )
        
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()


class TestAuthLogin:
    """Tests for the login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login returns token."""
        # Create user first
        await client.post(
            "/api/auth/signup",
            json={
                "username": "loginuser",
                "password": "TestPass123!",
                "email": "login@example.com",
                "role": "user"
            }
        )
        
        # Login
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "loginuser",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with wrong password fails."""
        # Create user
        await client.post(
            "/api/auth/signup",
            json={
                "username": "wrongpass",
                "password": "CorrectPass123!",
                "email": "wrong@example.com",
                "role": "user"
            }
        )
        
        # Login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "wrongpass",
                "password": "WrongPass123!"
            }
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()


class TestAdminProtection:
    """Tests for admin route protection."""
    
    @pytest.mark.asyncio
    async def test_admin_route_without_token(self, client: AsyncClient):
        """Test admin route returns 401 without token."""
        response = await client.get("/api/admin/flights")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_admin_route_with_user_token(self, client: AsyncClient):
        """Test admin route returns 403 for non-admin user."""
        # Create regular user
        signup_response = await client.post(
            "/api/auth/signup",
            json={
                "username": "regularuser",
                "password": "TestPass123!",
                "email": "regular@example.com",
                "role": "user"
            }
        )
        token = signup_response.json()["access_token"]
        
        # Try to access admin route
        response = await client.get(
            "/api/admin/flights",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_route_with_admin_token(self, client: AsyncClient):
        """Test admin route works for admin user."""
        # Create admin user
        signup_response = await client.post(
            "/api/auth/signup",
            json={
                "username": "adminuser",
                "password": "AdminPass123!",
                "email": "admin@example.com",
                "role": "admin"
            }
        )
        token = signup_response.json()["access_token"]
        
        # Access admin route
        response = await client.get(
            "/api/admin/flights",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should succeed (200) or return empty list, not 401/403
        assert response.status_code == 200
