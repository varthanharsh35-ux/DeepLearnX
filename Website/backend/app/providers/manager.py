"""
DeepLearnX LLM Provider Manager & Dispatcher.

Orchestrates provider selection, configuration discovery, transparent readiness reporting,
and strict, verifiable mode reporting (distinguishing 'live_llm' from 'offline_knowledge_synthesis').
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple, Union, Type
from pydantic import BaseModel

from .base import (
    BaseLLMProvider,
    LLMConfig,
    GenerationResult,
    ProviderHealth,
    LLMConfigurationError,
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
        gemini_model = os.environ.get("GEMINI_MODEL") or os.environ.get("GEMINI_DEFAULT_MODEL") or "gemini-1.5-flash"
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

    def reload_config(self) -> None:
        """Reloads configuration from os.environ."""
        self.__init__()

    def get_active_provider(self) -> Optional[BaseLLMProvider]:
        """Returns the configured and prioritized provider, or None if no keys exist."""
        pref = self.provider_pref
        if pref == "gemini":
            if self.gemini_config.api_key and not self.gemini_config.api_key.startswith("your_"):
                return self.gemini_provider
            return None
        elif pref == "openai":
            if self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"):
                return self.openai_provider
            return None
        else:  # 'auto'
            if self.gemini_config.api_key and not self.gemini_config.api_key.startswith("your_"):
                return self.gemini_provider
            if self.openai_config.api_key and not self.openai_config.api_key.startswith("your_"):
                return self.openai_provider
            return None

    def get_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Reports comprehensive provider status distinguishing configured,
        reachable, and active generation mode without making expensive generation calls.
        """
        gemini_health = self.gemini_provider.check_connection(force_refresh=force_refresh)
        openai_health = self.openai_provider.check_connection(force_refresh=force_refresh)

        active = self.get_active_provider()
        live_ready = False
        active_provider_name = None
        active_model = None

        if active:
            active_provider_name = active.provider_name
            active_model = active.config.model
            active_health = gemini_health if active_provider_name == "gemini" else openai_health
            live_ready = active_health.reachable

        active_mode = "live_llm" if live_ready else "offline_knowledge_synthesis"

        if live_ready:
            msg = f"Live cloud LLM provider '{active_provider_name}' ({active_model}) is active and verified."
        elif active_provider_name:
            msg = f"Provider '{active_provider_name}' configured but not reachable; fallback to offline knowledge synthesis enabled."
        else:
            msg = "No cloud LLM API keys configured in .env. DeepLearnX is operating in authentic offline knowledge synthesis mode."

        return {
            "active_mode": active_mode,
            "live_llm_ready": live_ready,
            "selected_provider": active_provider_name or "offline_synthesizer",
            "model": active_model or "deterministic_taxonomy_engine",
            "offline_ready": True,
            "fallback_enabled": self.fallback_enabled,
            "message": msg,
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
