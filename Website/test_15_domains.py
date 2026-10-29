"""
Comprehensive 15-Domain Diagnostic Assessment Evaluation Suite
Tests 15 completely unrelated domains across diverse disciplines.
Evaluates:
- Generation latency
- Concept & misconception validity
- Question tier distribution (Basic, Conceptual, Application)
- Two-Tier Reasoning Probes
- Option balance (A, B, C, D)
- Readability & jargon check
- Deep learning cognitive diagnostic pipeline compatibility
"""
import time
import json
import sqlite3
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "model"))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

from syllabus_generator import syllabus_engine
from predictor import DeepLearnXPredictor
from graph_engine import KnowledgeGraphEngine

DB_PATH = PROJECT_ROOT / "database" / "deeplearnx.db"

SAMPLE_TOPICS = [
    ("Fluid Mechanics", "Engineering / Physics"),
    ("Ancient Egyptian Architecture", "History / Archaeology"),
    ("Cybersecurity & Network Defense", "Computer Science"),
    ("Cognitive Psychology & Memory", "Social Sciences"),
    ("Microeconomics & Market Structures", "Economics / Business"),
    ("Organic Chemistry & Reaction Mechanisms", "Chemistry"),
    ("Cellular Genetics & CRISPR Gene Editing", "Biotechnology / Life Sciences"),
    ("Renewable Energy & Solar Photovoltaics", "Environmental Engineering"),
    ("Music Theory & Harmony", "Creative Arts & Humanities"),
    ("Aviation & Flight Dynamics", "Aerospace Engineering"),
    ("Constitutional Law & Civil Liberties", "Law & Governance"),
    ("Data Structures & Algorithms", "Software Engineering"),
    ("Marine Biology & Coral Reefs", "Oceanography & Ecology"),
    ("Astrophysics & Stellar Evolution", "Space Science"),
    ("Cognitive Neuroscience of Sleep", "Medicine & Health Sciences"),
]

BANNED_JARGON = [
    "parasitic field", "boundary flux", "asymptotic resource bounds",
    "spurious field perturbations", "sub-angstrom resolution",
    "downstream systemic equilibrium", "formal proof regarding"
]

def run_evaluation():
    print("=" * 80)
    print("STARTING 15 UNRELATED DOMAINS COMPREHENSIVE EVALUATION")
    print("=" * 80)

    predictor = DeepLearnXPredictor()
    graph_engine = KnowledgeGraphEngine()

    results = []
    total_start = time.time()

    for idx, (topic, domain_class) in enumerate(SAMPLE_TOPICS, 1):
        print(f"\n[{idx}/15] Testing Topic: '{topic}' ({domain_class})")
        t0 = time.time()
        gen_res = syllabus_engine.generate_custom_domain(
            topic_title=topic,
            num_questions=12
        )
        latency = (time.time() - t0) * 1000

        domain_id = gen_res["domain_id"]
        
        # Query generated records from DB
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        
        concepts = conn.execute("SELECT * FROM concepts WHERE domain_id = ?", (domain_id,)).fetchall()
        misconceptions = conn.execute("SELECT * FROM misconceptions WHERE domain_id = ?", (domain_id,)).fetchall()
        questions = conn.execute("SELECT * FROM questions WHERE domain_id = ?", (domain_id,)).fetchall()
        conn.close()

        # Metrics computation
        q_types = {}
        diffs = {}
        correct_opts = {}
        probes_count = 0
        jargon_hits = []

        for q in questions:
            qt = q["question_type"]
            q_types[qt] = q_types.get(qt, 0) + 1
            
            df = q["difficulty"]
            diffs[df] = diffs.get(df, 0) + 1
            
            co = q["correct_option"]
            correct_opts[co] = correct_opts.get(co, 0) + 1
            
            rp = q["reasoning_probe"]
            if rp:
                probes_count += 1

            # Check readability and banned jargon
            full_text = f"{q['question_text']} {q['option_a']} {q['option_b']} {q['option_c']} {q['option_d']}".lower()
            for j in BANNED_JARGON:
                if j in full_text:
                    jargon_hits.append((q["id"], j))

        # Test Deep Learning Cognitive Pipeline on simulated assessment
        # Simulate student with basic correct but application incorrect (False Mastery test)
        simulated_answers = []
        for q in questions[:10]:
            is_appl = (q["question_type"] == "application")
            correct = q["correct_option"]
            # If application, pick distractor B to test false mastery detection
            chosen = "B" if (is_appl and correct != "B") else correct
            
            simulated_answers.append({
                "question_id": q["id"],
                "selected_option": chosen,
                "time_taken_seconds": 12.5,
                "confidence_score": 0.85,
                "selected_probe_option": "B" if is_appl else None
            })

        dl_res = predictor.analyze_session(simulated_answers)
        pred_state = dl_res.get("predicted_state", "Unknown")

        # Graph evaluation
        concept_scores = {}
        for a in simulated_answers:
            qid = a["question_id"]
            q_row = next((r for r in questions if r["id"] == qid), None)
            if q_row:
                cid = q_row["concept_id"]
                if cid not in concept_scores:
                    concept_scores[cid] = {"correct": 0, "total": 0, "acc": 0.0}
                concept_scores[cid]["total"] += 1
                if a["selected_option"] == q_row["correct_option"]:
                    concept_scores[cid]["correct"] += 1

        for c, st in concept_scores.items():
            st["acc"] = st["correct"] / st["total"] if st["total"] > 0 else 0.0

        graph_eval = graph_engine.evaluate_student_graph(
            concept_scores=concept_scores,
            detected_misconceptions=dl_res.get("misconceptions_detected", []),
            primary_state=pred_state,
            domain_id=domain_id
        )

        res_entry = {
            "index": idx,
            "topic": topic,
            "domain_id": domain_id,
            "category": domain_class,
            "latency_ms": round(latency, 1),
            "concepts_count": len(concepts),
            "misconceptions_count": len(misconceptions),
            "questions_count": len(questions),
            "question_types": q_types,
            "difficulties": diffs,
            "correct_option_distribution": correct_opts,
            "probes_count": probes_count,
            "jargon_hits_count": len(jargon_hits),
            "jargon_hits": jargon_hits,
            "dl_predicted_state": pred_state,
            "graph_nodes_count": len(graph_eval.get("nodes", [])),
            "primary_gap": graph_eval.get("primary_gap_name", "None"),
            "sample_basic": questions[0]["question_text"] if len(questions) > 0 else "N/A",
            "sample_conceptual": next((q["question_text"] for q in questions if q["question_type"] == "conceptual"), "N/A"),
            "sample_application": next((q["question_text"] for q in questions if q["question_type"] == "application"), "N/A"),
        }
        results.append(res_entry)

        print(f"  -> Generated {len(concepts)} concepts, {len(misconceptions)} misconceptions, {len(questions)} questions in {latency:.1f}ms")
        print(f"  -> Q-Types: {q_types} | Option Dist: {correct_opts} | Probes: {probes_count}")
        print(f"  -> Readability: {len(jargon_hits)} jargon hits detected")
        print(f"  -> DL Inference State: {pred_state} (Graph nodes: {len(graph_eval.get('nodes', []))})")
        print(f"  -> Sample Basic: {res_entry['sample_basic'][:85]}...")
        print(f"  -> Sample Conceptual: {res_entry['sample_conceptual'][:85]}...")
        print(f"  -> Sample Application: {res_entry['sample_application'][:85]}...")

    total_time = time.time() - total_start
    print("\n" + "=" * 80)
    print(f"ALL 15 DOMAINS EVALUATED IN {total_time:.2f}s")
    print("=" * 80)

    # Summary table
    passed_all = True
    print(f"{'#':<3} | {'Topic':<36} | {'Concepts':<8} | {'Q-Count':<8} | {'Probes':<6} | {'Jargon':<6} | {'Status'}")
    print("-" * 80)
    for r in results:
        status = "PASS" if (r["concepts_count"] >= 3 and r["questions_count"] >= 10 and r["jargon_hits_count"] == 0) else "WARN"
        if status != "PASS":
            passed_all = False
        print(f"{r['index']:<3} | {r['topic']:<36} | {r['concepts_count']:<8} | {r['questions_count']:<8} | {r['probes_count']:<6} | {r['jargon_hits_count']:<6} | {status}")

    print("-" * 80)
    print(f"Overall Test Result: {'ALL 15 DOMAINS PASSED PERFECTLY' if passed_all else 'ATTENTION NEEDED'}")

    # Save summary report to JSON
    with open("scratch_15_domains_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Full evaluation saved to scratch_15_domains_evaluation.json")

if __name__ == "__main__":
    run_evaluation()
