"""
Tests for booking functionality.
Tests: ticket booking, luggage creation, booking validation.
"""
import pytest
from httpx import AsyncClient


class TestTicketBooking:
    """Tests for ticket booking flow."""
    
    @pytest.mark.asyncio
    async def test_book_ticket_unauthorized(self, client: AsyncClient):
        """Test booking without auth token returns 401."""
        response = await client.post(
            "/api/tickets/book",
            json={"ticket_id": 1}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_book_nonexistent_ticket(self, client: AsyncClient):
        """Test booking non-existent ticket returns 404."""
        # Create user and get token
        signup_response = await client.post(
            "/api/auth/signup",
            json={
                "username": "booker",
                "password": "TestPass123!",
                "email": "booker@example.com",
                "role": "user"
            }
        )
        token = signup_response.json()["access_token"]
        
        # Try to book non-existent ticket
        response = await client.post(
            "/api/tickets/book",
            json={"ticket_id": 99999},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestTicketSearch:
    """Tests for ticket search endpoint."""
    
    @pytest.mark.asyncio
    async def test_search_tickets_demo_mode(self, client: AsyncClient):
        """Test ticket fetch returns data (demo mode or cached)."""
        response = await client.post(
            "/api/tickets/fetch",
            json={
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": "2024-12-20"
            }
        )
        
        # Should return 200 with success message
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_all_tickets(self, client: AsyncClient):
        """Test getting all tickets endpoint."""
        response = await client.get("/api/tickets")
        
        # Should return 200 with list
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestUserTickets:
    """Tests for user's tickets."""
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_unauthorized(self, client: AsyncClient):
        """Test getting tickets without auth returns 401."""
        response = await client.get("/api/my-tickets")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_empty(self, client: AsyncClient):
        """Test getting tickets for user with no bookings."""
        # Create user
        signup_response = await client.post(
            "/api/auth/signup",
            json={
                "username": "newuser",
                "password": "TestPass123!",
                "email": "newuser@example.com",
                "role": "user"
            }
        )
        token = signup_response.json()["access_token"]
        
        # Get user's tickets
        response = await client.get(
            "/api/my-tickets",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should return empty tickets list
        assert "tickets" in data
        assert isinstance(data["tickets"], list)

