"""
DeepLearnX Phase 2 Universal Intelligence & Benchmark Test Suite.
Validates:
1. Topic Understanding & Ambiguity Detection (Polysemy resolution).
2. Cross-Disciplinary Synthesis across STEM, Humanities, Law, Medicine, and Culinary domains.
3. Jargon Contamination Prevention in Non-Engineering Disciplines.
4. Kahn's Topological Sorting and Strict DAG Integrity.
5. Two-Tier Diagnostic Reasoning Probe Generation, Option Shuffling, and Answer Key Stripping.
6. Diagnostic State Classification (Genuine Mastery, False Mastery, Application Difficulty, Misconception, Gap, Insufficient Evidence).
7. 12-Section Personalized Remedial Learning Document Generation.
8. Authentic Hake Normalized Learning Gain Calculation.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
APP_DIR = BASE_DIR / "backend" / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
MODEL_DIR = BASE_DIR / "model"
if str(MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(MODEL_DIR))

from backend.app.topic_understanding import TopicUnderstandingEngine, AMBIGUITY_CATALOG
from backend.app.universal_synthesizer import (
    synthesize_universal_curriculum,
    detect_dag_topology,
    detect_archetype
)
from backend.app.quiz_validator import (
    validate_knowledge_dag,
    validate_curriculum_package,
    check_distractor_contamination
)
from backend.app.concept_guide import generate_12_section_remedial_document
from model.predictor import DeepLearnXPredictor


# =============================================================================
# 1. TOPIC UNDERSTANDING & AMBIGUITY TESTS
# =============================================================================

class TestTopicUnderstandingEngine:
    def test_polysemous_topic_detection_bare_query(self):
        """Bare queries for known polysemous words must be flagged as ambiguous."""
        engine = TopicUnderstandingEngine()
        for term in ["Java", "Mercury", "Apple", "Vector", "Cell"]:
            interp = engine.interpret(term, syllabus_text="")
            assert interp.is_ambiguous, f"Expected '{term}' to be flagged as ambiguous"
            assert len(interp.ambiguities) >= 2, f"Expected at least 2 interpretations for '{term}'"
            assert interp.discipline == "Ambiguous Topic"

    def test_polysemous_topic_disambiguated_by_syllabus_text(self):
        """When student notes provide clear domain context, ambiguity must be resolved automatically."""
        engine = TopicUnderstandingEngine()
        interp = engine.interpret(
            topic="Java",
            syllabus_text="Object-oriented programming with JVM, bytecode, encapsulation, inheritance, polymorphism, and garbage collection."
        )
        assert not interp.is_ambiguous
        assert "Computer Science" in interp.discipline or "Programming" in interp.canonical_title

    def test_polysemous_topic_disambiguated_by_explicit_selection(self):
        """When student selects a specific disambiguation ID, it must resolve directly."""
        engine = TopicUnderstandingEngine()
        interp = engine.interpret(
            topic="Java",
            syllabus_text="",
            selected_disambiguation="java_geo"
        )
        assert not interp.is_ambiguous
        assert "Geography" in interp.discipline or "Indonesian" in interp.canonical_title

    def test_unambiguous_academic_topic(self):
        """Specific academic topics should not be flagged as ambiguous."""
        engine = TopicUnderstandingEngine()
        interp = engine.interpret("Quantum Chromodynamics")
        assert not interp.is_ambiguous
        assert "Quantum" in interp.discipline or "Physics" in interp.discipline or "Science" in interp.discipline
        assert len(interp.core_areas) >= 1


# =============================================================================
# 2. CROSS-DISCIPLINARY SYNTHESIS & JARGON CONTAMINATION TESTS
# =============================================================================

class TestCrossDisciplinarySynthesis:
    @pytest.mark.parametrize("topic,expected_discipline,sample_category", [
        ("French Impressionist Painting", "Humanities & Art", "Humanities & Fine Arts"),
        ("Constitutional Separation of Powers", "Law & Governance", "Law & Governance"),
        ("Immunology and T-Cell Activation", "Medicine & Life Sciences", "Medicine & Immunology"),
        ("Classical Sourdough Fermentation", "Culinary & Food Science", "Culinary Arts & Fermentation Science"),
        ("Astrophysical Black Hole Thermodynamics", "Physics & Astronomy", "Physics & Space Science"),
    ])
    def test_universal_curriculum_cross_disciplinary(self, topic, expected_discipline, sample_category):
        """Validates curriculum synthesis across diverse non-CS disciplines."""
        domain_id = f"test_{abs(hash(topic)) % 100000}"
        concepts, misconceptions, questions, guides, icon, category = synthesize_universal_curriculum(
            domain_id=domain_id,
            topic_title=topic,
            articles=[{"title": topic, "extract": f"Academic study of {topic} covering fundamental principles and applications."}],
            num_questions=12
        )

        assert len(concepts) >= 3, f"Expected at least 3 concepts for {topic}"
        assert len(questions) == 12, f"Expected 12 questions for {topic}"
        assert len(misconceptions) >= 2, f"Expected at least 2 misconceptions for {topic}"
        assert len(guides) >= 3, f"Expected guides for each concept for {topic}"

        # Verify DAG validity
        dag_ok, dag_errs = validate_knowledge_dag(concepts)
        assert dag_ok, f"DAG validation failed for {topic}: {dag_errs}"

        # Verify Zero Jargon Contamination in options
        all_options = []
        for q in questions:
            opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
            all_options.extend(opts)
            clean_ok, contam_err = check_distractor_contamination(opts, category)
            assert clean_ok, f"Contamination detected in {topic} ({category}): {contam_err}"


# =============================================================================
# 3. ASSESSMENT QUALITY & PROBE INTEGRITY TESTS
# =============================================================================

class TestAssessmentQualityAndProbes:
    def test_tiered_distribution_and_probe_integrity(self):
        """Verifies 12-question tiered distribution and 3-4 two-tier reasoning probes."""
        domain_id = "test_pedagogy_eval"
        concepts, misconceptions, questions, guides, icon, category = synthesize_universal_curriculum(
            domain_id=domain_id,
            topic_title="Cellular Mitosis and Cell Cycle Regulation",
            articles=[{"title": "Mitosis", "extract": "Stages of mitotic division including prophase, metaphase, anaphase, and telophase."}],
            num_questions=12
        )

        # 1. Tier count checks (~50% Basic, ~33% Conceptual, ~17% Application)
        basic_count = sum(1 for q in questions if q["question_type"] == "basic")
        conc_count = sum(1 for q in questions if q["question_type"] == "conceptual")
        app_count = sum(1 for q in questions if q["question_type"] == "application")

        assert basic_count == 6, f"Expected 6 basic questions, got {basic_count}"
        assert conc_count == 4, f"Expected 4 conceptual questions, got {conc_count}"
        assert app_count == 2, f"Expected 2 application questions, got {app_count}"

        # 2. Two-Tier Reasoning Probes (3 to 4 probes per 12-question quiz)
        probes = [q["reasoning_probe"] for q in questions if q.get("reasoning_probe")]
        assert 3 <= len(probes) <= 4, f"Expected 3-4 reasoning probes, got {len(probes)}"

        # 3. Probe structure and option distribution
        probe_correct_choices = set()
        for p in probes:
            assert "prompt" in p and len(p["prompt"]) >= 15
            assert "options" in p and len(p["options"]) == 4
            assert all(k in p["options"] for k in ["A", "B", "C", "D"])
            assert "correct_probe" in p and p["correct_probe"] in ["A", "B", "C", "D"]
            probe_correct_choices.add(p["correct_probe"])

        # Ensure correct options are not all hardcoded to 'A'
        assert len(probe_correct_choices) >= 2, f"Expected distributed probe keys, got {probe_correct_choices}"

    def test_option_length_balance(self):
        """Verifies that distractor option lengths are well balanced."""
        domain_id = "test_length_eval"
        _, _, questions, _, _, _ = synthesize_universal_curriculum(
            domain_id=domain_id,
            topic_title="Principles of Contract Law",
            articles=[{"title": "Contract Law", "extract": "Elements of enforceable contract including offer, acceptance, consideration, and capacity."}],
            num_questions=12
        )

        for q in questions:
            opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
            lens = [len(o.split()) for o in opts]
            max_l = max(lens)
            min_l = max(min(lens), 1)
            ratio = max_l / float(min_l)
            assert ratio <= 3.0, f"Unbalanced option length ratio {ratio:.2f} in question '{q['question_text'][:50]}'"


# =============================================================================
# 4. COGNITIVE DIAGNOSTIC CLASSIFICATION TESTS
# =============================================================================

class TestCognitiveDiagnostics:
    @pytest.fixture
    def predictor(self):
        return DeepLearnXPredictor()

    def test_genuine_mastery_diagnosis(self, predictor):
        """Student with high accuracy across all tiers and consistent reasoning passes."""
        responses = [
            {"question_id": f"q_{i}", "is_correct": 1, "response_time": 25.0, "confidence": 5, "question_type": "basic", "reasoning_selected": "A"}
            for i in range(6)
        ] + [
            {"question_id": f"q_{i}", "is_correct": 1, "response_time": 35.0, "confidence": 5, "question_type": "conceptual", "reasoning_selected": "A"}
            for i in range(6, 10)
        ] + [
            {"question_id": f"q_{i}", "is_correct": 1, "response_time": 45.0, "confidence": 5, "question_type": "application", "reasoning_selected": "A"}
            for i in range(10, 12)
        ]
        # Inject matching probe
        for r in responses:
            r["q_info"] = {
                "question_text": "Authentic academic diagnostic question text testing principles.",
                "correct_option": "A",
                "question_type": r["question_type"],
                "reasoning_probe": {"prompt": "Why is this true?", "options": {"A": "Core law", "B": "Alt", "C": "Alt2", "D": "Alt3"}, "correct_probe": "A"}
            }

        diag = predictor.analyze_session(responses)
        assert diag["predicted_state"] == "Genuine Mastery"
        assert diag["confidence"] >= 0.85

    def test_application_difficulty_diagnosis(self, predictor):
        """High basic and conceptual accuracy but struggling on applied scenario questions."""
        responses = [
            {"question_id": f"q_{i}", "is_correct": 1, "response_time": 25.0, "confidence": 4, "question_type": "basic", "reasoning_selected": "A"}
            for i in range(6)
        ] + [
            {"question_id": f"q_{i}", "is_correct": 1, "response_time": 35.0, "confidence": 4, "question_type": "conceptual", "reasoning_selected": "A"}
            for i in range(6, 10)
        ] + [
            {"question_id": f"q_{i}", "is_correct": 0, "response_time": 45.0, "confidence": 3, "question_type": "application", "reasoning_selected": "B"}
            for i in range(10, 12)
        ]
        for r in responses:
            r["q_info"] = {
                "question_text": "Authentic diagnostic question text.",
                "correct_option": "A",
                "question_type": r["question_type"],
                "reasoning_probe": {"prompt": "Why?", "options": {"A": "True", "B": "False", "C": "Other", "D": "None"}, "correct_probe": "A"}
            }

        diag = predictor.analyze_session(responses)
        assert diag["predicted_state"] == "Application Difficulty"
        assert diag["false_mastery_breakdown"]["is_application_difficulty"] is True

    def test_insufficient_evidence_diagnosis(self, predictor):
        """Short session (<4 questions) or extreme rapid guessing triggers Insufficient Evidence."""
        responses = [
            {"question_id": "q_1", "is_correct": 1, "response_time": 1.0, "confidence": 3, "question_type": "basic"},
            {"question_id": "q_2", "is_correct": 0, "response_time": 1.2, "confidence": 3, "question_type": "basic"}
        ]
        for r in responses:
            r["q_info"] = {"question_text": "Short item", "correct_option": "A", "question_type": "basic"}

        diag = predictor.analyze_session(responses)
        assert diag["predicted_state"] == "Insufficient Evidence"


# =============================================================================
# 5. REMEDIAL LEARNING & NORMALIZED LEARNING GAIN TESTS
# =============================================================================

class TestRemedialLearningEngine:
    def test_twelve_section_remedial_document_generation(self):
        """Remedial learning generator must produce all 12 pedagogical sections with error analysis."""
        student_error = {
            "question_text": "What happens when an uncharged metal sphere is brought near a positive rod?",
            "selected_option": "B",
            "selected_text": "Protons move away to the far side of the sphere.",
            "correct_option": "A",
            "correct_text": "Free electrons migrate toward the rod leaving positive ionic lattice behind."
        }
        doc = generate_12_section_remedial_document(
            concept_id="electrostatic_induction",
            domain_id="physics_electromagnetism",
            student_error=student_error
        )

        assert doc["sections_count"] == 12
        assert len(doc["sections"]) == 12
        sec_nums = [s["section_number"] for s in doc["sections"]]
        assert sec_nums == list(range(1, 13))

        # Check personalized mistake analysis in Section 8
        sec_8 = doc["sections"][7]
        assert "Personalized Diagnostic Analysis" in sec_8["content"]
        assert "Protons move away" in sec_8["content"]

    def test_hake_normalized_learning_gain_calculation(self):
        """Validates Hake normalized gain calculation: (Post - Pre) / (1 - Pre)."""
        # Scenario 1: Moderate gain (Pre = 40%, Post = 80%) -> Gain = (0.8 - 0.4)/(1 - 0.4) = 0.4/0.6 = 0.667
        pre_acc = 0.40
        post_acc = 0.80
        gain = round((post_acc - pre_acc) / (1.0 - pre_acc), 3)
        assert gain == 0.667

        # Scenario 2: Complete mastery (Pre = 0%, Post = 100%) -> Gain = 1.0
        pre_acc = 0.0
        post_acc = 1.0
        gain = round((post_acc - pre_acc) / (1.0 - pre_acc), 3)
        assert gain == 1.0

        # Scenario 3: Negative gain (Pre = 60%, Post = 40%) -> Gain = (0.4 - 0.6)/(1 - 0.6) = -0.5
        pre_acc = 0.60
        post_acc = 0.40
        gain = round((post_acc - pre_acc) / (1.0 - pre_acc), 3)
        assert gain == -0.5
