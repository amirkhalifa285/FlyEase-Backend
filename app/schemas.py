"""
Pydantic schemas for request/response validation.
Provides type safety and automatic documentation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ===================
# Auth Schemas
# ===================

class SignupRequest(BaseModel):
    """Request schema for user signup."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr
    role: str = Field(default="user", pattern="^(user|admin)$")


class LoginRequest(BaseModel):
    """Request schema for user login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    role: str


class UserResponse(BaseModel):
    """Response schema for user details."""
    id: int
    username: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


# ===================
# Flight Schemas
# ===================

class FlightBase(BaseModel):
    """Base flight schema with common fields."""
    airline_name: str
    flight_number: str
    origin: str = Field(..., min_length=2, max_length=10)
    destination: str = Field(..., min_length=2, max_length=10)
    departure_time: datetime
    arrival_time: datetime


class FlightCreate(FlightBase):
    """Schema for creating a new flight."""
    status: str = Field(default="Scheduled")


class FlightUpdate(BaseModel):
    """Schema for updating a flight (all fields optional)."""
    airline_name: Optional[str] = None
    flight_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    status: Optional[str] = None


class FlightResponse(FlightBase):
    """Response schema for flight details."""
    id: int
    status: str
    
    class Config:
        from_attributes = True


# ===================
# Ticket Schemas
# ===================

class TicketSearchParams(BaseModel):
    """Query parameters for ticket search."""
    origin: str = Field(..., min_length=2, max_length=10)
    destination: str = Field(..., min_length=2, max_length=10)
    departure_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class TicketResponse(BaseModel):
    """Response schema for ticket details."""
    id: int
    airline_name: str
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    luggage_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class BookTicketRequest(BaseModel):
    """Request schema for booking a ticket."""
    ticket_id: int


class BookingResponse(BaseModel):
    """Response schema for successful booking."""
    message: str
    flight_number: str
    luggage_id: int


# ===================
# Hotel Schemas
# ===================

class HotelSearchParams(BaseModel):
    """Query parameters for hotel search."""
    location: str = Field(..., min_length=2)
    radius: int = Field(default=5000, ge=100, le=50000)


class HotelResponse(BaseModel):
    """Response schema for hotel details."""
    id: Optional[int] = None
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    place_id: str
    photo_url: str
    open_now: Optional[bool] = None


# ===================
# Map Schemas
# ===================

class Coordinates(BaseModel):
    """Schema for x,y coordinates."""
    x: float
    y: float


class LocationCreate(BaseModel):
    """Request schema for creating a location."""
    name: str = Field(..., min_length=1, max_length=100)
    type: str
    category: Optional[str] = None
    description: Optional[str] = None
    coordinates: Coordinates


class LocationResponse(BaseModel):
    """Response schema for location details."""
    id: int
    name: str
    type: str
    category: Optional[str]
    description: Optional[str]
    coordinates: dict
    
    class Config:
        from_attributes = True


class PathCreate(BaseModel):
    """Request schema for creating a path."""
    source_id: int
    destination_id: int
    distance: float = Field(..., gt=0)
    congestion: int = Field(default=1, ge=1, le=10)


class PathResponse(BaseModel):
    """Response schema for path details."""
    id: int
    source_id: int
    destination_id: int
    distance: float
    congestion: int
    
    class Config:
        from_attributes = True


class NavigationRequest(BaseModel):
    """Request schema for navigation."""
    source_id: int
    destination_id: int


class NavigationResponse(BaseModel):
    """Response schema for navigation result."""
    path: List[int]
    total_distance: float


class WallResponse(BaseModel):
    """Response schema for wall/obstacle."""
    id: int
    x1: float
    y1: float
    x2: float
    y2: float
    
    class Config:
        from_attributes = True


class MapDataResponse(BaseModel):
    """Response schema for complete map data."""
    locations: List[LocationResponse]
    paths: List[PathResponse]
    walls: List[WallResponse]


# ===================
# Error Schemas
# ===================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
