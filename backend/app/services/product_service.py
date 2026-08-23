import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import ProductNotFoundException
from backend.app.models.product import Product
from backend.app.services.query_parser import query_parser


class ProductService:
    """Source of truth for e-commerce products loaded from products.json with hybrid search capability."""

    def __init__(self):
        self.products: List[Product] = []
        self.products_by_id: Dict[str, Product] = {}
        self.categories: List[str] = []
        self.brands: List[str] = []
        self._load_products()

    def _load_products(self):
        """Load and parse products.json."""
        file_path = settings.get_absolute_path(settings.PRODUCT_DATA_PATH)
        if not file_path.exists():
            logger.error(f"Product data file not found at {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self.products = [Product(**item) for item in raw_data]
            self.products_by_id = {p.product_id: p for p in self.products}
            self.categories = sorted(list(set(p.category for p in self.products)))
            self.brands = sorted(list(set(p.brand for p in self.products)))

            logger.info(f"Successfully loaded {len(self.products)} products across {len(self.categories)} categories from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load product dataset from {file_path}: {e}")
            raise

    def get_all(self) -> List[Product]:
        """Return all products in catalog."""
        return self.products

    def get_by_id(self, product_id: str) -> Product:
        """Get product by its unique product_id or raise ProductNotFoundException."""
        prod = self.products_by_id.get(product_id.strip().upper()) or self.products_by_id.get(product_id.strip())
        if not prod:
            raise ProductNotFoundException(product_id)
        return prod

    def get_by_id_safe(self, product_id: str) -> Optional[Product]:
        """Get product by ID without raising exception."""
        if not product_id:
            return None
        clean_id = product_id.strip()
        return self.products_by_id.get(clean_id.upper()) or self.products_by_id.get(clean_id)

    def find_by_name_or_query(self, query: str) -> Optional[Product]:
        """Find a specific product by product ID or exact/partial product name."""
        clean = query.strip()
        
        # Check direct product_id
        id_match = re.search(r'\b(PROD-[A-Z0-9]+)\b', clean, re.IGNORECASE)
        if id_match:
            pid = id_match.group(1).upper()
            if pid in self.products_by_id:
                return self.products_by_id[pid]

        q_lower = clean.lower()
        # Direct name substring match
        for p in self.products:
            if p.name.lower() in q_lower or q_lower in p.name.lower():
                return p

        # Check token overlap
        q_tokens = set(re.findall(r'\w+', q_lower))
        best_p = None
        best_overlap = 0
        for p in self.products:
            name_tokens = set(re.findall(r'\w+', p.name.lower()))
            overlap = len(q_tokens.intersection(name_tokens))
            if overlap > best_overlap and overlap >= 2:
                best_overlap = overlap
                best_p = p

        return best_p

    def filter_products(
        self,
        category: Optional[str] = None,
        max_price: Optional[int] = None,
        min_price: Optional[int] = None,
        brand: Optional[str] = None,
        in_stock_only: bool = False,
        search_query: Optional[str] = None
    ) -> List[Product]:
        """
        Apply deterministic filtering rules to products.json dataset.
        """
        results = self.products

        if category:
            cat_lower = category.lower()
            results = [p for p in results if p.category.lower() == cat_lower]

        if max_price is not None:
            results = [p for p in results if p.price <= max_price]

        if min_price is not None:
            results = [p for p in results if p.price >= min_price]

        if brand:
            brand_lower = brand.lower()
            results = [p for p in results if p.brand.lower() == brand_lower]

        if in_stock_only:
            results = [p for p in results if p.stock_status == "in_stock"]

        if search_query:
            q_lower = search_query.lower()
            results = [
                p for p in results
                if q_lower in p.name.lower()
                or q_lower in p.description.lower()
                or any(q_lower in f.lower() for f in p.features)
            ]

        return results

    def hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[int] = None,
        min_price: Optional[int] = None,
        brand: Optional[str] = None,
        in_stock_only: bool = False,
        top_k: Optional[int] = None
    ) -> List[Product]:
        """
        Execute Hybrid Search & Filtering:
        1. Parse natural-language query to extract structured constraints (budget, category, color, brand, features).
        2. Apply deterministic constraints strictly against catalog dataset.
        3. Compute semantic relevance with FAISS dense vector embeddings and keyword signals.
        4. Rank only products satisfying mandatory constraints.
        5. Return ranked Product list (compatible with product cards & UI).
        """
        parsed = query_parser.parse(query)

        target_category = category or parsed.category
        target_max_price = max_price if max_price is not None else parsed.max_price
        target_min_price = min_price if min_price is not None else parsed.min_price
        target_brand = brand or parsed.brand
        target_color = parsed.color

        candidates = self.products

        # 1. Deterministic Category Filter
        if target_category:
            cat_lower = target_category.lower()
            candidates = [p for p in candidates if p.category.lower() == cat_lower]

        # 2. Deterministic Price Filters
        if target_max_price is not None:
            candidates = [p for p in candidates if p.price <= target_max_price]

        if target_min_price is not None:
            candidates = [p for p in candidates if p.price >= target_min_price]

        # 3. Deterministic Brand Filter
        if target_brand:
            b_lower = target_brand.lower()
            candidates = [p for p in candidates if p.brand.lower() == b_lower]

        # 4. Deterministic Color Filter
        if target_color:
            color_lower = target_color.lower()
            matching_color = []
            for p in candidates:
                # Check name, description, features, specs
                text_corpus = (
                    f"{p.name} {p.description} {' '.join(p.features)} "
                    f"{' '.join(p.specifications.values())} {p.badge or ''}"
                ).lower()
                if re.search(r'\b' + re.escape(color_lower) + r'\b', text_corpus):
                    matching_color.append(p)
            candidates = matching_color

        # 5. Deterministic Stock Status Filter
        if in_stock_only:
            candidates = [p for p in candidates if p.stock_status == "in_stock"]

        # If strict constraints produced 0 matches, return empty immediately (prevents false matches)
        if not candidates:
            return []

        # 6. Rank Candidates using Hybrid Scoring (Vector Semantic Search + Keyword Overlap + Rating)
        scored_candidates: List[Tuple[Product, float]] = []

        # Try semantic search from FAISS
        semantic_scores: Dict[str, float] = {}
        try:
            from backend.app.services.vector_store_service import vector_store_service
            raw_semantic_query = parsed.semantic_query if parsed.semantic_query else query
            search_results = vector_store_service.search(
                collection="products",
                query=raw_semantic_query,
                top_k=len(self.products),
                min_score=0.0
            )
            for meta, score in search_results:
                pid = meta.get("product_id")
                if pid:
                    semantic_scores[pid] = max(0.0, float(score))
        except Exception as e:
            logger.warning(f"Vector search ranking fallback: {e}")

        # Compute keyword relevance signals
        query_words = set(re.findall(r'\w+', query.lower()))
        # Filter out common stop words from keyword scoring
        stop_words = {"the", "a", "an", "for", "with", "and", "or", "in", "under", "below", "to", "of", "is", "at", "show", "me", "suggest", "find"}
        meaningful_words = [w for w in query_words if w not in stop_words and len(w) > 1]

        for p in candidates:
            sem_score = semantic_scores.get(p.product_id, 0.5)

            # Keyword match bonus across name, description, and features
            name_lower = p.name.lower()
            desc_lower = p.description.lower()
            feat_lower = " ".join(p.features).lower()
            specs_lower = " ".join([f"{k} {v}" for k, v in p.specifications.items()]).lower()

            kw_score = 0.0
            for w in meaningful_words:
                if re.search(r'\b' + re.escape(w) + r'\b', name_lower):
                    kw_score += 0.4
                elif re.search(r'\b' + re.escape(w) + r'\b', feat_lower):
                    kw_score += 0.25
                elif re.search(r'\b' + re.escape(w) + r'\b', desc_lower):
                    kw_score += 0.15
                elif re.search(r'\b' + re.escape(w) + r'\b', specs_lower):
                    kw_score += 0.15

            # Normalize rating (e.g. 4.5/5.0 -> 0.9)
            rating_norm = (p.rating / 5.0) if p.rating else 0.8

            # Combine scores
            total_score = (sem_score * 0.55) + (min(kw_score, 1.0) * 0.35) + (rating_norm * 0.10)
            scored_candidates.append((p, total_score))

        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        ranked = [p for p, _ in scored_candidates]

        if top_k is not None and top_k > 0:
            return ranked[:top_k]
        return ranked


product_service = ProductService()
