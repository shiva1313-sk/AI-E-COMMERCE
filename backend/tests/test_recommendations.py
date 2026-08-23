import pytest
from backend.app.services.recommendation_service import recommendation_service
from backend.app.utils.text_processing import extract_budget, extract_category


def test_budget_extraction():
    """Verify various natural language budget formats."""
    assert extract_budget("Suggest running shoes under 3000") == 3000
    assert extract_budget("I need a phone under ₹20,000 with a good camera") == 20000
    assert extract_budget("show me laptops below 50k") == 50000
    assert extract_budget("budget of 1500 rs") == 1500
    assert extract_budget("products for office") is None


def test_category_extraction():
    """Verify natural language category extraction."""
    assert extract_category("Suggest running shoes under 3000") == "Running Shoes"
    assert extract_category("I need a phone under 20000") == "Smartphones"
    assert extract_category("good mechanical keyboard for coding") == "Keyboards"
    assert extract_category("desk accessories for college student") == "College Accessories"


@pytest.mark.asyncio
async def test_recommendation_under_budget():
    """Verify recommendation pipeline enforces budget constraint."""
    items, message = await recommendation_service.recommend(
        query="Suggest running shoes under 3000",
        top_k=4
    )
    assert len(items) > 0
    for item in items:
        assert item.price <= 3000
        assert item.category == "Running Shoes"
        assert item.product_id.startswith("PROD-")
        assert len(item.reason) > 0


@pytest.mark.asyncio
async def test_unmatched_budget_recommendation():
    """Verify behavior when budget is impossibly low."""
    items, message = await recommendation_service.recommend(
        query="Suggest a flagship laptop under 500 rupees",
        top_k=4
    )
    assert len(items) == 0
    assert "no products found" in message.lower() or "couldn't find any products" in message.lower()
