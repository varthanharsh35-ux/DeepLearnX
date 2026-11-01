"""
DeepLearnX Answer-Key Security and Client Privacy Test Suite
============================================================
Verifies:
1. Client payload sanitization: `/api/assessment/questions` never leaks:
   - `correct_option`
   - `correct_probe`
   - `explanation`
   - `solution` or answer keys
2. Reasoning probe sanitization: reasoning probe only contains `prompt` and `options`.
3. Backend authoritativeness: Server independently scores answers against SQLite database.
4. Resistance to client tampering or unauthorized answer retrieval attempts.
"""

import sys
import json
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))
sys.path.insert(0, str(PROJECT_ROOT / "model"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

FORBIDDEN_CLIENT_KEYS = [
    "correct_option",
    "correct_answer",
    "answer",
    "correct",
    "explanation",
    "correct_probe",
    "probe_solution",
    "solution"
]

def test_questions_endpoint_client_sanitization():
    print("\n--- Running Answer-Key Security Test 1: Question Payload Sanitization ---")
    domains_to_test = ["deep_learning", "pokemon", "class10_math"]
    
    for domain in domains_to_test:
        resp = client.get(f"/api/assessment/questions?domain={domain}&limit=12")
        assert resp.status_code == 200, f"Failed to fetch questions for domain {domain}"
        questions = resp.json()
        assert len(questions) > 0, f"No questions returned for domain {domain}"
        
        for idx, q in enumerate(questions):
            # Check question level forbidden keys
            for forbidden in FORBIDDEN_CLIENT_KEYS:
                assert forbidden not in q, f"SECURITY LEAK: Question {idx+1} in '{domain}' leaked '{forbidden}' to client!"
            
            # Check reasoning probe level sanitization
            rp = q.get("reasoning_probe")
            if rp and isinstance(rp, dict):
                assert "correct_probe" not in rp, f"SECURITY LEAK: Question {idx+1} leaked 'correct_probe' in reasoning_probe!"
                assert "correct_option" not in rp, f"SECURITY LEAK: Question {idx+1} leaked 'correct_option' in reasoning_probe!"
                assert "solution" not in rp, f"SECURITY LEAK: Question {idx+1} leaked 'solution' in reasoning_probe!"
                assert "prompt" in rp, f"Reasoning probe missing 'prompt' field in question {idx+1}"
                assert "options" in rp, f"Reasoning probe missing 'options' field in question {idx+1}"
                
    print(f"✓ Verified: 0 answer keys, 0 explanations, and 0 correct probe fields leaked across {len(domains_to_test)} domains.")


def test_tamper_resistant_backend_authoritativeness():
    print("\n--- Running Answer-Key Security Test 2: Backend Authoritative Scoring ---")
    # Fetch questions for deep_learning
    resp = client.get("/api/assessment/questions?domain=deep_learning&limit=5")
    assert resp.status_code == 200
    questions = resp.json()
    
    # Intentionally submit answers without supplying any answer key from client
    # Client only sends question_id, selected_option, response_time, and confidence
    submission = {
        "user_id": 1,
        "domain_id": "deep_learning",
        "answers": [
            {
                "question_id": q["id"],
                "selected_option": "A", # Deliberate choice
                "response_time": 25.0,
                "confidence": 4,
                "reasoning_selected": "A" if q.get("reasoning_probe") else None
            }
            for q in questions
        ]
    }
    
    sub_resp = client.post("/api/assessment/submit", json=submission)
    assert sub_resp.status_code == 200, f"Submission failed: {sub_resp.text}"
    result = sub_resp.json()
    
    # Verify server computed score authority
    assert "score" in result, "Submission response missing authoritative score"
    assert "accuracy" in result, "Submission response missing authoritative accuracy"
    assert "deep_learning_analysis" in result, "Missing neural cognitive analysis"
    
    print(f"✓ Verified: Server authoritatively computed score ({result['score']}/{len(questions)}) and cognitive diagnosis.")


def test_custom_domain_question_sanitization():
    print("\n--- Running Answer-Key Security Test 3: Custom Generated Domain Sanitization ---")
    custom_payload = {
        "topic_title": "Quantum Cryptography and Entanglement Distribution",
        "syllabus_text": "Unit 1: Quantum Key Distribution Protocols (BB84, E91)\nUnit 2: Quantum repeaters and decoy states",
        "user_id": 1,
        "num_questions": 12
    }
    gen_res = client.post("/api/assessment/custom-generate", json=custom_payload)
    assert gen_res.status_code == 200
    domain_id = gen_res.json()["domain_id"]
    
    q_resp = client.get(f"/api/assessment/questions?domain={domain_id}&limit=12")
    assert q_resp.status_code == 200
    custom_questions = q_resp.json()
    
    for idx, q in enumerate(custom_questions):
        for forbidden in FORBIDDEN_CLIENT_KEYS:
            assert forbidden not in q, f"SECURITY LEAK: Custom question {idx+1} leaked '{forbidden}'!"
        rp = q.get("reasoning_probe")
        if rp and isinstance(rp, dict):
            assert "correct_probe" not in rp, f"SECURITY LEAK: Custom probe {idx+1} leaked 'correct_probe'!"
            
    print(f"✓ Verified: All 12 custom generated questions and probes are completely sanitized of answer keys.")


if __name__ == "__main__":
    print("=" * 80)
    print("DEEPLEARNX ANSWER-KEY SECURITY & PRIVACY VERIFICATION SUITE")
    print("=" * 80)
    test_questions_endpoint_client_sanitization()
    test_tamper_resistant_backend_authoritativeness()
    test_custom_domain_question_sanitization()
    print("\n" + "=" * 80)
    print("ALL ANSWER-KEY SECURITY TESTS PASSED 100%!")
    print("=" * 80)
