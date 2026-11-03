"""
Unit Tests for DeepLearnX Gemini Rate Limiter, Model Selection, and Fallback Infrastructure.
Verifies:
1. gemini-3.8-flash is configured as primary.
2. gemini-3.6-flash and gemini-3.5-flash are removed from automatic selection.
3. gemini-3.5-flash-lite is configured as high-headroom fallback.
4. RequestLimiter serializes calls and throttles to <= 3 RPM.
5. Circuit breaker halts retries when daily quota is exhausted.
6. Topic research and interpretation caching eliminates redundant calls.
7. Accurate provider provenance reporting across Gemini, Lite, and Offline.
"""

import os
import sys
import time
import json
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.providers.base import (
    LLMConfig,
    GenerationResult,
    LLMQuotaExhaustedError,
    LLMRateLimitError,
    LLMServerError
)
from backend.app.providers.rate_limiter import GeminiRequestLimiter, get_request_limiter
from backend.app.providers.gemini_provider import GeminiProvider
from backend.app.providers.manager import LLMProviderManager, get_provider_manager
from backend.app.topic_cache import TopicResearchCache, get_topic_cache


class TestGeminiRateLimiter(unittest.TestCase):
    """Verifies concurrency serialization, RPM throttling, and quota circuit breaker."""

    def setUp(self):
        self.limiter = GeminiRequestLimiter()
        self.limiter.reset_for_tests()

    def tearDown(self):
        self.limiter.reset_for_tests()

    def test_primary_model_rpm_limit(self):
        """Verifies gemini-3.8-flash is capped at <= 3 requests per minute."""
        cfg = self.limiter._get_config("gemini-3.8-flash")
        self.assertEqual(cfg.max_rpm, 3)
        self.assertEqual(cfg.min_interval_seconds, 20.0)

    def test_lite_model_rpm_limit(self):
        """Verifies gemini-3.5-flash-lite has higher RPM allowance."""
        cfg = self.limiter._get_config("gemini-3.5-flash-lite")
        self.assertEqual(cfg.max_rpm, 10)
        self.assertEqual(cfg.min_interval_seconds, 6.0)

    @patch("time.sleep")
    def test_acquire_throttles_rapid_requests(self, mock_sleep):
        """Verifies rapid acquire calls trigger throttling sleep."""
        # First request should proceed immediately
        self.limiter.acquire("gemini-3.8-flash")
        self.assertEqual(len(self.limiter._get_config("gemini-3.8-flash").timestamps), 1)

        # Second rapid request should trigger sleep
        self.limiter.acquire("gemini-3.8-flash")
        mock_sleep.assert_called()
        self.assertEqual(len(self.limiter._get_config("gemini-3.8-flash").timestamps), 2)

    def test_daily_quota_circuit_breaker_trips(self):
        """Verifies recording daily quota trips circuit breaker and raises immediately."""
        self.limiter.record_retry_after("gemini-3.8-flash", retry_after_seconds=3600.0, is_daily_quota=True)
        self.assertFalse(self.limiter.is_model_available("gemini-3.8-flash"))

        # acquire should immediately raise LLMQuotaExhaustedError without retrying
        with self.assertRaises(LLMQuotaExhaustedError) as ctx:
            self.limiter.acquire("gemini-3.8-flash")
        self.assertIn("exhausted", str(ctx.exception).lower())

    def test_retry_after_backoff_respected(self):
        """Verifies retry-after backoff blocks subsequent calls if wait is too long."""
        self.limiter.record_retry_after("gemini-3.8-flash", retry_after_seconds=120.0, is_daily_quota=False)
        self.assertFalse(self.limiter.is_model_available("gemini-3.8-flash"))

        with self.assertRaises(LLMRateLimitError):
            self.limiter.acquire("gemini-3.8-flash", wait_timeout=30.0)


class TestModelSelectionAndSanitization(unittest.TestCase):
    """Verifies gemini-3.8-flash is primary and gemini-3.6/3.5 are disallowed."""

    def test_disallowed_models_remapped_in_provider(self):
        """Verifies gemini-3.6-flash and gemini-3.5-flash are remapped to gemini-3.8-flash."""
        p1 = GeminiProvider(LLMConfig(provider="gemini", model="gemini-3.6-flash"))
        self.assertEqual(p1.config.model, "gemini-3.8-flash")

        p2 = GeminiProvider(LLMConfig(provider="gemini", model="gemini-3.5-flash"))
        self.assertEqual(p2.config.model, "gemini-3.8-flash")

        p3 = GeminiProvider(LLMConfig(provider="gemini", model="gemini-1.5-flash"))
        self.assertEqual(p3.config.model, "gemini-3.8-flash")

    def test_disallowed_models_remapped_in_manager(self):
        """Verifies manager __init__ disallows gemini-3.6-flash."""
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.6-flash"}):
            mgr = LLMProviderManager()
            self.assertEqual(mgr.gemini_config.model, "gemini-3.8-flash")
            self.assertEqual(mgr.gemini_lite_model, "gemini-3.5-flash-lite")

    def test_primary_and_fallback_models_configured(self):
        """Verifies manager maintains primary 3.8 and fallback 3.5-flash-lite."""
        mgr = LLMProviderManager()
        self.assertEqual(mgr.gemini_config.model, "gemini-3.8-flash")
        self.assertEqual(mgr.gemini_lite_config.model, "gemini-3.5-flash-lite")


class TestGeminiFlashToLiteFallback(unittest.TestCase):
    """Verifies failover from gemini-3.8-flash to gemini-3.5-flash-lite on quota exhaustion."""

    def setUp(self):
        self.mgr = LLMProviderManager()
        self.mgr.gemini_config.api_key = "AIzaSyMockKey123"
        self.mgr.gemini_lite_config.api_key = "AIzaSyMockKey123"

    @patch("backend.app.providers.gemini_provider.get_request_limiter")
    def test_quota_exhausted_fails_over_to_lite(self, mock_limiter):
        """Verifies 3.8 Flash quota exhaustion falls over to 3.5 Flash Lite successfully."""
        mock_lite_res = GenerationResult(
            provider="gemini",
            model="gemini-3.5-flash-lite",
            content={"test": "lite_success"},
            generation_mode="live_llm"
        )

        quota_err = LLMQuotaExhaustedError("Daily quota exhausted for gemini-3.8-flash", provider="gemini")

        with patch.object(self.mgr.gemini_provider, "generate_structured", side_effect=quota_err):
            with patch.object(self.mgr.gemini_lite_provider, "generate_structured", return_value=mock_lite_res) as mock_lite_call:
                res = self.mgr.generate_structured(schema={}, prompt="Test Fallback Prompt")
                mock_lite_call.assert_called_once()
                self.assertEqual(res.model, "gemini-3.5-flash-lite")
                self.assertEqual(res.content["test"], "lite_success")
                self.assertIsNotNone(self.mgr.last_failover_event)
                self.assertIn("gemini-3.8-flash", self.mgr.last_failover_event["from_provider"])
                self.assertIn("gemini-3.5-flash-lite", self.mgr.last_failover_event["to_provider"])
                self.assertTrue(self.mgr.last_failover_event["succeeded"])


class TestTopicCache(unittest.TestCase):
    """Verifies topic research and concept extraction caching."""

    def setUp(self):
        self.cache = TopicResearchCache()
        self.cache.clear()

    def test_research_cache_hit(self):
        sample_data = {
            "articles": [{"title": "Photosynthesis", "extract": "Light energy converted to chemical energy."}],
            "extracted_facts": ["Thylakoid membranes contain chlorophyll."]
        }
        self.cache.set_research("Photosynthesis", sample_data)

        # Hit
        retrieved = self.cache.get_research("Photosynthesis")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["articles"][0]["title"], "Photosynthesis")
        self.assertEqual(self.cache._hits, 1)

        # Case-insensitive hit
        retrieved2 = self.cache.get_research("photosynthesis  ")
        self.assertIsNotNone(retrieved2)
        self.assertEqual(self.cache._hits, 2)

    def test_interpretation_cache_hit(self):
        interp = {
            "canonical_title": "Game Design",
            "discipline": "Game Technology",
            "scope": "MDA framework and mechanics."
        }
        self.cache.set_interpretation("Game Design", "", interp)
        hit = self.cache.get_interpretation("game design")
        self.assertIsNotNone(hit)
        self.assertEqual(hit["canonical_title"], "Game Design")
        self.assertEqual(self.cache._hits, 1)


class TestProvenanceLabels(unittest.TestCase):
    """Verifies accurate provenance labels for Gemini, Lite, and Offline."""

    def setUp(self):
        self.mgr = LLMProviderManager()

    def test_gemini_flash_provenance(self):
        prov = self.mgr.create_provenance_record(
            mode="live_llm",
            provider="gemini",
            model="gemini-3.8-flash"
        )
        self.assertEqual(prov["provenance_label"], "Gemini-generated")
        self.assertEqual(prov["model"], "gemini-3.8-flash")

    def test_gemini_lite_provenance(self):
        prov = self.mgr.create_provenance_record(
            mode="live_llm",
            provider="gemini",
            model="gemini-3.5-flash-lite"
        )
        self.assertEqual(prov["provenance_label"], "Lite-generated")
        self.assertEqual(prov["model"], "gemini-3.5-flash-lite")

    def test_offline_provenance(self):
        prov = self.mgr.create_provenance_record(
            mode="offline_knowledge_synthesis",
            provider=None,
            model=None
        )
        self.assertEqual(prov["provenance_label"], "Offline-generated")


if __name__ == "__main__":
    unittest.main()
