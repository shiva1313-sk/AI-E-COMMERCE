from fastapi import APIRouter, status
from backend.app.schemas.chat import ChatRequest, ChatResponse, SourceDocument
from backend.app.services.conversation_service import conversation_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.rag_service import rag_service
from backend.app.services.order_service import order_service
from backend.app.services.product_service import product_service
from backend.app.models.recommendation import RecommendationItem
from backend.app.utils.text_processing import (
    classify_intent,
    INTENT_PRODUCT_SEARCH,
    INTENT_PRODUCT_DETAILS,
    INTENT_ORDER_STATUS,
    INTENT_CUSTOMER_SUPPORT,
    INTENT_GENERAL_QUERY,
    INTENT_OUT_OF_SCOPE
)
from backend.app.utils.validators import validate_query_text
from backend.app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, summary="Unified conversational AI chat endpoint")
async def chat_endpoint(request: ChatRequest):
    """
    Main conversational endpoint:
    - Maintains multi-turn context with conversation_id
    - Classifies intent (PRODUCT_SEARCH, PRODUCT_DETAILS, ORDER_STATUS, CUSTOMER_SUPPORT, GENERAL_APPLICATION_QUERY, OUT_OF_SCOPE)
    - Routes to strictly grounded pipelines with zero external hallucinations
    - Formats concise 1-3 sentence answers
    """
    clean_message = validate_query_text(request.message)
    session = conversation_service.get_or_create_session(request.conversation_id)
    conversation_id = session.conversation_id

    # Classify intent across 6 categories
    intent = classify_intent(clean_message)
    logger.info(f"POST /api/chat | CID: {conversation_id} | Intent: {intent} | Message: '{clean_message}'")

    # Get conversation context
    history_str = conversation_service.format_history(conversation_id, max_turns=3)
    prev_product_ids = conversation_service.get_last_recommended_products(conversation_id)

    response_message = ""
    recommended_items = []
    sources = []

    if intent == INTENT_OUT_OF_SCOPE:
        response_message = "I can help only with products, orders, and customer support information available in ShopEase."

    elif intent == INTENT_ORDER_STATUS:
        response_message = order_service.resolve_order_query(clean_message, request.orders)
        if request.orders:
            sources.append(
                SourceDocument(
                    source_type="order",
                    title="Active User Orders",
                    snippet=f"Retrieved from {len(request.orders)} order(s) in session."
                )
            )

    elif intent == INTENT_PRODUCT_DETAILS:
        product = product_service.find_by_name_or_query(clean_message)
        if product:
            specs_list = [f"{k}: {v}" for k, v in list(product.specifications.items())[:3]]
            specs_str = f" Specs: {', '.join(specs_list)}." if specs_list else ""
            response_message = (
                f"{product.name} ({product.product_id}) is priced at ₹{product.price:,} (MRP: ₹{product.mrp:,}) "
                f"and is currently {product.stock_status.replace('_', ' ')}.{specs_str}"
            )
            recommended_items = [
                RecommendationItem(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    brand=product.brand,
                    category=product.category,
                    features=product.features[:3],
                    reason=f"Details for {product.name}",
                    stock_status=product.stock_status,
                    product_details=product
                )
            ]
            sources.append(
                SourceDocument(
                    source_type="product",
                    title=f"{product.name} ({product.product_id})",
                    snippet=f"Price: ₹{product.price:,} | Stock: {product.stock_status}"
                )
            )
        else:
            response_message = "I couldn't find a matching product in the catalog for that request."

    elif intent == INTENT_CUSTOMER_SUPPORT:
        answer, sources, is_grounded = await rag_service.query_knowledge_base(
            query=clean_message,
            conversation_history=history_str
        )
        response_message = answer

    elif intent == INTENT_GENERAL_QUERY:
        response_message = (
            "Hello! I am ShopEase AI, your shopping and customer support assistant. "
            "I can help you search products, track orders, or answer questions about store policies."
        )

    else:
        # PRODUCT_SEARCH
        items, explanation = await recommendation_service.recommend(
            query=clean_message,
            conversation_history=history_str,
            previous_product_ids=prev_product_ids
        )
        response_message = explanation
        recommended_items = items

        for item in items:
            sources.append(
                SourceDocument(
                    source_type="product",
                    title=f"{item.name} ({item.product_id})",
                    snippet=f"Price: ₹{item.price:,} | Brand: {item.brand} | Category: {item.category}"
                )
            )

    # Save to conversation memory
    conversation_service.add_message(
        conversation_id=conversation_id,
        role="user",
        content=clean_message
    )
    rec_ids = [item.product_id for item in recommended_items]
    conversation_service.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_message,
        recommended_product_ids=rec_ids if rec_ids else None
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message=response_message,
        intent=intent,
        products=recommended_items,
        sources=sources
    )
