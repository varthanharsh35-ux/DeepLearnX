"""
Unit Tests for DeepLearnX LLM Provider Infrastructure & Error Normalization.
Verifies provider contracts, structured schemas, bounded retries, and honest fallback reporting.
"""

import os
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import json
import time

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.providers.base import (
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
    LLMSafetyRefusalError,
    LLMTruncationError,
    LLMFormatError
)
from backend.app.providers.gemini_provider import GeminiProvider
from backend.app.providers.openai_provider import OpenAIProvider
from backend.app.providers.manager import LLMProviderManager


class TestProviderConfiguration(unittest.TestCase):
    """Verifies safe configuration handling and key masking."""

    def test_key_masking(self):
        cfg_unset = LLMConfig(provider="gemini", api_key=None)
        self.assertEqual(cfg_unset.mask_api_key(), "UNSET")

        cfg_short = LLMConfig(provider="gemini", api_key="secret")
        self.assertEqual(cfg_short.mask_api_key(), "***")

        cfg_valid = LLMConfig(provider="gemini", api_key="AIzaSyA1234567890abcdef")
        masked = cfg_valid.mask_api_key()
        self.assertTrue(masked.startswith("AIza...cdef"))
        self.assertNotIn("1234567890", masked)


class TestGeminiProviderMocked(unittest.TestCase):
    """Verifies GeminiProvider under mocked network conditions."""

    def setUp(self):
        self.config = LLMConfig(
            provider="gemini",
            api_key="mock_test_key_gemini",
            model="gemini-1.5-flash",
            max_retries=2,
            request_timeout=5.0
        )
        self.provider = GeminiProvider(self.config)

    def test_missing_credentials_health(self):
        empty_cfg = LLMConfig(provider="gemini", api_key="")
        p = GeminiProvider(empty_cfg)
        health = p.check_connection(force_refresh=True)
        self.assertFalse(health.configured)
        self.assertFalse(health.reachable)
        self.assertEqual(health.last_status, "missing_credentials")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_successful_structured_generation(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        mock_response = MagicMock()
        mock_response.text = json.dumps({"test_field": "deeplearnx_success"})
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_response.usage_metadata.prompt_token_count = 120
        mock_response.usage_metadata.candidates_token_count = 45
        mock_client.models.generate_content.return_value = mock_response

        res = self.provider.generate_structured(schema={}, prompt="Generate test curriculum")
        self.assertIsInstance(res, GenerationResult)
        self.assertEqual(res.provider, "gemini")
        self.assertEqual(res.generation_mode, "live_llm")
        self.assertEqual(res.content.get("test_field"), "deeplearnx_success")
        self.assertEqual(res.input_tokens, 120)
        self.assertEqual(res.output_tokens, 45)

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_safety_refusal(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.candidates = [MagicMock(finish_reason="SAFETY")]
        mock_client.models.generate_content.return_value = mock_response

        with self.assertRaises(LLMSafetyRefusalError):
            self.provider.generate_structured(schema={}, prompt="Hazardous prompt")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_rate_limit_backoff(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        # First call raises rate limit (429), second succeeds
        from google.genai import errors
        api_err = errors.APIError(code=429, response_json={"error": {"message": "Rate limit exceeded"}}, response=MagicMock())

        mock_success = MagicMock()
        mock_success.text = json.dumps({"status": "recovered"})
        mock_success.candidates = [MagicMock(finish_reason="STOP")]
        mock_success.usage_metadata = None

        mock_client.models.generate_content.side_effect = [api_err, mock_success]

        with patch("time.sleep", return_value=None):
            res = self.provider.generate_structured(schema={}, prompt="Rate limited prompt")
        self.assertEqual(res.content.get("status"), "recovered")
        self.assertEqual(mock_client.models.generate_content.call_count, 2)

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_auth_rejection_no_retry(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        from google.genai import errors
        api_err = errors.APIError(code=401, response_json={"error": {"message": "API_KEY_INVALID"}}, response=MagicMock())
        mock_client.models.generate_content.side_effect = api_err

        with self.assertRaises(LLMAuthenticationError):
            self.provider.generate_structured(schema={}, prompt="Auth test")
        # Ensure authentication error is NOT retried
        self.assertEqual(mock_client.models.generate_content.call_count, 1)


class TestOpenAIProviderMocked(unittest.TestCase):
    """Verifies OpenAIProvider under mocked network conditions."""

    def setUp(self):
        self.config = LLMConfig(
            provider="openai",
            api_key="mock_test_key_openai",
            model="gpt-4o-mini",
            max_retries=2,
            request_timeout=5.0
        )
        self.provider = OpenAIProvider(self.config)

    @patch("backend.app.providers.openai_provider.OPENAI_AVAILABLE", True)
    @patch("backend.app.providers.openai_provider.OpenAI")
    def test_openai_successful_structured_generation(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        self.provider._client = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({"discipline": "Physics", "concepts": 4})
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 90
        mock_response.usage.completion_tokens = 40
        mock_response.id = "req-123"
        mock_client.chat.completions.create.return_value = mock_response

        res = self.provider.generate_structured(schema={}, prompt="Test curriculum")
        self.assertEqual(res.provider, "openai")
        self.assertEqual(res.generation_mode, "live_llm")
        self.assertEqual(res.content.get("discipline"), "Physics")
        self.assertEqual(res.input_tokens, 90)

    @patch("backend.app.providers.openai_provider.OPENAI_AVAILABLE", True)
    @patch("backend.app.providers.openai_provider.OpenAI")
    def test_openai_safety_filter(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        self.provider._client = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = ""
        mock_choice.finish_reason = "content_filter"
        mock_response = MagicMock(choices=[mock_choice])
        mock_client.chat.completions.create.return_value = mock_response

        with self.assertRaises(LLMSafetyRefusalError):
            self.provider.generate_structured(schema={}, prompt="Hazardous prompt")


class TestProviderManager(unittest.TestCase):
    """Verifies provider manager orchestration and readiness reporting."""

    def test_offline_mode_when_unconfigured(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "", "OPENAI_API_KEY": ""}, clear=True):
            mgr = LLMProviderManager()
            status = mgr.get_status(force_refresh=True)
            self.assertEqual(status["active_mode"], "offline_knowledge_synthesis")
            self.assertFalse(status["live_llm_ready"])
            self.assertTrue(status["offline_ready"])
            self.assertIn("offline", status["message"].lower())


if __name__ == "__main__":
    unittest.main()
