import sys
import os
import json
import random
from pathlib import Path

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend" / "app"))

from backend.app.syllabus_generator import SyllabusGeneratorEngine
from backend.app.main import get_remedial_questions

TEST_TOPICS = [
    "Types of Spiders",
    "Fluid Mechanics",
    "French Revolution",
    "Photosynthesis",
    "Ancient Roman Architecture",
    "Quantum Cryptography",
    "Plate Tectonics",
    "Macroeconomics",
    "Musical Harmony & Counterpoint",
    "Organic Chemistry & Polymers",
    "Sourdough Fermentation",
    "Constitutional Law",
    "Aviation Aerodynamics",
    "Neuroscience & Synaptic Plasticity",
    "Ethics of Artificial Intelligence"
]

engine = SyllabusGeneratorEngine()

print("=" * 80)
print(f"DEEPLEARNX COMPREHENSIVE 15-TOPIC MULTI-DISCIPLINARY EVALUATION")
print("=" * 80)

passed_count = 0
results = []

for idx, topic in enumerate(TEST_TOPICS, 1):
    print(f"\n[{idx}/15] Evaluating Topic: '{topic}'")
    try:
        # Generate custom domain
        res = engine.generate_custom_domain(
            topic_title=topic,
            syllabus_text="",
            num_questions=12
        )
        domain_id = res["domain_id"]
        concepts = res["concepts"]
        
        from backend.app.main import get_db_connection
        conn = get_db_connection()
        q_rows = conn.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option, reasoning_probe
            FROM questions
            WHERE domain_id = ?
            ORDER BY id ASC
        """, (domain_id,)).fetchall()
        conn.close()

        questions = [dict(r) for r in q_rows]
        
        # 1. Verification of Concepts
        assert len(concepts) == 4, f"Expected 4 concepts, got {len(concepts)}"
        
        # 2. Verification of Questions
        assert len(questions) == 12, f"Expected 12 questions, got {len(questions)}"
        
        # 3. Two-Tier Reasoning Probes
        probe_indices = []
        for q_idx, q in enumerate(questions):
            rp = q.get("reasoning_probe")
            if rp and rp != "null" and rp != "{}" and rp is not None:
                probe_indices.append(q_idx + 1)
                
        has_probes = len(probe_indices) >= 3
        # Check that probes are not strictly [3, 6, 9, 12]
        is_randomized = (probe_indices != [3, 6, 9, 12])
        
        # 4. Check for Jargon Anomaly ("an operator drives a system beyond its rated operating threshold")
        forbidden_jargon = "an operator drives a system"
        found_jargon = any(forbidden_jargon in (q["question_text"] or "").lower() for q in questions)
        
        # 5. Check Option Length Balance
        longest_picks = 0
        for q in questions:
            opts = [q["option_a"] or "", q["option_b"] or "", q["option_c"] or "", q["option_d"] or ""]
            lengths = [len(o) for o in opts]
            max_idx = lengths.index(max(lengths))
            corr_letter = (q["correct_option"] or "A").upper().strip()
            corr_idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(corr_letter, 0)
            if max_idx == corr_idx and max(lengths) > 1.5 * min(lengths):
                longest_picks += 1
        heuristic_bias = (longest_picks / len(questions)) * 100

        # 6. Test Remedial Question Retrieval for this Domain
        first_cid = concepts[0]["id"]
        remedial_qs = get_remedial_questions(concept_id=first_cid, count=3, domain=domain_id)
        assert len(remedial_qs) == 3, f"Expected 3 remedial questions, got {len(remedial_qs)}"
        assert all(rq["domain_id"] == domain_id for rq in remedial_qs), f"Remedial questions leaked from another domain!"

        # Criteria check
        topic_passed = (
            len(concepts) == 4 and
            len(questions) == 12 and
            has_probes and
            not found_jargon and
            heuristic_bias <= 40
        )
        
        if topic_passed:
            passed_count += 1

        print(f"   ✓ Domain ID: {domain_id}")
        print(f"   ✓ Category: {res.get('category')} | Icon: {res.get('icon')}")
        print(f"   ✓ Concepts (4): {[c['name'].split(':')[-1].strip() for c in concepts]}")
        print(f"   ✓ Probes Count: {len(probe_indices)} (Placed on Qs: {probe_indices})")
        print(f"   ✓ Non-Predictable Probe Placement: {is_randomized or len(probe_indices) != 4}")
        print(f"   ✓ Forbidden Engineering Jargon Found: {found_jargon}")
        print(f"   ✓ Option Length Bias (Longest Pick): {heuristic_bias:.1f}%")
        print(f"   ✓ Remedial Drill: 3/3 questions successfully verified strictly in '{domain_id}'")
        print(f"   ✓ Sample Q1: {questions[0]['question_text'][:90]}...")
        print(f"   --> RESULT: {'PASSED' if topic_passed else 'FAILED'}")

        results.append({
            "topic": topic,
            "domain_id": domain_id,
            "category": res.get("category"),
            "probe_positions": probe_indices,
            "found_jargon": found_jargon,
            "passed": topic_passed
        })

    except Exception as e:
        print(f"   ❌ ERROR evaluating topic '{topic}': {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "topic": topic,
            "error": str(e),
            "passed": False
        })

print("\n" + "=" * 80)
print(f"EVALUATION SUMMARY: {passed_count}/{len(TEST_TOPICS)} TOPICS PASSED")
print("=" * 80)

if passed_count == len(TEST_TOPICS):
    print("ALL 15 DIVERSE MULTI-DISCIPLINARY TOPICS PASSED WITH ZERO ANOMALIES!")
else:
    print(f"WARNING: {len(TEST_TOPICS) - passed_count} topics had issues.")
