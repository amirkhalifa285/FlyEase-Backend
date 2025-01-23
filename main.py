import sys
import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes.flight_routes import router as flight_router
from app.auth.auth_routes import router as auth_router
from app.routes.map_routes import router as map_router
from app.routes.tickets_router import router as ticket_router
from app.routes.hotel_router import router as hotel_router
from app.routes.user_routes import router as user_router
from app.routes.messages_router import router as messages_router
from app.db.database import create_tables
from dotenv import load_dotenv
from app.routes.admin_flight_router import router as admin_flight_router
from app.websocket.notifications import websocket_endpoint


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
    allow_origins=["http://localhost:3000"],  # Allow only your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

load_dotenv()  # Load variables from .env into the environment
print("Client ID:", os.getenv("AMADEUS_CLIENT_ID"))
print("Client Secret:", os.getenv("AMADEUS_CLIENT_SECRET"))

# Include routes
app.include_router(auth_router, prefix="/api/auth")  
app.include_router(flight_router, prefix="/api")  
# app.include_router(service_router, prefix="/api")  # Include service routes
app.include_router(map_router, prefix="/api")
app.include_router(ticket_router, prefix="/api")
app.include_router(hotel_router, prefix="/api")     
#app.include_router(car_router, prefix="/api")       
app.include_router(admin_flight_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

@app.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    await websocket_endpoint(websocket)

@app.get("/")
def read_root():
    return {"message": "Welcome to FlyEase!"}