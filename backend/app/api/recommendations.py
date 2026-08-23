from fastapi import APIRouter, status
from backend.app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from backend.app.services.recommendation_service import recommendation_service
from backend.app.utils.validators import validate_query_text
from backend.app.core.logging import logger

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse, summary="Get AI-powered product recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Search and recommend products using natural language requirements, deterministic budget filtering, and FAISS.
    """
    clean_query = validate_query_text(request.query)
    logger.info(f"POST /api/recommendations for query: '{clean_query}'")

    items, explanation = await recommendation_service.recommend(
        query=clean_query,
        category=request.category,
        max_price=request.max_price,
        top_k=request.top_k or 4
    )

    return RecommendationResponse(
        status="success",
        query=clean_query,
        message=explanation,
        products=items,
        total_found=len(items)
    )
