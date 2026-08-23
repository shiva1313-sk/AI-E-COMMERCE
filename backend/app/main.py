import os
import sys
import types
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure both 'backend.app...' and direct 'app...' imports work from any working directory
_app_dir = Path(__file__).resolve().parent
_backend_dir = _app_dir.parent
_root_dir = _backend_dir.parent

for _p in [str(_root_dir), str(_backend_dir), str(_app_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

if "backend" not in sys.modules:
    _backend_mod = types.ModuleType("backend")
    _backend_mod.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = _backend_mod

if "backend.app" not in sys.modules:
    import backend.app
    _backend_mod.app = sys.modules.get("backend.app")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import (
    AIShoppingAssistantException,
    app_exception_handler,
    generic_exception_handler,
)
from backend.app.core.security import get_cors_origins
from backend.app.services.product_service import product_service
from backend.app.services.vector_store_service import vector_store_service
from backend.app.services.ollama_service import ollama_service

from backend.app.api.products import router as products_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize services, load indexes, check Ollama."""
    logger.info("Initializing AI Shopping Assistant application...")
    
    # 1. Verify product dataset
    logger.info(f"Loaded {len(product_service.products)} products into memory.")

    # 2. Load FAISS indices
    logger.info("Loading FAISS vector store indices...")
    vector_store_service.load_all_indices()

    # If vector store is missing, trigger automatic ingestion
    if not vector_store_service.is_index_ready("products") or not vector_store_service.is_index_ready("knowledge"):
        logger.warning("FAISS indices not found on disk. Triggering auto-ingestion...")
        try:
            from backend.scripts.ingest import run_ingestion
            run_ingestion()
            vector_store_service.load_all_indices()
        except Exception as e:
            logger.error(f"Auto-ingestion failed: {e}")

    # 3. Check Ollama LLM health
    logger.info("Checking Ollama LLM connectivity...")
    ollama_status = await ollama_service.check_health()
    logger.info(f"Ollama health check result: {ollama_status}")

    yield

    logger.info("Shutting down AI Shopping Assistant application...")


app = FastAPI(
    title="ShopEase AI Assistant API",
    description="Production-ready AI E-Commerce Product Recommendation & Customer Support Assistant using RAG, FAISS, Sentence Transformers, and Ollama.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception handlers
app.add_exception_handler(AIShoppingAssistantException, app_exception_handler)  # type: ignore
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware
origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint returning system status, vector store readiness, and AI assistant availability.
    """
    ollama_health = await ollama_service.check_health()
    vector_ready = vector_store_service.is_index_ready("products") and vector_store_service.is_index_ready("knowledge")
    
    status_str = "healthy" if vector_ready else "degraded"

    return {
        "status": status_str,
        "environment": settings.ENVIRONMENT,
        "fast_synthesis": "active" if settings.FAST_SYNTHESIS_MODE else "disabled",
        "ollama": ollama_health.get("status", "unknown"),
        "model": settings.OLLAMA_MODEL,
        "ollama_details": ollama_health,
        "vector_store": "ready" if vector_ready else "not_ready",
        "embedding_model": settings.EMBEDDING_MODEL,
        "products_indexed": len(product_service.products),
        "categories": len(product_service.categories)
    }


# Include API Routers under /api
app.include_router(chat_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
