import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import faiss
import numpy as np

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import VectorStoreException
from backend.app.services.embedding_service import embedding_service


class VectorStoreService:
    """Manages FAISS vector indexes and metadata for products and knowledge base documents."""

    def __init__(self):
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata_store: Dict[str, List[Dict[str, Any]]] = {}
        self._initialized = False

    def get_index_dir(self, collection: str) -> Path:
        """Resolve storage directory for a collection index."""
        if collection == "products":
            return settings.get_absolute_path(settings.FAISS_PRODUCT_INDEX_PATH)
        elif collection == "knowledge":
            return settings.get_absolute_path(settings.FAISS_KNOWLEDGE_INDEX_PATH)
        else:
            return settings.get_absolute_path(f"vectorstore/faiss_index/{collection}")

    def is_index_ready(self, collection: str) -> bool:
        """Check if an index is in memory or exists on disk."""
        if collection in self.indices and len(self.metadata_store.get(collection, [])) > 0:
            return True
        index_dir = self.get_index_dir(collection)
        return (index_dir / "index.faiss").exists() and (index_dir / "metadata.json").exists()

    def build_and_save_index(
        self,
        collection: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None
    ) -> int:
        """
        Build FAISS IndexFlatIP (cosine similarity) from texts and save to disk.
        """
        if not texts:
            logger.warning(f"No texts provided to build index for '{collection}'.")
            return 0

        logger.info(f"Generating embeddings for {len(texts)} items in collection '{collection}'...")
        if embeddings is None:
            embeddings = embedding_service.embed_texts(texts)

        dimension = embeddings.shape[1]
        logger.info(f"Creating FAISS IndexFlatIP with dimension {dimension}...")
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Update in-memory
        self.indices[collection] = index
        self.metadata_store[collection] = metadatas

        # Persist to disk
        index_dir = self.get_index_dir(collection)
        index_dir.mkdir(parents=True, exist_ok=True)

        faiss_file = str(index_dir / "index.faiss")
        metadata_file = index_dir / "metadata.json"

        faiss.write_index(index, faiss_file)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadatas, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved FAISS index and metadata for '{collection}' ({index.ntotal} vectors) to {index_dir}")
        return index.ntotal

    def load_index(self, collection: str) -> bool:
        """Load index and metadata from disk into memory."""
        index_dir = self.get_index_dir(collection)
        faiss_file = index_dir / "index.faiss"
        metadata_file = index_dir / "metadata.json"

        if not faiss_file.exists() or not metadata_file.exists():
            logger.warning(f"Index files for collection '{collection}' not found in {index_dir}.")
            return False

        try:
            logger.info(f"Loading FAISS index for '{collection}' from {faiss_file}...")
            self.indices[collection] = faiss.read_index(str(faiss_file))
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata_store[collection] = json.load(f)
            logger.info(f"Loaded '{collection}' index with {self.indices[collection].ntotal} items.")
            return True
        except Exception as e:
            logger.error(f"Failed to load index for '{collection}': {e}")
            return False

    def load_all_indices(self):
        """Attempt to load both product and knowledge base indexes."""
        self.load_index("products")
        self.load_index("knowledge")
        self._initialized = True

    def search(
        self,
        collection: str,
        query: str,
        top_k: int = 4,
        min_score: float = 0.0
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Perform semantic similarity search against FAISS index.
        Returns list of (metadata_dict, similarity_score) sorted by highest similarity score.
        """
        if collection not in self.indices:
            loaded = self.load_index(collection)
            if not loaded:
                logger.warning(f"Vector store collection '{collection}' is not available.")
                return []

        index = self.indices[collection]
        metadata = self.metadata_store.get(collection, [])

        if index.ntotal == 0 or not metadata:
            return []

        # Generate query embedding
        query_vector = embedding_service.embed_text(query).reshape(1, -1)
        
        # FAISS search
        k = min(top_k, index.ntotal)
        scores, indices = index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            if score >= min_score and idx < len(metadata):
                results.append((metadata[idx], float(score)))

        return results


vector_store_service = VectorStoreService()
