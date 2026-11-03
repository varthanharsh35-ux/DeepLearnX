"""
DeepLearnX Project-Wide LLM Rate Limiter & Concurrency Serializer.

Enforces:
1. Strict request serialization: no concurrent LLM calls to Gemini.
2. Model-specific rate limiting:
   - gemini-3.8-flash: <= 3 requests per minute (minimum 20s interval).
   - gemini-3.5-flash-lite: <= 10 requests per minute (minimum 6s interval).
3. Dynamic retry-after backoff tracking.
4. Circuit breaker that stops useless retry loops when daily quota is exhausted.
"""

import time
import json
import threading
import logging
from typing import Dict, Any, Optional, List
from collections import deque

logger = logging.getLogger("deeplearnx.providers.rate_limiter")


class ModelRateLimitConfig:
    """Rate limit configuration for a specific model."""
    def __init__(self, model_name: str, max_rpm: int = 3, min_interval_seconds: float = 20.0):
        self.model_name = model_name
        self.max_rpm = max_rpm
        self.min_interval_seconds = min_interval_seconds
        self.timestamps: deque = deque()
        self.blocked_until: float = 0.0
        self.daily_quota_exhausted: bool = False
        self.daily_quota_reset_time: float = 0.0
        self.last_request_time: float = 0.0


class GeminiRequestLimiter:
    """Project-wide thread-safe rate limiter and serializer for Gemini API calls."""

    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._lock = threading.RLock()
        self._model_configs: Dict[str, ModelRateLimitConfig] = {
            "gemini-3.8-flash": ModelRateLimitConfig("gemini-3.8-flash", max_rpm=3, min_interval_seconds=20.0),
            "gemini-3.5-flash-lite": ModelRateLimitConfig("gemini-3.5-flash-lite", max_rpm=10, min_interval_seconds=6.0),
            "gemini-flash-latest": ModelRateLimitConfig("gemini-flash-latest", max_rpm=3, min_interval_seconds=20.0),
        }
        # Fallback default for unlisted models
        self._default_config = ModelRateLimitConfig("default", max_rpm=3, min_interval_seconds=20.0)
        self._total_requests_served = 0
        self._total_delays_applied = 0.0
        
        # Persistent quota tracking
        from pathlib import Path
        self._state_file = Path(__file__).resolve().parents[3] / "database" / ".gemini_quota_state.json"
        self._load_quota_state()
        
        self._initialized = True

    def _load_quota_state(self) -> None:
        """Loads persistent quota exhaustion state from disk if active."""
        try:
            if self._state_file and self._state_file.exists():
                with open(self._state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                now = time.time()
                for model_name, info in data.items():
                    cfg = self._get_config(model_name)
                    reset_time = float(info.get("daily_quota_reset_time", 0.0))
                    if reset_time > now:
                        cfg.daily_quota_exhausted = True
                        cfg.daily_quota_reset_time = reset_time
                        cfg.blocked_until = max(cfg.blocked_until, reset_time)
                        logger.info(
                            f"[RateLimiter] Persistent daily quota block loaded for '{cfg.model_name}' until "
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset_time))}."
                        )
        except Exception as e:
            logger.debug(f"[RateLimiter] Failed loading quota state: {e}")

    def _save_quota_state(self) -> None:
        """Persists active daily quota exhaustion state to disk."""
        try:
            now = time.time()
            data = {}
            for k, cfg in self._model_configs.items():
                if cfg.daily_quota_exhausted and cfg.daily_quota_reset_time > now:
                    data[k] = {
                        "daily_quota_exhausted": True,
                        "daily_quota_reset_time": cfg.daily_quota_reset_time,
                        "retry_after_seconds": max(0.0, cfg.daily_quota_reset_time - now),
                        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }
            if self._state_file:
                self._state_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self._state_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.debug(f"[RateLimiter] Failed saving quota state: {e}")

    def _get_config(self, model_name: str) -> ModelRateLimitConfig:
        clean = (model_name or "").lower().replace("models/", "")
        for k, cfg in self._model_configs.items():
            if k in clean:
                return cfg
        return self._default_config

    def acquire(self, model_name: str, wait_timeout: float = 60.0) -> None:
        """
        Serializes and rate-limits outbound API calls with strict thread locking.
        Sleeps if necessary to stay within the RPM and minimum interval limits.
        Raises RuntimeError if daily quota is known to be exhausted.
        """
        with self._lock:
            cfg = self._get_config(model_name)
            now = time.time()

            # Check circuit breaker for daily quota exhaustion
            if cfg.daily_quota_exhausted:
                if now < cfg.daily_quota_reset_time:
                    rem = cfg.daily_quota_reset_time - now
                    logger.warning(f"[RateLimiter] Model '{cfg.model_name}' daily quota exhausted. Blocked for {rem:.0f}s more.")
                    from .base import LLMQuotaExhaustedError
                    raise LLMQuotaExhaustedError(
                        f"Daily quota for model '{cfg.model_name}' is currently exhausted. Retry after reset.",
                        provider="gemini",
                        status_code=429,
                        retry_after_seconds=rem
                    )
                else:
                    # Quota window has elapsed, reset
                    cfg.daily_quota_exhausted = False
                    cfg.daily_quota_reset_time = 0.0

            # Check active retry-after block
            if now < cfg.blocked_until:
                wait_needed = cfg.blocked_until - now
                if wait_needed > wait_timeout:
                    from .base import LLMRateLimitError
                    raise LLMRateLimitError(
                        f"Model '{cfg.model_name}' is rate limited. Retry required in {wait_needed:.1f}s.",
                        provider="gemini",
                        status_code=429,
                        retry_after_seconds=wait_needed
                    )
                logger.info(f"[RateLimiter] Respecting retry-after for '{cfg.model_name}': waiting {wait_needed:.2f}s...")
                time.sleep(wait_needed)
                now = time.time()

            # Enforce minimum interval spacing and RPM sliding window
            sleep_time = 0.0
            time_since_last = now - cfg.last_request_time
            if time_since_last < cfg.min_interval_seconds:
                sleep_time = max(sleep_time, cfg.min_interval_seconds - time_since_last)

            # Clean timestamps older than 60s
            while cfg.timestamps and (now - cfg.timestamps[0]) > 60.0:
                cfg.timestamps.popleft()

            # If at max RPM, sleep until oldest timestamp clears 60s
            if len(cfg.timestamps) >= cfg.max_rpm:
                oldest = cfg.timestamps[0]
                needed_window_wait = 60.0 - (now - oldest) + 0.1
                if needed_window_wait > 0:
                    sleep_time = max(sleep_time, needed_window_wait)

            if sleep_time > 0:
                logger.info(f"[RateLimiter] Throttling '{cfg.model_name}' by {sleep_time:.2f}s to maintain <= {cfg.max_rpm} RPM...")
                time.sleep(sleep_time)
                self._total_delays_applied += sleep_time

            # Record this request
            actual_req_time = time.time()
            cfg.last_request_time = actual_req_time
            cfg.timestamps.append(actual_req_time)
            self._total_requests_served += 1

    async def acquire_async(self, model_name: str, wait_timeout: float = 60.0) -> None:
        """Async-friendly wrapper for acquire that offloads waiting to a thread pool."""
        import asyncio
        await asyncio.to_thread(self.acquire, model_name, wait_timeout)

    def record_retry_after(self, model_name: str, retry_after_seconds: float, is_daily_quota: bool = False) -> None:
        """Records a 429 backoff or daily quota exhaustion event."""
        with self._lock:
            cfg = self._get_config(model_name)
            now = time.time()
            secs = max(1.0, float(retry_after_seconds))
            cfg.blocked_until = now + secs

            if is_daily_quota or secs > 180:
                cfg.daily_quota_exhausted = True
                cfg.daily_quota_reset_time = now + secs
                self._save_quota_state()
                logger.warning(
                    f"[RateLimiter] Daily quota circuit breaker TRIPPED for '{cfg.model_name}'. "
                    f"Blocked until {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cfg.daily_quota_reset_time))} ({secs:.0f}s)."
                )
            else:
                logger.info(f"[RateLimiter] Backoff registered for '{cfg.model_name}': {secs:.1f}s.")

    def is_model_available(self, model_name: str) -> bool:
        """Checks if a model is currently unblocked and not quota-exhausted."""
        with self._lock:
            cfg = self._get_config(model_name)
            now = time.time()
            if cfg.daily_quota_exhausted and now < cfg.daily_quota_reset_time:
                return False
            if now < cfg.blocked_until:
                return False
            return True

    def reset_for_tests(self) -> None:
        """Resets all rate limit state (for unit tests)."""
        with self._lock:
            for cfg in self._model_configs.values():
                cfg.timestamps.clear()
                cfg.blocked_until = 0.0
                cfg.daily_quota_exhausted = False
                cfg.daily_quota_reset_time = 0.0
                cfg.last_request_time = 0.0
            self._default_config.timestamps.clear()
            self._default_config.blocked_until = 0.0
            self._default_config.daily_quota_exhausted = False
            self._default_config.daily_quota_reset_time = 0.0
            self._default_config.last_request_time = 0.0


# Global singleton access
_global_limiter: Optional[GeminiRequestLimiter] = None

def get_request_limiter() -> GeminiRequestLimiter:
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = GeminiRequestLimiter()
    return _global_limiter
