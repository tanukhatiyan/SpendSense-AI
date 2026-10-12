from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import process_ai_chat
from app.api.deps import get_optional_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI Spending Assistant"])

@router.post("/chat", response_model=AIChatResponse)
async def chat_with_assistant(
    request: AIChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Ask questions to the AI spending assistant grounded in verified user financial data."""
    user_id = current_user.id if current_user else None
    response = await process_ai_chat(db=db, request=request, user_id=user_id)
    return response
