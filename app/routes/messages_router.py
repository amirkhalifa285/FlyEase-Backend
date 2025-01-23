from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.auth_utils import get_current_user
from app.models.messages import Message
from app.models.users import User
from ..db.database import get_db

router = APIRouter()



@router.get("/messages", tags=["Messages"])
async def get_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all messages for the logged-in user.
    """
    result = await db.execute(select(Message).filter(Message.user_id == current_user.id))
    messages = result.scalars().all()
    return {"messages": [{"id": m.id, "content": m.content, "status": m.status, "created_at": m.created_at} for m in messages]}


@router.put("/messages/{message_id}", tags=["Messages"])
async def mark_message_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a message as read.
    """
    result = await db.execute(select(Message).filter(Message.id == message_id, Message.user_id == current_user.id))
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.status = "read"
    await db.commit()
    return {"message": "Message marked as read"}
