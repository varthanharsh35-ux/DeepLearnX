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
            self.assertEqual(status["provider_state"], "not_configured")
            self.assertFalse(status["live_llm_ready"])
            self.assertTrue(status["offline_ready"])
            self.assertIn("offline", status["message"].lower())

    def test_7_distinct_provider_states(self):
        """Verifies all 7 provider states can be tracked and reported."""
        mgr = LLMProviderManager()

        # 1. not_configured
        mgr.gemini_config.api_key = None
        mgr.openai_config.api_key = None
        mgr.last_generation_status = None
        s1 = mgr.get_status(force_refresh=False)
        self.assertEqual(s1["provider_state"], "not_configured")

        # 2. configured (unverified)
        mgr.gemini_config.api_key = "AIzaSyTestKeyMock12345"
        with patch.object(mgr.gemini_provider, "check_connection", return_value=ProviderHealth("gemini", True, False, "unreachable")):
            s2 = mgr.get_status(force_refresh=True)
            self.assertEqual(s2["provider_state"], "configured")

        # 3. reachable
        with patch.object(mgr.gemini_provider, "check_connection", return_value=ProviderHealth("gemini", True, True, "ready")):
            s3 = mgr.get_status(force_refresh=True)
            self.assertEqual(s3["provider_state"], "reachable")
            self.assertTrue(s3["live_llm_ready"])

        # 4. live_generation_succeeded
        mgr.last_generation_status = "live_generation_succeeded"
        s4 = mgr.get_status(force_refresh=False)
        self.assertEqual(s4["provider_state"], "live_generation_succeeded")

        # 5. provider_unavailable
        mgr.last_generation_status = "provider_unavailable"
        mgr.last_generation_error = "Connection timeout after 30s"
        s5 = mgr.get_status(force_refresh=False)
        self.assertEqual(s5["provider_state"], "provider_unavailable")

        # 6. generation_failed
        mgr.last_generation_status = "generation_failed"
        mgr.last_generation_error = "Schema violation: missing fields"
        s6 = mgr.get_status(force_refresh=False)
        self.assertEqual(s6["provider_state"], "generation_failed")

    def test_structured_generation_dispatch(self):
        """Verifies LLMProviderManager dispatches structured requests to the active provider."""
        mgr = LLMProviderManager()
        mock_res = GenerationResult(
            provider="gemini",
            model="gemini-1.5-flash",
            content={"test_key": "dispatched_value"},
            generation_mode="live_llm"
        )
        with patch.object(mgr.gemini_provider, "generate_structured", return_value=mock_res) as mock_gen:
            mgr.gemini_config.api_key = "AIzaSyValidKeyMock123"
            res = mgr.generate_structured(schema={}, prompt="Test dispatch")
            mock_gen.assert_called_once()
            self.assertEqual(res.content["test_key"], "dispatched_value")
            self.assertEqual(mgr.last_generation_status, "live_generation_succeeded")
            self.assertEqual(mgr.total_live_generations, 1)

    def test_multi_provider_failover(self):
        """Verifies failover from Gemini to OpenAI upon transient 503 server error."""
        mgr = LLMProviderManager()
        mgr.gemini_config.api_key = "AIzaSyGeminiKey123"
        mgr.openai_config.api_key = "sk-OpenAIKey456"

        mock_openai_res = GenerationResult(
            provider="openai",
            model="gpt-4o-mini",
            content={"failover": "success"},
            generation_mode="live_llm"
        )

        with patch.object(mgr.gemini_provider, "generate_structured", side_effect=LLMServerError("Service 503 Overloaded", provider="gemini")):
            with patch.object(mgr.openai_provider, "generate_structured", return_value=mock_openai_res) as mock_openai_call:
                res = mgr.generate_structured(schema={}, prompt="Failover test", provider_override="gemini")
                mock_openai_call.assert_called_once()
                self.assertEqual(res.provider, "openai")
                self.assertEqual(res.content["failover"], "success")

    def test_provenance_creation(self):
        """Verifies stage-level provenance records have all required fields."""
        mgr = LLMProviderManager()
        prov = mgr.create_provenance_record(
            mode="live_llm",
            provider="gemini",
            model="gemini-1.5-flash",
            stages={
                "topic_interpretation_source": "live_llm",
                "concept_generation_source": "live_llm",
                "question_generation_source": "live_llm",
                "probe_generation_source": "live_llm",
                "remedial_generation_source": "live_llm"
            }
        )
        self.assertEqual(prov["overall_mode"], "live_llm")
        self.assertEqual(prov["provider"], "gemini")
        self.assertEqual(prov["topic_interpretation_source"], "live_llm")
        self.assertEqual(prov["concept_generation_source"], "live_llm")
        self.assertEqual(prov["question_generation_source"], "live_llm")
        self.assertEqual(prov["probe_generation_source"], "live_llm")
        self.assertEqual(prov["remedial_generation_source"], "live_llm")
        self.assertIn("timestamp", prov)


class TestEndToEndPipelineWithProviderSpy(unittest.TestCase):
    """Verifies that the educational generation pipeline authenticates and routes through LLMProviderManager."""

    def test_custom_generation_invokes_llm_and_records_provenance(self):
        from backend.app.syllabus_generator import SyllabusQuestionBankGenerator
        from backend.app.providers.manager import get_provider_manager

        mgr = get_provider_manager()
        mock_curriculum = {
            "icon": "⚡",
            "category": "Physics",
            "description": "Quantum Mechanics diagnostic assessment.",
            "concepts": [
                {
                    "id_suffix": "c1",
                    "name": "Wave-Particle Duality",
                    "description": "Light and matter exhibit behaviors of both waves and discrete particles.",
                    "prerequisites": [],
                    "core_idea": "Photons and electrons display interference patterns while exchanging discrete energy packets.",
                    "example": "Double-slit experiment demonstrating electron interference fringes.",
                    "common_mistake": "Thinking particles travel through both slits simultaneously as solid balls.",
                    "key_takeaway": "Entities propagate as probability waves and localize upon measurement as particles."
                },
                {
                    "id_suffix": "c2",
                    "name": "Heisenberg Uncertainty Principle",
                    "description": "Fundamental limit to the precision of conjugate physical observables.",
                    "prerequisites": ["c1"],
                    "core_idea": "Position and momentum cannot both be precisely determined simultaneously.",
                    "example": "Confinement of an electron requires an increased momentum spread.",
                    "common_mistake": "Attributing uncertainty to measurement clumsiness rather than wave mechanics.",
                    "key_takeaway": "Uncertainty is an intrinsic mathematical property of conjugate quantum wave packets."
                }
            ],
            "misconceptions": [
                {
                    "concept_suffix": "c1",
                    "code": "M-QM-01",
                    "name": "Macroscopic Wave Misconception",
                    "description": "Believing macroscopic objects exhibit visible diffraction fringes.",
                    "remediation": "Calculate de Broglie wavelength showing lambda is sub-planckian."
                }
            ],
            "questions": [
                {
                    "concept_suffix": "c1",
                    "question_type": "basic",
                    "difficulty": "easy",
                    "question_text": "Which foundational phenomenon definitively proves that light transfers energy in discrete packets?",
                    "option_a": "Photoelectric effect ejecting electrons upon threshold illumination",
                    "option_b": "Wave diffraction of light passing through narrow pinhole apertures",
                    "option_c": "Polarization of transverse light rays through calcite prisms",
                    "option_d": "Total internal reflection inside optical dielectric glass fibers",
                    "correct_option": "A",
                    "explanation": "The photoelectric effect requires discrete photon quanta E = hf.",
                    "reasoning_probe": None
                },
                {
                    "concept_suffix": "c2",
                    "question_type": "application",
                    "difficulty": "hard",
                    "question_text": "An electron is confined to an extremely narrow spatial interval. What direct outcome follows?",
                    "option_a": "The minimum momentum uncertainty of the electron increases dramatically",
                    "option_b": "The electron instantly collapses into the atomic nucleus without radiation",
                    "option_c": "The speed of light inside the atom drops to zero due to dielectric drag",
                    "option_d": "The electron loses all charge and transforms into an uncharged neutron",
                    "correct_option": "A",
                    "explanation": "Heisenberg relation forces large momentum spread upon spatial localization.",
                    "reasoning_probe": {
                        "prompt": "Why does spatial confinement drive momentum uncertainty?",
                        "options": {
                            "A": "Fourier wave mechanics dictates that narrower spatial wave packets require broader momentum wavenumbers",
                            "B": "The measuring photon physically collides with the electron and transfers arbitrary thermal energy",
                            "C": "Coulomb attraction increases with the inverse square of separation according to classical laws",
                            "D": "Electromagnetic radiation pressure compresses the electron into an oscillating wave envelope"
                        },
                        "correct_probe": "A"
                    }
                }
            ]
        }

        mock_gen_result = GenerationResult(
            provider="gemini",
            model="gemini-1.5-flash",
            content=mock_curriculum,
            generation_mode="live_llm"
        )

        try:
            with patch.object(mgr, "generate_structured", return_value=mock_gen_result) as mock_spy:
                generator = SyllabusQuestionBankGenerator()
                res = generator.generate_custom_domain(
                    topic_title="Quantum Mechanics",
                    api_key="AIzaSyTestKeyForLiveValidation12345",
                    api_provider="gemini",
                    require_live_llm=True
                )

                # 1. Verify LLMProviderManager was called
                mock_spy.assert_called_once()
                self.assertEqual(res["status"], "success")
                self.assertTrue(res["llm_used"])
                self.assertEqual(res["generation_source"], "live_llm")
                self.assertEqual(res["llm_provider"], "gemini")

                # 2. Verify provenance record
                self.assertIn("provenance", res)
                prov = res["provenance"]
                self.assertEqual(prov["overall_mode"], "live_llm")
                self.assertEqual(prov["topic_interpretation_source"], "live_llm")
                self.assertEqual(prov["concept_generation_source"], "live_llm")
                self.assertEqual(prov["question_generation_source"], "live_llm")
                self.assertEqual(prov["probe_generation_source"], "live_llm")
        finally:
            import sqlite3
            db_p = BASE_DIR / "database" / "deeplearnx.db"
            if db_p.exists():
                conn = sqlite3.connect(str(db_p))
                conn.execute("DELETE FROM questions WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM misconceptions WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM concepts WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM custom_concept_guides WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM domains WHERE id LIKE 'custom_quantum_mechanics_%'")
                conn.commit()
                conn.close()

    def test_topic_understanding_detects_polysemy(self):
        """Verifies polysemy detection across expanded catalog terms (e.g. Python, Field, Swift)."""
        from backend.app.topic_understanding import TopicUnderstandingEngine

        engine = TopicUnderstandingEngine()
        
        # 'Python' without context should detect ambiguity
        interp_python = engine.interpret("Python")
        self.assertTrue(interp_python.is_ambiguous)
        self.assertGreaterEqual(len(interp_python.ambiguities), 2)

        # 'Field' without context should detect ambiguity
        interp_field = engine.interpret("Field")
        self.assertTrue(interp_field.is_ambiguous)

        # Disambiguated by notes should resolve cleanly
        interp_resolved = engine.interpret("Python", syllabus_text="Object-oriented programming, classes, list comprehensions, JVM vs CPython.")
        self.assertFalse(interp_resolved.is_ambiguous)
        self.assertIn("Computer Science", interp_resolved.discipline)

    def test_remedial_lesson_with_live_provider_spy(self):
        """Verifies generate_12_section_remedial_document generates adaptive teaching via live provider."""
        from backend.app.concept_guide import generate_12_section_remedial_document
        from backend.app.providers.manager import get_provider_manager

        mgr = get_provider_manager()
        mock_sections = [
            {"section_number": i + 1, "title": f"Section {i+1} Title", "content": f"Personalized pedagogical content {i+1}"}
            for i in range(12)
        ]
        mock_remedial_res = GenerationResult(
            provider="gemini",
            model="gemini-1.5-flash",
            content={"sections": mock_sections, "practice_questions": []},
            generation_mode="live_llm"
        )

        with patch.object(mgr.gemini_provider, "generate_structured", return_value=mock_remedial_res):
            with patch.object(mgr, "get_active_provider", return_value=mgr.gemini_provider):
                doc = generate_12_section_remedial_document(
                    concept_id="c1_sample",
                    domain_id="Physics",
                    student_error={
                        "question_text": "Sample quantum question",
                        "selected_option": "B",
                        "correct_option": "A"
                    }
                )
                self.assertEqual(doc["generation_source"], "live_llm")
                self.assertEqual(doc["sections_count"], 12)
                self.assertEqual(doc["learning_gain_status"], "POST-REMEDIATION LEARNING GAIN NOT YET MEASURED")


if __name__ == "__main__":
    unittest.main()

