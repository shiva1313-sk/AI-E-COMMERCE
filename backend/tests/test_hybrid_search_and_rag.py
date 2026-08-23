import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.product_service import product_service
from backend.app.services.vector_store_service import vector_store_service
from backend.app.services.query_parser import query_parser
from backend.app.utils.text_processing import (
    classify_intent,
    INTENT_PRODUCT_SEARCH,
    INTENT_PRODUCT_DETAILS,
    INTENT_ORDER_STATUS,
    INTENT_CUSTOMER_SUPPORT,
    INTENT_GENERAL_QUERY,
    INTENT_OUT_OF_SCOPE
)


@pytest.fixture(autouse=True)
def setup_services():
    """Ensure all vector indexes are loaded."""
    vector_store_service.load_all_indices()


# ============================================================================
# SEARCH ACCEPTANCE TESTS (Tests 1 to 6)
# ============================================================================

def test_search_test_1_phones_under_30000():
    """Search Test 1: 'phones under 30000' -> Show actual phones with price <= 30000."""
    results = product_service.hybrid_search("phones under 30000")
    assert len(results) > 0, "Expected matching phones under 30000"
    for p in results:
        assert p.category == "Smartphones", f"Expected Smartphone, got {p.category}"
        assert p.price <= 30000, f"Price {p.price} exceeds budget 30000"


def test_search_test_2_phone_under_20000_with_good_camera():
    """Search Test 2: 'phone under 20000 with good camera' -> Show matching phones under 20000 with camera features."""
    results = product_service.hybrid_search("phone under 20000 with good camera")
    assert len(results) > 0, "Expected matching camera phones under 20000"
    for p in results:
        assert p.category == "Smartphones"
        assert p.price <= 20000
    
    # Top result should be a camera-oriented phone (e.g. CamMaster V20 or Aura Lite)
    top_p = results[0]
    p_text = (top_p.name + " " + top_p.description + " " + " ".join(top_p.features)).lower()
    assert "camera" in p_text or "mp" in p_text or "ois" in p_text


def test_search_test_3_running_shoes_under_3000():
    """Search Test 3: 'running shoes under 3000' -> Show matching running shoes under 3000."""
    results = product_service.hybrid_search("running shoes under 3000")
    assert len(results) > 0, "Expected matching running shoes under 3000"
    for p in results:
        assert p.category == "Running Shoes"
        assert p.price <= 3000


def test_search_test_4_black_smartphone():
    """Search Test 4: 'black smartphone' -> Show matching black smartphones only if color exists, no false matches."""
    results = product_service.hybrid_search("black smartphone")
    # In catalog, check if all returned items match 'Smartphones' and contain 'black'
    for p in results:
        assert p.category == "Smartphones"
        text = (p.name + " " + p.description + " " + " ".join(p.features) + " " + " ".join(p.specifications.values())).lower()
        assert "black" in text


def test_search_test_5_laptop_for_college_student():
    """Search Test 5: 'laptop for college student' -> Show semantically relevant student laptops."""
    results = product_service.hybrid_search("laptop for college student")
    assert len(results) > 0, "Expected matching laptops"
    for p in results:
        assert p.category == "Laptops"
    # EduBook 14 Student Essential Laptop should be top ranked
    top_names = [p.name for p in results[:3]]
    assert any("student" in n.lower() or "edubook" in n.lower() or "zenbook" in n.lower() or "probook" in n.lower() for n in top_names)


def test_search_test_6_gaming_laptop_under_10000():
    """Search Test 6: 'gaming laptop under 10000' -> Must return 0 products (no false matches)."""
    results = product_service.hybrid_search("gaming laptop under 10000")
    assert len(results) == 0, f"Expected 0 results for budget 10000 on laptops, got {len(results)}"


# ============================================================================
# AI ASSISTANT ACCEPTANCE TESTS (Tests 1 to 5)
# ============================================================================

@pytest.mark.asyncio
async def test_ai_assistant_test_1_order_status_with_orders():
    """AI Assistant Test 1A: 'What is my order status?' with real order in session."""
    sample_orders = [
        {
            "orderId": "OD1024",
            "date": "2026-08-22T10:00:00Z",
            "items": [
                {
                    "product": {
                        "product_id": "PROD-SP02",
                        "name": "Aura Lite 5G Budget Smartphone",
                        "price": 14499
                    },
                    "quantity": 1
                }
            ],
            "totalAmount": 14499,
            "status": "Shipped",
            "expectedDelivery": "Tomorrow by 8 PM"
        }
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "What is my order status?",
            "orders": sample_orders
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_ORDER_STATUS
        msg = data["message"]
        # Must contain actual order details
        assert "OD1024" in msg or "Aura Lite" in msg
        assert "Shipped" in msg or "Tomorrow" in msg
        assert "My Orders" not in msg or "going to My Orders" not in msg


@pytest.mark.asyncio
async def test_ai_assistant_test_1_order_status_no_orders():
    """AI Assistant Test 1B: 'What is my order status?' without orders in session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "What is my order status?",
            "orders": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_ORDER_STATUS
        assert "couldn't find order information" in data["message"].lower()


@pytest.mark.asyncio
async def test_ai_assistant_test_2_return_policy():
    """AI Assistant Test 2: 'Can I return a product after 7 days?' -> Grounded short answer."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "Can I return a product after 7 days?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_CUSTOMER_SUPPORT
        msg = data["message"]
        assert len(msg) > 0
        # Check return window mentioned
        assert "7" in msg or "return" in msg.lower()


@pytest.mark.asyncio
async def test_ai_assistant_test_3_international_delivery_fallback():
    """AI Assistant Test 3: 'Do you offer international delivery?' -> Strict fallback, no hallucination."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "Do you offer international delivery?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_CUSTOMER_SUPPORT
        # The knowledge base does not offer international delivery information
        # Must return grounded fallback
        assert "don't have enough information" in data["message"].lower()


@pytest.mark.asyncio
async def test_ai_assistant_test_4_out_of_scope():
    """AI Assistant Test 4: 'Who is the Prime Minister of India?' -> Strict refusal."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "Who is the Prime Minister of India?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_OUT_OF_SCOPE
        assert "I can help only with products, orders, and customer support information available in ShopEase." in data["message"]


@pytest.mark.asyncio
async def test_ai_assistant_test_5_recommendation_under_budget():
    """AI Assistant Test 5: 'Suggest a phone under 20000 with good camera' -> Recommends actual products."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "Suggest a phone under 20000 with good camera"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == INTENT_PRODUCT_SEARCH
        assert len(data["products"]) > 0
        for p in data["products"]:
            assert p["price"] <= 20000
            assert p["category"] == "Smartphones"
            assert p["product_id"].startswith("PROD-")
            assert len(p["reason"]) > 0


# ============================================================================
# API PRODUCTS SEARCH ENDPOINT TEST
# ============================================================================

@pytest.mark.asyncio
async def test_api_products_natural_language_search():
    """Verify GET /api/products?search=phone+under+20000."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/products?search=phone under 20000")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0
        for p in data["data"]:
            assert p["category"] == "Smartphones"
            assert p["price"] <= 20000
