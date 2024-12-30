import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .app.routes.flight_routes import router as flight_router
from .app.routes.services_routes import router as service_router
from .app.auth.auth_routes import router as auth_router


# Initialize FastAPI app
app = FastAPI()

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

@app.get("/")
def read_root():
    return {"message": "Welcome to FlyEase!"}
