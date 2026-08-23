from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.models.recommendation import RecommendationItem


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message/query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation session ID")
    orders: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="User orders from session for grounded order lookups")


class SourceDocument(BaseModel):
    source_type: str = Field(..., description="product, policy, or order")
    title: str = Field(..., description="Source title or document name")
    score: Optional[float] = Field(None, description="Similarity score")
    snippet: Optional[str] = Field(None, description="Relevant text snippet")


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    intent: str = Field(..., description="Classified intent (e.g. PRODUCT_SEARCH, CUSTOMER_SUPPORT, ORDER_STATUS, etc.)")
    products: List[RecommendationItem] = Field(default_factory=list)
    sources: List[SourceDocument] = Field(default_factory=list)


class KnowledgeQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    top_k: Optional[int] = Field(3, ge=1, le=8)


class KnowledgeQueryResponse(BaseModel):
    status: str = "success"
    query: str
    answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    is_grounded: bool = True
