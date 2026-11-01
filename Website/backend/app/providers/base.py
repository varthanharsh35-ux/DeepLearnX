"""
DeepLearnX LLM Provider Base Contracts & Exceptions.

Defines normalized interfaces, health check representations, generation results,
and explicit error hierarchies for all LLM providers (Google Gemini, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, Type
import time
from pydantic import BaseModel


# =============================================================================
# EXPLICIT EXCEPTION HIERARCHY
# =============================================================================

class LLMError(Exception):
    """Base exception for all DeepLearnX LLM provider errors."""
    def __init__(self, message: str, provider: str = "unknown", status_code: Optional[int] = None, retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.retryable = retryable

    def __str__(self) -> str:
        code_str = f" [HTTP {self.status_code}]" if self.status_code else ""
        return f"[{self.provider.upper()}]{code_str} {self.message}"


class LLMConfigurationError(LLMError):
    """Raised when provider configuration or credentials are missing or invalidly formatted."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, retryable=False)


class LLMAuthenticationError(LLMError):
    """Raised when API key or authentication is explicitly rejected by the provider."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 401):
        super().__init__(message, provider=provider, status_code=status_code, retryable=False)


class LLMQuotaExhaustedError(LLMError):
    """Raised when provider account quota has been completely exhausted (non-transient)."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 429):
        super().__init__(message, provider=provider, status_code=status_code, retryable=False)


class LLMRateLimitError(LLMError):
    """Raised when rate limit is temporarily exceeded (transient, retryable with backoff)."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 429, retry_after: Optional[float] = None):
        super().__init__(message, provider=provider, status_code=status_code, retryable=True)
        self.retry_after = retry_after


class LLMNetworkError(LLMError):
    """Raised on connection drop, DNS failure, or network unreachability (retryable)."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, retryable=True)


class LLMTimeoutError(LLMError):
    """Raised when provider response exceeds configured timeout limit (retryable)."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, status_code=408, retryable=True)


class LLMServerError(LLMError):
    """Raised when provider reports internal service failure 500/503 (transient, retryable)."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 503):
        super().__init__(message, provider=provider, status_code=status_code, retryable=True)


class LLMUnsupportedModelError(LLMError):
    """Raised when specified model identifier is not recognized or decommissioned."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, status_code=404, retryable=False)


class LLMInvalidRequestError(LLMError):
    """Raised when prompt or parameters violate provider API contract."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 400):
        super().__init__(message, provider=provider, status_code=status_code, retryable=False)


class LLMSafetyRefusalError(LLMError):
    """Raised when prompt or response triggers safety policy refusal."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, retryable=False)


class LLMTruncationError(LLMError):
    """Raised when model output was abruptly truncated due to token limit."""
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider, retryable=False)


class LLMFormatError(LLMError):
    """Raised when model returns malformed JSON or unparseable structured data."""
    def __init__(self, message: str, provider: str = "unknown", raw_output: str = ""):
        super().__init__(message, provider=provider, retryable=True)
        self.raw_output = raw_output


class LLMSchemaViolationError(LLMError):
    """Raised when structured JSON is valid JSON but misses required schema fields."""
    def __init__(self, message: str, provider: str = "unknown", missing_fields: Optional[list] = None):
        super().__init__(message, provider=provider, retryable=False)
        self.missing_fields = missing_fields or []


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class LLMConfig:
    """Normalized provider configuration."""
    provider: str
    api_key: Optional[str] = None
    model: str = ""
    request_timeout: float = 30.0
    max_retries: int = 2
    fallback_enabled: bool = True
    max_output_tokens: Optional[int] = None
    temperature: float = 0.2
    base_url: Optional[str] = None

    def mask_api_key(self) -> str:
        """Returns safe masked key for logging/telemetry."""
        if not self.api_key:
            return "UNSET"
        k = self.api_key.strip()
        if len(k) <= 8:
            return "***"
        return f"{k[:4]}...{k[-4:]}"


@dataclass
class GenerationResult:
    """Normalized output contract across all LLM providers."""
    provider: str
    model: str
    content: Dict[str, Any]
    finish_reason: str = "completed"
    raw_text: str = ""
    request_id: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: float = 0.0
    generation_mode: str = "live_llm"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "content": self.content,
            "finish_reason": self.finish_reason,
            "request_id": self.request_id,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": round(self.latency_ms, 2),
            "generation_mode": self.generation_mode,
            "timestamp": self.timestamp
        }


@dataclass
class ProviderHealth:
    """Granular health & connectivity status."""
    provider: str
    configured: bool
    reachable: bool
    last_status: str  # "ready", "missing_credentials", "auth_failed", "rate_limited", "quota_exhausted", "unreachable", "error"
    model: str = ""
    last_checked: Optional[float] = None
    latency_ms: Optional[float] = None
    message: str = ""
    error_category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "configured": self.configured,
            "reachable": self.reachable,
            "last_status": self.last_status,
            "model": self.model,
            "last_checked": self.last_checked,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms is not None else None,
            "message": self.message,
            "error_category": self.error_category
        }


# =============================================================================
# ABSTRACT PROVIDER INTERFACE
# =============================================================================

class BaseLLMProvider(ABC):
    """Abstract base class for all DeepLearnX LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._cached_health: Optional[ProviderHealth] = None
        self._last_health_check_time: float = 0.0

    @property
    def provider_name(self) -> str:
        return self.config.provider

    @abstractmethod
    def generate_structured(
        self,
        schema: Union[Dict[str, Any], Type[BaseModel]],
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """
        Generates structured JSON conforming strictly to the requested schema.
        Must normalize errors into the explicit LLMError hierarchy.
        """
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: str = ""
    ) -> GenerationResult:
        """
        Generates free-form text.
        Must normalize errors into the explicit LLMError hierarchy.
        """
        pass

    @abstractmethod
    def check_connection(self, force_refresh: bool = False) -> ProviderHealth:
        """
        Performs non-destructive connectivity verification.
        Distinguishes missing credentials from invalid credentials from reachable service.
        """
        pass
