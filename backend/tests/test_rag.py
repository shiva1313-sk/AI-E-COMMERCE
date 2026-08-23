import pytest
from backend.app.services.rag_service import rag_service
from backend.app.services.vector_store_service import vector_store_service


@pytest.fixture(autouse=True)
def ensure_indices():
    """Ensure vector store indices are loaded."""
    vector_store_service.load_all_indices()


@pytest.mark.asyncio
async def test_return_policy_rag_query():
    """Verify return policy query retrieves grounded response and sources."""
    answer, sources, is_grounded = await rag_service.query_knowledge_base(
        query="Can I return a product after 7 days?",
        top_k=3
    )
    assert is_grounded is True
    assert len(sources) > 0
    assert any("return" in s.title.lower() or "refund" in s.title.lower() for s in sources)
    # Check that return window is mentioned
    assert "7" in answer or "return" in answer.lower()


@pytest.mark.asyncio
async def test_warranty_policy_rag_query():
    """Verify warranty inquiry retrieval."""
    answer, sources, is_grounded = await rag_service.query_knowledge_base(
        query="How long is the product warranty?",
        top_k=2
    )
    assert is_grounded is True
    assert len(sources) > 0
    assert any("warranty" in s.title.lower() for s in sources)


@pytest.mark.asyncio
async def test_out_of_domain_query_fallback():
    """Verify unanswerable/out-of-domain queries return safe fallback without hallucination."""
    answer, sources, is_grounded = await rag_service.query_knowledge_base(
        query="How do I book a private submarine tour in Antarctica?",
        top_k=2
    )
    assert is_grounded is False
    assert len(sources) == 0
    assert "don't have enough information" in answer.lower()
