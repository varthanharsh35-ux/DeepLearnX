"""
DEEPLEARNX UNIVERSAL CURRICULUM COVERAGE AND EMPTY QUESTION BANK TEST MATRIX
Verifies all 10 core scenarios specified in Phase 5:
1. Class 10 Chemistry: Chemical Reactions (retrieves preloaded questions)
2. Class 10 Chemistry: Acids, Bases and Salts (retrieves preloaded questions)
3. Class 10 Biology: Life Processes (retrieves Life Processes questions)
4. Class 10 Mathematics: Quadratic Equations (retrieves preloaded questions)
5. Unfamiliar university-level topic (synthesizes 12 questions)
6. Ambiguous topic (prompts disambiguation modal / requires scope)
7. Invalid topic (displays 400 validation error)
8. Topic with existing questions (Deep Learning Fundamentals)
9. Topic with 0 preloaded questions (Class 10 Chemistry: Periodic Classification of Elements, generates 12 questions)
10. Quota exhaustion scenario (displays exact 429 quota notice with offline fallback option)
"""

import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch

# Ensure paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.main import app, get_db_connection
from backend.app.curriculum_resolver import resolve_curriculum_domain
from backend.app.providers.base import LLMQuotaExhaustedError

client = TestClient(app)


def test_scenario_01_chemistry_chemical_reactions_preloaded():
    """Test 1: Class 10 NCERT Chemistry – Chemical Reactions retrieves preloaded questions with concept isolation."""
    topic = "Class 10 NCERT Chemistry \u2013 Chemical Reactions"
    res = resolve_curriculum_domain(topic)
    assert res.canonical_domain_id == "class10_chemistry"
    assert "chem_equations" in res.matched_concept_ids
    assert res.suggested_action == "use_preloaded"
    assert res.available_questions >= 9

    # Test API endpoint
    resp = client.get(f"/api/assessment/questions?limit=10&domain={topic}")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 9
    assert all(q["domain_id"] == "class10_chemistry" for q in questions)
    assert all(q["concept_id"] == "chem_equations" for q in questions)
    # Verify no answer key leakage
    assert all("correct_option" not in q for q in questions)
    # Check safe headers
    assert resp.headers.get("X-Resolved-Domain") == "class10_chemistry"
    assert resp.headers.get("X-Resolved-Concepts") == "chem_equations"


def test_scenario_02_chemistry_acids_bases_preloaded():
    """Test 2: Class 10 Chemistry: Acids, Bases and Salts retrieves preloaded questions without stoichiometry contamination."""
    topic = "Class 10 Chemistry: Acids, Bases and Salts"
    res = resolve_curriculum_domain(topic)
    assert res.canonical_domain_id == "class10_chemistry"
    assert "acids_bases" in res.matched_concept_ids

    resp = client.get(f"/api/assessment/questions?limit=10&domain={topic}")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 10
    assert all(q["concept_id"] == "acids_bases" for q in questions)
    # Verify no chemical equations or carbon questions mixed in
    assert not any(q["concept_id"] == "chem_equations" for q in questions)
    assert not any(q["concept_id"] == "carbon_compounds" for q in questions)


def test_scenario_03_biology_life_processes_preloaded():
    """Test 3: Class 10 Biology: Life Processes retrieves Life Processes questions with cross-subject isolation."""
    topic = "Class 10 Biology: Life Processes"
    res = resolve_curriculum_domain(topic)
    assert res.canonical_domain_id == "class10_biology"
    assert any("bio_" in c for c in res.matched_concept_ids)

    resp = client.get(f"/api/assessment/questions?limit=10&domain={topic}")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 10
    assert all(q["domain_id"] == "class10_biology" for q in questions)
    assert all(q["concept_id"] in ["bio_respiration", "bio_digestion", "bio_circulation"] for q in questions)


def test_scenario_04_math_quadratic_equations_preloaded():
    """Test 4: Class 10 Mathematics: Quadratic Equations retrieves preloaded questions."""
    topic = "Class 10 Mathematics: Quadratic Equations"
    res = resolve_curriculum_domain(topic)
    assert res.canonical_domain_id == "class10_math"
    assert "math_quadratics" in res.matched_concept_ids

    resp = client.get(f"/api/assessment/questions?limit=10&domain={topic}")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 8
    assert all(q["concept_id"] == "math_quadratics" for q in questions)


def test_scenario_05_unfamiliar_university_topic_synthesis():
    """Test 5: Unfamiliar university-level topic synthesizes exactly 12 questions with complete options and DAG."""
    topic = "Quantum Chromodynamics and Asymptotic Freedom"
    payload = {
        "topic_title": topic,
        "syllabus_text": "Quark-gluon interactions, strong coupling constant, asymptotic freedom at high energies, color charge confinement.",
        "api_provider": "offline",  # deterministic offline test
        "num_questions": 12
    }
    resp = client.post("/api/assessment/custom-generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["questions_count"] == 12
    assert len(data["concepts"]) >= 3
    assert data["provenance_label"] == "Offline-generated"

    # Verify attempt token issued
    assert "attempt_token" in data
    assert data["attempt_token"] is not None

    # Verify questions in database
    conn = get_db_connection()
    q_rows = conn.execute("SELECT * FROM questions WHERE domain_id = ?", (data["domain_id"],)).fetchall()
    conn.close()
    assert len(q_rows) == 12
    # Verify all options end with terminal punctuation
    for qr in q_rows:
        for opt_key in ["option_a", "option_b", "option_c", "option_d"]:
            txt = qr[opt_key].strip()
            assert txt[-1] in '.?!', f"Option {opt_key} missing terminal punctuation: {txt}"


def test_scenario_06_ambiguous_topic_detection():
    """Test 6: Ambiguous topic returns status 'ambiguous' and candidate academic scopes."""
    resp = client.post("/api/assessment/custom-generate", json={
        "topic_title": "Transformer",
        "syllabus_text": ""
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ambiguous"
    assert data["is_ambiguous"] is True
    assert len(data["ambiguities"]) >= 2
    texts = [f"{a.get('title', '')} {a.get('discipline', '')} {a.get('scope', '')}" for a in data["ambiguities"]]
    assert any("Electrical" in t or "Electromagnetic" in t for t in texts)
    assert any("Deep Learning" in t or "Machine Learning" in t or "Attention" in t for t in texts)


def test_scenario_07_invalid_topic_rejection():
    """Test 7: Meaningless or purely symbolic input is rejected with HTTP 400."""
    invalid_topics = [
        "1234567890",
        "$$$%%%###@@@",
        "   "
    ]
    for inv in invalid_topics:
        resp = client.post("/api/assessment/custom-generate", json={
            "topic_title": inv
        })
        assert resp.status_code in [400, 422], f"Expected 400/422 for '{inv}', got {resp.status_code}"


def test_scenario_08_canonical_topic_existing_questions():
    """Test 8: Topic with existing questions (Deep Learning Fundamentals) returns directly without synthesis."""
    resp = client.get("/api/assessment/questions?limit=15&domain=deep_learning")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 15
    assert all(q["domain_id"] == "deep_learning" for q in questions)


def test_scenario_09_unmatched_chapter_synthesis():
    """Test 9: Chapter with 0 preloaded questions (Periodic Classification) generates 12 questions."""
    topic = "Class 10 Chemistry: Periodic Classification of Elements"
    # First verify resolution recognizes unmatched chapter
    res = resolve_curriculum_domain(topic)
    assert res.canonical_domain_id == "class10_chemistry"
    assert res.matched_concept_ids == []
    assert res.suggested_action == "synthesize_chapter"

    # Now synthesize assessment for this chapter
    resp = client.post("/api/assessment/custom-generate", json={
        "topic_title": topic,
        "syllabus_text": "Mendeleev's periodic table, Modern periodic table, groups and periods, periodic trends in valency, atomic size, and metallic character.",
        "api_provider": "offline",
        "num_questions": 12
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["questions_count"] == 12
    assert "attempt_token" in data


def test_scenario_10_quota_exhaustion_handling_and_fallback():
    """Test 10: Quota exhaustion returns HTTP 429 with retry_after and does NOT silently replace with offline without student request."""
    # When live Gemini is requested but hits quota limit
    with patch("backend.app.providers.manager.LLMProviderManager.generate_structured") as mock_gen:
        mock_gen.side_effect = LLMQuotaExhaustedError("Daily quota exceeded", provider="gemini", retry_after="18h 45m", retry_after_seconds=67500)
        
        resp = client.post("/api/assessment/custom-generate", json={
            "topic_title": "Organic Chemistry: Carbonyl Condensations",
            "api_provider": "gemini",
            "require_live_llm": True
        })
        assert resp.status_code == 429
        data = resp.json()
        assert data["error"] == "quota_exhausted"
        assert data["quota_exhausted"] is True
        assert "18h 45m" in data["detail"] or "18h 45m" in data.get("retry_after", "")

    # Now simulate student clicking offline fallback button
    fb_resp = client.post("/api/assessment/custom-generate", json={
        "topic_title": "Organic Chemistry: Carbonyl Condensations",
        "api_provider": "offline",
        "num_questions": 12
    })
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert fb_data["status"] == "success"
    assert fb_data["provenance_label"] == "Offline-generated"
    assert fb_data["questions_count"] == 12


def test_assessment_submission_and_learning_gain():
    """Verifies that an assessment on a curriculum topic can be submitted and produce learning gains."""
    # 1. Fetch preloaded questions for Chemical Reactions
    topic = "Class 10 NCERT Chemistry \u2013 Chemical Reactions"
    q_resp = client.get(f"/api/assessment/questions?limit=10&domain={topic}&user_id=1")
    assert q_resp.status_code == 200
    questions = q_resp.json()
    q_ids = [q["id"] for q in questions]

    # 2. Start attempt
    att_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 1,
        "domain_id": "class10_chemistry",
        "question_ids": q_ids
    })
    assert att_resp.status_code == 200
    att_data = att_resp.json()
    attempt_token = att_data["attempt_token"]
    attempt_id = att_data["attempt_id"]

    # 3. Submit assessment
    answers = [
        {
            "question_id": qid,
            "selected_option": "A",
            "response_time": 10.0,
            "confidence": 4
        }
        for qid in q_ids
    ]
    sub_resp = client.post("/api/assessment/submit", json={
        "user_id": 1,
        "domain_id": "class10_chemistry",
        "attempt_id": attempt_id,
        "attempt_token": attempt_token,
        "answers": answers
    })
    assert sub_resp.status_code == 200
    res_data = sub_resp.json()
    assert "score" in res_data
    assert "session_id" in res_data
    assert res_data["domain_id"] == "class10_chemistry"
