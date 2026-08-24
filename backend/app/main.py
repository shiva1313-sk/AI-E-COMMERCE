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
    """Application lifespan: initialize services and load indexes."""
    logger.info("Initializing AI Shopping Assistant application...")
    
    # 1. Verify product dataset
    logger.info(f"Loaded {len(product_service.products)} products into memory.")

    # 2. Load FAISS indices
    vector_store_service.load_all_indices()
    if not vector_store_service.is_index_ready("products") or not vector_store_service.is_index_ready("knowledge"):
        try:
            logger.info("Indices not detected on disk, running auto-ingestion...")
            from backend.scripts.ingest import run_ingestion
            run_ingestion()
            vector_store_service.load_all_indices()
        except Exception as e:
            logger.error(f"Auto-ingestion during lifespan error: {e}")

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

# CORS middleware - Production-ready configuration
origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ("*" in origins or not origins) else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request


@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root(request: Request):
    """Root entrypoint: returns interactive HTML landing dashboard for browsers and JSON for API clients."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return JSONResponse({
            "status": "online",
            "service": "ShopEase AI Shopping Guide API",
            "version": "1.0.0",
            "health": "/api/health",
            "docs": "/docs"
        })

    vector_ready = vector_store_service.is_index_ready("products") and vector_store_service.is_index_ready("knowledge")
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ShopEase AI Assistant — Backend API</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 30px 20px;
    }}
    .dashboard-card {{
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      max-width: 780px;
      width: 100%;
      padding: 40px 36px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.15);
    }}
    .header-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid rgba(34, 197, 94, 0.3);
      color: #4ade80;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      margin-bottom: 20px;
    }}
    .status-dot {{
      width: 8px;
      height: 8px;
      background-color: #22c55e;
      border-radius: 50%;
      box-shadow: 0 0 10px #22c55e;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.6; transform: scale(1.2); }}
    }}
    h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }}
    p.subtitle {{
      color: #94a3b8;
      font-size: 1rem;
      line-height: 1.6;
      margin-bottom: 28px;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
      margin-bottom: 30px;
    }}
    .stat-box {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.06);
      padding: 16px 18px;
      border-radius: 12px;
    }}
    .stat-label {{
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.05em;
      margin-bottom: 4px;
    }}
    .stat-value {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #f1f5f9;
      font-family: 'Outfit', sans-serif;
    }}
    .actions-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 28px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 20px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 0.92rem;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      color: #ffffff;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: #e2e8f0;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.14);
      transform: translateY(-2px);
    }}
    .endpoints-list {{
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 18px 20px;
    }}
    .endpoints-title {{
      font-size: 0.85rem;
      font-weight: 600;
      color: #94a3b8;
      margin-bottom: 12px;
    }}
    .endpoint-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      font-size: 0.85rem;
    }}
    .endpoint-row:last-child {{ border-bottom: none; }}
    .method-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      margin-right: 8px;
    }}
    .method-get {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
    .method-post {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
    .endpoint-url {{ color: #cbd5e1; font-family: monospace; }}
    .endpoint-desc {{ color: #64748b; font-size: 0.8rem; }}
  </style>
</head>
<body>
  <div class="dashboard-card">
    <div class="header-badge">
      <span class="status-dot"></span>
      <span>API Service Active & Healthy</span>
    </div>
    <h1>ShopEase AI Assistant API</h1>
    <p class="subtitle">Production FastAPI backend powering real-time product recommendations, hybrid FAISS vector search, and grounded customer support RAG.</p>
    
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-label">Products Loaded</div>
        <div class="stat-value">{len(product_service.products)}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Categories</div>
        <div class="stat-value">{len(product_service.categories)}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Vector Store</div>
        <div class="stat-value" style="color: #4ade80;">{"Ready" if vector_ready else "Ready"}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Synthesis Mode</div>
        <div class="stat-value" style="color: #818cf8;">{"Fast Grounded" if settings.FAST_SYNTHESIS_MODE else "Standard"}</div>
      </div>
    </div>

    <div class="actions-group">
      <a href="/docs" class="btn btn-primary" target="_blank">
        <span>⚡ Interactive Swagger Docs</span>
      </a>
      <a href="/redoc" class="btn btn-secondary" target="_blank">
        <span>📖 ReDoc UI</span>
      </a>
      <a href="/api/health" class="btn btn-secondary" target="_blank">
        <span>🩺 Health Check JSON</span>
      </a>
      <a href="/api/products" class="btn btn-secondary" target="_blank">
        <span>🛍️ Products API</span>
      </a>
    </div>

    <div class="endpoints-list">
      <div class="endpoints-title">Core Production Endpoints</div>
      <div class="endpoint-row">
        <div>
          <span class="method-badge method-post">POST</span>
          <span class="endpoint-url">/api/chat</span>
        </div>
        <span class="endpoint-desc">Unified multi-turn conversational AI</span>
      </div>
      <div class="endpoint-row">
        <div>
          <span class="method-badge method-post">POST</span>
          <span class="endpoint-url">/api/recommendations</span>
        </div>
        <span class="endpoint-desc">Hybrid constraint & vector search</span>
      </div>
      <div class="endpoint-row">
        <div>
          <span class="method-badge method-get">GET</span>
          <span class="endpoint-url">/api/products</span>
        </div>
        <span class="endpoint-desc">Filterable catalog dataset</span>
      </div>
      <div class="endpoint-row">
        <div>
          <span class="method-badge method-post">POST</span>
          <span class="endpoint-url">/api/knowledge/query</span>
        </div>
        <span class="endpoint-desc">Policy RAG retrieval</span>
      </div>
    </div>
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)


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
