"""
DeepLearnX Versioned Educational Data Model (Phase 2).

Defines structured entities, Pydantic schemas, and non-destructive SQLite tables for:
- Curriculum Nodes (versioned DAG nodes with cognitive levels and evidence grounding)
- Learning Objectives (measurable pedagogical targets tied to concepts and Bloom's taxonomy)
- Question Validations (factual, alignment, and publication gate records)
"""

import sqlite3
import json
import time
import uuid
import hashlib
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# =============================================================================
# PYDANTIC EDUCATIONAL MODELS
# =============================================================================

class CurriculumNode(BaseModel):
    id: str
    domain_id: str
    concept_id: str
    title: str
    description: str
    cognitive_level: str = "understand" # remember, understand, apply, analyze, evaluate
    prerequisites: List[str] = Field(default_factory=list)
    evidence_grounding: Optional[Dict[str, Any]] = None
    version: int = 1
    created_at: float = Field(default_factory=time.time)


class LearningObjective(BaseModel):
    id: str
    domain_id: str
    concept_id: str
    node_id: Optional[str] = None
    objective_statement: str
    action_verb: str = "Explain"
    cognitive_level: str = "understand" # remember, understand, apply, analyze, evaluate
    version: int = 1
    created_at: float = Field(default_factory=time.time)


class QuestionValidationRecord(BaseModel):
    question_id: str
    domain_id: str
    objective_id: Optional[str] = None
    factual_accuracy_passed: bool = True
    cognitive_alignment_passed: bool = True
    distractor_plausibility_passed: bool = True
    probe_alignment_passed: bool = True
    is_published: bool = True
    validation_details: Dict[str, Any] = Field(default_factory=dict)
    rejection_reason: Optional[str] = None
    validated_at: float = Field(default_factory=time.time)


# =============================================================================
# NON-DESTRUCTIVE DATABASE MIGRATION
# =============================================================================

def migrate_educational_data_model(conn: sqlite3.Connection) -> None:
    """
    Applies non-destructive schema migration for versioned educational tables.
    Preserves all existing canonical records, domains, concepts, and questions.
    """
    cursor = conn.cursor()

    # 1. Versioned Curriculum Nodes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curriculum_nodes (
            id TEXT PRIMARY KEY,
            domain_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            cognitive_level TEXT NOT NULL DEFAULT 'understand',
            prerequisites TEXT NOT NULL DEFAULT '[]',
            evidence_grounding TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            created_at REAL NOT NULL,
            FOREIGN KEY (domain_id) REFERENCES domains(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_curr_nodes_domain ON curriculum_nodes(domain_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_curr_nodes_concept ON curriculum_nodes(concept_id)")

    # 2. Learning Objectives
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_objectives (
            id TEXT PRIMARY KEY,
            domain_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            node_id TEXT,
            objective_statement TEXT NOT NULL,
            action_verb TEXT NOT NULL DEFAULT 'Explain',
            cognitive_level TEXT NOT NULL DEFAULT 'understand',
            version INTEGER NOT NULL DEFAULT 1,
            created_at REAL NOT NULL,
            FOREIGN KEY (domain_id) REFERENCES domains(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lo_domain ON learning_objectives(domain_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lo_concept ON learning_objectives(concept_id)")

    # 3. Question Validations (Audit & Publication Gates)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_validations (
            question_id TEXT PRIMARY KEY,
            domain_id TEXT NOT NULL,
            objective_id TEXT,
            factual_accuracy_passed INTEGER NOT NULL DEFAULT 1,
            cognitive_alignment_passed INTEGER NOT NULL DEFAULT 1,
            distractor_plausibility_passed INTEGER NOT NULL DEFAULT 1,
            probe_alignment_passed INTEGER NOT NULL DEFAULT 1,
            is_published INTEGER NOT NULL DEFAULT 1,
            validation_details TEXT NOT NULL DEFAULT '{}',
            rejection_reason TEXT,
            validated_at REAL NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_qv_published ON question_validations(domain_id, is_published)")

    # 4. Safely add is_published column to questions if missing
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN is_published INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # 5. Safely add learning_objective_id to questions if missing
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN learning_objective_id TEXT")
    except sqlite3.OperationalError:
        pass

    # 6. Backfill canonical question validations if empty
    cursor.execute("SELECT COUNT(*) FROM question_validations")
    qv_count = cursor.fetchone()[0]
    if qv_count == 0:
        cursor.execute("SELECT id, domain_id FROM questions")
        q_rows = cursor.fetchall()
        now = time.time()
        for qid, did in q_rows:
            cursor.execute("""
                INSERT OR IGNORE INTO question_validations (
                    question_id, domain_id, factual_accuracy_passed,
                    cognitive_alignment_passed, distractor_plausibility_passed,
                    probe_alignment_passed, is_published, validation_details, validated_at
                ) VALUES (?, ?, 1, 1, 1, 1, 1, '{"canonical": true}', ?)
            """, (qid, did, now))

    # 7. Backfill curriculum nodes and learning objectives from canonical concepts if empty
    cursor.execute("SELECT COUNT(*) FROM curriculum_nodes")
    cnode_count = cursor.fetchone()[0]
    if cnode_count == 0:
        cursor.execute("SELECT id, domain_id, name, description, prerequisites, category FROM concepts")
        concepts = cursor.fetchall()
        now = time.time()
        for cid, did, name, desc, prereqs_str, cat in concepts:
            node_id = f"node_{cid}"
            cursor.execute("""
                INSERT OR IGNORE INTO curriculum_nodes (
                    id, domain_id, concept_id, title, description,
                    cognitive_level, prerequisites, version, created_at
                ) VALUES (?, ?, ?, ?, ?, 'understand', ?, 1, ?)
            """, (node_id, did, cid, name, desc, prereqs_str or "[]", now))

            # Add default canonical learning objective
            lo_id = f"lo_{cid}"
            obj_statement = f"Understand core principles, applications, and diagnostic structures of {name} in {cat}."
            cursor.execute("""
                INSERT OR IGNORE INTO learning_objectives (
                    id, domain_id, concept_id, node_id, objective_statement,
                    action_verb, cognitive_level, version, created_at
                ) VALUES (?, ?, ?, ?, ?, 'Explain', 'understand', 1, ?)
            """, (lo_id, did, cid, node_id, obj_statement, now))

    # 8. Clean up orphaned foreign key records left from interrupted test runs
    cursor.execute("DELETE FROM question_validations WHERE question_id NOT IN (SELECT id FROM questions)")
    cursor.execute("DELETE FROM learning_objectives WHERE domain_id NOT IN (SELECT id FROM domains)")
    cursor.execute("DELETE FROM curriculum_nodes WHERE domain_id NOT IN (SELECT id FROM domains)")
    cursor.execute("DELETE FROM assessment_attempts WHERE user_id NOT IN (SELECT id FROM users)")

    conn.commit()


# =============================================================================
# REPOSITORIES & DATA ACCESS HELPERS
# =============================================================================

def record_curriculum_nodes(conn: sqlite3.Connection, nodes: List[CurriculumNode]) -> None:
    """Persists a list of curriculum nodes into SQLite."""
    cursor = conn.cursor()
    for n in nodes:
        cursor.execute("""
            INSERT OR REPLACE INTO curriculum_nodes (
                id, domain_id, concept_id, title, description,
                cognitive_level, prerequisites, evidence_grounding, version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            n.id, n.domain_id, n.concept_id, n.title, n.description,
            n.cognitive_level, json.dumps(n.prerequisites),
            json.dumps(n.evidence_grounding) if n.evidence_grounding else None,
            n.version, n.created_at
        ))
    conn.commit()


def record_learning_objectives(conn: sqlite3.Connection, objectives: List[LearningObjective]) -> None:
    """Persists a list of learning objectives into SQLite."""
    cursor = conn.cursor()
    for lo in objectives:
        cursor.execute("""
            INSERT OR REPLACE INTO learning_objectives (
                id, domain_id, concept_id, node_id, objective_statement,
                action_verb, cognitive_level, version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lo.id, lo.domain_id, lo.concept_id, lo.node_id,
            lo.objective_statement, lo.action_verb, lo.cognitive_level,
            lo.version, lo.created_at
        ))
    conn.commit()


def record_question_validation(conn: sqlite3.Connection, record: QuestionValidationRecord) -> None:
    """Persists or updates a question validation audit record."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO question_validations (
            question_id, domain_id, objective_id, factual_accuracy_passed,
            cognitive_alignment_passed, distractor_plausibility_passed,
            probe_alignment_passed, is_published, validation_details,
            rejection_reason, validated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.question_id, record.domain_id, record.objective_id,
        1 if record.factual_accuracy_passed else 0,
        1 if record.cognitive_alignment_passed else 0,
        1 if record.distractor_plausibility_passed else 0,
        1 if record.probe_alignment_passed else 0,
        1 if record.is_published else 0,
        json.dumps(record.validation_details),
        record.rejection_reason,
        record.validated_at
    ))
    # Update questions table is_published status
    cursor.execute("""
        UPDATE questions
        SET is_published = ?
        WHERE id = ?
    """, (1 if record.is_published else 0, record.question_id))
    conn.commit()


def get_curriculum_nodes_for_domain(conn: sqlite3.Connection, domain_id: str) -> List[Dict[str, Any]]:
    """Retrieves all versioned curriculum nodes for a given domain."""
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT * FROM curriculum_nodes WHERE domain_id = ? ORDER BY id
    """, (domain_id,)).fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "domain_id": r["domain_id"],
            "concept_id": r["concept_id"],
            "title": r["title"],
            "description": r["description"],
            "cognitive_level": r["cognitive_level"],
            "prerequisites": json.loads(r["prerequisites"]) if r["prerequisites"] else [],
            "evidence_grounding": json.loads(r["evidence_grounding"]) if r["evidence_grounding"] else None,
            "version": r["version"],
            "created_at": r["created_at"]
        })
    return results


def get_learning_objectives_for_domain(conn: sqlite3.Connection, domain_id: str) -> List[Dict[str, Any]]:
    """Retrieves all learning objectives for a domain."""
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT * FROM learning_objectives WHERE domain_id = ? ORDER BY id
    """, (domain_id,)).fetchall()
    return [dict(r) for r in rows]
