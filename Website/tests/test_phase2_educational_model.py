"""
Test Suite for Phase 2: Versioned Educational Data Model.
Verifies Curriculum Nodes, Learning Objectives, Question Validations, and non-destructive migrations.
"""

import sys
import sqlite3
import time
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))

from backend.app.educational_data_model import (
    CurriculumNode,
    LearningObjective,
    QuestionValidationRecord,
    migrate_educational_data_model,
    record_curriculum_nodes,
    record_learning_objectives,
    record_question_validation,
    get_curriculum_nodes_for_domain,
    get_learning_objectives_for_domain
)
from backend.app.database import get_db_connection, init_db


def test_pydantic_educational_schemas():
    """Verifies Pydantic schema validation for CurriculumNode, LearningObjective, and QuestionValidationRecord."""
    cnode = CurriculumNode(
        id="cnode_test_1",
        domain_id="test_domain",
        concept_id="test_concept",
        title="Pipelining Hazards",
        description="Structural, data, and control hazards in processor pipelines.",
        cognitive_level="analyze",
        prerequisites=["cnode_alu"]
    )
    assert cnode.cognitive_level == "analyze"
    assert cnode.prerequisites == ["cnode_alu"]

    lo = LearningObjective(
        id="lo_test_1",
        domain_id="test_domain",
        concept_id="test_concept",
        node_id="cnode_test_1",
        objective_statement="Identify and resolve data hazards using forwarding and stalling.",
        action_verb="Resolve",
        cognitive_level="apply"
    )
    assert lo.action_verb == "Resolve"

    qv = QuestionValidationRecord(
        question_id="q_test_1",
        domain_id="test_domain",
        objective_id="lo_test_1",
        factual_accuracy_passed=True,
        cognitive_alignment_passed=True,
        distractor_plausibility_passed=True,
        probe_alignment_passed=True,
        is_published=True
    )
    assert qv.is_published is True


def test_migration_idempotence_and_canonical_records():
    """Verifies that running migration repeatedly is idempotent and preserves all canonical records."""
    conn = get_db_connection()
    try:
        # Run migration multiple times
        migrate_educational_data_model(conn)
        migrate_educational_data_model(conn)

        cursor = conn.cursor()

        # Verify 0 FK violations
        cursor.execute("PRAGMA foreign_key_check")
        assert len(cursor.fetchall()) == 0

        # Verify all 5 canonical domains have exactly 185 canonical questions
        canonical_domains = ["pokemon", "class10_chemistry", "class10_biology", "class10_math", "deep_learning"]
        cursor.execute("""
            SELECT domain_id, COUNT(*)
            FROM questions
            WHERE domain_id IN ('pokemon', 'class10_chemistry', 'class10_biology', 'class10_math', 'deep_learning')
            GROUP BY domain_id
        """)
        counts = dict(cursor.fetchall())
        assert counts["pokemon"] == 35
        assert counts["class10_chemistry"] == 35
        assert counts["class10_biology"] == 35
        assert counts["class10_math"] == 35
        assert counts["deep_learning"] == 45
        assert sum(counts.values()) == 185

        # Verify all canonical questions have a published validation record
        cursor.execute("""
            SELECT COUNT(*)
            FROM questions q
            JOIN question_validations v ON q.id = v.question_id
            WHERE q.domain_id IN ('pokemon', 'class10_chemistry', 'class10_biology', 'class10_math', 'deep_learning')
              AND v.is_published = 1
        """)
        valid_canonical_count = cursor.fetchone()[0]
        assert valid_canonical_count == 185
    finally:
        conn.close()


def test_crud_curriculum_nodes_and_objectives():
    """Verifies inserting and querying versioned nodes and objectives."""
    conn = get_db_connection()
    try:
        now = time.time()
        test_domain = "custom_test_phase2"

        # Ensure domain exists
        conn.execute("INSERT OR IGNORE INTO domains (id, name, icon, category, description) VALUES (?, ?, ?, ?, ?)",
                     (test_domain, "Test Domain", "🔬", "Testing", "Test domain for Phase 2"))
        conn.commit()

        nodes = [
            CurriculumNode(
                id="cnode_phase2_1",
                domain_id=test_domain,
                concept_id="c_p2_1",
                title="Instruction Pipelining",
                description="Principles of multi-stage execution pipelines.",
                cognitive_level="understand",
                prerequisites=[]
            ),
            CurriculumNode(
                id="cnode_phase2_2",
                domain_id=test_domain,
                concept_id="c_p2_2",
                title="Hazard Resolution",
                description="Handling data and branch hazards.",
                cognitive_level="apply",
                prerequisites=["cnode_phase2_1"]
            )
        ]
        record_curriculum_nodes(conn, nodes)

        retrieved_nodes = get_curriculum_nodes_for_domain(conn, test_domain)
        assert len(retrieved_nodes) == 2
        titles = [n["title"] for n in retrieved_nodes]
        assert "Instruction Pipelining" in titles
        assert "Hazard Resolution" in titles

        # Clean up test domain
        conn.execute("DELETE FROM curriculum_nodes WHERE domain_id = ?", (test_domain,))
        conn.execute("DELETE FROM domains WHERE id = ?", (test_domain,))
        conn.commit()
    finally:
        conn.close()
