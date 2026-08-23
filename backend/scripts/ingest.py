import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure backend root is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = BACKEND_ROOT.parent

for p in [str(WORKSPACE_ROOT), str(BACKEND_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.models.product import Product
from backend.app.services.embedding_service import embedding_service
from backend.app.services.vector_store_service import vector_store_service


def split_markdown_into_chunks(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse a policy markdown file into logical section chunks.
    Preserves section titles, document name, and text.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    doc_name = filepath.stem.replace("_", " ").title()
    chunks = []

    # Split by level 2 headings ## or level 1 #
    sections = re.split(r'\n(?=##?\s+)', content)
    for idx, sec in enumerate(sections):
        cleaned = sec.strip()
        if not cleaned:
            continue
        
        # Extract title from first line
        lines = cleaned.split("\n")
        title_line = lines[0].lstrip("#").strip()
        title = f"{doc_name} - {title_line}" if title_line and title_line != doc_name else doc_name

        chunks.append({
            "source_type": "policy",
            "source_file": filepath.name,
            "document": doc_name,
            "title": title,
            "chunk_index": idx,
            "content": cleaned
        })

    return chunks


def run_ingestion() -> Dict[str, Any]:
    """Execute ingestion pipeline for products and knowledge base documents."""
    logger.info("=== Starting AI Shopping Assistant Ingestion Pipeline ===")

    # 1. Ingest Products
    products_file = settings.get_absolute_path(settings.PRODUCT_DATA_PATH)
    if not products_file.exists():
        raise FileNotFoundError(f"Product dataset not found at {products_file}")

    with open(products_file, "r", encoding="utf-8") as f:
        raw_products = json.load(f)

    products = [Product(**item) for item in raw_products]
    logger.info(f"Loaded and validated {len(products)} products from {products_file.name}")

    product_texts = []
    product_metadatas = []

    for p in products:
        text = p.to_searchable_text()
        product_texts.append(text)
        product_metadatas.append({
            "source_type": "product",
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "price": p.price,
            "mrp": p.mrp,
            "stock_status": p.stock_status,
            "searchable_text": text
        })

    products_count = vector_store_service.build_and_save_index(
        collection="products",
        texts=product_texts,
        metadatas=product_metadatas
    )

    # 2. Ingest Knowledge Base Markdown Documents
    kb_dir = settings.get_absolute_path(settings.KNOWLEDGE_BASE_PATH)
    if not kb_dir.exists():
        raise FileNotFoundError(f"Knowledge base directory not found at {kb_dir}")

    md_files = list(kb_dir.glob("*.md"))
    logger.info(f"Found {len(md_files)} markdown policy documents in {kb_dir.name}")

    kb_texts = []
    kb_metadatas = []

    for md_path in md_files:
        chunks = split_markdown_into_chunks(md_path)
        for chunk in chunks:
            text = f"Policy Document: {chunk['document']}\nSection: {chunk['title']}\n\n{chunk['content']}"
            kb_texts.append(text)
            kb_metadatas.append(chunk)

    kb_count = vector_store_service.build_and_save_index(
        collection="knowledge",
        texts=kb_texts,
        metadatas=kb_metadatas
    )

    # 3. Print Report
    report = {
        "status": "Success",
        "products_indexed": products_count,
        "knowledge_documents_indexed": len(md_files),
        "knowledge_chunks_indexed": kb_count,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_dimension": embedding_service.dimension,
        "vector_store": "FAISS IndexFlatIP (Cosine Similarity)"
    }

    print("\n" + "=" * 55)
    print("      AI SHOPPING ASSISTANT - INGESTION REPORT     ")
    print("=" * 55)
    print(f"Products indexed             : {report['products_indexed']}")
    print(f"Knowledge documents indexed  : {report['knowledge_documents_indexed']}")
    print(f"Knowledge chunks indexed     : {report['knowledge_chunks_indexed']}")
    print(f"Embedding model              : {report['embedding_model']}")
    print(f"Embedding dimension          : {report['embedding_dimension']}")
    print(f"Vector store                 : {report['vector_store']}")
    print(f"Status                       : {report['status']}")
    print("=" * 55 + "\n")

    return report


if __name__ == "__main__":
    run_ingestion()
