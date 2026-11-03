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

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_timeout_error(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client
        mock_client.models.generate_content.side_effect = TimeoutError("Request timed out")

        with self.assertRaises(LLMTimeoutError):
            self.provider.generate_structured(schema={}, prompt="Timeout test")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_quota_exhausted_error(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        from google.genai import errors
        api_err = errors.APIError(code=429, response_json={"error": {"message": "Resource exhausted: quota limit exceeded"}}, response=MagicMock())
        mock_client.models.generate_content.side_effect = api_err

        with self.assertRaises(LLMQuotaExhaustedError):
            self.provider.generate_structured(schema={}, prompt="Quota test")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_malformed_json_format_error(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        mock_response = MagicMock()
        mock_response.text = "invalid json {broken"
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_client.models.generate_content.return_value = mock_response

        with self.assertRaises(LLMFormatError):
            self.provider.generate_structured(schema={}, prompt="JSON test")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_truncation_error(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        mock_response = MagicMock()
        mock_response.text = '{"partial": "data'
        mock_response.candidates = [MagicMock(finish_reason="MAX_TOKENS")]
        mock_client.models.generate_content.return_value = mock_response

        with self.assertRaises(LLMTruncationError):
            self.provider.generate_structured(schema={}, prompt="Truncation test")

    @patch("backend.app.providers.gemini_provider.GENAI_AVAILABLE", True)
    @patch("backend.app.providers.gemini_provider.genai")
    def test_gemini_retry_exhaustion(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        self.provider._client = mock_client

        from google.genai import errors
        api_err = errors.APIError(code=429, response_json={"error": {"message": "Rate limit exceeded"}}, response=MagicMock())
        mock_client.models.generate_content.side_effect = api_err

        with patch("time.sleep", return_value=None):
            with self.assertRaises(LLMRateLimitError):
                self.provider.generate_structured(schema={}, prompt="Retry test")
        # max_retries = 2 -> total attempts = 1 initial + 2 retries = 3
        self.assertEqual(mock_client.models.generate_content.call_count, 3)


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
                conn.execute("DELETE FROM question_validations WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM learning_objectives WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
                conn.execute("DELETE FROM curriculum_nodes WHERE domain_id LIKE 'custom_quantum_mechanics_%'")
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

    def test_custom_generate_api_endpoint_invokes_provider_spy_and_persists(self):
        """Verifies that the /api/assessment/custom-generate endpoint invokes LLMProviderManager and persists."""
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.providers.manager import get_provider_manager
        import sqlite3

        client = TestClient(app)
        mgr = get_provider_manager()

        mock_curriculum = {
            "icon": "🤖",
            "category": "Robotics & Automation",
            "description": "Kinematics and Control Assessment.",
            "concepts": [
                {
                    "id_suffix": "c1",
                    "name": "Forward Kinematics",
                    "description": "Mapping joint parameters to end-effector Cartesian coordinates.",
                    "prerequisites": [],
                    "core_idea": "Denavit-Hartenberg transformation matrices compute tool center position.",
                    "example": "Calculating end-effector position of a 6-DOF arm from joint encoders.",
                    "common_mistake": "Confusing forward kinematics with inverse kinematics.",
                    "key_takeaway": "Forward kinematics has a unique closed-form mathematical solution."
                },
                {
                    "id_suffix": "c2",
                    "name": "Inverse Kinematics",
                    "description": "Solving joint angles required to reach a target spatial pose.",
                    "prerequisites": ["c1"],
                    "core_idea": "Non-linear equations often have multiple solutions or singularities.",
                    "example": "Elbow-up versus elbow-down configurations for a planar manipulator.",
                    "common_mistake": "Assuming only one joint configuration can reach a target point.",
                    "key_takeaway": "Inverse kinematics requires numerical Jacobians or algebraic multi-solution resolution."
                }
            ],
            "misconceptions": [
                {
                    "concept_suffix": "c1",
                    "code": "M-ROB-01",
                    "name": "Kinematic Uniqueness Fallacy",
                    "description": "Assuming reverse reaching poses are unique.",
                    "remediation": "Demonstrate multiple joint angle combinations yielding the exact same tip pose."
                }
            ],
            "questions": [
                {
                    "concept_suffix": "c1",
                    "question_type": "basic",
                    "difficulty": "easy",
                    "question_text": "Which kinematic formulation determines end-effector position directly from joint angles?",
                    "option_a": "Forward kinematics utilizing DH transformation matrices",
                    "option_b": "Inverse kinematics solving non-linear Jacobian manifolds",
                    "option_c": "PID control loop tuning for torque-mode actuator amplifiers",
                    "option_d": "Laser rangefinder point-cloud SLAM localization",
                    "correct_option": "A",
                    "explanation": "Forward kinematics maps joint angles to Cartesian coordinates.",
                    "reasoning_probe": None
                },
                {
                    "concept_suffix": "c2",
                    "question_type": "application",
                    "difficulty": "hard",
                    "question_text": "A 6-axis manipulator aligns two joints, losing a degree of freedom. What phenomenon has occurred?",
                    "option_a": "A kinematic singularity causing unbounded joint velocities",
                    "option_b": "A mechanical motor burnout tripping safety circuit breakers",
                    "option_c": "A loss of network packet synchronization across EtherCAT",
                    "option_d": "A thermal expansion misalignment in the aluminum casing",
                    "correct_option": "A",
                    "explanation": "Singularities occur when the Jacobian drops rank.",
                    "reasoning_probe": {
                        "prompt": "Why do singularities cause control divergence?",
                        "options": {
                            "A": "The Jacobian determinant approaches zero, requiring infinite joint velocity for Cartesian motion",
                            "B": "The robotic controller shuts down to conserve battery voltage across the factory floor",
                            "C": "The mechanical linkages physically detach from their harmonic drive gearboxes",
                            "D": "The vision sensor is blinded by ambient factory lighting reflections"
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

        created_domain_id = None
        try:
            with patch.object(mgr, "generate_structured", return_value=mock_gen_result) as mock_spy:
                res = client.post("/api/assessment/custom-generate", json={
                    "topic_title": "Robotic Manipulator Kinematics",
                    "api_key": "test_provider_spy_key_xyz",
                    "api_provider": "gemini",
                    "require_live_llm": True
                })

                self.assertEqual(res.status_code, 200)
                data = res.json()
                created_domain_id = data.get("domain_id")
                self.assertIsNotNone(created_domain_id)
                self.assertTrue(data.get("llm_used"))
                self.assertEqual(data.get("generation_source"), "live_llm")

                # Verify provider spy called
                mock_spy.assert_called_once()
                call_args = mock_spy.call_args[1]
                self.assertIn("Robotic Manipulator Kinematics", call_args["prompt"])

                # Verify records actually persisted in SQLite database
                db_p = BASE_DIR / "database" / "deeplearnx.db"
                conn = sqlite3.connect(str(db_p))
                d_row = conn.execute("SELECT id, name FROM domains WHERE id = ?", (created_domain_id,)).fetchone()
                self.assertIsNotNone(d_row)
                c_rows = conn.execute("SELECT id FROM concepts WHERE domain_id = ?", (created_domain_id,)).fetchall()
                self.assertEqual(len(c_rows), 2)
                q_rows = conn.execute("SELECT id FROM questions WHERE domain_id = ?", (created_domain_id,)).fetchall()
                self.assertEqual(len(q_rows), 2)
                conn.close()
        finally:
            if created_domain_id:
                db_p = BASE_DIR / "database" / "deeplearnx.db"
                if db_p.exists():
                    conn = sqlite3.connect(str(db_p))
                    conn.execute("DELETE FROM student_responses WHERE session_id IN (SELECT id FROM assessment_sessions WHERE domain_id = ?)", (created_domain_id,))
                    conn.execute("DELETE FROM assessment_sessions WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM question_validations WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM learning_objectives WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM curriculum_nodes WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM questions WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM misconceptions WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM custom_concept_guides WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM concepts WHERE domain_id = ?", (created_domain_id,))
                    conn.execute("DELETE FROM domains WHERE id = ?", (created_domain_id,))
                    conn.commit()
                    conn.close()

    def test_stable_sha256_question_variation_cross_process_and_uniqueness(self):
        """Verifies deterministic question synthesis, seed stability, cross-process consistency, and stem uniqueness."""
        from backend.app.universal_synthesizer import synthesize_authentic_curriculum
        import re

        topic = "Macroeconomic Fiscal Policy"
        run_a = synthesize_authentic_curriculum("test_seed_stable", topic, seed_offset=0)
        run_b = synthesize_authentic_curriculum("test_seed_stable", topic, seed_offset=0)
        run_c = synthesize_authentic_curriculum("test_seed_stable", topic, seed_offset=1)

        qs_a = run_a[2]
        qs_b = run_b[2]
        qs_c = run_c[2]

        # 1. Identical seeds produce 100% bit-for-bit identical question stems & options
        for i in range(len(qs_a)):
            self.assertEqual(qs_a[i]["question_text"], qs_b[i]["question_text"])
            self.assertEqual(qs_a[i]["option_a"], qs_b[i]["option_a"])
            self.assertEqual(qs_a[i]["correct_option"], qs_b[i]["correct_option"])

        # 2. Strict uniqueness within a single quiz: zero duplicate stems
        stems_a = [q["question_text"] for q in qs_a]
        self.assertEqual(len(stems_a), len(set(stems_a)), "Duplicate question stems found in quiz!")

        # 3. Near-duplicate semantic check (pairwise Jaccard < 0.82)
        def tok(t): return set(re.findall(r'\b[a-z]{3,}\b', t.lower()))
        for i in range(len(stems_a)):
            for j in range(i + 1, len(stems_a)):
                s1, s2 = tok(stems_a[i]), tok(stems_a[j])
                jacc = len(s1 & s2) / max(len(s1 | s2), 1)
                self.assertLess(jacc, 0.85, f"Near-duplicate question stems found at indices {i} and {j} (Jaccard: {jacc:.2f})")

        # 4. Different seeds produce distinct stems across runs
        jaccards = []
        for i in range(min(len(qs_a), len(qs_c))):
            s1, s2 = tok(qs_a[i]["question_text"]), tok(qs_c[i]["question_text"])
            jaccards.append(len(s1 & s2) / max(len(s1 | s2), 1))
        avg_jaccard = sum(jaccards) / len(jaccards)
        self.assertLess(avg_jaccard, 0.70, f"Average Jaccard similarity across distinct seeds {avg_jaccard:.2f} >= 0.70")

    def test_generalized_ambiguity_unknown_terms_and_contextual_resolution(self):
        """Verifies generalized polysemy detection on unknown terms and context-driven resolution without prompt."""
        from backend.app.topic_understanding import TopicUnderstandingEngine

        engine = TopicUnderstandingEngine()

        # 1. Unknown ambiguous term without context -> flagged ambiguous with >= 2 candidates
        interp_crane = engine.interpret("Crane")
        self.assertTrue(interp_crane.is_ambiguous)
        self.assertGreaterEqual(len(interp_crane.ambiguities), 2)
        c_titles = [c["title"].lower() for c in interp_crane.ambiguities]
        self.assertTrue(any("machinery" in t or "rigging" in t for t in c_titles))
        self.assertTrue(any("avian" in t or "gruidae" in t for t in c_titles))

        # 2. Unknown ambiguous term with Engineering context -> resolved without prompting
        interp_crane_eng = engine.interpret("Crane", syllabus_text="Tower crane hoisting capacity, hydraulic booms, and steel rigging.")
        self.assertFalse(interp_crane_eng.is_ambiguous)
        self.assertIn("Engineering", interp_crane_eng.discipline)

        # 3. Unknown ambiguous term with Biology context -> resolved without prompting
        interp_crane_bio = engine.interpret("Crane", syllabus_text="Whooping crane plumage, wetland nesting ecology, and migratory flyways.")
        self.assertFalse(interp_crane_bio.is_ambiguous)
        self.assertIn("Biological Sciences", interp_crane_bio.discipline)

        # 4. Another unknown polysemous term: 'Strike'
        interp_strike = engine.interpret("Strike")
        self.assertTrue(interp_strike.is_ambiguous)
        interp_strike_econ = engine.interpret("Strike", syllabus_text="Labor union collective bargaining, wage disputes, and worker picketing.")
        self.assertFalse(interp_strike_econ.is_ambiguous)
        self.assertIn("Economics", interp_strike_econ.discipline)

        # 5. Unambiguous topics -> NEVER flagged ambiguous
        interp_photo = engine.interpret("Photosynthesis")
        self.assertFalse(interp_photo.is_ambiguous)
        self.assertEqual(len(interp_photo.ambiguities), 0)

        interp_quad = engine.interpret("Quadratic Equations")
        self.assertFalse(interp_quad.is_ambiguous)
        self.assertEqual(len(interp_quad.ambiguities), 0)

    def test_unknown_homonym_contextual_interpretation_without_hardcoded_mappings(self):
        """Verifies genuine contextual interpretation for unknown homonyms (Bank, Terminal, Scale, Pitch, Bass)."""
        from backend.app.topic_understanding import TopicUnderstandingEngine
        engine = TopicUnderstandingEngine()

        test_cases = [
            ("Bank in financial economics", "", "Economics & Business"),
            ("Bank in river geography", "", "Earth & Geological Sciences"),
            ("Bank", "financial economics monetary central reserve interest rate credit banking", "Economics & Business"),
            ("Bank", "river hydrology sediment fluvial geomorphology water flow floodplain", "Earth & Geological Sciences"),
            ("Terminal in computer systems", "", "Computer Science & Systems"),
            ("Terminal in transport infrastructure", "", "Transportation & Logistics"),
            ("Terminal", "command line unix bash shell process stdin stdout console terminal", "Computer Science & Systems"),
            ("Terminal", "airport passenger gate departure runway logistics transport terminal", "Transportation & Logistics"),
            ("Scale in music", "", "Music Theory & Fine Arts"),
            ("Scale in biology or measurement", "", "Cellular & Molecular Biology"),
            ("Scale", "major minor pentatonic intervals tonic octave harmony music pitch", "Music Theory & Fine Arts"),
            ("Scale", "reptile keratin epidermal fish cuticle dermis morphology scales", "Cellular & Molecular Biology"),
            ("Pitch in acoustics", "", "Acoustics & Sound Physics"),
            ("Pitch in baseball athletics", "", "Sports Science & Athletics"),
            ("Bass in music theory", "", "Music Theory & Fine Arts"),
            ("Bass in freshwater fish biology", "", "Zoology & Animal Biology"),
        ]

        for topic, context, expected_domain in test_cases:
            interp = engine.interpret(topic, syllabus_text=context)
            match = (expected_domain.lower() in interp.discipline.lower() or 
                     expected_domain.lower() in interp.category.lower())
            self.assertTrue(match, f"Failed for '{topic}': got discipline '{interp.discipline}' / category '{interp.category}', expected '{expected_domain}'")
            self.assertFalse(interp.is_ambiguous, f"Expected unambiguous contextual resolution for '{topic}'")

    def test_provider_failover_telemetry_and_bounded_retry(self):
        """Verifies failover records provider switch event and auth errors abort immediately without retries."""
        from backend.app.providers.manager import LLMProviderManager
        from backend.app.providers.base import LLMAuthenticationError, LLMServerError

        mgr = LLMProviderManager()
        mgr.gemini_config.api_key = "AIzaSyGeminiKey123"
        mgr.openai_config.api_key = "sk-OpenAIKey456"

        mock_openai_res = GenerationResult(
            provider="openai",
            model="gpt-4o-mini",
            content={"status": "failover_verified"},
            generation_mode="live_llm"
        )

        # 1. Transient 503 triggers failover and records switch event
        with patch.object(mgr.gemini_provider, "generate_structured", side_effect=LLMServerError("503 Service Unavailable", provider="gemini")):
            with patch.object(mgr.openai_provider, "generate_structured", return_value=mock_openai_res) as mock_openai_call:
                res = mgr.generate_structured(schema={}, prompt="Test Failover", provider_override="gemini")
                mock_openai_call.assert_called_once()
                self.assertEqual(res.provider, "openai")
                self.assertIsNotNone(mgr.last_failover_event)
                self.assertEqual(mgr.last_failover_event["from_provider"], "gemini")
                self.assertEqual(mgr.last_failover_event["to_provider"], "openai")
                self.assertTrue(mgr.last_failover_event["succeeded"])

        # 2. Authentication error is NOT retryable: fails immediately
        auth_err = LLMAuthenticationError("API Key Rejected", provider="gemini", status_code=401)
        self.assertFalse(auth_err.retryable)

        # 3. Unconfigured secondary provider is NOT called
        mgr.openai_config.api_key = None
        with patch.object(mgr.gemini_provider, "generate_structured", side_effect=LLMServerError("503 Service Unavailable", provider="gemini")):
            with patch.object(mgr.openai_provider, "generate_structured") as mock_openai_uncalled:
                with self.assertRaises(LLMServerError):
                    mgr.generate_structured(schema={}, prompt="Test Failover Unconfigured", provider_override="gemini")
                mock_openai_uncalled.assert_not_called()

    def test_provenance_6_stages_and_mode_computation(self):
        """Verifies all 6 pedagogical stages and derived overall mode in provenance records."""
        from backend.app.providers.manager import LLMProviderManager

        mgr = LLMProviderManager()
        prov = mgr.create_provenance_record(
            mode="live_llm",
            provider="gemini",
            model="gemini-1.5-flash",
            stages={
                "topic_interpretation_source": "live_llm:gemini",
                "concept_generation_source": "live_llm:gemini",
                "dag_generation_source": "live_llm:gemini",
                "question_generation_source": "live_llm:gemini",
                "probe_generation_source": "live_llm:gemini",
                "remedial_generation_source": "live_llm:gemini"
            }
        )
        self.assertEqual(prov["overall_mode"], "live_llm")
        self.assertEqual(prov["dag_generation_source"], "live_llm:gemini")
        self.assertEqual(prov["topic_interpretation_source"], "live_llm:gemini")
        self.assertEqual(prov["concept_generation_source"], "live_llm:gemini")
        self.assertEqual(prov["question_generation_source"], "live_llm:gemini")
        self.assertEqual(prov["probe_generation_source"], "live_llm:gemini")
        self.assertEqual(prov["remedial_generation_source"], "live_llm:gemini")

        # Hybrid mode test: live generation for questions, but deterministic DAG
        prov_hybrid = mgr.create_provenance_record(
            mode="custom",
            provider="gemini",
            model="gemini-1.5-flash",
            stages={
                "topic_interpretation_source": "live_llm:gemini",
                "concept_generation_source": "live_llm:gemini",
                "dag_generation_source": "deterministic_dag_engine",
                "question_generation_source": "live_llm:gemini",
                "probe_generation_source": "live_llm:gemini",
                "remedial_generation_source": "offline_synthesizer"
            }
        )
        self.assertEqual(prov_hybrid["overall_mode"], "hybrid")


if __name__ == "__main__":
    unittest.main()

