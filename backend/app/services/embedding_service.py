import numpy as np
from typing import List, Union
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import AIShoppingAssistantException


class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self):
        model_name = settings.EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {model_name}...")
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            logger.info(f"Embedding model '{model_name}' loaded successfully (dimension: {self.dimension}).")
        except Exception as e:
            logger.error(f"Failed to load primary embedding model '{model_name}': {e}. Attempting fallback to 'all-MiniLM-L6-v2'...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Fallback embedding model 'all-MiniLM-L6-v2' loaded successfully.")
            except Exception as fallback_err:
                logger.critical(f"Failed to load any embedding model: {fallback_err}")
                raise AIShoppingAssistantException(
                    message=f"Failed to initialize embedding model: {str(fallback_err)}",
                    status_code=500
                )

    @property
    def dimension(self) -> int:
        """Return embedding vector dimension."""
        if self._model is None:
            self._load_model()
        if hasattr(self._model, "get_embedding_dimension"):
            dim = self._model.get_embedding_dimension()
        elif hasattr(self._model, "get_sentence_embedding_dimension"):
            dim = self._model.get_sentence_embedding_dimension()
        else:
            dim = 384
        return int(dim) if dim is not None else 384

    def embed_text(self, text: str) -> np.ndarray:
        """Generate a normalized 1D embedding vector for a single text string."""
        if not text or not text.strip():
            text = "empty"
        embedding = self.model.encode(text, normalize_embeddings=True)
        return np.array(embedding, dtype=np.float32)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate normalized 2D embedding array for a batch of text strings."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        # Replace empty strings
        cleaned = [t if t and t.strip() else "empty" for t in texts]
        embeddings = self.model.encode(
            cleaned,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return np.array(embeddings, dtype=np.float32)


embedding_service = EmbeddingService()
