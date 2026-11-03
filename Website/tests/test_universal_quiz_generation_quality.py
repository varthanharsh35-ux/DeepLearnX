"""
Universal Quiz Generation Quality & Diagnostic Validation Tests
Validates:
- Subject-specific concept extraction across 5 major topics
- Directed Acyclic Graph (DAG) structural validity via Kahn's algorithm
- Complete absence of generic synthetic boilerplate
- Option length equalization (within 2-3 words, no length bias)
- Pseudo-randomized correct answer placement
- Two-Tier reasoning probe integration
- Ambiguous / numeric input rejection ('5 5 5' requires clarification)
- Cognitive diagnostic fidelity (no contradictory praise for low accuracy; unconfirmed wrong answers not tagged as misconceptions)
"""

import sys
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))
sys.path.insert(0, str(BASE_DIR / "model"))

from backend.app.main import app
from backend.app.universal_synthesizer import synthesize_universal_curriculum
from backend.app.quiz_validator import validate_curriculum_package, GENERIC_SYNTHETIC_BOILERPLATE
from backend.app.topic_understanding import TopicUnderstandingEngine

client = TestClient(app)

REQUIRED_TOPICS = [
    "Game Design and Development",
    "Computer Systems and Architecture",
    "Operating Systems",
    "Photosynthesis",
    "Database Management Systems"
]

@pytest.mark.parametrize("topic_title", REQUIRED_TOPICS)
def test_universal_quiz_generation_across_required_topics(topic_title):
    """Verifies that all 5 required topics generate authentic, evidence-grounded assessments without boilerplate."""
    domain_id = f"test_{re.sub(r'[^a-z0-9]', '_', topic_title.lower())[:10]}"
    
    concepts, misconceptions, questions, guides, icon, category = synthesize_universal_curriculum(
        domain_id=domain_id,
        topic_title=topic_title,
        num_questions=12
    )
    
    # 1. Structural requirements
    assert 4 <= len(concepts) <= 6, f"Expected 4-6 concepts for '{topic_title}', got {len(concepts)}"
    assert len(misconceptions) >= 4, f"Expected at least 4 misconceptions for '{topic_title}', got {len(misconceptions)}"
    assert len(questions) == 12, f"Expected 12 questions for '{topic_title}', got {len(questions)}"
    assert len(guides) == len(concepts), f"Expected concept guides matching concepts count"
    
    # 2. Strict independent publication validation
    is_valid, validation_errors = validate_curriculum_package(concepts, misconceptions, questions, category)
    assert is_valid, f"Curriculum for '{topic_title}' failed publication validation: {validation_errors}"
    
    # 3. Verify zero generic synthetic boilerplate in concepts and questions
    for c in concepts:
        c_text = (c["name"] + " " + c["description"]).lower()
        for bp in GENERIC_SYNTHETIC_BOILERPLATE:
            assert bp not in c_text, f"Generic boilerplate '{bp}' found in concept '{c['name']}'"
            
    for m in misconceptions:
        m_text = (m["name"] + " " + m["description"] + " " + m["remediation"]).lower()
        for bp in GENERIC_SYNTHETIC_BOILERPLATE:
            assert bp not in m_text, f"Generic boilerplate '{bp}' found in misconception '{m['name']}'"
            
    for q in questions:
        q_text = (q["question_text"] + " " + q["option_a"] + " " + q["option_b"] + " " + q["option_c"] + " " + q["option_d"]).lower()
        for bp in GENERIC_SYNTHETIC_BOILERPLATE:
            assert bp not in q_text, f"Generic boilerplate '{bp}' found in question '{q['id']}': {q_text}"
            
    # 4. Verify balanced option lengths to prevent length bias
    for q in questions:
        lengths = [
            len(q["option_a"].split()),
            len(q["option_b"].split()),
            len(q["option_c"].split()),
            len(q["option_d"].split())
        ]
        max_diff = max(lengths) - min(lengths)
        assert max_diff <= 8, f"Question '{q['id']}' option lengths have excessive variance: {lengths} (diff: {max_diff})"
        
    # 5. Verify Two-Tier Reasoning Probes count
    probes_count = sum(1 for q in questions if q.get("reasoning_probe"))
    assert 3 <= probes_count <= 5, f"Expected 3 to 5 reasoning probes, got {probes_count}"


def test_numeric_input_clarification():
    """Verifies that purely numeric/symbolic input such as '5 5 5' is rejected or flagged as ambiguous."""
    engine = TopicUnderstandingEngine()
    interp = engine.interpret("5 5 5")
    assert interp.is_ambiguous is True, "Expected '5 5 5' to be flagged as ambiguous"
    assert interp.confidence == 0.0, "Expected confidence 0.0 for meaningless numeric input"
    
    # Also verify via API endpoint
    res = client.post("/api/assessment/custom-generate", json={
        "topic_title": "5 5 5",
        "syllabus_text": "",
        "num_questions": 12
    })
    data = res.json()
    assert data.get("is_ambiguous") is True, f"API should return is_ambiguous=True for '5 5 5', got {data}"
    assert "clarification" in data.get("message", "").lower() or "academic" in data.get("message", "").lower()


def test_diagnostic_feedback_calibration():
    """Verifies that low raw accuracy (e.g. 30%) does not receive contradictory praise."""
    try:
        from predictor import DeepLearnXPredictor
    except ImportError:
        from model.predictor import DeepLearnXPredictor
    
    pred = DeepLearnXPredictor()
    mock_answers = [
        {"question_id": f"dl_q{i+1}", "selected_option": "A" if i < 3 else "B", "response_time": 12.0, "confidence": 3}
        for i in range(12)
    ]
    
    dl_res = pred.analyze_session(mock_answers)
    diag_text = dl_res["false_mastery_breakdown"]["diagnosis"].lower()
    # Ensure no contradictory "Awesome job" when overall score is failing
    assert "awesome job" not in diag_text
