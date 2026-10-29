import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "model"))
from backend.app.syllabus_generator import SyllabusGeneratorEngine
from model.predictor import DeepLearnXPredictor

TEST_TOPICS = [
    "Fluid Mechanics",
    "Engineering Graphics",
    "Cellular Respiration & Bioenergetics",
    "Quantum Cryptography",
    "Macroeconomics & Monetary Policy",
    "Ancient Roman Constitutional Law",
    "Soil Mechanics & Geotechnical Engineering",
    "Music Theory & Harmonic Counterpoint",
    "Aviation Aerodynamics & Flight Stability",
    "Organic Synthesis of Polymers",
    "Sourdough Fermentation Science",
    "Underwater Acoustic Navigation",
    "Woodworking Joinery & Structural Timber",
    "Public Health Epidemiology",
    "Cognitive Behavioral Therapy & Psychology"
]

def run_evaluation():
    gen = SyllabusGeneratorEngine()
    predictor = DeepLearnXPredictor()
    
    print("=" * 80)
    print("DEEPLEARNX UNIVERSAL DOMAIN ENGINE - 15 UNRELATED TOPICS EVALUATION")
    print("=" * 80)
    
    results = []
    
    for idx, topic in enumerate(TEST_TOPICS, start=1):
        print(f"\n[{idx}/15] Evaluating: '{topic}'")
        res = gen.generate_custom_domain(topic_title=topic)
        domain_id = res["domain_id"]
        
        # Verify from database
        conn = sqlite3.connect("database/deeplearnx.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, category, icon FROM domains WHERE id = ?", (domain_id,))
        dom_row = cursor.fetchone()
        
        cursor.execute("SELECT id, name, prerequisites, order_index FROM concepts WHERE domain_id = ? ORDER BY order_index", (domain_id,))
        concepts = cursor.fetchall()
        
        cursor.execute("SELECT id, code, name, description FROM misconceptions WHERE domain_id = ?", (domain_id,))
        misconceptions = cursor.fetchall()
        
        cursor.execute("""
            SELECT id, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, reasoning_probe
            FROM questions WHERE domain_id = ? ORDER BY id
        """, (domain_id,))
        questions = cursor.fetchall()
        conn.close()
        
        # Check uniqueness of question texts
        q_texts = [q[3] for q in questions]
        unique_q_texts = set(q_texts)
        has_duplicates = (len(q_texts) != len(unique_q_texts))
        
        # Check difficulty counts
        difficulties = [q[2] for q in questions]
        easy_count = difficulties.count("easy")
        med_count = difficulties.count("medium")
        hard_count = difficulties.count("hard")
        
        # Check two-tier probes on application questions
        probes_count = sum(1 for q in questions if q[9] is not None)
        
        # Check for false domain leakages
        lower_all_q = " ".join(q_texts).lower()
        has_big_o_leak = ("$o(n^2)$" in lower_all_q or "big-o" in lower_all_q) and "software" not in topic.lower() and "algorithm" not in topic.lower()
        has_vacuum_leak = "vacuum chamber" in lower_all_q and "fluid" in topic.lower()
        
        # Check option length balance (max diff in word count across A, B, C, D)
        length_diffs = []
        for q in questions:
            lens = [len(q[4].split()), len(q[5].split()), len(q[6].split()), len(q[7].split())]
            length_diffs.append(max(lens) - min(lens))
        avg_len_diff = sum(length_diffs) / len(length_diffs) if length_diffs else 0
        
        # Simulate student cognitive diagnostic prediction (50% score with misconceptions)
        responses = []
        for i, q in enumerate(questions):
            is_correct = (i % 2 == 0) # 50% accuracy
            correct_opt = q[8]
            selected_opt = correct_opt if is_correct else ("B" if correct_opt != "B" else "C")
            responses.append({
                "question_id": q[0],
                "selected_option": selected_opt,
                "response_time": 4.5,
                "confidence": 4 if is_correct else 2,
                "switch_count": 1,
                "reasoning_selected": "A"
            })
        
        pred = predictor.analyze_session(responses)
        predicted_state = pred["predicted_state"]
        diagnosis_text = pred["false_mastery_breakdown"]["diagnosis"]
        has_praise_contradiction = ("awesome job" in diagnosis_text.lower() and (predicted_state != "Genuine Mastery" or pred["metrics_summary"]["overall_accuracy"] < 80))
        
        # Status evaluation
        passed = (
            len(concepts) == 4 and
            len(questions) == 12 and
            not has_duplicates and
            easy_count == 4 and
            med_count == 4 and
            hard_count == 4 and
            probes_count == 4 and
            not has_big_o_leak and
            not has_vacuum_leak and
            not has_praise_contradiction
        )
        
        results.append({
            "topic": topic,
            "category": dom_row[2] if dom_row else "Unknown",
            "icon": dom_row[3] if dom_row else "📚",
            "concepts_count": len(concepts),
            "questions_count": len(questions),
            "unique_questions": len(unique_q_texts),
            "probes_count": probes_count,
            "avg_option_word_diff": round(avg_len_diff, 1),
            "predicted_state": predicted_state,
            "diagnosis_snippet": diagnosis_text[:75] + "...",
            "passed": passed
        })
        
        status_sym = "✅ PASS" if passed else "❌ FAIL"
        print(f"   Status: {status_sym} | Category: {dom_row[2]} {dom_row[3]}")
        print(f"   Concepts: {len(concepts)} | Questions: {len(questions)} (100% Unique: {not has_duplicates})")
        print(f"   Breakdown: {easy_count} Easy, {med_count} Medium, {hard_count} Hard | Probes: {probes_count}")
        print(f"   50% Score Diagnostic State: '{predicted_state}'")
        print(f"   Diagnostic Feedback: \"{diagnosis_text[:70]}...\"")
        print(f"   Praise Contradiction Check: {'None (Correct)' if not has_praise_contradiction else 'FOUND CONTRADICTION!'}")

    print("\n" + "=" * 80)
    print("SUMMARY RESULTS TABLE:")
    print("=" * 80)
    print(f"{'#':<3} | {'Topic':<38} | {'Category':<25} | {'Questions':<9} | {'Probes':<6} | {'Status'}")
    print("-" * 95)
    for i, r in enumerate(results, 1):
        print(f"{i:<3} | {r['topic'][:38]:<38} | {r['category'][:25]:<25} | {r['questions_count']} ({r['unique_questions']} unq) | {r['probes_count']} probes | {'✅ PASS' if r['passed'] else '❌ FAIL'}")
    
    all_passed = all(r["passed"] for r in results)
    print("=" * 80)
    print(f"FINAL RESULT: {sum(1 for r in results if r['passed'])} / {len(results)} TOPICS PASSED")
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_evaluation()
    sys.exit(0 if success else 1)
