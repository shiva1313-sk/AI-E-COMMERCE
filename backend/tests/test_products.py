import pytest
from backend.app.services.product_service import product_service
from backend.app.core.exceptions import ProductNotFoundException


def test_products_loaded_count():
    """Verify that 30-50 products are loaded from dataset."""
    products = product_service.get_all()
    assert len(products) >= 30, f"Expected at least 30 products, found {len(products)}"
    assert len(product_service.categories) >= 8


def test_product_lookup_by_id():
    """Verify valid product lookup."""
    p = product_service.get_by_id("PROD-SP01")
    assert p.product_id == "PROD-SP01"
    assert "NovaPixel" in p.name
    assert p.price > 0
    assert p.category == "Smartphones"


def test_product_lookup_invalid_id():
    """Verify that querying a non-existent product ID raises ProductNotFoundException."""
    with pytest.raises(ProductNotFoundException):
        product_service.get_by_id("NON_EXISTENT_ID_999")


def test_filter_by_price():
    """Verify price filtering constraint."""
    budget = 3000
    filtered = product_service.filter_products(max_price=budget)
    assert len(filtered) > 0
    for p in filtered:
        assert p.price <= budget, f"Product {p.name} price {p.price} exceeds budget {budget}"


def test_filter_by_category():
    """Verify category filtering."""
    shoes = product_service.filter_products(category="Running Shoes")
    assert len(shoes) > 0
    for s in shoes:
        assert s.category == "Running Shoes"


def test_filter_by_category_and_price():
    """Verify compound category + price filtering."""
    budget = 3000
    shoes_under_3k = product_service.filter_products(category="Running Shoes", max_price=budget)
    assert len(shoes_under_3k) > 0
    for s in shoes_under_3k:
        assert s.category == "Running Shoes"
        assert s.price <= budget
