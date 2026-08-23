import re
from typing import Dict, List, Optional, Tuple
from backend.app.services.query_parser import (
    CANONICAL_CATEGORIES,
    CATEGORY_SYNONYMS,
    KNOWN_BRANDS,
    KNOWN_COLORS,
    query_parser
)

# Intent Constants
INTENT_PRODUCT_SEARCH = "PRODUCT_SEARCH"
INTENT_PRODUCT_DETAILS = "PRODUCT_DETAILS"
INTENT_ORDER_STATUS = "ORDER_STATUS"
INTENT_CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
INTENT_GENERAL_QUERY = "GENERAL_APPLICATION_QUERY"
INTENT_OUT_OF_SCOPE = "OUT_OF_SCOPE"


# Legacy category export
CATEGORIES = CANONICAL_CATEGORIES


def extract_budget(query: str) -> Optional[int]:
    """Extract maximum budget from query using query_parser."""
    parsed = query_parser.parse(query)
    return parsed.max_price


def extract_category(query: str) -> Optional[str]:
    """Extract category from query using query_parser."""
    parsed = query_parser.parse(query)
    return parsed.category


ORDER_PATTERNS = [
    r'\border\s+status\b',
    r'\bwhere\s+is\s+my\s+order\b',
    r'\btrack(?:\s+my)?\s+order\b',
    r'\btrack(?:\s+my)?\s+shipment\b',
    r'\btrack(?:\s+my)?\s+package\b',
    r'\btracking\s+(?:number|id|status)\b',
    r'\bwhen\s+will\s+my\b',
    r'\bmy\s+order\b',
    r'\bmy\s+orders\b',
    r'\border\s+(?:#|id|no|number)?\s*(?:od|ord)?\d+\b',
    r'\bcheck(?:\s+my)?\s+order\b',
    r'\border\s+details\b',
    r'\bstatus\s+of\s+my\s+order\b',
    r'\bstatus\s+of\s+order\b',
    r'\bhas\s+my\s+order\s+been\s+shipped\b',
    r'\bhas\s+my\s+order\s+shipped\b',
    r'\bwhere\s+is\s+my\s+(?:laptop|phone|shoes|headphones|watch|package|item)\b'
]

SUPPORT_KEYWORDS = [
    "return", "refund", "cancel", "cancellation", "delivery", "shipping",
    "courier", "payment", "cod", "upi", "card", "net banking", "emi",
    "warranty", "guarantee", "claim", "contact", "support", "helpline",
    "email support", "faq", "policy", "replacement", "replace", "exchange",
    "defective", "damaged", "tax invoice", "gst", "service center",
    "international delivery", "shipping fee", "delivery charge", "pincode"
]

GREETING_PATTERNS = [
    r'^(?:hi|hello|hey|good\s+morning|good\s+evening|good\s+afternoon|howdy|sup|what\'?s\s+up|namaste)\b',
    r'^(?:who\s+are\s+you|what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+is\s+shopease|help(?:\s+me)?)$'
]

OUT_OF_SCOPE_TRIGGERS = [
    r'\bwho\s+is\s+(?:the\s+)?(?:prime\s+minister|president|ceo|founder|king|queen)\b',
    r'\bwrite\s+(?:a\s+)?(?:poem|story|essay|code|python|java|javascript|script|song|letter)\b',
    r'\bwhat\s+is\s+(?:photosynthesis|quantum|gravity|dna|ai|capital\s+of|weather|meaning\s+of\s+life)\b',
    r'\bwho\s+won\s+the\b',
    r'\btell\s+me\s+a\s+joke\b',
    r'\bhow\s+to\s+(?:cook|bake|hack|code|learn\s+french|fly)\b',
    r'\btranslate\s+',
    r'\bprime\s+minister\b',
    r'\bpresident\s+of\b',
    r'\bcapital\s+of\b',
    r'\bweather\s+in\b',
    r'\bmath\s+problem\b',
    r'\bcalculate\s+\d+'
]

PRODUCT_DETAIL_PATTERNS = [
    r'\b(?:what\s+is\s+the\s+price\s+of|price\s+of|cost\s+of|how\s+much\s+is)\s+([a-zA-Z0-9\s\-]+)',
    r'\b(?:specifications|specs|features|battery|ram|storage|display|camera)\s+of\s+([a-zA-Z0-9\s\-]+)',
    r'\bprod-[a-zA-Z0-9]+\b',
    r'\btell\s+me\s+about\s+(?:the\s+)?(novapixel|camMaster|auramobile|zenbook|probook|edubook|apex\s+predator|cloudstride|audiozen|prod-[a-zA-Z0-9]+)\b'
]


def classify_intent(query: str) -> str:
    """
    Classify user query into 6 standard intents:
    1. ORDER_STATUS
    2. CUSTOMER_SUPPORT
    3. PRODUCT_DETAILS
    4. GENERAL_APPLICATION_QUERY
    5. OUT_OF_SCOPE
    6. PRODUCT_SEARCH
    """
    clean = query.strip()
    lower = clean.lower()

    # 1. Check Out of Scope first
    for oos in OUT_OF_SCOPE_TRIGGERS:
        if re.search(oos, lower):
            return INTENT_OUT_OF_SCOPE

    # 2. Check Order Status
    for op in ORDER_PATTERNS:
        if re.search(op, lower):
            return INTENT_ORDER_STATUS

    # 3. Check General Greeting / Help
    for gp in GREETING_PATTERNS:
        if re.search(gp, lower):
            return INTENT_GENERAL_QUERY

    # 4. Check Product Details
    for pd in PRODUCT_DETAIL_PATTERNS:
        if re.search(pd, lower):
            # Verify if it's asking specific product info rather than a general recommendation search
            if not any(word in lower for word in ["suggest", "recommend", "show me", "best", "under", "below"]):
                return INTENT_PRODUCT_DETAILS

    # 5. Check Customer Support / Policy
    for kw in SUPPORT_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, lower):
            # If user is asking for products WITH a feature like "waterproof" or "fast charging", ensure it's not misclassified
            if any(term in lower for term in ["suggest", "recommend", "show me", "phone", "laptop", "shoes", "headphones", "under", "below", "buy"]):
                # If it has both support keyword (e.g. warranty) and recommendation trigger, decide based on query structure
                if any(w in lower for w in ["return policy", "refund policy", "cancellation", "shipping fee", "tax invoice", "gst", "delivery time", "helpline", "payment methods", "international delivery"]):
                    return INTENT_CUSTOMER_SUPPORT
                return INTENT_PRODUCT_SEARCH
            return INTENT_CUSTOMER_SUPPORT

    # 6. Check Product Search / Recommendation
    parsed = query_parser.parse(clean)
    if parsed.category or parsed.max_price or parsed.min_price or parsed.color or parsed.brand or parsed.features:
        return INTENT_PRODUCT_SEARCH

    search_verbs = [
        "suggest", "recommend", "show", "find", "looking for", "best",
        "cheap", "affordable", "buy", "purchase", "options", "compare",
        "which", "lightweight", "budget", "product", "items", "good"
    ]
    if any(re.search(r'\b' + re.escape(v) + r'\b', lower) for v in search_verbs):
        return INTENT_PRODUCT_SEARCH

    # If it's a short 1-3 word query, e.g. "smartphones", "iPhones", "shoes", "sony"
    words = lower.split()
    if len(words) <= 4:
        return INTENT_PRODUCT_SEARCH

    # If nothing matched and looks unrelated to shopping, categorize as OUT_OF_SCOPE
    # e.g., "tell me how a rocket engine works", "what is the speed of light"
    shopping_context_words = [
        "product", "item", "buy", "shop", "cart", "store", "price", "rupees", "rs", "inr", "discount", "sale",
        "brand", "deal", "delivery", "order", "return", "refund", "warranty", "specs", "feature"
    ]
    if not any(sc in lower for sc in shopping_context_words):
        return INTENT_OUT_OF_SCOPE

    return INTENT_PRODUCT_SEARCH
