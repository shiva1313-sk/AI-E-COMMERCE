from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.models.recommendation import RecommendationItem


class RecommendationRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Natural language search query")
    category: Optional[str] = Field(None, description="Optional category filter")
    max_price: Optional[int] = Field(None, ge=0, description="Optional maximum budget")
    top_k: Optional[int] = Field(4, ge=1, le=10, description="Number of recommendations to return")


class RecommendationResponse(BaseModel):
    status: str = "success"
    query: str
    message: str
    products: List[RecommendationItem] = Field(default_factory=list)
    total_found: int = 0
