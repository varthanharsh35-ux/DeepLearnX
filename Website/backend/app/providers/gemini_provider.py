"""
Google Gemini LLM Provider Implementation.

Uses the official modern `google-genai` SDK (`from google import genai`) with
structured output enforcement, bounded backoff retries, and comprehensive error mapping.
"""

import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional, Union, Type
from pydantic import BaseModel

from .base import (
    BaseLLMProvider,
    LLMConfig,
    GenerationResult,
    ProviderHealth,
    LLMError,
    LLMConfigurationError,
    LLMAuthenticationError,
    LLMQuotaExhaustedError,
    LLMRateLimitError,
    LLMNetworkError,
    LLMTimeoutError,
    LLMServerError,
    LLMUnsupportedModelError,
    LLMInvalidRequestError,
    LLMSafetyRefusalError,
    LLMTruncationError,
    LLMFormatError,
    LLMSchemaViolationError
)

logger = logging.getLogger("deeplearnx.providers.gemini")

try:
    from google import genai
    from google.genai import types, errors
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None
    errors = None


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider conforming to BaseLLMProvider."""

    DEFAULT_MODEL = "gemini-3.5-flash"

    def __init__(self, config: Optional[LLMConfig] = None):
        env_model = os.environ.get("GEMINI_MODEL") or os.environ.get("GEMINI_DEFAULT_MODEL") or self.DEFAULT_MODEL
        cfg = config or LLMConfig(
            provider="gemini",
            model=env_model
        )
        if not cfg.model or cfg.model in ("gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"):
            cfg.model = env_model
        super().__init__(cfg)
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        if not GENAI_AVAILABLE:
            raise LLMConfigurationError("google-genai SDK is not installed in the Python environment", provider="gemini")
        if not self.config.api_key or self.config.api_key.startswith("your_") or "here" in self.config.api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured", provider="gemini")
        if self._client is None:
            self._client = genai.Client(api_key=self.config.api_key)
        return self._client

    def _map_error(self, exc: Exception) -> Exception:
        """Maps provider/SDK exceptions into the explicit DeepLearnX LLMError hierarchy."""
        if isinstance(exc, LLMError):
            return exc

        err_str = str(exc)
        
        # Check if it's an APIError from google.genai
        if errors and isinstance(exc, errors.APIError):
            code = getattr(exc, "code", None)
            msg = getattr(exc, "message", err_str)
            if code in (401, 403) or "API_KEY_INVALID" in msg or "PERMISSION_DENIED" in msg:
                return LLMAuthenticationError(f"Gemini API key rejected: {msg}", provider="gemini", status_code=code or 401)
            if code == 404 or "NOT_FOUND" in msg:
                return LLMUnsupportedModelError(f"Gemini model '{self.config.model}' not found: {msg}", provider="gemini")
            if code == 429 or "RESOURCE_EXHAUSTED" in msg:
                if "quota" in msg.lower():
                    return LLMQuotaExhaustedError(f"Gemini quota exhausted: {msg}", provider="gemini", status_code=429)
                return LLMRateLimitError(f"Gemini rate limit exceeded: {msg}", provider="gemini", status_code=429)
            if code in (500, 502, 503, 504) or "UNAVAILABLE" in msg:
                return LLMServerError(f"Gemini server error: {msg}", provider="gemini", status_code=code or 503)
            if code == 400 or "INVALID_ARGUMENT" in msg:
                return LLMInvalidRequestError(f"Invalid Gemini request: {msg}", provider="gemini", status_code=400)

        # Fallback string heuristics for generic network/timeout exceptions
        low = err_str.lower()
        if "timed out" in low or "timeout" in low:
            return LLMTimeoutError(f"Gemini request timed out: {err_str}", provider="gemini")
        if "connection" in low or "nodename" in low or "dns" in low or "network" in low:
            return LLMNetworkError(f"Network error communicating with Gemini: {err_str}", provider="gemini")

        return LLMInvalidRequestError(f"Gemini call failed: {err_str}", provider="gemini")

    def generate_structured(
        self,
        schema: Union[Dict[str, Any], Type[BaseModel]],
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """Generates schema-validated structured output with bounded retries."""
        client = self._get_client()
        max_retries = max(0, self.config.max_retries)
        last_error = None

        config_args: Dict[str, Any] = {
            "response_mime_type": "application/json",
            "temperature": self.config.temperature,
        }
        if system_instruction:
            config_args["system_instruction"] = system_instruction
        if schema:
            config_args["response_schema"] = schema
        if self.config.max_output_tokens:
            config_args["max_output_tokens"] = self.config.max_output_tokens

        gen_config = types.GenerateContentConfig(**config_args)

        for attempt in range(max_retries + 1):
            t0 = time.time()
            try:
                response = client.models.generate_content(
                    model=self.config.model,
                    contents=prompt,
                    config=gen_config
                )
                latency_ms = (time.time() - t0) * 1000.0

                raw_text = response.text or ""
                finish_reason = "completed"

                if hasattr(response, "candidates") and response.candidates:
                    c = response.candidates[0]
                    fr = getattr(c, "finish_reason", None)
                    if fr:
                        finish_reason = str(fr).lower()
                        if "safety" in finish_reason:
                            raise LLMSafetyRefusalError("Gemini refused content due to safety policy", provider="gemini")
                        if "max_tokens" in finish_reason or "length" in finish_reason:
                            raise LLMTruncationError("Gemini response was truncated by max_output_tokens", provider="gemini")

                # Parse JSON
                raw_clean = raw_text.strip()
                if raw_clean.startswith("```"):
                    raw_clean = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", raw_clean)
                    raw_clean = re.sub(r"\n?```$", "", raw_clean).strip()

                try:
                    parsed_content = json.loads(raw_clean)
                except Exception as json_err:
                    raise LLMFormatError(f"Gemini returned invalid JSON: {json_err}", provider="gemini", raw_output=raw_text)

                # Token usage
                input_tokens = None
                output_tokens = None
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
                    output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

                return GenerationResult(
                    provider="gemini",
                    model=self.config.model,
                    content=parsed_content,
                    finish_reason=finish_reason,
                    raw_text=raw_text,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    generation_mode="live_llm"
                )

            except Exception as e:
                mapped = self._map_error(e)
                last_error = mapped
                if getattr(mapped, "retryable", False) and attempt < max_retries:
                    backoff = min(1.0 * (2 ** attempt), 8.0)
                    logger.warning(f"[Gemini] Attempt {attempt+1} failed ({mapped.message}). Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    raise mapped

        raise last_error or LLMServerError("Gemini generation failed after retries", provider="gemini")

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """Generates free-form text with bounded retries."""
        client = self._get_client()
        max_retries = max(0, self.config.max_retries)
        last_error = None

        config_args: Dict[str, Any] = {
            "temperature": self.config.temperature,
        }
        if system_instruction:
            config_args["system_instruction"] = system_instruction
        if self.config.max_output_tokens:
            config_args["max_output_tokens"] = self.config.max_output_tokens

        gen_config = types.GenerateContentConfig(**config_args)

        for attempt in range(max_retries + 1):
            t0 = time.time()
            try:
                response = client.models.generate_content(
                    model=self.config.model,
                    contents=prompt,
                    config=gen_config
                )
                latency_ms = (time.time() - t0) * 1000.0
                raw_text = response.text or ""
                return GenerationResult(
                    provider="gemini",
                    model=self.config.model,
                    content={"text": raw_text},
                    finish_reason="completed",
                    raw_text=raw_text,
                    latency_ms=latency_ms,
                    generation_mode="live_llm"
                )
            except Exception as e:
                mapped = self._map_error(e)
                last_error = mapped
                if getattr(mapped, "retryable", False) and attempt < max_retries:
                    backoff = min(1.0 * (2 ** attempt), 8.0)
                    time.sleep(backoff)
                else:
                    raise mapped

        raise last_error or LLMServerError("Gemini text generation failed", provider="gemini")

    def check_connection(self, force_refresh: bool = False) -> ProviderHealth:
        """Verifies Gemini credentials and API reachability."""
        now = time.time()
        if not force_refresh and self._cached_health and (now - self._last_health_check_time < 60):
            return self._cached_health

        if not self.config.api_key or self.config.api_key.startswith("your_") or "here" in self.config.api_key:
            health = ProviderHealth(
                provider="gemini",
                configured=False,
                reachable=False,
                last_status="missing_credentials",
                model=self.config.model,
                last_checked=now,
                message="GEMINI_API_KEY is unset in environment (.env). Operating in offline knowledge synthesis mode."
            )
            self._cached_health = health
            self._last_health_check_time = now
            return health

        if not GENAI_AVAILABLE:
            health = ProviderHealth(
                provider="gemini",
                configured=True,
                reachable=False,
                last_status="sdk_missing",
                model=self.config.model,
                last_checked=now,
                message="google-genai SDK is not installed."
            )
            self._cached_health = health
            self._last_health_check_time = now
            return health

        t0 = time.time()
        try:
            client = self._get_client()
            # Lightweight probe
            model_info = client.models.get(model=self.config.model)
            latency = (time.time() - t0) * 1000.0
            health = ProviderHealth(
                provider="gemini",
                configured=True,
                reachable=True,
                last_status="ready",
                model=self.config.model,
                last_checked=now,
                latency_ms=latency,
                message=f"Gemini API connected successfully to model {self.config.model} ({latency:.1f}ms)."
            )
        except Exception as e:
            latency = (time.time() - t0) * 1000.0
            mapped = self._map_error(e)
            category = "authentication_rejected" if isinstance(mapped, LLMAuthenticationError) else (
                "quota_exhausted" if isinstance(mapped, LLMQuotaExhaustedError) else (
                    "rate_limited" if isinstance(mapped, LLMRateLimitError) else "connection_error"
                )
            )
            health = ProviderHealth(
                provider="gemini",
                configured=True,
                reachable=False,
                last_status="error",
                model=self.config.model,
                last_checked=now,
                latency_ms=latency,
                error_category=category,
                message=f"Gemini connectivity verification failed: {mapped.message}"
            )

        self._cached_health = health
        self._last_health_check_time = now
        return health
