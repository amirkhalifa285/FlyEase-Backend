import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes.flight_routes import router as flight_router
from app.routes.services_routes import router as service_router
from app.auth.auth_routes import router as auth_router
from app.routes.map_routes import router as map_router
from app.db.database import create_tables


# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await create_tables()
    yield
    # Shutdown logic (if needed) goes here

# Use the lifespan function directly in FastAPI
app = FastAPI(lifespan=lifespan)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/auth")  # Include authentication routes
app.include_router(flight_router, prefix="/api")  # Include flight routes
app.include_router(service_router, prefix="/api")  # Include service routes
app.include_router(map_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to FlyEase!"}
