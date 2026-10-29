"""
Automated End-to-End Verification Test
Verifies:
1. Question Bank Expansion and Non-Repeating Question Rotation across consecutive attempts.
2. Custom Syllabus / Topic Generator:
   - Topic decomposition into DAG concepts
   - 12 tiered diagnostic questions with Two-Tier reasoning probes
   - Full PyTorch cognitive model inference and recommendation synthesis
   - Interactive DAG knowledge map rendering
"""

import sys
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))
sys.path.insert(0, str(BASE_DIR / "model"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_unseen_question_rotation():
    print("\n--- TEST 1: Unseen Question Rotation Engine ---")
    user_id = 999 # Dedicated test user
    domain = "class10_math"

    # Clean prior test responses for this user
    conn = sqlite3.connect(str(BASE_DIR / "database" / "deeplearnx.db"))
    conn.execute("DELETE FROM student_responses WHERE session_id IN (SELECT id FROM assessment_sessions WHERE user_id = ?)", (user_id,))
    conn.execute("DELETE FROM assessment_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    # Attempt 1: Fetch 10 questions
    res1 = client.get(f"/api/assessment/questions?limit=10&domain={domain}&user_id={user_id}")
    assert res1.status_code == 200
    q_set_1 = res1.json()
    q_ids_1 = [q["id"] for q in q_set_1]
    assert len(q_ids_1) == 10, f"Expected 10 questions, got {len(q_ids_1)}"
    print(f"Attempt 1 returned {len(q_ids_1)} questions: {q_ids_1[:4]}...")

    # Submit Attempt 1
    sub1 = {
        "user_id": user_id,
        "domain_id": domain,
        "answers": [{"question_id": qid, "selected_option": "A", "response_time": 25.0, "confidence": 4} for qid in q_ids_1]
    }
    submit_res1 = client.post("/api/assessment/submit", json=sub1)
    assert submit_res1.status_code == 200

    # Attempt 2: Fetch 10 questions for the same user
    res2 = client.get(f"/api/assessment/questions?limit=10&domain={domain}&user_id={user_id}")
    assert res2.status_code == 200
    q_set_2 = res2.json()
    q_ids_2 = [q["id"] for q in q_set_2]
    assert len(q_ids_2) == 10

    # Check intersection
    overlap_1_2 = set(q_ids_1).intersection(set(q_ids_2))
    print(f"Attempt 2 returned {len(q_ids_2)} questions: {q_ids_2[:4]}...")
    print(f"Overlap between Attempt 1 and Attempt 2: {len(overlap_1_2)} questions")
    assert len(overlap_1_2) == 0, f"Expected 0 repeated questions between attempt 1 & 2, found {overlap_1_2}"

    # Submit Attempt 2
    sub2 = {
        "user_id": user_id,
        "domain_id": domain,
        "answers": [{"question_id": qid, "selected_option": "B", "response_time": 20.0, "confidence": 3} for qid in q_ids_2]
    }
    submit_res2 = client.post("/api/assessment/submit", json=sub2)
    assert submit_res2.status_code == 200

    # Attempt 3: Fetch 10 questions for the same user
    res3 = client.get(f"/api/assessment/questions?limit=10&domain={domain}&user_id={user_id}")
    assert res3.status_code == 200
    q_set_3 = res3.json()
    q_ids_3 = [q["id"] for q in q_set_3]
    assert len(q_ids_3) == 10

    overlap_all = (set(q_ids_1) | set(q_ids_2)).intersection(set(q_ids_3))
    print(f"Attempt 3 returned {len(q_ids_3)} questions: {q_ids_3[:4]}...")
    print(f"Overlap between Attempt 3 and all previous attempts: {len(overlap_all)} questions")
    assert len(overlap_all) == 0, f"Expected 0 repeated questions in Attempt 3, found {overlap_all}"

    print(">>> PASS: Student received 30 completely non-repeating questions across 3 consecutive tests!")

def test_custom_syllabus_generator():
    print("\n--- TEST 2: Custom Syllabus & Topic Generator ---")
    custom_payload = {
        "topic_title": "Operating Systems: Virtual Memory & Page Replacement",
        "syllabus_text": (
            "Unit 1: Paging and Segmentation memory allocation models\n"
            "Unit 2: Page table lookup mechanisms and Translation Lookaside Buffer (TLB)\n"
            "Unit 3: Page replacement algorithms (FIFO, LRU, Optimal) and thrashing mitigation"
        ),
        "user_id": 2,
        "num_questions": 12
    }

    # Generate custom domain
    gen_res = client.post("/api/assessment/custom-generate", json=custom_payload)
    assert gen_res.status_code == 200, f"Generation failed: {gen_res.text}"
    data = gen_res.json()
    domain_id = data["domain_id"]
    print(f"Custom Domain Generated: '{data['name']}' ({domain_id})")
    print(f"Concepts Generated: {data['concepts_count']}, Questions: {data['questions_count']}")
    assert data["concepts_count"] >= 3
    assert data["questions_count"] == 12

    # Verify domain exists in domains list
    domains_res = client.get("/api/domains")
    assert domains_res.status_code == 200
    all_domains = domains_res.json()
    assert any(d["id"] == domain_id for d in all_domains)
    print(">>> Domain successfully registered in SQLite domains table!")

    # Verify Knowledge Graph structure
    graph_res = client.get(f"/api/graph/base?domain={domain_id}")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["nodes"]) >= 3
    assert len(graph_data["edges"]) >= 2
    print(f">>> Knowledge DAG built: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} prerequisite directed edges.")

    # Fetch custom questions
    q_res = client.get(f"/api/assessment/questions?limit=12&domain={domain_id}")
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) == 12
    
    # Verify Two-Tier Reasoning Probes exist on application questions
    app_probes = [q for q in questions if q.get("reasoning_probe") is not None]
    print(f">>> {len(app_probes)} application questions equipped with Two-Tier Reasoning Probes.")
    assert len(app_probes) > 0

    # Submit assessment with PyTorch cognitive model inference
    answers = []
    for i, q in enumerate(questions):
        # Alternate correct (A) and distractor (B)
        sel = "A" if i % 2 == 0 else "B"
        r_probe = "A" if q.get("reasoning_probe") else None
        answers.append({
            "question_id": q["id"],
            "selected_option": sel,
            "response_time": 28.0,
            "confidence": 4,
            "reasoning_selected": r_probe
        })

    sub_res = client.post("/api/assessment/submit", json={
        "user_id": 2,
        "domain_id": domain_id,
        "answers": answers
    })
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    dl_analysis = sub_data["deep_learning_analysis"]
    print("Assessment Result with Neural Inference:")
    print(f" - Predicted State: {dl_analysis['predicted_state']} (Confidence: {dl_analysis['confidence'] * 100:.1f}%)")
    print(f" - Accuracy: {sub_data['accuracy']}%")
    print(f" - Recommendations Generated: {len(sub_data['recommendations'])}")
    assert "predicted_state" in dl_analysis
    assert len(sub_data["recommendations"]) > 0

    # Verify Personalized Concept Guides are populated in recommendations
    first_rec = sub_data["recommendations"][0]
    guide = first_rec.get("guide")
    assert guide is not None, "Concept guide should be populated in recommendation"
    print(f" - Recommendation Title: {first_rec['title']}")
    print(f" - Guide Core Idea: {guide['core_idea'][:80]}...")
    print(f" - Guide Real-World Example: {guide['example'][:80]}...")

    # Verify Student Knowledge Graph evaluation
    eval_graph_res = client.get(f"/api/graph/student/2?domain={domain_id}")
    assert eval_graph_res.status_code == 200
    eval_graph = eval_graph_res.json()
    assert len(eval_graph["graph_nodes"]) >= 3
    print(f">>> Student personalized DAG color-coded across all {len(eval_graph['graph_nodes'])} concepts.")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_unseen_question_rotation()
    test_custom_syllabus_generator()
