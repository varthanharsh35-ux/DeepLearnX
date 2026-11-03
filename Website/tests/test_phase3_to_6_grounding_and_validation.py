"""
Test Suite for Phases 3 through 6:
- Phase 3: Topic understanding and evidence grounding (Fix for Computer Systems & Architecture)
- Phase 4: Curriculum and knowledge DAG construction
- Phase 5: Learning-objective-driven assessment generation
- Phase 6: Independent question validation and publication gates
"""

import sys
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.main import app
from backend.app.universal_synthesizer import (
    detect_topic_metadata,
    synthesize_authentic_curriculum
)
from backend.app.quiz_validator import (
    validate_question,
    validate_knowledge_dag,
    validate_curriculum_package,
    GENERIC_SYNTHETIC_BOILERPLATE,
    GENERIC_ENGINEERING_CONTAMINANTS
)
from backend.app.database import get_db_connection

client = TestClient(app)


def test_topic_classification_computer_systems_not_history():
    """Verifies Computer Systems and Architecture is classified as CS, not History."""
    icon, cat, key = detect_topic_metadata("Computer Systems and Architecture")
    assert key == "cs", f"Expected key 'cs', got '{key}'"
    assert "Computer" in cat, f"Expected Computer in category, got '{cat}'"
    assert "History" not in cat, f"Contaminated category: '{cat}'"


def test_computer_systems_concepts_are_domain_authentic():
    """Verifies that generated concepts for Computer Systems are genuine technical modules."""
    c, m, q, g, icon, cat = synthesize_authentic_curriculum("test_cs_arch", "Computer Systems and Architecture")
    c_names = [item["name"] for item in c]
    
    # Must contain real microarchitectural concepts
    assert any("Instruction Set" in name or "ISA" in name for name in c_names)
    assert any("Pipelining" in name for name in c_names)
    assert any("Cache" in name or "Memory Hierarchy" in name for name in c_names)
    assert any("Virtual Memory" in name or "TLB" in name for name in c_names)
    
    # Must NOT contain generic academic boilerplate
    for name in c_names:
        assert "Core Taxonomy" not in name
        assert "Primary Classification" not in name
        assert "Alternative Typology" not in name
        assert "Comparative Synthesis" not in name
        assert "Theoretical Foundation A" not in name


def test_computer_systems_questions_have_zero_generic_boilerplate():
    """Verifies questions and options do not contain platitudes or generic templates."""
    c, m, q, g, icon, cat = synthesize_authentic_curriculum("test_cs_arch", "Computer Systems and Architecture")
    assert len(q) == 12

    for idx, item in enumerate(q):
        text = item["question_text"]
        opts = [item["option_a"], item["option_b"], item["option_c"], item["option_d"]]
        
        # Check against forbidden generic templates
        for bp in GENERIC_SYNTHETIC_BOILERPLATE:
            assert bp.lower() not in text.lower(), f"Q{idx+1} stem contains boilerplate '{bp}'"
            for o_idx, opt in enumerate(opts):
                assert bp.lower() not in opt.lower(), f"Q{idx+1} option {chr(65+o_idx)} contains boilerplate '{bp}'"


def test_all_computer_systems_questions_pass_validation():
    """Verifies every single question in the generated package passes independent quality validation."""
    c, m, q, g, icon, cat = synthesize_authentic_curriculum("test_cs_arch", "Computer Systems and Architecture")
    for idx, item in enumerate(q):
        valid, errs = validate_question(item, cat)
        assert valid, f"Q{idx+1} failed validation: {errs}"


def test_publication_gate_rejects_synthetic_boilerplate():
    """Verifies that validate_question rejects any question containing generic filler."""
    bogus_question = {
        "id": "q_bogus_1",
        "question_text": "What is the primary operational objective associated with 'Core Taxonomy'?",
        "option_a": "Conduct controlled isolation experiments to test which mechanism reproduces the failure mode.",
        "option_b": "Double the operating load immediately in an effort to overpower the detected instability.",
        "option_c": "Accept the explanation favored by the most senior team member without reviewing empirical data.",
        "option_d": "Functions solely to introduce cosmetic terminology without affecting functional behavior.",
        "correct_option": "A",
        "explanation": "Valid explanation text that meets minimum length criteria for testing.",
        "reasoning_probe": None
    }
    valid, errs = validate_question(bogus_question, "cs")
    assert not valid, "Validation gate should have REJECTED the bogus boilerplate question!"
    assert any("boilerplate" in e.lower() for e in errs)


def test_knowledge_dag_acyclicity_and_prerequisites():
    """Verifies the generated DAG has valid prerequisite links and passes Kahn's acyclicity check."""
    c, m, q, g, icon, cat = synthesize_authentic_curriculum("test_cs_arch", "Computer Systems and Architecture")
    dag_ok, dag_errs = validate_knowledge_dag(c)
    assert dag_ok, f"DAG validation failed: {dag_errs}"
    
    # Check that root node has no prerequisites, and subsequent nodes have valid prerequisites
    assert len(c[0]["prerequisites"]) == 0
    assert len(c[1]["prerequisites"]) > 0
