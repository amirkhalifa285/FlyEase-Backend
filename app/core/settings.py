"""
FlyEase Settings Configuration

Centralized configuration using Pydantic BaseSettings.
All environment variables are loaded once and validated at startup.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    SSL_REQUIRED: bool = Field(True, description="Require SSL for database connection")
    
    # Security
    SECRET_KEY: str = Field(..., description="JWT signing secret key")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # External API Keys (optional for demo mode)
    FLIGHTS_API_KEY: Optional[str] = Field(None, description="AviationStack API key")
    BOOKING_API_KEY: Optional[str] = Field(None, description="SkyScanner/RapidAPI key")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Google Places API key")
    
    # Feature flags
    DEMO_MODE: bool = Field(False, description="Return stub data when API keys missing")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars
        
    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (explicit or missing keys)."""
        if self.DEMO_MODE:
            return True
        # Auto-enable demo mode if critical API keys are missing
        return not all([self.BOOKING_API_KEY, self.GOOGLE_API_KEY])


# Singleton instance - loaded once at import
try:
    settings = Settings()
except Exception as e:
    # Provide helpful error message for missing required vars
    import sys
    print(f"❌ Configuration Error: {e}")
    print("Required environment variables: DATABASE_URL, SECRET_KEY")
    print("Create a .env file or set environment variables.")
    sys.exit(1)
