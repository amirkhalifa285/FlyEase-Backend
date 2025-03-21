from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException
from .auth_utils import hash_password, verify_password, create_access_token
from ..models.users import User

async def signup(db, username: str, password: str, role: str, email: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password and create a new user
    hashed_password = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password, role=role, email=email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate JWT token for the new user
    token = create_access_token({"sub": new_user.username, "role": new_user.role})
    
    # Return the user object and token
    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "email": new_user.email,
        "created_at": new_user.created_at,
        "access_token": token,
        "token_type": "bearer"
    }



async def login(db, username: str, password: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    token = create_access_token({"sub": user.username, "role": user.role})
    #print(f"Generated token: {token}")  # Debugging line
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }

