from backend.app.core.exceptions import InvalidQueryException


def validate_query_text(query: str, min_len: int = 1, max_len: int = 1000) -> str:
    """Validate query length and non-emptiness."""
    if not query or not query.strip():
        raise InvalidQueryException("Query message cannot be empty or whitespace.")
    
    cleaned = query.strip()
    if len(cleaned) < min_len:
        raise InvalidQueryException(f"Query is too short (minimum {min_len} character required).")
    if len(cleaned) > max_len:
        raise InvalidQueryException(f"Query is too long (maximum {max_len} characters allowed).")
        
    return cleaned
