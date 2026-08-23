import time
from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import OllamaServiceException


class OllamaService:
    """Service to communicate with local or remote Ollama LLM instance with fast circuit breaking and caching."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self._last_health_check_time: float = 0.0
        self._cached_health: Optional[Dict[str, Any]] = None
        self._health_cache_ttl: float = 45.0  # Cache health check for 45 seconds

    @property
    def timeout(self) -> float:
        return float(settings.OLLAMA_TIMEOUT_SECONDS)

    async def check_health(self, force: bool = False) -> Dict[str, Any]:
        """
        Check if Ollama server is reachable and verify if the configured model is available.
        Uses cached result within TTL to eliminate unnecessary latency.
        """
        now = time.time()
        if not force and self._cached_health is not None and (now - self._last_health_check_time) < self._health_cache_ttl:
            return self._cached_health

        try:
            # Use quick timeout for health checks (1.5s max)
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    model_found = any(
                        self.model == m or self.model in m or m.startswith(self.model.split(":")[0])
                        for m in models
                    )
                    health_res = {
                        "status": "available" if model_found else "model_missing",
                        "server_online": True,
                        "configured_model": self.model,
                        "model_installed": model_found,
                        "available_models": models
                    }
                else:
                    health_res = {
                        "status": "unavailable",
                        "server_online": False,
                        "error": f"Ollama returned HTTP {resp.status_code}"
                    }
        except httpx.ConnectError:
            health_res = {
                "status": "offline",
                "server_online": False,
                "error": f"Cannot connect to Ollama at {self.base_url}."
            }
        except Exception as e:
            health_res = {
                "status": "error",
                "server_online": False,
                "error": str(e)
            }

        self._cached_health = health_res
        self._last_health_check_time = now
        return health_res

    async def is_available(self) -> bool:
        """Quick boolean check for Ollama availability."""
        health = await self.check_health()
        return health.get("server_online", False) and health.get("model_installed", False)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 150
    ) -> str:
        """
        Generate text response from configured Ollama model with fast circuit breaking.
        """
        # Fast circuit breaker: if we know Ollama is offline, fail instantly without waiting
        if not await self.is_available():
            raise OllamaServiceException("Ollama service is offline or model not installed.")

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
            logger.info(f"Sending fast generation request to Ollama ({self.model})...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    logger.info(f"Ollama returned {len(generated_text)} chars.")
                    return generated_text
                elif response.status_code == 404:
                    msg = f"Model '{self.model}' not found in Ollama."
                    logger.error(msg)
                    raise OllamaServiceException(msg, details={"model": self.model})
                else:
                    msg = f"Ollama API returned HTTP {response.status_code}: {response.text}"
                    logger.error(msg)
                    raise OllamaServiceException(msg)

        except httpx.ConnectError:
            self._cached_health = {"status": "offline", "server_online": False}
            self._last_health_check_time = time.time()
            raise OllamaServiceException(f"Ollama server is not reachable at {self.base_url}.")
        except httpx.TimeoutException:
            raise OllamaServiceException(f"Ollama request timed out after {self.timeout} seconds.")
        except OllamaServiceException:
            raise
        except Exception as e:
            raise OllamaServiceException(f"Unexpected error during Ollama generation: {str(e)}")


ollama_service = OllamaService()
