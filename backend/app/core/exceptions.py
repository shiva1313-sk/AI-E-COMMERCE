from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.core.logging import logger


class AIShoppingAssistantException(Exception):
    """Base exception for AI Shopping Assistant application."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ProductNotFoundException(AIShoppingAssistantException):
    def __init__(self, product_id: str):
        super().__init__(
            message=f"Product with ID '{product_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"product_id": product_id}
        )


class OllamaServiceException(AIShoppingAssistantException):
    def __init__(self, message: str = "Ollama LLM service is currently unavailable or unreachable.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class VectorStoreException(AIShoppingAssistantException):
    def __init__(self, message: str = "Vector store error or index not initialized.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class InvalidQueryException(AIShoppingAssistantException):
    def __init__(self, message: str = "Query is invalid, empty, or exceeds maximum length."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


async def app_exception_handler(request: Request, exc: AIShoppingAssistantException) -> JSONResponse:
    """Global exception handler for application-defined errors."""
    logger.error(f"Application error on {request.method} {request.url.path}: {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled exceptions without leaking stack traces."""
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected server error occurred. Please try again shortly.",
            "path": request.url.path
        }
    )
