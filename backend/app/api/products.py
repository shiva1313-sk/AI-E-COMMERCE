from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.product import Product
from backend.app.schemas.product import ProductListResponse, ProductResponse
from backend.app.services.product_service import product_service
from backend.app.core.logging import logger

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse, summary="Get all products with optional filters and hybrid search")
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price filter"),
    stock_status: Optional[str] = Query(None, description="Filter by stock status (in_stock, out_of_stock)"),
    search: Optional[str] = Query(None, description="Natural language search query or keywords")
):
    """
    Retrieve catalog products with hybrid natural language search and deterministic filtering.
    """
    logger.info(f"GET /api/products with category={category}, brand={brand}, max_price={max_price}, search={search}")
    
    in_stock_only = (stock_status == "in_stock") if stock_status else False

    if search and search.strip():
        products = product_service.hybrid_search(
            query=search.strip(),
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only
        )
    else:
        products = product_service.filter_products(
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only
        )

    return ProductListResponse(
        status="success",
        total=len(products),
        categories=product_service.categories,
        brands=product_service.brands,
        data=products
    )


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product details by ID")
async def get_product_by_id(product_id: str):
    """Retrieve a single product by its unique product_id."""
    logger.info(f"GET /api/products/{product_id}")
    product = product_service.get_by_id(product_id)
    return ProductResponse(
        status="success",
        data=product
    )
