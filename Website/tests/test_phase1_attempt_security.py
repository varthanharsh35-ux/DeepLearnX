"""
Test Suite for Phase 1: Secure API & Server-Issued Assessment Attempts.
Verifies cryptographic attempt token issuance, replay protection, expiration enforcement,
tamper rejection, and backward compatibility.
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
from backend.app.attempt_manager import create_assessment_attempt
from backend.app.database import get_db_connection

client = TestClient(app)


def test_start_attempt_endpoint_issues_valid_signed_token():
    """Verifies POST /api/assessment/start-attempt issues a cryptographically signed token."""
    payload = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1", "q_ann_concept_1", "q_ann_app_1"],
        "expires_in_seconds": 3600
    }
    resp = client.post("/api/assessment/start-attempt", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "attempt_id" in data
    assert "attempt_token" in data
    assert data["attempt_id"].startswith("att_")
    assert "." in data["attempt_token"]
    assert data["user_id"] == 3
    assert data["domain_id"] == "deep_learning"
    assert data["question_count"] == 3


def test_get_questions_attaches_attempt_headers_for_user():
    """Verifies GET /api/assessment/questions attaches attempt headers when user_id is provided."""
    resp = client.get("/api/assessment/questions?domain=deep_learning&limit=5&user_id=3")
    assert resp.status_code == 200
    assert "X-Assessment-Attempt-Id" in resp.headers
    assert "X-Assessment-Attempt-Token" in resp.headers
    assert resp.headers["X-Assessment-Attempt-Id"].startswith("att_")
    assert "." in resp.headers["X-Assessment-Attempt-Token"]


def test_submit_with_valid_attempt_token_succeeds_and_prevents_replay():
    """Verifies valid submission succeeds, and subsequent replay submission is rejected with HTTP 400."""
    # 1. Start an attempt
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1", "q_ann_concept_1", "q_ann_app_1"]
    })
    assert start_resp.status_code == 200
    att_data = start_resp.json()
    token = att_data["attempt_token"]
    att_id = att_data["attempt_id"]

    # 2. First submission with valid token -> Must succeed
    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_id": att_id,
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 20.0, "confidence": 4},
            {"question_id": "q_ann_concept_1", "selected_option": "B", "response_time": 25.0, "confidence": 3},
            {"question_id": "q_ann_app_1", "selected_option": "C", "response_time": 40.0, "confidence": 4}
        ]
    }
    resp1 = client.post("/api/assessment/submit", json=submission)
    assert resp1.status_code == 200
    res1_data = resp1.json()
    assert res1_data["status"] == "success"
    assert res1_data.get("attempt_id") == att_id

    # 3. Replay attack: Re-submitting the same attempt token -> Must be rejected with HTTP 400
    resp2 = client.post("/api/assessment/submit", json=submission)
    assert resp2.status_code == 400
    assert "already been submitted" in resp2.json()["detail"].lower()


def test_submit_with_tampered_token_is_rejected():
    """Verifies that tampering with the token signature or payload causes immediate HTTP 400 rejection."""
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]
    # Tamper with the token
    tampered_token = token[:-4] + "XXXX"

    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": tampered_token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "signature verification failed" in resp.json()["detail"].lower()


def test_submit_with_expired_token_is_rejected():
    """Verifies that an expired attempt token is rejected with HTTP 400."""
    conn = get_db_connection()
    try:
        att = create_assessment_attempt(
            conn=conn,
            user_id=3,
            domain_id="deep_learning",
            question_ids=["q_ann_basic_1"],
            expires_in_seconds=-60  # Already expired
        )
    finally:
        conn.close()

    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "attempt_token": att["attempt_token"],
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"].lower()


def test_submit_with_user_mismatch_is_rejected():
    """Verifies that submitting with another user's attempt token is rejected with HTTP 400."""
    start_resp = client.post("/api/assessment/start-attempt", json={
        "user_id": 3,
        "domain_id": "deep_learning",
        "question_ids": ["q_ann_basic_1"]
    })
    token = start_resp.json()["attempt_token"]

    submission = {
        "user_id": 4, # Mismatch with token issued to user 3
        "domain_id": "deep_learning",
        "attempt_token": token,
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 10.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 400
    assert "user_id" in resp.json()["detail"].lower()


def test_legacy_submission_without_token_preserves_compatibility():
    """Verifies that legacy submissions without attempt tokens remain supported for backward compatibility."""
    submission = {
        "user_id": 3,
        "domain_id": "deep_learning",
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 15.0, "confidence": 5}
        ]
    }
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
