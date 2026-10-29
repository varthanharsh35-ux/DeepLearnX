"""
Seed script for DeepLearnX database with multi-domain support:
1. Pokemon Battle Mechanics (10 questions)
2. Class 10 Chemistry (10 questions)
3. Class 10 Biology (10 questions)
4. Class 10 Mathematics (10 questions)
5. Deep Learning Fundamentals (30 questions)
"""

import json
import sqlite3
import hashlib
import uuid
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset"
DB_PATH = BASE_DIR / "database" / "deeplearnx.db"

sys.path.insert(0, str(BASE_DIR / "backend" / "app"))
from database import init_db, get_db_connection

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def seed_database():
    print("Seeding DeepLearnX SQLite database with multi-domain subjects...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load multi-domain data
    with open(DATASET_DIR / "all_domains_data.json", "r", encoding="utf-8") as f:
        multi_data = json.load(f)
        
    # Load Deep Learning fundamentals
    with open(DATASET_DIR / "questions_dl_fundamentals.json", "r", encoding="utf-8") as f:
        dl_data = json.load(f)
        
    # 0. Seed Domains
    for d in multi_data["domains"]:
        cursor.execute("""
            INSERT OR REPLACE INTO domains (id, name, icon, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (d["id"], d["name"], d["icon"], d["category"], d["description"]))
        
    # 1. Seed Deep Learning Concepts, Misconceptions, Questions
    for c in dl_data["concepts"]:
        cursor.execute("""
            INSERT OR REPLACE INTO concepts (id, domain_id, name, slug, category, description, prerequisites, order_index)
            VALUES (?, 'deep_learning', ?, ?, ?, ?, ?, ?)
        """, (c["id"], c["name"], c["slug"], c["category"], c["description"], json.dumps(c["prerequisites"]), c["order_index"]))
        
    for m in dl_data["misconceptions"]:
        cursor.execute("""
            INSERT OR REPLACE INTO misconceptions (id, domain_id, code, concept_id, name, description, remediation)
            VALUES (?, 'deep_learning', ?, ?, ?, ?, ?)
        """, (m["id"], m["code"], m["concept_id"], m["name"], m["description"], m["remediation"]))
        
    for q in dl_data["questions"]:
        rp_json = json.dumps(q.get("reasoning_probe")) if q.get("reasoning_probe") else None
        cursor.execute("""
            INSERT OR REPLACE INTO questions (
                id, domain_id, concept_id, question_type, difficulty, question_text,
                option_a, option_b, option_c, option_d, correct_option,
                explanation, misconception_id, prerequisite_id, reasoning_probe
            ) VALUES (?, 'deep_learning', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], q["concept_id"], q["question_type"], q["difficulty"], q["question_text"],
            q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
            q["correct_option"], q["explanation"], q.get("misconception_id"), q.get("prerequisite_id"),
            rp_json
        ))
        
    # 2. Seed Pokemon, Chemistry, Biology, Math
    subject_keys = ["pokemon", "class10_chemistry", "class10_biology", "class10_math"]
    for s_key in subject_keys:
        s_data = multi_data[s_key]
        for c in s_data["concepts"]:
            cursor.execute("""
                INSERT OR REPLACE INTO concepts (id, domain_id, name, slug, category, description, prerequisites, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c["id"], s_key, c["name"], c["slug"], c["category"], c["description"], json.dumps(c["prerequisites"]), c["order_index"]))
            
        for m in s_data.get("misconceptions", []):
            cursor.execute("""
                INSERT OR REPLACE INTO misconceptions (id, domain_id, code, concept_id, name, description, remediation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (m["id"], s_key, m["code"], m["concept_id"], m["name"], m["description"], m["remediation"]))
            
        for q in s_data.get("questions", []):
            rp_json = json.dumps(q.get("reasoning_probe")) if q.get("reasoning_probe") else None
            cursor.execute("""
                INSERT OR REPLACE INTO questions (
                    id, domain_id, concept_id, question_type, difficulty, question_text,
                    option_a, option_b, option_c, option_d, correct_option,
                    explanation, misconception_id, prerequisite_id, reasoning_probe
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"], s_key, q["concept_id"], q["question_type"], q["difficulty"], q["question_text"],
                q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
                q["correct_option"], q["explanation"], q.get("misconception_id"), q.get("prerequisite_id"),
                rp_json
            ))
            
    # 3. Seed Demo Users
    users = [
        ("admin", "admin@deeplearnx.edu", "Prof. Dr. R. K. Murthy", hash_pw("admin123"), "faculty"),
        ("student_a", "ananya@student.deeplearnx.edu", "Ananya Sharma", hash_pw("student123"), "student"),
        ("student_b", "rahul@student.deeplearnx.edu", "Rahul Verma", hash_pw("student123"), "student"),
        ("student_c", "sneha@student.deeplearnx.edu", "Sneha Patel", hash_pw("student123"), "student"),
        ("student_d", "karan@student.deeplearnx.edu", "Karan Singh", hash_pw("student123"), "student"),
    ]
    for u in users:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, email, full_name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, u)
        
    conn.commit()
    
    # 4. Insert Demo Historical Sessions
    user_rows = cursor.execute("SELECT id, username FROM users").fetchall()
    user_map = {row["username"]: row["id"] for row in user_rows}
    
    # Rahul Verma in Pokemon: False Mastery (100% on basic types, fails on 4x dual type multipliers)
    sess_poke_rahul = "sess-demo-rahul-poke-falsemastery"
    cursor.execute("""
        INSERT OR REPLACE INTO assessment_sessions (
            id, user_id, domain_id, score, total_questions, accuracy, predicted_state, confidence,
            state_probabilities, primary_gap_id, primary_gap_name, detected_misconceptions,
            false_mastery_data, recommendations, concept_mastery_map, created_at
        ) VALUES (?, ?, 'pokemon', 6, 10, 60.0, 'False Mastery', 0.932,
            ?, 'poke_dual_types', 'Dual-Type Multipliers', ?, ?, ?, ?, datetime('now', '-3 hours'))
    """, (
        sess_poke_rahul, user_map["student_b"],
        json.dumps({"Genuine Mastery": 0.03, "False Mastery": 0.932, "Conceptual Misconception": 0.025, "Knowledge Gap": 0.013}),
        json.dumps([multi_data["pokemon"]["misconceptions"][2]]), # Dual Add
        json.dumps({
            "is_false_mastery": True, "basic_accuracy": 100.0, "conceptual_accuracy": 75.0,
            "application_accuracy": 25.0, "tier_divergence": 75.0, "divergence_significance": "HIGH",
            "diagnosis": "Student memorized single type weaknesses (100%), but fails to calculate compound dual-type multipliers (e.g. Charizard taking 4x from Rock)."
        }),
        json.dumps([
            {
                "step": 1, "type": "Multiplication Practice", "title": "Revise Compound Dual-Type Multipliers",
                "description": "Remember that dual-type weaknesses multiply (2x * 2x = 4x; 2x * 0.5x = 1.0x neutral).",
                "action": "Practice calculating 4x weaknesses on Pokemon like Charizard and Dragonite.",
                "concept_id": "poke_dual_types", "urgency": "High"
            },
            {
                "step": 2, "type": "Remedial Drill", "title": "Take 3-Question Dual-Type Drill",
                "description": "Complete a quick drill to repair the gap.", "action": "Start Remedial Drill",
                "concept_id": "poke_dual_types", "urgency": "Medium"
            }
        ]),
        json.dumps({
            "poke_types": "mastered", "poke_immunities": "mastered", "poke_dual_types": "gap",
            "poke_stab": "partial", "poke_stat_stages": "partial"
        })
    ))

    conn.commit()
    conn.close()
    print("Database successfully seeded with Pokemon, Chemistry, Biology, Math, and Deep Learning!")

if __name__ == "__main__":
    seed_database()
