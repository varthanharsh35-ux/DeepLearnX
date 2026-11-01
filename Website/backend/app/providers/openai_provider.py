"""
OpenAI LLM Provider Implementation.

Uses the official `openai` SDK (`from openai import OpenAI`) with structured JSON mode,
bounded backoff retries, and explicit exception normalization.
"""

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

logger = logging.getLogger("deeplearnx.providers.openai")

try:
    import openai
    from openai import (
        OpenAI,
        APIError,
        AuthenticationError,
        RateLimitError,
        APITimeoutError,
        APIConnectionError,
        BadRequestError,
        NotFoundError
    )
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider conforming to BaseLLMProvider."""

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, config: Optional[LLMConfig] = None):
        cfg = config or LLMConfig(
            provider="openai",
            model=OpenAIProvider.DEFAULT_MODEL
        )
        if not cfg.model:
            cfg.model = self.DEFAULT_MODEL
        super().__init__(cfg)
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        if not OPENAI_AVAILABLE:
            raise LLMConfigurationError("openai SDK is not installed in the Python environment", provider="openai")
        if not self.config.api_key or self.config.api_key.startswith("your_") or "here" in self.config.api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured", provider="openai")
        if self._client is None:
            self._client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.request_timeout,
                base_url=self.config.base_url
            )
        return self._client

    def _map_error(self, exc: Exception) -> Exception:
        """Maps OpenAI SDK exceptions into the explicit DeepLearnX LLMError hierarchy."""
        if isinstance(exc, LLMError):
            return exc

        err_str = str(exc)

        if OPENAI_AVAILABLE:
            if isinstance(exc, AuthenticationError):
                return LLMAuthenticationError(f"OpenAI API key rejected: {err_str}", provider="openai", status_code=401)
            if isinstance(exc, RateLimitError):
                if "quota" in err_str.lower() or "billing" in err_str.lower():
                    return LLMQuotaExhaustedError(f"OpenAI account quota exhausted: {err_str}", provider="openai", status_code=429)
                return LLMRateLimitError(f"OpenAI rate limit exceeded: {err_str}", provider="openai", status_code=429)
            if isinstance(exc, NotFoundError):
                return LLMUnsupportedModelError(f"OpenAI model '{self.config.model}' not found: {err_str}", provider="openai")
            if isinstance(exc, APITimeoutError):
                return LLMTimeoutError(f"OpenAI request timed out: {err_str}", provider="openai")
            if isinstance(exc, APIConnectionError):
                return LLMNetworkError(f"Failed to connect to OpenAI API: {err_str}", provider="openai")
            if isinstance(exc, BadRequestError):
                return LLMInvalidRequestError(f"Invalid OpenAI request: {err_str}", provider="openai", status_code=400)
            if isinstance(exc, APIError):
                code = getattr(exc, "status_code", 500)
                if code and code >= 500:
                    return LLMServerError(f"OpenAI server error: {err_str}", provider="openai", status_code=code)

        low = err_str.lower()
        if "timed out" in low or "timeout" in low:
            return LLMTimeoutError(f"OpenAI request timed out: {err_str}", provider="openai")
        if "connection" in low or "network" in low:
            return LLMNetworkError(f"Network error communicating with OpenAI: {err_str}", provider="openai")

        return LLMInvalidRequestError(f"OpenAI call failed: {err_str}", provider="openai")

    def generate_structured(
        self,
        schema: Union[Dict[str, Any], Type[BaseModel]],
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """Generates schema-validated structured output via JSON mode with bounded retries."""
        client = self._get_client()
        max_retries = max(0, self.config.max_retries)
        last_error = None

        system_prompt = system_instruction or "You are an expert academic cognitive assessment designer."
        system_prompt += " You MUST reply with valid JSON only."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        create_kwargs: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": self.config.temperature
        }
        if self.config.max_output_tokens:
            create_kwargs["max_tokens"] = self.config.max_output_tokens

        for attempt in range(max_retries + 1):
            t0 = time.time()
            try:
                response = client.chat.completions.create(**create_kwargs)
                latency_ms = (time.time() - t0) * 1000.0

                choice = response.choices[0]
                raw_text = choice.message.content or ""
                finish_reason = choice.finish_reason or "completed"

                if finish_reason == "content_filter":
                    raise LLMSafetyRefusalError("OpenAI refused content due to safety filter", provider="openai")
                if finish_reason == "length":
                    raise LLMTruncationError("OpenAI response was truncated by max_tokens", provider="openai")

                try:
                    parsed_content = json.loads(raw_text)
                except Exception as json_err:
                    raise LLMFormatError(f"OpenAI returned invalid JSON: {json_err}", provider="openai", raw_output=raw_text)

                input_tokens = getattr(response.usage, "prompt_tokens", None) if hasattr(response, "usage") else None
                output_tokens = getattr(response.usage, "completion_tokens", None) if hasattr(response, "usage") else None

                return GenerationResult(
                    provider="openai",
                    model=self.config.model,
                    content=parsed_content,
                    finish_reason=finish_reason,
                    raw_text=raw_text,
                    request_id=getattr(response, "id", None),
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
                    logger.warning(f"[OpenAI] Attempt {attempt+1} failed ({mapped.message}). Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    raise mapped

        raise last_error or LLMServerError("OpenAI generation failed after retries", provider="openai")

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """Generates free-form text with bounded retries."""
        client = self._get_client()
        max_retries = max(0, self.config.max_retries)
        last_error = None

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        create_kwargs: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature
        }
        if self.config.max_output_tokens:
            create_kwargs["max_tokens"] = self.config.max_output_tokens

        for attempt in range(max_retries + 1):
            t0 = time.time()
            try:
                response = client.chat.completions.create(**create_kwargs)
                latency_ms = (time.time() - t0) * 1000.0
                raw_text = response.choices[0].message.content or ""
                return GenerationResult(
                    provider="openai",
                    model=self.config.model,
                    content={"text": raw_text},
                    finish_reason=response.choices[0].finish_reason or "completed",
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

        raise last_error or LLMServerError("OpenAI text generation failed", provider="openai")

    def check_connection(self, force_refresh: bool = False) -> ProviderHealth:
        """Verifies OpenAI credentials and API reachability."""
        now = time.time()
        if not force_refresh and self._cached_health and (now - self._last_health_check_time < 60):
            return self._cached_health

        if not self.config.api_key or self.config.api_key.startswith("your_") or "here" in self.config.api_key:
            health = ProviderHealth(
                provider="openai",
                configured=False,
                reachable=False,
                last_status="missing_credentials",
                model=self.config.model,
                last_checked=now,
                message="OPENAI_API_KEY is unset in environment (.env). Operating in offline knowledge synthesis mode."
            )
            self._cached_health = health
            self._last_health_check_time = now
            return health

        if not OPENAI_AVAILABLE:
            health = ProviderHealth(
                provider="openai",
                configured=True,
                reachable=False,
                last_status="sdk_missing",
                model=self.config.model,
                last_checked=now,
                message="openai SDK is not installed."
            )
            self._cached_health = health
            self._last_health_check_time = now
            return health

        t0 = time.time()
        try:
            client = self._get_client()
            # Lightweight probe
            client.models.retrieve(self.config.model)
            latency = (time.time() - t0) * 1000.0
            health = ProviderHealth(
                provider="openai",
                configured=True,
                reachable=True,
                last_status="ready",
                model=self.config.model,
                last_checked=now,
                latency_ms=latency,
                message=f"OpenAI API connected successfully to model {self.config.model} ({latency:.1f}ms)."
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
                provider="openai",
                configured=True,
                reachable=False,
                last_status="error",
                model=self.config.model,
                last_checked=now,
                latency_ms=latency,
                error_category=category,
                message=f"OpenAI connectivity verification failed: {mapped.message}"
            )

        self._cached_health = health
        self._last_health_check_time = now
        return health
