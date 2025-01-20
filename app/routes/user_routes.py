from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.auth_utils import get_current_user
from app.models.users import User
from app.db.database import get_db

router = APIRouter()

@router.get("/profile", tags=["User"])
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch profile information for the logged-in user.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "preferences": current_user.preferences,
        "created_at": current_user.created_at
    }
