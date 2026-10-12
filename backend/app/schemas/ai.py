from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's query to the spending assistant")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Prior conversation messages")

class AIChatResponse(BaseModel):
    reply: str
    context_summary: Optional[str] = None
    provider: str
    status: Literal["success", "fallback", "setup_required"] = "success"
