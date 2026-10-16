"""
Synthetic Dataset Generator for DeepLearnX
Generates realistic cognitive response sequences and structured performance vectors
modeling 4 distinct cognitive states:
1. Genuine Mastery
2. False Mastery
3. Conceptual Misconception
4. Prerequisite Knowledge Gap
"""

import json
import random
import numpy as np
import pandas as pd
from pathlib import Path

# Fix random seeds for reproducibility
random.seed(42)
np.random.seed(42)

DATASET_DIR = Path(__file__).parent
with open(DATASET_DIR / "questions_dl_fundamentals.json", "r") as f:
    bank_data = json.load(f)

CONCEPTS = [c["id"] for c in bank_data["concepts"]]
CONCEPT_MAP = {c["id"]: idx for idx, c in enumerate(bank_data["concepts"])}
QUESTIONS = bank_data["questions"]
MISCONCEPTIONS = [m["id"] for m in bank_data["misconceptions"]]
MISCONCEPTION_MAP = {m["id"]: idx + 1 for idx, m in enumerate(bank_data["misconceptions"])}
MISCONCEPTION_MAP[None] = 0

COGNITIVE_LABELS = {
    0: "Genuine Mastery",
    1: "False Mastery",
    2: "Conceptual Misconception",
    3: "Knowledge Gap"
}

def simulate_student_session(student_id: int, target_state: int):
    """
    Simulates a sequence of question responses for a given cognitive state.
    """
    # Select a primary misconception for misconception archetypes
    assigned_misc = random.choice(MISCONCEPTIONS) if target_state == 2 else None
    
    # Prerequisite gap primary root concept
    prereq_gap_concept = random.choice(["derivatives", "chain_rule", "linear_algebra"]) if target_state == 3 else None

    # Assessment sequence (e.g., 15 questions per session sampled across tiers)
    # Ensure representation of Basic, Conceptual, Application
    sampled_questions = random.sample(QUESTIONS, min(18, len(QUESTIONS)))
    
    sequence_data = []
    
    for q in sampled_questions:
        c_id = q["concept_id"]
        q_type = q["question_type"] # basic, conceptual, application
        tier_idx = 0 if q_type == "basic" else (1 if q_type == "conceptual" else 2)
        q_misc = q.get("misconception_id")
        q_prereq = q.get("prerequisite_id")
        
        # Determine probability of correct answer based on target cognitive archetype
        if target_state == 0:  # Genuine Mastery
            p_correct = 0.94 if q_type == "basic" else (0.90 if q_type == "conceptual" else 0.85)
            time_spent = random.uniform(15.0, 45.0)
            confidence = random.choice([4, 5, 5])
            chosen_misc = 0
            
        elif target_state == 1:  # False Mastery
            # Great at basic recall, good at memorized conceptual, collapses on application!
            if q_type == "basic":
                p_correct = 0.92
                confidence = 5
                time_spent = random.uniform(12.0, 30.0)
            elif q_type == "conceptual":
                p_correct = 0.82
                confidence = 4
                time_spent = random.uniform(25.0, 50.0)
            else:  # application
                p_correct = 0.18
                confidence = random.choice([3, 4])  # false confidence!
                time_spent = random.uniform(40.0, 95.0)
            chosen_misc = 0
            
        elif target_state == 2:  # Conceptual Misconception
            if q_misc == assigned_misc:
                # Strong misconception trap: 85% probability of picking misconception distractor
                p_correct = 0.10
                chosen_misc = MISCONCEPTION_MAP.get(assigned_misc, 0)
                confidence = 5  # Confident in wrong misconception
                time_spent = random.uniform(20.0, 45.0)
            else:
                p_correct = 0.72 if q_type == "basic" else 0.55
                chosen_misc = 0
                confidence = random.choice([2, 3, 4])
                time_spent = random.uniform(30.0, 60.0)
                
        else:  # target_state == 3: Knowledge Gap
            # If this question relies on the missing prerequisite concept
            if q_prereq == prereq_gap_concept or c_id == prereq_gap_concept:
                p_correct = 0.15
                confidence = 1
                time_spent = random.uniform(50.0, 110.0)
            else:
                p_correct = 0.40 if q_type == "basic" else 0.25
                confidence = random.choice([1, 2])
                time_spent = random.uniform(40.0, 80.0)
            chosen_misc = random.choice([0, MISCONCEPTION_MAP.get(q_misc, 0)])

        # Sample actual correctness
        is_correct = 1 if (random.random() < p_correct) else 0
        if is_correct:
            chosen_misc = 0
        
        sequence_data.append({
            "question_id": q["id"],
            "concept_idx": CONCEPT_MAP.get(c_id, 0),
            "tier_idx": tier_idx,
            "is_correct": is_correct,
            "response_time": round(time_spent, 1),
            "confidence": confidence,
            "selected_misconception": chosen_misc
        })
        
    # Aggregate structured cognitive features
    total_q = len(sequence_data)
    correct_count = sum(s["is_correct"] for s in sequence_data)
    acc_overall = correct_count / total_q
    
    basic_q = [s for s in sequence_data if s["tier_idx"] == 0]
    conc_q = [s for s in sequence_data if s["tier_idx"] == 1]
    app_q = [s for s in sequence_data if s["tier_idx"] == 2]
    
    acc_basic = (sum(s["is_correct"] for s in basic_q) / len(basic_q)) if basic_q else 0.0
    acc_conc = (sum(s["is_correct"] for s in conc_q) / len(conc_q)) if conc_q else 0.0
    acc_app = (sum(s["is_correct"] for s in app_q) / len(app_q)) if app_q else 0.0
    
    # Key cognitive feature: tier divergence (basic - application)
    tier_divergence = acc_basic - acc_app
    
    avg_conf = np.mean([s["confidence"] for s in sequence_data]) / 5.0
    avg_time = np.mean([s["response_time"] for s in sequence_data]) / 100.0  # normalized
    
    # Distractor misconception pattern frequency
    misc_errors = [s["selected_misconception"] for s in sequence_data if s["selected_misconception"] > 0]
    distractor_ratio = len(misc_errors) / total_q
    
    # Maximum consecutive error streak
    max_streak = 0
    cur_streak = 0
    for s in sequence_data:
        if s["is_correct"] == 0:
            cur_streak += 1
            max_streak = max(max_streak, cur_streak)
        else:
            cur_streak = 0
    streak_norm = max_streak / float(total_q)
    
    # Prerequisite risk continuous target
    if target_state == 0:
        prereq_risk = random.uniform(0.02, 0.15)
    elif target_state == 1:
        prereq_risk = random.uniform(0.20, 0.45)
    elif target_state == 2:
        prereq_risk = random.uniform(0.40, 0.70)
    else:
        prereq_risk = random.uniform(0.75, 0.98)
        
    primary_misc_idx = MISCONCEPTION_MAP.get(assigned_misc, 0)
    
    return {
        "student_id": student_id,
        "target_state": target_state,
        "state_name": COGNITIVE_LABELS[target_state],
        "primary_misc_idx": primary_misc_idx,
        "prereq_risk": round(prereq_risk, 3),
        "acc_overall": round(acc_overall, 3),
        "acc_basic": round(acc_basic, 3),
        "acc_conc": round(acc_conc, 3),
        "acc_app": round(acc_app, 3),
        "tier_divergence": round(tier_divergence, 3),
        "avg_conf": round(avg_conf, 3),
        "avg_time": round(avg_time, 3),
        "distractor_ratio": round(distractor_ratio, 3),
        "streak_norm": round(streak_norm, 3),
        "sequence": sequence_data
    }

def generate_datasets(train_size=2400, test_size=600):
    print(f"Generating {train_size} training sessions and {test_size} test sessions...")
    
    train_records = []
    test_records = []
    
    # Balanced distribution of 4 cognitive archetypes
    for i in range(train_size):
        state = i % 4
        rec = simulate_student_session(student_id=1000 + i, target_state=state)
        train_records.append(rec)
        
    for i in range(test_size):
        state = i % 4
        rec = simulate_student_session(student_id=5000 + i, target_state=state)
        test_records.append(rec)
        
    # Save as JSON (rich sequence data) and CSV (tabular summary)
    with open(DATASET_DIR / "student_sessions_train.json", "w") as f:
        json.dump(train_records, f, indent=2)
        
    with open(DATASET_DIR / "student_sessions_test.json", "w") as f:
        json.dump(test_records, f, indent=2)
        
    # Flat CSV for inspection & scikit-learn metrics
    df_train = pd.DataFrame([{
        k: v for k, v in r.items() if k != "sequence"
    } for r in train_records])
    df_train.to_csv(DATASET_DIR / "student_responses_train.csv", index=False)
    
    df_test = pd.DataFrame([{
        k: v for k, v in r.items() if k != "sequence"
    } for r in test_records])
    df_test.to_csv(DATASET_DIR / "student_responses_test.csv", index=False)
    
    print(f"Dataset generated successfully:")
    print(f" - {len(train_records)} training records")
    print(f" - {len(test_records)} test records")
    print(f"Saved to {DATASET_DIR}")

if __name__ == "__main__":
    generate_datasets()
