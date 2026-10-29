"""
Deep Verification of Phase 5:
Simulates student taking the dynamically generated quiz on 'Plants and their parts'
with 3 deliberate errors (basic recall, conceptual, and application with failed probe).
Inspects:
- Deep Learning diagnostic prediction & confidence
- Knowledge gap detection & prerequisite tracking
- Exact question reviews with concept explanations and remedial mini-lessons
"""

import sys
import json
import sqlite3
import urllib.request

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('Website/database/deeplearnx.db')
conn.row_factory = sqlite3.Row
domain_id = 'custom_plants_and_their_parts_53ba9a'

q_rows = conn.execute('SELECT * FROM questions WHERE domain_id = ? ORDER BY id ASC', (domain_id,)).fetchall()
questions = [dict(r) for r in q_rows]
print(f"Retrieved {len(questions)} questions for {domain_id}")

answers = []
for idx, q in enumerate(questions):
    corr = q['correct_option']
    rp_raw = q.get('reasoning_probe')
    rp = json.loads(rp_raw) if rp_raw else None
    
    # 3 Deliberate student errors: Q2 (basic), Q5 (conceptual), Q9 (application + probe)
    if idx == 1:
        # Deliberate error 1: Basic recall mistake on concept 1
        wrong_opt = 'B' if corr == 'A' else 'A'
        answers.append({
            'question_id': q['id'],
            'selected_option': wrong_opt,
            'response_time': 18.0,
            'confidence': 3,
            'reasoning_selected': None
        })
    elif idx == 4:
        # Deliberate error 2: Conceptual mistake on concept 2
        wrong_opt = 'B' if corr == 'A' else 'A'
        answers.append({
            'question_id': q['id'],
            'selected_option': wrong_opt,
            'response_time': 22.0,
            'confidence': 2,
            'reasoning_selected': None
        })
    elif idx == 8:
        # Deliberate error 3: Application mistake with failed reasoning probe on concept 3
        wrong_opt = 'C' if corr != 'C' else 'B'
        wrong_probe = 'C' if rp and rp.get('correct_probe') != 'C' else 'B'
        answers.append({
            'question_id': q['id'],
            'selected_option': wrong_opt,
            'response_time': 35.0,
            'confidence': 4,
            'reasoning_selected': wrong_probe
        })
    else:
        # Correct answer with matching correct reasoning probe
        p_sel = rp.get('correct_probe', 'A') if rp else None
        answers.append({
            'question_id': q['id'],
            'selected_option': corr,
            'response_time': 20.0,
            'confidence': 4,
            'reasoning_selected': p_sel
        })

payload = {
    'user_id': 1,
    'domain_id': domain_id,
    'answers': answers
}

req = urllib.request.Request(
    'http://localhost:8055/api/assessment/submit',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req, timeout=15) as resp:
    res = json.loads(resp.read().decode())
    print("\n" + "=" * 80)
    print("DEEP LEARNING COGNITIVE DIAGNOSTIC REPORT (PLANTS AND THEIR PARTS)")
    print("=" * 80)
    print(f"Session ID:                  {res['session_id']}")
    print(f"Raw Accuracy:                {res['score']}/{res['total_questions']} ({res['accuracy']}%)")
    print(f"Predicted Understanding State: {res['deep_learning_analysis']['predicted_state']}")
    print(f"DNN Confidence:              {res['deep_learning_analysis']['confidence'] * 100:.1f}%")
    print(f"Primary Prerequisite Gap:    {res['knowledge_gap_detection']['primary_gap_name']}")
    
    print("\n" + "-" * 80)
    print("QUESTION-BY-QUESTION DIAGNOSTICS & REMEDIAL MINI-LESSONS")
    print("-" * 80)
    for q_idx, q_rev in enumerate(res['question_reviews'], 1):
        status_icon = "✓ Correct" if q_rev['is_correct'] else "❌ Incorrect"
        print(f"\nQuestion {q_idx} [{q_rev['question_type'].capitalize()}] — {status_icon}")
        print(f"  Prompt:   {q_rev['question_text']}")
        print(f"  Selected: Option {q_rev['selected_option']}: {q_rev['selected_text']}")
        print(f"  Correct:  Option {q_rev['correct_option']}: {q_rev['correct_text']}")
        if not q_rev['is_correct']:
            print(f"  Concept:  {q_rev['concept_name']}")
            print(f"  Teacher Explanation: {q_rev['explanation']}")
            if q_rev.get('misconception'):
                m = q_rev['misconception']
                print(f"  Targeted Misconception: {m.get('name')}")
                print(f"  Remediation Guidance:   {m.get('remediation')}")
            if q_rev.get('reasoning_probe'):
                prb = q_rev['reasoning_probe']
                prb_stat = "✓ Passed" if prb.get('is_correct') else "❌ Failed"
                print(f"  Two-Tier Probe ({prb_stat}): {prb.get('prompt')}")
                print(f"    Student Reasoning: [{prb.get('selected')}] {prb.get('selected_text')}")
                print(f"    Valid Scientific Reasoning: [{prb.get('correct')}] {prb.get('correct_text')}")
