from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import OllamaServiceException


class OllamaService:
    """Service to communicate with local or remote Ollama LLM instance."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Ollama server is reachable and verify if the configured model is available.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    # Check if requested model or its base tag exists
                    model_found = any(
                        self.model == m or self.model in m or m.startswith(self.model.split(":")[0])
                        for m in models
                    )
                    return {
                        "status": "available",
                        "server_online": True,
                        "configured_model": self.model,
                        "model_installed": model_found,
                        "available_models": models
                    }
                else:
                    return {
                        "status": "unavailable",
                        "server_online": False,
                        "error": f"Ollama returned HTTP {resp.status_code}"
                    }
        except httpx.ConnectError:
            return {
                "status": "offline",
                "server_online": False,
                "error": f"Cannot connect to Ollama at {self.base_url}. Ensure Ollama is running ('ollama serve')."
            }
        except Exception as e:
            return {
                "status": "error",
                "server_online": False,
                "error": str(e)
            }

    async def is_available(self) -> bool:
        """Quick boolean check for Ollama availability."""
        health = await self.check_health()
        return health.get("server_online", False) and health.get("model_installed", False)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800
    ) -> str:
        """
        Generate text response from configured Ollama model.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system:
            payload["system"] = system

        try:
            logger.info(f"Sending generation request to Ollama ({self.model})...")
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    logger.info(f"Ollama successfully returned {len(generated_text)} characters.")
                    return generated_text
                elif response.status_code == 404:
                    msg = f"Model '{self.model}' not found in Ollama. Please run: 'ollama pull {self.model}'"
                    logger.error(msg)
                    raise OllamaServiceException(msg, details={"model": self.model})
                else:
                    msg = f"Ollama API returned HTTP {response.status_code}: {response.text}"
                    logger.error(msg)
                    raise OllamaServiceException(msg)

        except httpx.ConnectError:
            msg = f"Ollama server is not reachable at {self.base_url}. Please ensure Ollama is running ('ollama serve')."
            logger.warning(msg)
            raise OllamaServiceException(msg)
        except httpx.TimeoutException:
            msg = f"Ollama request timed out after {self.timeout} seconds."
            logger.error(msg)
            raise OllamaServiceException(msg)
        except OllamaServiceException:
            raise
        except Exception as e:
            msg = f"Unexpected error during Ollama generation: {str(e)}"
            logger.exception(msg)
            raise OllamaServiceException(msg)


ollama_service = OllamaService()
