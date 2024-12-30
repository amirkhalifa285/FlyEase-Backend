from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .auth_controller import signup, login
from ..db.database import get_db
from pydantic import BaseModel

router = APIRouter()

class SignupRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/signup")
async def signup_user(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Await the signup function
    return await signup(db, request.username, request.password, request.role, request.email)

@router.post("/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login(db, request.username, request.password)
