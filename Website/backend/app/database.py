"""
Database connection and schema initialization for DeepLearnX
Supports multi-domain learning: Pokemon, Class 10 Chemistry, Class 10 Biology, Class 10 Math, and Deep Learning.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "deeplearnx.db"

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 0. Domains table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        icon TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL
    );
    """)
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Concepts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL DEFAULT 'deep_learning',
        name TEXT NOT NULL,
        slug TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        prerequisites TEXT NOT NULL, -- JSON string
        order_index INTEGER NOT NULL
    );
    """)
    
    # Check if domain_id column exists in concepts
    try:
        cursor.execute("ALTER TABLE concepts ADD COLUMN domain_id TEXT DEFAULT 'deep_learning'")
    except sqlite3.OperationalError:
        pass
    
    # 3. Misconceptions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS misconceptions (
        id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL DEFAULT 'deep_learning',
        code TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        remediation TEXT NOT NULL
    );
    """)
    
    try:
        cursor.execute("ALTER TABLE misconceptions ADD COLUMN domain_id TEXT DEFAULT 'deep_learning'")
    except sqlite3.OperationalError:
        pass
    
    # 4. Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL DEFAULT 'deep_learning',
        concept_id TEXT NOT NULL,
        question_type TEXT NOT NULL, -- basic, conceptual, application
        difficulty TEXT NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL,
        explanation TEXT NOT NULL,
        misconception_id TEXT,
        prerequisite_id TEXT,
        FOREIGN KEY (concept_id) REFERENCES concepts(id)
    );
    """)
    
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN domain_id TEXT DEFAULT 'deep_learning'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN reasoning_probe TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    
    # 5. Assessment Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        domain_id TEXT NOT NULL DEFAULT 'deep_learning',
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        accuracy REAL NOT NULL,
        predicted_state TEXT NOT NULL,
        confidence REAL NOT NULL,
        state_probabilities TEXT NOT NULL, -- JSON string
        primary_gap_id TEXT,
        primary_gap_name TEXT,
        detected_misconceptions TEXT, -- JSON string
        false_mastery_data TEXT, -- JSON string
        recommendations TEXT, -- JSON string
        concept_mastery_map TEXT, -- JSON string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    
    try:
        cursor.execute("ALTER TABLE assessment_sessions ADD COLUMN domain_id TEXT DEFAULT 'deep_learning'")
    except sqlite3.OperationalError:
        pass
    
    # 6. Student Responses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        selected_option TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        response_time REAL NOT NULL,
        confidence INTEGER NOT NULL,
        FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)
    );
    """)
    
    # 7. Remedial Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS remedial_sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        domain_id TEXT NOT NULL DEFAULT 'deep_learning',
        original_session_id TEXT NOT NULL,
        target_concept_id TEXT NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        updated_mastery_status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    
    try:
        cursor.execute("ALTER TABLE remedial_sessions ADD COLUMN domain_id TEXT DEFAULT 'deep_learning'")
    except sqlite3.OperationalError:
        pass
    
    # 8. Custom Concept Guides (for user-generated syllabi)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_concept_guides (
        concept_id TEXT PRIMARY KEY,
        domain_id TEXT NOT NULL,
        name TEXT NOT NULL,
        core_idea TEXT NOT NULL,
        example TEXT NOT NULL,
        common_mistake TEXT NOT NULL,
        key_takeaway TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables initialized with multi-domain support.")

if __name__ == "__main__":
    init_db()
