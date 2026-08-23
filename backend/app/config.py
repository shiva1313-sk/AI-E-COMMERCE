import os
from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend Root Directory
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]

    # LLM & Fast Synthesis Settings
    FAST_SYNTHESIS_MODE: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_TIMEOUT_SECONDS: float = 2.5
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Embedding & Vector Store Settings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.58

    # Paths (relative to backend root if not absolute)
    PRODUCT_DATA_PATH: str = "data/products.json"
    KNOWLEDGE_BASE_PATH: str = "knowledge_base"
    FAISS_PRODUCT_INDEX_PATH: str = "vectorstore/faiss_index/products"
    FAISS_KNOWLEDGE_INDEX_PATH: str = "vectorstore/faiss_index/knowledge"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def get_absolute_path(self, relative_or_absolute: str) -> Path:
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p
        return BACKEND_DIR / p


settings = Settings()
