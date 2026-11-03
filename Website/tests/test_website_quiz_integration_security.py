"""
DeepLearnX - Integration Security & Regression Test Suite
Tests attempt token enforcement, replay protection, cross-student session isolation,
cross-domain concept isolation, remedial session verification, and question count consistency.
"""

import sys
import json
import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.main import app
from backend.app.database import get_db_connection
from backend.app.attempt_manager import create_assessment_attempt

client = TestClient(app)


def test_custom_assessment_missing_attempt_token_rejected():
    """Verifies that submitting a custom domain assessment without attempt_token is rejected."""
    submission = {
        "user_id": 3,
        "domain_id": "custom_robotics_slam_test123",
        "answers": [
            {"question_id": "custom_robotics_slam_test123_q1", "selected_option": "B", "response_time": 10.0, "confidence": 4}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "attempt token" in resp.json()["detail"].lower()


def test_invalid_attempt_token_signature_rejected():
    """Verifies that an attempt token with a forged or corrupted signature is rejected."""
    conn = get_db_connection()
    try:
        att = create_assessment_attempt(
            conn=conn,
            user_id=3,
            domain_id="deep_learning",
            question_ids=["q_ann_basic_1"]
        )
    finally:
        conn.close()

    # Tamper with the token signature
    parts = att["attempt_token"].split(".")
    tampered_token = f"{parts[0]}.forged_signature_xyz"

    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": tampered_token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 12.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "signature" in resp.json()["detail"].lower()


def test_expired_attempt_token_rejected():
    """Verifies that an expired attempt token is rejected."""
    conn = get_db_connection()
    try:
        att = create_assessment_attempt(
            conn=conn,
            user_id=3,
            domain_id="deep_learning",
            question_ids=["q_ann_basic_1"],
            expires_in_seconds=-100 # Already expired
        )
    finally:
        conn.close()

    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": att["attempt_token"],
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 12.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"].lower()


def test_replayed_attempt_token_rejected():
    """Verifies that submitting the same attempt token twice is rejected as a replay attack."""
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]

    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 4}
        ]
    }
    # 1. First submission succeeds
    resp1 = client.post("/api/assessment/submit", json=submission)
    assert resp1.status_code == 200

    # 2. Replay submission must fail with HTTP 400
    resp2 = client.post("/api/assessment/submit", json=submission)
    assert resp2.status_code == 400
    assert "replay" in resp2.json()["detail"].lower() or "already been submitted" in resp2.json()["detail"].lower()


def test_attempt_token_user_mismatch_rejected():
    """Verifies that using another student's attempt token is rejected."""
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3, # Issued to Rahul
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]

    submission = {
        "user_id": 2, # Submitted by Ananya
        "domain_id": "deep_learning",
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 4}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "user_id" in resp.json()["detail"].lower()


def test_remedial_submission_missing_original_session_rejected():
    """Verifies that remedial submission requires a valid original_session_id."""
    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "original_session_id": "",
        "target_concept_id": "ann_basics",
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 4}
        ]
    }
    resp = client.post("/api/remedial/submit", json=submission)
    assert resp.status_code == 400


def test_remedial_submission_cross_student_ownership_rejected():
    """Verifies that Student A cannot submit remediation against Student B's session (HTTP 403)."""
    # 1. Create a session for Student B (user_id=3)
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]
    submit_resp = client.post("/api/assessment/submit", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 4}
        ]
    })
    sess_id = submit_resp.json()["session_id"]

    # 2. Student A (user_id=2) tries to submit remediation against Student B's session
    rem_resp = client.post("/api/remedial/submit", json={
        "user_id": 2, # Cross-student tamper attempt!
        "domain_id": "deep_learning",
        "original_session_id": sess_id,
        "target_concept_id": "ann_basics",
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 15.0, "confidence": 4}
        ]
    })
    assert rem_resp.status_code == 403
    assert "another student" in rem_resp.json()["detail"].lower()


def test_remedial_submission_domain_mismatch_rejected():
    """Verifies that submitting remediation with mismatched domain is rejected (HTTP 400)."""
    # 1. Session created for deep_learning
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]
    submit_resp = client.post("/api/assessment/submit", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 4}
        ]
    })
    sess_id = submit_resp.json()["session_id"]

    # 2. Remedial submitted claiming domain is 'pokemon'
    rem_resp = client.post("/api/remedial/submit", json={
        "user_id": 3,
        "domain_id": "pokemon", # Domain mismatch!
        "original_session_id": sess_id,
        "target_concept_id": "ann_basics",
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 15.0, "confidence": 4}
        ]
    })
    assert rem_resp.status_code == 400
    assert "domain mismatch" in rem_resp.json()["detail"].lower()


def test_remedial_questions_cross_domain_isolation():
    """Verifies that requesting remedial questions strictly isolates by domain."""
    # When requesting an alien concept_id 'ann_basics' inside 'pokemon', it must return Pokemon questions, never DL questions!
    resp = client.get("/api/remedial/questions?concept_id=ann_basics&count=3&domain=pokemon")
    assert resp.status_code == 200
    data = resp.json()
    for q in data:
        assert q["domain_id"] == "pokemon"
        assert "Artificial Neural Networks" not in q["concept_name"]


def test_question_count_consistency_custom_domain_fetches_12_questions():
    """Verifies that custom domains retrieve all 12 generated questions."""
    # Check any existing custom domain in the database
    conn = get_db_connection()
    row = conn.execute("SELECT domain_id FROM questions WHERE domain_id LIKE 'custom_%' GROUP BY domain_id HAVING COUNT(*) >= 12 LIMIT 1;").fetchone()
    conn.close()

    if row:
        c_dom = row["domain_id"]
        resp = client.get(f"/api/assessment/questions?domain={c_dom}&limit=10&user_id=3")
        assert resp.status_code == 200
        # Must return full 12 questions despite limit=10 default!
        assert len(resp.json()) == 12
