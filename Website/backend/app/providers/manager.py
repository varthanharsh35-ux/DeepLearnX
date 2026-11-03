"""
DeepLearnX LLM Provider Manager & Dispatcher.

Orchestrates provider selection, configuration discovery, transparent readiness reporting,
and strict, verifiable mode reporting (distinguishing 'live_llm' from 'offline_knowledge_synthesis').
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Tuple, Union, Type
from pydantic import BaseModel

from .base import (
    BaseLLMProvider,
    LLMConfig,
    GenerationResult,
    ProviderHealth,
    LLMConfigurationError,
    LLMAuthenticationError,
    LLMQuotaExhaustedError,
    LLMRateLimitError,
    LLMNetworkError,
    LLMTimeoutError,
    LLMServerError,
    LLMError
)
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider

logger = logging.getLogger("deeplearnx.providers.manager")


def _get_env_bool(key: str, default: bool = True) -> bool:
    val = os.environ.get(key, "").strip().lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


def _get_env_int(key: str, default: int) -> int:
    val = os.environ.get(key, "").strip()
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _get_env_float(key: str, default: float) -> float:
    val = os.environ.get(key, "").strip()
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class LLMProviderManager:
    """Manages active LLM provider, fallback mechanisms, and readiness status."""

    def __init__(self):
        self.provider_pref = os.environ.get("LLM_PROVIDER", "auto").strip().lower()
        self.request_timeout = _get_env_float("LLM_REQUEST_TIMEOUT", 30.0)
        self.max_retries = _get_env_int("LLM_MAX_RETRIES", 2)
        self.fallback_enabled = _get_env_bool("LLM_FALLBACK_ENABLED", True)
        self.temperature = _get_env_float("LLM_TEMPERATURE", 0.2)
        
        # Discover Gemini config
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        gemini_model = os.environ.get("GEMINI_MODEL") or os.environ.get("GEMINI_DEFAULT_MODEL") or "gemini-3.8-flash"
        # Temporarily disallow gemini-3.6-flash, gemini-3.5-flash, and legacy models
        disallowed_models = {
            "gemini-3.6-flash", "gemini-3.5-flash",
            "gemini-1.5-flash", "gemini-1.5-pro",
            "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"
        }
        if gemini_model in disallowed_models:
            gemini_model = "gemini-3.8-flash"

        self.gemini_config = LLMConfig(
            provider="gemini",
            api_key=gemini_key if gemini_key else None,
            model=gemini_model,
            request_timeout=self.request_timeout,
            max_retries=self.max_retries,
            fallback_enabled=self.fallback_enabled,
            temperature=self.temperature
        )
        self.gemini_provider = GeminiProvider(self.gemini_config)

        # Gemini Lite Fallback Provider (high headroom: 15 RPM, 500 RPD)
        self.gemini_lite_model = os.environ.get("GEMINI_FALLBACK_MODEL") or "gemini-3.5-flash-lite"
        self.gemini_lite_config = LLMConfig(
            provider="gemini",
            api_key=gemini_key if gemini_key else None,
            model=self.gemini_lite_model,
            request_timeout=self.request_timeout,
            max_retries=self.max_retries,
            fallback_enabled=self.fallback_enabled,
            temperature=self.temperature
        )
        self.gemini_lite_provider = GeminiProvider(self.gemini_lite_config)

        # Discover OpenAI config
        openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        openai_model = os.environ.get("OPENAI_MODEL") or os.environ.get("OPENAI_DEFAULT_MODEL") or "gpt-4o-mini"
        self.openai_config = LLMConfig(
            provider="openai",
            api_key=openai_key if openai_key else None,
            model=openai_model,
            request_timeout=self.request_timeout,
            max_retries=self.max_retries,
            fallback_enabled=self.fallback_enabled,
            temperature=self.temperature
        )
        self.openai_provider = OpenAIProvider(self.openai_config)
        
        # Generation telemetry & runtime status tracking
        self.last_generation_status: Optional[str] = None  # "live_generation_succeeded", "generation_failed", "provider_unavailable", "quota_exhausted"
        self.last_generation_error: Optional[str] = None
        self.last_generation_time: Optional[float] = None
        self.total_live_generations: int = 0
        self.last_failover_event: Optional[Dict[str, Any]] = None
        self.failover_history: List[Dict[str, Any]] = []
        self.quota_exhausted_retry_after: Optional[str] = None
        self.quota_exhausted_retry_seconds: Optional[float] = None

    def reload_config(self) -> None:
        """Reloads configuration from os.environ."""
        self.__init__()

    def get_active_provider(self) -> Optional[BaseLLMProvider]:
        """Returns the configured and prioritized provider, or None if no keys exist."""
        pref = self.provider_pref
        from .rate_limiter import get_request_limiter
        limiter = get_request_limiter()

        def _resolve_gemini() -> Optional[BaseLLMProvider]:
            if not self.gemini_config.api_key or self.gemini_config.api_key.startswith("your_"):
                return None
            # If primary Gemini model is under daily quota circuit breaker, route to Lite
            if not limiter.is_model_available(self.gemini_config.model):
                if self.fallback_enabled and limiter.is_model_available(self.gemini_lite_model):
                    return self.gemini_lite_provider
            return self.gemini_provider

        if pref in ("gemini", "auto"):
            gemini = _resolve_gemini()
            if gemini:
                return gemini
            if pref == "auto" and self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"):
                return self.openai_provider
            return None
        elif pref == "openai":
            if self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"):
                return self.openai_provider
            return None
        return None

    def get_provider_for_request(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Optional[BaseLLMProvider]:
        """
        Resolves or dynamically creates a provider instance for an incoming request.
        If api_key is supplied directly, a request-scoped provider is returned.
        """
        p_name = (provider_name or self.provider_pref or "gemini").lower()
        if p_name == "auto":
            p_name = "gemini" if (self.gemini_config.api_key or (api_key and api_key.startswith("AIzaSy"))) else "openai"

        if api_key and api_key.strip():
            k = api_key.strip()
            if p_name == "openai":
                cfg = LLMConfig(
                    provider="openai",
                    api_key=k,
                    model=model_name or self.openai_config.model,
                    request_timeout=self.request_timeout,
                    max_retries=self.max_retries,
                    fallback_enabled=self.fallback_enabled,
                    temperature=self.temperature
                )
                return OpenAIProvider(cfg)
            else:
                cfg = LLMConfig(
                    provider="gemini",
                    api_key=k,
                    model=model_name or self.gemini_config.model,
                    request_timeout=self.request_timeout,
                    max_retries=self.max_retries,
                    fallback_enabled=self.fallback_enabled,
                    temperature=self.temperature
                )
                return GeminiProvider(cfg)

        # No dynamic api_key override: use configured system providers
        if provider_name:
            if p_name == "gemini" and self.gemini_config.api_key and not self.gemini_config.api_key.startswith("your_"):
                if model_name:
                    cfg = LLMConfig(
                        provider="gemini",
                        api_key=self.gemini_config.api_key,
                        model=model_name,
                        request_timeout=self.request_timeout,
                        max_retries=self.max_retries,
                        fallback_enabled=self.fallback_enabled,
                        temperature=self.temperature
                    )
                    return GeminiProvider(cfg)
                return self.gemini_provider
            elif p_name == "openai" and self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"):
                if model_name:
                    cfg = LLMConfig(
                        provider="openai",
                        api_key=self.openai_config.api_key,
                        model=model_name,
                        request_timeout=self.request_timeout,
                        max_retries=self.max_retries,
                        fallback_enabled=self.fallback_enabled,
                        temperature=self.temperature
                    )
                    return OpenAIProvider(cfg)
                return self.openai_provider

        return self.get_active_provider()

    def generate_structured(
        self,
        schema: Union[Dict[str, Any], Type[BaseModel]],
        prompt: str,
        system_instruction: str = "",
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> GenerationResult:
        """
        Executes structured generation using the resolved provider, with transparent
        multi-provider fallback and comprehensive status tracking.
        """
        primary = self.get_provider_for_request(
            provider_name=provider_override,
            model_name=model_override,
            api_key=api_key_override
        )
        if not primary or not primary.config.api_key:
            raise LLMConfigurationError("No live LLM provider is configured with valid credentials.")

        try:
            res = primary.generate_structured(schema=schema, prompt=prompt, system_instruction=system_instruction)
            self.last_generation_status = "live_generation_succeeded"
            self.last_generation_error = None
            self.last_generation_time = time.time()
            self.total_live_generations += 1
            return res
        except LLMQuotaExhaustedError as qe:
            logger.warning(f"Primary provider '{primary.provider_name}' daily quota exhausted: {qe}")
            if self.fallback_enabled and not api_key_override:
                # 1. Try Gemini Lite fallback if primary was Gemini Flash
                if primary.provider_name == "gemini" and "lite" not in (primary.config.model or "").lower():
                    logger.info(f"Primary Gemini model '{primary.config.model}' quota exhausted. Failing over to validated fallback '{self.gemini_lite_model}'...")
                    try:
                        res = self.gemini_lite_provider.generate_structured(schema=schema, prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(qe),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "model_quota_fallback",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as lite_e:
                        logger.warning(f"Gemini Lite fallback failed: {lite_e}")
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(qe),
                            "secondary_error": str(lite_e),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "model_quota_fallback",
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                secondary_name = "openai" if primary.provider_name == "gemini" else "gemini"
                secondary = self.get_provider_for_request(provider_name=secondary_name)
                if (
                    secondary
                    and secondary.provider_name != primary.provider_name
                    and secondary.config.api_key
                    and not secondary.config.api_key.startswith("your_")
                    and secondary.config.api_key != primary.config.api_key
                ):
                    logger.info(f"Failing over from '{primary.provider_name}' to configured secondary provider '{secondary.provider_name}' due to quota exhaustion...")
                    try:
                        res = secondary.generate_structured(schema=schema, prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(qe),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "quota_exhaustion",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as sec_e:
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(qe),
                            "secondary_error": str(sec_e),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "quota_exhaustion",
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        logger.error(f"Secondary fallback provider '{secondary.provider_name}' also failed: {sec_e}")

            # No alternative configured or failover failed: preserve quota state and re-raise without retrying
            self.last_generation_status = "quota_exhausted"
            self.last_generation_error = str(qe)
            self.quota_exhausted_retry_after = getattr(qe, "retry_after", None)
            self.quota_exhausted_retry_seconds = getattr(qe, "retry_after_seconds", None)
            logger.error(f"Provider '{primary.provider_name}' daily quota exhausted. No alternative provider configured. Preserving quota limitation without retries.")
            raise qe
        except (LLMNetworkError, LLMTimeoutError, LLMServerError) as e:
            logger.warning(f"Primary provider '{primary.provider_name}' transient error: {e}")
            if self.fallback_enabled and not api_key_override:
                # 1. Fallback to Gemini Lite if primary was Gemini Flash
                if primary.provider_name == "gemini" and "lite" not in (primary.config.model or "").lower():
                    logger.info(f"Primary Gemini model '{primary.config.model}' transient error ({e}). Failing over to validated fallback '{self.gemini_lite_model}'...")
                    try:
                        res = self.gemini_lite_provider.generate_structured(schema=schema, prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(e),
                            "primary_error_type": type(e).__name__,
                            "reason": "transient_service_error_fallback",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as lite_e:
                        logger.warning(f"Gemini Lite fallback also encountered error: {lite_e}")
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(e),
                            "secondary_error": str(lite_e),
                            "primary_error_type": type(e).__name__,
                            "reason": "transient_service_error_fallback",
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                secondary_name = "openai" if primary.provider_name == "gemini" else "gemini"
                secondary = self.get_provider_for_request(provider_name=secondary_name)
                # Ensure secondary provider is actually configured with valid credentials
                if secondary and secondary.config.api_key and secondary.config.api_key != primary.config.api_key:
                    logger.info(f"Failing over to secondary provider '{secondary.provider_name}'...")
                    try:
                        res = secondary.generate_structured(schema=schema, prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(e),
                            "primary_error_type": type(e).__name__,
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as sec_e:
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(e),
                            "secondary_error": str(sec_e),
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        logger.error(f"Secondary fallback provider '{secondary.provider_name}' also failed: {sec_e}")
            self.last_generation_status = "provider_unavailable"
            self.last_generation_error = str(e)
            raise
        except Exception as e:
            self.last_generation_status = "generation_failed"
            self.last_generation_error = str(e)
            raise

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> GenerationResult:
        """
        Executes free-form text generation using the resolved provider, with transparent
        multi-provider fallback.
        """
        primary = self.get_provider_for_request(
            provider_name=provider_override,
            model_name=model_override,
            api_key=api_key_override
        )
        if not primary or not primary.config.api_key:
            raise LLMConfigurationError("No live LLM provider is configured with valid credentials.")

        try:
            res = primary.generate_text(prompt=prompt, system_instruction=system_instruction)
            self.last_generation_status = "live_generation_succeeded"
            self.last_generation_error = None
            self.last_generation_time = time.time()
            self.total_live_generations += 1
            return res
        except LLMQuotaExhaustedError as qe:
            logger.warning(f"Primary provider '{primary.provider_name}' text daily quota exhausted: {qe}")
            if self.fallback_enabled and not api_key_override:
                # 1. Try Gemini Lite fallback if primary was Gemini Flash
                if primary.provider_name == "gemini" and "lite" not in (primary.config.model or "").lower():
                    logger.info(f"Primary Gemini model '{primary.config.model}' text quota exhausted. Failing over to validated fallback '{self.gemini_lite_model}'...")
                    try:
                        res = self.gemini_lite_provider.generate_text(prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(qe),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "model_quota_fallback",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as lite_e:
                        logger.warning(f"Gemini Lite fallback failed: {lite_e}")
                secondary_name = "openai" if primary.provider_name == "gemini" else "gemini"
                secondary = self.get_provider_for_request(provider_name=secondary_name)
                if (
                    secondary
                    and secondary.provider_name != primary.provider_name
                    and secondary.config.api_key
                    and not secondary.config.api_key.startswith("your_")
                    and secondary.config.api_key != primary.config.api_key
                ):
                    try:
                        res = secondary.generate_text(prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(qe),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "quota_exhaustion",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as sec_e:
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(qe),
                            "secondary_error": str(sec_e),
                            "primary_error_type": "LLMQuotaExhaustedError",
                            "reason": "quota_exhaustion",
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        logger.error(f"Secondary text provider '{secondary.provider_name}' failed: {sec_e}")
            self.last_generation_status = "quota_exhausted"
            self.last_generation_error = str(qe)
            self.quota_exhausted_retry_after = getattr(qe, "retry_after", None)
            self.quota_exhausted_retry_seconds = getattr(qe, "retry_after_seconds", None)
            logger.error(f"Provider '{primary.provider_name}' text daily quota exhausted. Preserving quota limitation without retries.")
            raise qe
        except (LLMNetworkError, LLMTimeoutError, LLMServerError) as e:
            logger.warning(f"Primary provider '{primary.provider_name}' text transient error: {e}")
            if self.fallback_enabled and not api_key_override:
                # 1. Fallback to Gemini Lite if primary was Gemini Flash
                if primary.provider_name == "gemini" and "lite" not in (primary.config.model or "").lower():
                    logger.info(f"Primary Gemini model '{primary.config.model}' text transient error ({e}). Failing over to validated fallback '{self.gemini_lite_model}'...")
                    try:
                        res = self.gemini_lite_provider.generate_text(prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": f"gemini ({primary.config.model})",
                            "to_provider": f"gemini ({self.gemini_lite_model})",
                            "primary_error": str(e),
                            "primary_error_type": type(e).__name__,
                            "reason": "transient_service_error_fallback",
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as lite_e:
                        logger.warning(f"Gemini Lite fallback failed: {lite_e}")
                secondary_name = "openai" if primary.provider_name == "gemini" else "gemini"
                secondary = self.get_provider_for_request(provider_name=secondary_name)
                if secondary and secondary.config.api_key and secondary.config.api_key != primary.config.api_key:
                    try:
                        res = secondary.generate_text(prompt=prompt, system_instruction=system_instruction)
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(e),
                            "primary_error_type": type(e).__name__,
                            "timestamp": time.time(),
                            "succeeded": True
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        self.last_generation_status = "live_generation_succeeded"
                        self.last_generation_error = None
                        self.last_generation_time = time.time()
                        self.total_live_generations += 1
                        return res
                    except Exception as sec_e:
                        failover_record = {
                            "from_provider": primary.provider_name,
                            "to_provider": secondary.provider_name,
                            "primary_error": str(e),
                            "secondary_error": str(sec_e),
                            "timestamp": time.time(),
                            "succeeded": False
                        }
                        self.last_failover_event = failover_record
                        self.failover_history.append(failover_record)
                        logger.error(f"Secondary text provider '{secondary.provider_name}' failed: {sec_e}")
            self.last_generation_status = "provider_unavailable"
            self.last_generation_error = str(e)
            raise
        except Exception as e:
            self.last_generation_status = "generation_failed"
            self.last_generation_error = str(e)
            raise

    def create_provenance_record(
        self,
        mode: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        stages: Optional[Dict[str, str]] = None,
        failover_occurred: bool = False,
        original_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Constructs normalized, verifiable stage-level generation provenance."""
        st = stages or {}
        t_src = st.get("topic_interpretation_source", mode)
        c_src = st.get("concept_generation_source", mode)
        d_src = st.get("dag_generation_source", c_src)
        q_src = st.get("question_generation_source", mode)
        p_src = st.get("probe_generation_source", mode)
        r_src = st.get("remedial_generation_source", mode)

        all_sources = [t_src, c_src, d_src, q_src, p_src, r_src]
        has_live = any("live_llm" in str(s) for s in all_sources)
        has_offline = any(s in ("offline_synthesizer", "offline_knowledge_synthesis", "deterministic_dag_engine", "deterministic_taxonomy_engine") for s in all_sources)
        has_curated = any("curated" in str(s) for s in all_sources)

        if has_live and not has_offline and not has_curated:
            computed_mode = "live_llm"
        elif has_live and (has_offline or has_curated):
            computed_mode = "hybrid"
        elif has_curated and not has_live:
            computed_mode = "curated_retrieval"
        else:
            computed_mode = "offline_knowledge_synthesis"

        prov_label = "Offline-generated"
        if has_live:
            if model and "lite" in model.lower():
                prov_label = "Lite-generated"
            elif provider and "gemini" in provider.lower():
                prov_label = "Gemini-generated"
            else:
                prov_label = f"{provider.capitalize()}-generated" if provider else "Live-generated"

        return {
            "overall_mode": mode if mode in ("live_llm", "offline_knowledge_synthesis", "hybrid") else computed_mode,
            "provider": provider,
            "model": model,
            "provenance_label": prov_label,
            "topic_interpretation_source": t_src,
            "concept_generation_source": c_src,
            "dag_generation_source": d_src,
            "question_generation_source": q_src,
            "probe_generation_source": p_src,
            "remedial_generation_source": r_src,
            "failover_occurred": failover_occurred or bool(self.last_failover_event and self.last_failover_event.get("succeeded")),
            "original_provider": original_provider or (self.last_failover_event.get("from_provider") if self.last_failover_event else None),
            "timestamp": time.time()
        }

    def get_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Reports comprehensive provider status distinguishing configured,
        reachable, and active generation mode across the 7 distinct states:
        - not_configured
        - configured
        - reachable
        - live_generation_succeeded
        - provider_unavailable
        - generation_failed
        - offline_knowledge_synthesis
        """
        gemini_health = self.gemini_provider.check_connection(force_refresh=force_refresh)
        openai_health = self.openai_provider.check_connection(force_refresh=force_refresh)

        active = self.get_active_provider()
        has_any_configured = bool(
            (self.gemini_config.api_key and not self.gemini_config.api_key.startswith("your_")) or
            (self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"))
        )

        live_ready = False
        active_provider_name = None
        active_model = None
        active_health = None

        if active:
            active_provider_name = active.provider_name
            active_model = active.config.model
            if active_provider_name == "gemini":
                active_health = self.gemini_lite_provider.check_connection(force_refresh=force_refresh) if active_model == self.gemini_lite_model else gemini_health
            else:
                active_health = openai_health
            live_ready = active_health.reachable

        # Compute 8-state taxonomy
        if not has_any_configured:
            provider_state = "not_configured"
        elif self.last_generation_status == "quota_exhausted" or (active_health and (active_health.last_status == "quota_exhausted" or active_health.error_category == "quota_exhausted")):
            provider_state = "quota_exhausted"
        elif self.last_generation_status == "live_generation_succeeded":
            provider_state = "live_generation_succeeded"
        elif self.last_generation_status == "provider_unavailable":
            provider_state = "provider_unavailable"
        elif self.last_generation_status == "generation_failed":
            provider_state = "generation_failed"
        elif live_ready:
            provider_state = "reachable"
        else:
            provider_state = "configured"

        # Active operational mode
        if provider_state in ("reachable", "live_generation_succeeded"):
            active_mode = "live_llm"
        else:
            active_mode = "offline_knowledge_synthesis"

        if provider_state == "quota_exhausted":
            retry_str = self.quota_exhausted_retry_after or (active_health.retry_after if active_health else None)
            if retry_str:
                msg = f"Live cloud LLM provider '{active_provider_name}' Free Tier daily quota is exhausted. Retry available in {retry_str}. You can configure an alternate provider (OpenAI) or use offline knowledge synthesis."
            else:
                msg = f"Live cloud LLM provider '{active_provider_name}' daily request quota is exhausted. You can configure an alternate provider (OpenAI) or use offline knowledge synthesis."
        elif provider_state == "live_generation_succeeded":
            msg = f"Live cloud LLM provider '{active_provider_name}' ({active_model}) is active, verified, and generation succeeded."
        elif provider_state == "reachable":
            msg = f"Live cloud LLM provider '{active_provider_name}' ({active_model}) is active and verified reachable."
        elif provider_state == "configured":
            msg = f"Provider '{active_provider_name}' configured but network reachability unverified; fallback to offline knowledge synthesis enabled."
        elif provider_state == "provider_unavailable":
            msg = f"Provider '{active_provider_name}' currently unavailable ({self.last_generation_error or 'network error'}); operating in authentic offline mode."
        elif provider_state == "generation_failed":
            msg = f"Live generation failed ({self.last_generation_error or 'error'}); fallen back to authentic offline knowledge synthesis."
        else:
            msg = "No cloud LLM API keys configured in .env. DeepLearnX is operating in authentic offline knowledge synthesis mode."

        return {
            "active_mode": active_mode,
            "provider_state": provider_state,
            "live_llm_ready": live_ready or (provider_state == "live_generation_succeeded"),
            "selected_provider": active_provider_name or "offline_synthesizer",
            "model": active_model or "deterministic_taxonomy_engine",
            "offline_ready": True,
            "fallback_enabled": self.fallback_enabled,
            "message": msg,
            "quota_exhausted": (provider_state == "quota_exhausted"),
            "retry_after": self.quota_exhausted_retry_after or (active_health.retry_after if active_health else None),
            "retry_after_seconds": self.quota_exhausted_retry_seconds or (active_health.retry_after_seconds if active_health else None),
            "last_generation_status": self.last_generation_status,
            "last_generation_error": self.last_generation_error,
            "last_failover_event": self.last_failover_event,
            "total_live_generations": self.total_live_generations,
            "providers": {
                "gemini": gemini_health.to_dict(),
                "openai": openai_health.to_dict()
            }
        }


# Global singleton instance
_provider_manager: Optional[LLMProviderManager] = None


def get_provider_manager() -> LLMProviderManager:
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = LLMProviderManager()
    return _provider_manager


# Synchronize module aliases across import styles
import sys
for _mod_alias in ("backend.app.providers.manager", "app.providers.manager", "providers.manager"):
    sys.modules[_mod_alias] = sys.modules[__name__]


