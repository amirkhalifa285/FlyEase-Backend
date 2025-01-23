# user_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.auth_utils import get_current_user
from app.models.users import User
from app.db.database import get_db
from sqlalchemy.future import select
from app.models.messages import Message  

router = APIRouter()

@router.get("/profile", tags=["User"])
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch profile information and messages for the logged-in user.
    """
    # Fetch user messages
    result = await db.execute(
        select(Message).filter(Message.user_id == current_user.id)
    )
    messages = result.scalars().all()

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at
        },
        "messages": [
            {"id": m.id, "content": m.content, "status": m.status} 
            for m in messages
        ]
    }