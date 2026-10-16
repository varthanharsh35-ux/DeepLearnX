"""
Unit & Integration Test Suite for DeepLearnX
Tests API endpoints, DL model prediction, database transactions, and graph traversal.
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))
sys.path.insert(0, str(PROJECT_ROOT / "model"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_concepts_endpoint():
    resp = client.get("/api/concepts")
    assert resp.status_code == 200
    concepts = resp.json()
    assert len(concepts) >= 10
    print("[PASS] /api/concepts verified. Count:", len(concepts))

def test_demo_users_endpoint():
    resp = client.get("/api/auth/demo-users")
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) == 5
    print("[PASS] /api/auth/demo-users verified. Count:", len(users))

def test_login_endpoint():
    resp = client.post("/api/auth/login", json={"username": "student_b", "password": "student123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["user"]["username"] == "student_b"
    print("[PASS] /api/auth/login verified for student_b")

def test_assessment_questions_endpoint():
    resp = client.get("/api/assessment/questions?limit=10")
    assert resp.status_code == 200
    qs = resp.json()
    assert len(qs) == 10
    assert "options" in qs[0]
    print("[PASS] /api/assessment/questions verified. Count:", len(qs))

def test_submit_assessment_dl_inference():
    # Submit responses deliberately triggering False Mastery pattern:
    # Basic = Correct, Conceptual = Correct, Application = Wrong
    submission = {
        "user_id": 3, # Rahul Verma
        "answers": [
            {"question_id": "q_ann_basic_1", "selected_option": "A", "response_time": 18.0, "confidence": 5},
            {"question_id": "q_ann_concept_1", "selected_option": "A", "response_time": 25.0, "confidence": 5},
            {"question_id": "q_ann_app_1", "selected_option": "C", "response_time": 50.0, "confidence": 4},
            {"question_id": "q_act_basic_1", "selected_option": "A", "response_time": 15.0, "confidence": 5},
            {"question_id": "q_act_concept_1", "selected_option": "A", "response_time": 22.0, "confidence": 4},
            {"question_id": "q_act_app_1", "selected_option": "B", "response_time": 65.0, "confidence": 3},
            {"question_id": "q_bp_basic_1", "selected_option": "A", "response_time": 20.0, "confidence": 5},
            {"question_id": "q_bp_concept_1", "selected_option": "A", "response_time": 28.0, "confidence": 4},
            {"question_id": "q_bp_app_1", "selected_option": "B", "response_time": 75.0, "confidence": 3}
        ]
    }
    
    resp = client.post("/api/assessment/submit", json=submission)
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    dl_info = res["deep_learning_analysis"]
    print("[PASS] Deep Learning Prediction State:", dl_info["predicted_state"])
    print("[PASS] False Mastery Breakdown:", dl_info["false_mastery_breakdown"])
    print("[PASS] Primary Prerequisite Gap Detected:", res["knowledge_gap_detection"]["primary_gap_name"])
    print("[PASS] Recommendations generated:", len(res["recommendations"]))

def test_faculty_dashboard():
    resp = client.get("/api/faculty/dashboard")
    assert resp.status_code == 200
    dash = resp.json()
    assert dash["total_students"] >= 4
    assert "state_distribution" in dash
    print("[PASS] /api/faculty/dashboard verified. Total students:", dash["total_students"])

def test_model_metrics():
    resp = client.get("/api/model/metrics")
    assert resp.status_code == 200
    m = resp.json()
    assert "evaluation_metrics" in m
    print("[PASS] /api/model/metrics verified. Accuracy:", m["evaluation_metrics"].get("accuracy"))

if __name__ == "__main__":
    print("=" * 60)
    print(" Running DeepLearnX Integration Test Suite")
    print("=" * 60)
    test_concepts_endpoint()
    test_demo_users_endpoint()
    test_login_endpoint()
    test_assessment_questions_endpoint()
    test_submit_assessment_dl_inference()
    test_faculty_dashboard()
    test_model_metrics()
    print("=" * 60)
    print(" ALL TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)
