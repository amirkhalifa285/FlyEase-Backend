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
from app.routes.admin_flight_router import router as admin_flight_router
from app.websocket.notifications import websocket_endpoint
from app.core.settings import settings


# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    # Note: Database tables are now managed by Alembic migrations
    yield
    # Shutdown logic (if needed) goes here

# Use the lifespan function directly in FastAPI
app = FastAPI(
    title="FlyEase API",
    description="Airport navigation and flight booking API",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware for CORS - using configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routes
app.include_router(auth_router, prefix="/api/auth")  
app.include_router(flight_router, prefix="/api")  
app.include_router(map_router, prefix="/api")
app.include_router(ticket_router, prefix="/api")
app.include_router(hotel_router, prefix="/api")        
app.include_router(admin_flight_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

@app.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    await websocket_endpoint(websocket)

@app.get("/")
def read_root():
    return {"message": "Welcome to FlyEase!"}