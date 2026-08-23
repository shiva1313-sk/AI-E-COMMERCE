from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str = Field(..., description="Unique product identifier (e.g. PROD-SP01)")
    name: str = Field(..., description="Full commercial product name")
    category: str = Field(..., description="Product category")
    brand: str = Field(..., description="Brand name")
    description: str = Field(..., description="Detailed product description")
    price: int = Field(..., ge=0, description="Selling price in INR")
    mrp: int = Field(..., ge=0, description="Maximum retail price in INR")
    features: List[str] = Field(default_factory=list, description="Key features and highlights")
    specifications: Dict[str, str] = Field(default_factory=dict, description="Technical specifications map")
    stock_status: str = Field("in_stock", description="Stock status: in_stock, low_stock, out_of_stock")
    rating: float = Field(4.2, ge=1.0, le=5.0, description="Customer rating out of 5.0")
    rating_count: int = Field(150, ge=0, description="Number of customer ratings")
    delivery_time: str = Field("Free delivery by Tomorrow", description="Estimated delivery promise")
    badge: Optional[str] = Field(None, description="Product badge e.g. Bestseller, Top Rated")
    image_url: Optional[str] = Field(None, description="High quality product image URL")

    def to_searchable_text(self) -> str:
        """Convert product attributes into rich semantic text for dense embeddings."""
        features_str = " | ".join(self.features)
        specs_str = " | ".join([f"{k}: {v}" for k, v in self.specifications.items()])
        badge_str = f"Badge: {self.badge}\n" if self.badge else ""
        return (
            f"Product Name: {self.name}\n"
            f"Category: {self.category}\n"
            f"Brand: {self.brand}\n"
            f"Price: ₹{self.price} (MRP: ₹{self.mrp})\n"
            f"Rating: {self.rating} stars ({self.rating_count} reviews)\n"
            f"{badge_str}"
            f"Description: {self.description}\n"
            f"Key Features: {features_str}\n"
            f"Specifications: {specs_str}\n"
            f"Availability: {self.stock_status}"
        )
