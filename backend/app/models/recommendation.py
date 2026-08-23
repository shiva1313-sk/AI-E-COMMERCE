from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.models.product import Product


class RecommendationItem(BaseModel):
    product_id: str = Field(..., description="Product ID from dataset")
    name: str = Field(..., description="Product name")
    price: int = Field(..., description="Price in INR")
    brand: Optional[str] = None
    category: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    reason: str = Field(..., description="Personalized grounded reasoning for recommendation")
    stock_status: Optional[str] = "in_stock"
    product_details: Optional[Product] = None


class RecommendationResult(BaseModel):
    query: str
    extracted_category: Optional[str] = None
    extracted_budget: Optional[int] = None
    products: List[RecommendationItem] = Field(default_factory=list)
    explanation: Optional[str] = None
    total_found: int = 0
