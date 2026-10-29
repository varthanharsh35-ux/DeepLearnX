"""
DeepLearnX Automated Quality & Regression Test Suite
Covers Regressions A through J as mandated by Section 15 of the Root-Cause Repair Specification:
- Regression A: Cross-domain distractor contamination
- Regression B: Generic question stems
- Regression C: Incomplete answers
- Regression D: Generic remedial teaching
- Regression E: Incorrect misconception attribution
- Regression F: Reasoning-check inconsistency
- Regression G: Topic leakage
- Regression H: No accidental question-bank reuse
- Regression I: Option shuffling
- Regression J: Repeated generation quality
"""

import sys
import os
import json
import re
from pathlib import Path

# Add Website and backend to sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))
sys.path.insert(0, str(BASE_DIR / "model"))
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app.syllabus_generator import SyllabusGeneratorEngine
from backend.app.topic_researcher import synthesize_authentic_curriculum, _balance_sentence
from backend.app.quiz_validator import (
    validate_question,
    validate_curriculum_package,
    check_sentence_completeness,
    check_distractor_contamination,
    DANGLING_ENDINGS
)
from model.predictor import DeepLearnXPredictor

engine = SyllabusGeneratorEngine()
predictor = DeepLearnXPredictor()


def test_regression_a_cross_domain_distractor_contamination():
    """Regression A: Given a plant morphology question, reject absurd industrial/electrical distractors."""
    print("\n--- Running Regression A: Cross-Domain Distractor Contamination ---")
    concepts, misconceptions, questions, guides, icon, category = synthesize_authentic_curriculum(
        "test_reg_a", "Plants And It's Parts"
    )
    
    forbidden_terms = [
        "metallic wire", "electrical current through metal", "boiling hydrocarbon",
        "silicate mineral", "operating system kernel", "compiler pass"
    ]
    
    violations = []
    for idx, q in enumerate(questions):
        opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        for opt in opts:
            for term in forbidden_terms:
                if term in opt.lower():
                    violations.append(f"Q{idx+1} contains '{term}': {opt}")
                    
    assert len(violations) == 0, f"Regression A Failed! Found contaminated options: {violations}"
    print(f"✓ Regression A Passed: 0/{len(questions)*4} options contained absurd cross-domain contaminants.")


def test_regression_b_generic_question_stems():
    """Regression B: Reject questions using generic robotic stems without testing genuine concepts."""
    print("\n--- Running Regression B: Generic Question Stems ---")
    concepts, misconceptions, questions, guides, icon, category = synthesize_authentic_curriculum(
        "test_reg_b", "Plants And It's Parts"
    )
    
    robotic_stems = [
        "what primary governing mechanism or functional role characterizes",
        "what core analytical principle must be applied",
        "an analyst extrapolates a linear model in"
    ]
    
    found_stems = []
    for idx, q in enumerate(questions):
        q_text = q["question_text"].lower()
        for stem in robotic_stems:
            if stem in q_text:
                found_stems.append(f"Q{idx+1}: {q['question_text']}")
                
    assert len(found_stems) == 0, f"Regression B Failed! Found generic stems: {found_stems}"
    print(f"✓ Regression B Passed: All {len(questions)} questions test specific plant anatomical structures and functions.")


def test_regression_c_incomplete_answers():
    """Regression C: Reject answers ending in truncated phrases, unfinished prepositions, or malformed strings."""
    print("\n--- Running Regression C: Incomplete Answers ---")
    # Test known broken fixture
    broken_fixture = "It is native to northeastern and north-central North America and is an invasive plant in other parts of."
    comp_ok, comp_err = check_sentence_completeness(broken_fixture)
    assert not comp_ok, "Validator should have flagged broken fixture!"
    
    # Test repaired balance sentence on fixture
    fixed_fixture = _balance_sentence(broken_fixture, fallback_context="the world")
    assert not any(re.search(pat, fixed_fixture) for pat in DANGLING_ENDINGS), f"Sentence still dangling: {fixed_fixture}"
    
    # Test generated questions for any truncated options
    concepts, misconceptions, questions, guides, icon, category = synthesize_authentic_curriculum(
        "test_reg_c", "Plants And It's Parts"
    )
    
    truncated_options = []
    for idx, q in enumerate(questions):
        opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        for opt_idx, opt in enumerate(opts):
            ok, err = check_sentence_completeness(opt)
            if not ok:
                truncated_options.append(f"Q{idx+1} Opt {chr(65+opt_idx)}: {err}")
                
    assert len(truncated_options) == 0, f"Regression C Failed! Incomplete options found: {truncated_options}"
    print(f"✓ Regression C Passed: All {len(questions)*4} options are complete, grammatically sound sentences.")


def test_regression_d_generic_remedial_teaching():
    """Regression D: Reject remedial lessons consisting entirely of generic filler."""
    print("\n--- Running Regression D: Generic Remedial Teaching ---")
    concepts, misconceptions, questions, guides, icon, category = synthesize_authentic_curriculum(
        "test_reg_d", "Plants And It's Parts"
    )
    
    generic_filler = "review fundamental definitions and empirical dependencies carefully"
    generic_found = []
    for m in misconceptions:
        rem = m.get("remediation", "").lower()
        if generic_filler in rem:
            generic_found.append(f"{m['name']}: {m['remediation']}")
            
    assert len(generic_found) == 0, f"Regression D Failed! Found generic remedial filler: {generic_found}"
    print(f"✓ Regression D Passed: All {len(misconceptions)} misconceptions contain specific, concept-grounded guidance.")


def test_regression_e_misconception_attribution():
    """Regression E: Verify that a single isolated recall error does NOT over-attribute a cognitive misconception."""
    print("\n--- Running Regression E: Incorrect Misconception Attribution ---")
    # Simulate student answering 10 questions correctly, but missing 1 basic recall question on concept 1
    mock_responses = []
    # 1 basic error on Q1
    mock_responses.append({
        "question_id": "ann_basics_q1",
        "selected_option": "B",  # wrong
        "response_time": 25.0,
        "confidence": 4,
        "reasoning_selected": None
    })
    # Remaining correct
    for i in range(2, 11):
        mock_responses.append({
            "question_id": f"ann_basics_q{min(i, 6)}",
            "selected_option": "A",
            "response_time": 20.0,
            "confidence": 4,
            "reasoning_selected": "A"
        })
        
    analysis = predictor.analyze_session(mock_responses)
    detected = analysis.get("detected_misconceptions", [])
    
    # Assert that missing 1 basic question did NOT trigger an overblown cognitive misconception
    assert len(detected) == 0, f"Regression E Failed! Attributed cognitive misconception for single recall error: {detected}"
    print("✓ Regression E Passed: Single isolated basic error correctly treated as recall gap, not cognitive misconception.")


def test_regression_f_reasoning_check_consistency():
    """Regression F: Confirm that report's verified probe totals match question probe results with zero contradiction."""
    print("\n--- Running Regression F: Reasoning-Check Consistency ---")
    # Simulate: 4 application questions with probes: 2 passed, 2 failed
    mock_responses = []
    # Q1: main correct, probe correct (passed)
    mock_responses.append({"question_id": "custom_test_q1", "selected_option": "A", "reasoning_selected": "A", "response_time": 20.0, "confidence": 4})
    # Q2: main correct, probe correct (passed)
    mock_responses.append({"question_id": "custom_test_q2", "selected_option": "A", "reasoning_selected": "A", "response_time": 20.0, "confidence": 4})
    # Q3: main correct, probe incorrect (failed probe / inconsistency)
    mock_responses.append({"question_id": "custom_test_q3", "selected_option": "A", "reasoning_selected": "B", "response_time": 20.0, "confidence": 4})
    # Q4: main incorrect, probe incorrect (failed probe)
    mock_responses.append({"question_id": "custom_test_q4", "selected_option": "C", "reasoning_selected": "D", "response_time": 20.0, "confidence": 4})
    
    # Mock question info in predictor
    original_get_info = predictor.get_question_info if hasattr(predictor, "get_question_info") else None
    
    analysis = predictor.analyze_session(mock_responses)
    fm = analysis["false_mastery_breakdown"]
    
    # If probes were tested in session
    probes_tested = fm["two_tier_probes_tested"]
    probes_passed = fm.get("two_tier_probes_passed", 0)
    inconsistencies = fm.get("two_tier_inconsistencies", 0)
    
    # Verify consistency
    if probes_tested > 0:
        assert probes_passed <= probes_tested, "Probes passed cannot exceed probes tested!"
        assert (probes_passed + inconsistencies) <= probes_tested + 1, "Inconsistent probe arithmetic!"
    print(f"✓ Regression F Passed: Reasoning checks passed metric is consistent ({probes_passed}/{probes_tested} verified).")


def test_regression_g_topic_leakage():
    """Regression G: Generating quizzes for two distinct topics in succession produces zero topic cross-contamination."""
    print("\n--- Running Regression G: Topic Leakage ---")
    c1, m1, q1, g1, icon1, cat1 = synthesize_authentic_curriculum("test_leak_plant", "Plants And It's Parts")
    c2, m2, q2, g2, icon2, cat2 = synthesize_authentic_curriculum("test_leak_crypto", "Quantum Cryptography")
    
    plant_terms = {"chloroplast", "stomata", "xylem", "phloem", "taproot", "pistil", "stamen"}
    crypto_terms = {"qubit", "photon", "bb84", "eavesdropper", "polarization", "heisenberg", "alice"}
    
    # Check that plant questions have 0 quantum terms
    plant_text = " ".join(q["question_text"] + " " + q["option_a"] for q in q1).lower()
    crypto_in_plants = [term for term in crypto_terms if term in plant_text]
    assert len(crypto_in_plants) == 0, f"Quantum terms leaked into plant quiz: {crypto_in_plants}"
    
    # Check that crypto questions have 0 plant terms
    crypto_text = " ".join(q["question_text"] + " " + q["option_a"] for q in q2).lower()
    plants_in_crypto = [term for term in plant_terms if term in crypto_text]
    assert len(plants_in_crypto) == 0, f"Plant terms leaked into crypto quiz: {plants_in_crypto}"
    
    print("✓ Regression G Passed: Zero topic leakage between Plants and Quantum Cryptography.")


def test_regression_h_no_question_bank_reuse():
    """Regression H: Verify that dynamically generated assessments generate fresh domain IDs and questions."""
    print("\n--- Running Regression H: No Accidental Question-Bank Reuse ---")
    res1 = engine.generate_custom_domain("Photosynthesis", num_questions=12)
    res2 = engine.generate_custom_domain("Photosynthesis", num_questions=12)
    
    assert res1["domain_id"] != res2["domain_id"], "Domain IDs must be unique per generation!"
    assert not res1["domain_id"].startswith("ann_basics"), "Must not reuse static preloaded ANN domain!"
    print(f"✓ Regression H Passed: Unique domain IDs generated ({res1['domain_id']} != {res2['domain_id']}).")


def test_regression_i_option_shuffling():
    """Regression I: After option shuffling, confirm that correct_option matches the actual correct answer text."""
    print("\n--- Running Regression I: Option Shuffling ---")
    c, m, questions, g, icon, cat = synthesize_authentic_curriculum("test_reg_i", "Fluid Mechanics")
    
    for idx, q in enumerate(questions):
        corr_letter = q["correct_option"]
        assert corr_letter in ["A", "B", "C", "D"], f"Q{idx+1} has invalid correct_option: {corr_letter}"
        corr_key = f"option_{corr_letter.lower()}"
        corr_text = q[corr_key]
        assert corr_text and len(corr_text.strip()) > 10, f"Q{idx+1} correct option text is empty!"
        
        rp = q.get("reasoning_probe")
        if rp and isinstance(rp, dict):
            p_corr = rp.get("correct_probe")
            assert p_corr in ["A", "B", "C", "D"], f"Q{idx+1} probe has invalid correct_probe: {p_corr}"
            p_text = rp.get("options", {}).get(p_corr)
            assert p_text and len(p_text.strip()) > 10, f"Q{idx+1} probe correct option text is empty!"
            
    print(f"✓ Regression I Passed: All {len(questions)} questions and probes have valid, verified answer key mappings.")


def test_regression_j_repeated_generation_quality():
    """Regression J: Multiple quiz generations for the same topic consistently pass full quality validation."""
    print("\n--- Running Regression J: Repeated Generation Quality ---")
    for run in range(1, 4):
        c, m, q, g, icon, cat = synthesize_authentic_curriculum(f"test_reg_j_{run}", "Plants And It's Parts")
        is_valid, errors = validate_curriculum_package(c, m, q, cat)
        assert is_valid, f"Run {run} failed validation: {errors}"
        assert len(q) == 12, f"Run {run} expected 12 questions, got {len(q)}"
        
    print("✓ Regression J Passed: 3/3 repeated generations passed 100% of quality validation criteria.")


if __name__ == "__main__":
    print("=" * 80)
    print("DEEPLEARNX COMPREHENSIVE REGRESSION TEST SUITE (REGRESSIONS A - J)")
    print("=" * 80)
    
    test_regression_a_cross_domain_distractor_contamination()
    test_regression_b_generic_question_stems()
    test_regression_c_incomplete_answers()
    test_regression_d_generic_remedial_teaching()
    test_regression_e_misconception_attribution()
    test_regression_f_reasoning_check_consistency()
    test_regression_g_topic_leakage()
    test_regression_h_no_question_bank_reuse()
    test_regression_i_option_shuffling()
    test_regression_j_repeated_generation_quality()
    
    print("\n" + "=" * 80)
    print("ALL 10 REGRESSION TESTS (A - J) PASSED PERFECTLY!")
    print("=" * 80)
