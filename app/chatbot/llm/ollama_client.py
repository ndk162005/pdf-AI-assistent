import logging
import httpx
from typing import Optional, Dict, Any
import config

logger = logging.getLogger(__name__)

class OllamaClientError(Exception):
    """Exception raised when calling Ollama LLM service fails."""
    pass

class OllamaClient:
    """HTTP Client for communicating with the local Ollama LLM service."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: float = None):
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or config.OLLAMA_MODEL
        self.timeout = timeout or config.OLLAMA_TIMEOUT
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            timeout_cfg = httpx.Timeout(self.timeout, read=self.timeout, connect=30.0)
            self._client = httpx.Client(timeout=timeout_cfg)
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a generation request to the Ollama API.

        Args:
            prompt: User / Context prompt.
            system_prompt: System prompt instructing the model.

        Returns:
            str: Generated completion text.
        """
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "24h",
            "options": {
                "num_ctx": 4096,
                "temperature": 0.2
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            client = self._get_client()
            response = client.post(endpoint, json=payload)
                
            if response.status_code == 404:
                raise OllamaClientError(
                    f"Ollama model '{self.model}' not found or endpoint invalid (404). "
                    f"Ensure model is pulled via 'ollama pull {self.model}'."
                )
            elif response.status_code != 200:
                raise OllamaClientError(f"Ollama API returned status code {response.status_code}: {response.text}")

            data = response.json()
            if "response" in data:
                return data["response"].strip()
            else:
                raise OllamaClientError(f"Malformed response from Ollama API: {data}")

        except httpx.ConnectError:
            raise OllamaClientError(
                f"Could not connect to Ollama service at {self.base_url}. "
                "Ensure Ollama is running locally ('ollama serve')."
            )
        except httpx.TimeoutException:
            raise OllamaClientError(f"Ollama request timed out after {self.timeout} seconds.")
        except Exception as e:
            if isinstance(e, OllamaClientError):
                raise
            raise OllamaClientError(f"Ollama client error: {str(e)}")
