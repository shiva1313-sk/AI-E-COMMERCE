from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ChatMessageRecord(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recommended_product_ids: Optional[List[str]] = None


class ConversationSession(BaseModel):
    conversation_id: str
    messages: List[ChatMessageRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    last_recommended_product_ids: List[str] = Field(default_factory=list)
