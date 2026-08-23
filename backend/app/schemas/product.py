from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.models.product import Product


class ProductResponse(BaseModel):
    status: str = "success"
    data: Product


class ProductListResponse(BaseModel):
    status: str = "success"
    total: int
    categories: List[str]
    brands: List[str]
    data: List[Product]


class ProductFilterQuery(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    stock_status: Optional[str] = None
    search: Optional[str] = None
