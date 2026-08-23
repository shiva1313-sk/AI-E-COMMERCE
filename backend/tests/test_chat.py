import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.vector_store_service import vector_store_service


@pytest.fixture(autouse=True)
def setup_app():
    vector_store_service.load_all_indices()


@pytest.mark.asyncio
async def test_chat_product_recommendation():
    """Test POST /api/chat with product recommendation query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "Suggest running shoes under 3000"
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["intent"] in ["PRODUCT_SEARCH", "product_recommendation"]
        assert len(data["products"]) > 0
        for p in data["products"]:
            assert p["price"] <= 3000


@pytest.mark.asyncio
async def test_chat_customer_support_query():
    """Test POST /api/chat with support policy query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "What is your refund policy for UPI payments?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] in ["CUSTOMER_SUPPORT", "customer_support"]
        assert len(data["message"]) > 0


@pytest.mark.asyncio
async def test_chat_empty_query_error():
    """Test POST /api/chat with empty message."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={
            "message": "   "
        })
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test GET /api/health."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "products_indexed" in data
