import re
from typing import List, Optional, Tuple
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.models.product import Product
from backend.app.models.recommendation import RecommendationItem, RecommendationResult
from backend.app.services.product_service import product_service
from backend.app.services.query_parser import query_parser
from backend.app.services.ollama_service import ollama_service
from backend.app.prompts.recommendation_prompt import build_recommendation_prompt
from backend.app.prompts.system_prompt import SYSTEM_PROMPT


class RecommendationService:
    """Hybrid recommendation service combining query parsing, deterministic constraints, semantic ranking, and grounded generation."""

    async def recommend(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[int] = None,
        min_price: Optional[int] = None,
        conversation_history: str = "",
        previous_product_ids: Optional[List[str]] = None,
        top_k: int = 4
    ) -> Tuple[List[RecommendationItem], str]:
        """
        Execute grounded recommendation pipeline:
        1. Extract constraints and perform hybrid search.
        2. If 0 matching products, return 'No products found matching your requirements.'
        3. Formulate short grounded reasons and 1-3 sentence summary message.
        """
        logger.info(f"Processing recommendation for query: '{query}'")

        # 1. Check for follow-up query referencing previous products
        is_comparison_or_followup = any(
            phrase in query.lower()
            for phrase in ["which one", "compare", "the first", "the second", "cheaper", "better", "between these"]
        )

        candidate_products: List[Product] = []

        if is_comparison_or_followup and previous_product_ids:
            logger.info(f"Follow-up query referencing previous products: {previous_product_ids}")
            candidate_products = [
                product_service.get_by_id_safe(pid)
                for pid in previous_product_ids
                if product_service.get_by_id_safe(pid) is not None
            ]

        # 2. Execute hybrid search
        if not candidate_products:
            candidate_products = product_service.hybrid_search(
                query=query,
                category=category,
                max_price=max_price,
                min_price=min_price,
                top_k=top_k
            )

        # 3. Handle No Products Found
        if not candidate_products:
            return [], "No products found matching your requirements."

        # 4. Generate grounded reasons for each product
        parsed = query_parser.parse(query)
        items: List[RecommendationItem] = []

        for p in candidate_products:
            reason = self._build_grounded_reason(p, parsed)
            items.append(
                RecommendationItem(
                    product_id=p.product_id,
                    name=p.name,
                    price=p.price,
                    brand=p.brand,
                    category=p.category,
                    features=p.features[:3],
                    reason=reason,
                    stock_status=p.stock_status,
                    product_details=p
                )
            )

        # 5. Generate concise 1-3 sentence intro message
        ai_message = ""
        candidate_text_chunks = []
        for p in candidate_products:
            chunk = (
                f"- {p.name} (ID: {p.product_id}) | ₹{p.price:,}\n"
                f"  Features: {', '.join(p.features[:2])}\n"
                f"  Availability: {p.stock_status}"
            )
            candidate_text_chunks.append(chunk)

        prompt = build_recommendation_prompt(
            query=query,
            candidate_products_text="\n".join(candidate_text_chunks),
            conversation_history=conversation_history
        )

        try:
            raw_msg = await ollama_service.generate(
                prompt=prompt,
                system=SYSTEM_PROMPT,
                temperature=0.2
            )
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_msg.strip()) if s.strip()]
            ai_message = " ".join(sentences[:3]) if len(sentences) > 3 else raw_msg.strip()
        except Exception:
            # Deterministic concise fallback
            if len(candidate_products) == 1:
                ai_message = f"I recommend the {candidate_products[0].name} (₹{candidate_products[0].price:,}), which best matches your criteria."
            else:
                top_names = ", ".join([f"{p.name} (₹{p.price:,})" for p in candidate_products[:2]])
                ai_message = f"Based on your requirements, here are our top recommendations: {top_names}."

        return items, ai_message

    def _build_grounded_reason(self, product: Product, parsed) -> str:
        """Construct a factual, grounded explanation of why this product fits the query."""
        reasons = []

        if parsed.max_price and product.price <= parsed.max_price:
            reasons.append(f"Fits within your ₹{parsed.max_price:,} budget at ₹{product.price:,}.")
        elif parsed.min_price and product.price >= parsed.min_price:
            reasons.append(f"Priced at ₹{product.price:,}.")

        # Check matched features
        matched_features = []
        p_text = f"{product.name} {product.description} {' '.join(product.features)} {' '.join(product.specifications.values())}".lower()
        for f in parsed.features:
            if re.search(r'\b' + re.escape(f) + r'\b', p_text):
                matched_features.append(f)

        if matched_features:
            reasons.append(f"Offers {', '.join(matched_features[:2])}.")
        elif product.features:
            reasons.append(f"Features {product.features[0]}.")

        if product.badge:
            reasons.append(f"Marked as {product.badge}.")

        return " ".join(reasons) if reasons else product.description[:120]


recommendation_service = RecommendationService()
