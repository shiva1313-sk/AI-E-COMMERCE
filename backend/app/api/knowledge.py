from fastapi import APIRouter, status
from backend.app.schemas.chat import KnowledgeQueryRequest, KnowledgeQueryResponse
from backend.app.services.rag_service import rag_service
from backend.app.utils.validators import validate_query_text
from backend.app.core.logging import logger

router = APIRouter(prefix="", tags=["Knowledge & Support"])


@router.post("/knowledge/query", response_model=KnowledgeQueryResponse, summary="Query customer support policies via RAG")
async def query_knowledge(request: KnowledgeQueryRequest):
    """
    Direct RAG query to retrieve grounded answers from customer support knowledge base.
    """
    clean_query = validate_query_text(request.query)
    logger.info(f"POST /api/knowledge/query: '{clean_query}'")

    answer, sources, is_grounded = await rag_service.query_knowledge_base(
        query=clean_query,
        top_k=request.top_k or 3
    )

    return KnowledgeQueryResponse(
        status="success",
        query=clean_query,
        answer=answer,
        sources=sources,
        is_grounded=is_grounded
    )


@router.post("/admin/ingest", summary="Rebuild vector indexes for products and policies")
async def trigger_ingestion():
    """
    Admin endpoint to trigger vector store ingestion for products and knowledge base markdown files.
    """
    from backend.scripts.ingest import run_ingestion
    logger.info("POST /api/admin/ingest triggered")
    stats = run_ingestion()
    return {
        "status": "success",
        "message": "Vector store ingestion completed successfully.",
        "stats": stats
    }
