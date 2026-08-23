import html
from typing import List
from backend.app.config import settings

MAX_QUERY_LENGTH = 1000


def sanitize_input(text: str) -> str:
    """Sanitize and strip dangerous HTML/script injection from user input."""
    if not text:
        return ""
    # Strip whitespace and trim to safe character bounds
    trimmed = text.strip()[:MAX_QUERY_LENGTH]
    # Escape HTML special characters
    return html.escape(trimmed)


def get_cors_origins() -> List[str]:
    """Return validated CORS origins list."""
    if isinstance(settings.CORS_ORIGINS, list):
        return settings.CORS_ORIGINS
    return ["http://localhost:5173", "http://localhost:3000"]
