import jwt
from jwt import DecodeError, ExpiredSignatureError, exceptions
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User
from ..db.database import get_db
from sqlalchemy.orm import joinedload


# Configuration
SECRET_KEY = "your_secret_key"  # Replace with environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password Hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

# JWT Token Generation
def create_access_token(data: dict):
    """
    Generate a new access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decode JWT
def decode_access_token(token: str):
    """
    Decode and validate the JWT token.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except DecodeError:
        raise ValueError("Token is invalid")
    except exceptions.PyJWTError as e:
        raise ValueError(f"Token decoding error: {str(e)}")
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Decode the JWT, retrieve the user ID, and fetch the user object with tickets eagerly loaded.
    """
    #print(f"Token received: {token}")
    try:
        payload = decode_access_token(token)
        user_id_or_username = payload.get("sub")

        if not user_id_or_username:
            print("Token payload is missing 'sub':", payload)
            raise ValueError("Invalid token payload: 'sub' not found")

        # Determine if sub is an integer (user_id) or string (username)
        if user_id_or_username.isdigit():
            user_id = int(user_id_or_username)
            query = select(User).options(joinedload(User.tickets)).filter(User.id == user_id)
        else:
            query = select(User).options(joinedload(User.tickets)).filter(User.username == user_id_or_username)

        result = await db.execute(query)
        # Use unique() to deduplicate rows caused by joined eager loading
        user = result.unique().scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except ValueError as e:
        print("Error decoding token or fetching user:", str(e))
        raise HTTPException(status_code=401, detail=str(e))


def admin_only(user: User = Depends(get_current_user)):
    """
    Restrict access to admin users only.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
