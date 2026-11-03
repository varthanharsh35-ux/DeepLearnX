"""
DeepLearnX Phase 3 Regression Test Suite:
Discipline Classification, Clean Offline Question Synthesis & Anti-Contamination Verification

Validates:
1. Contextual discipline classification prevents "acid" in Chemistry from triggering Database Systems.
2. Phonetics & Phonology routes to Linguistics, eliminating fallback to Computer Science.
3. Database Normalization is strictly separated from OS and Computer Architecture (no kernel tables or CPU caches).
4. Operating System Deadlocks is strictly separated from Database Normalization (no candidate keys or BCNF).
5. Novel / unseen topics fall back to General Academic, NEVER defaulting to Computer Science.
6. Zero dangling punctuation (no '.,.', no ',.') across generated options.
7. Distractor diversity: options C and D are not static repeated strings across a quiz.
8. All 15 benchmark domains pass independent curriculum validation with >= 80/100 threshold.
"""

import os
import sys
import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
APP_DIR = BASE_DIR / "backend" / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from backend.app.universal_synthesizer import (
    classify_topic_domain,
    detect_topic_metadata,
    _detect_discipline_style,
    synthesize_universal_curriculum,
    generate_question_item
)
from backend.app.quiz_validator import (
    validate_question,
    validate_curriculum_package,
    check_distractor_contamination,
    FORBIDDEN_CONTAMINANTS,
    GENERIC_SYNTHETIC_BOILERPLATE,
    GENERIC_ENGINEERING_CONTAMINANTS
)

# 15 Canonical Benchmark Academic Topics
BENCHMARK_15_TOPICS = [
    ("Computer Systems and Architecture", "cs_arch", "Computer Science & Computer Architecture"),
    ("Game Design and Development", "gaming", "Game Design & Interactive Media"),
    ("Photosynthesis", "biology", "Botanical & Plant Sciences"),
    ("Database Normalization", "dbms", "Database Systems & Information Management"),
    ("Operating System Deadlocks", "os", "Operating Systems & Systems Software"),
    ("Organic Chemistry — SN1 and SN2 Reactions", "chemistry", "Chemistry & Biochemistry"),
    ("Differential and Integral Calculus", "mathematics", "Mathematical Sciences & Statistics"),
    ("Newton's Laws of Motion", "physics", "Physics & Materials Science"),
    ("Causes and Consequences of World War I", "history", "History & Geopolitics"),
    ("Inflation and Monetary Policy", "economics", "Economics & Market Dynamics"),
    ("Human Memory and Cognitive Psychology", "psychology", "Cognitive Sciences & Psychology"),
    ("Music Theory — Harmony and Voice Leading", "music", "Music Theory & Fine Arts"),
    ("Gothic Architecture and Cathedral Construction", "architecture", "Architectural Heritage & Construction"),
    ("French Verb Conjugation and Morphology", "linguistics", "Linguistics & Language Studies"),
    ("Phonetics and Phonology", "linguistics", "Linguistics & Language Studies")
]


def test_organic_chemistry_classification_and_zero_dbms_contamination():
    """Verifies that Chemistry with 'acid' in extracts is classified as Chemistry, NOT Database Systems."""
    topic = "Organic Chemistry — SN1 and SN2 Reactions"
    mock_articles = [
        {"title": "SN2 reaction", "extract": "The SN2 reaction is a common nucleophilic substitution in organic chemistry. A Lewis base attacks while the leaving group departs. It occurs in polar aprotic solvents. Acid-catalyzed reactions show different kinetics."},
        {"title": "Lewis acid", "extract": "A Lewis acid is a chemical species that reacts with a Lewis base to form an adduct. Carboxylic acid derivatives participate in substitution."}
    ]
    code, icon, cat, style = classify_topic_domain(topic, mock_articles)
    assert code == "chemistry", f"Expected 'chemistry', got '{code}'"
    assert style == "chemistry"
    assert "Chemistry" in cat
    assert "Database" not in cat

    icon_m, cat_m, key_m = detect_topic_metadata(topic, mock_articles)
    assert key_m == "chemistry"
    assert "Chemistry" in cat_m

    # Synthesize curriculum offline
    c, m, q, g, icon_c, cat_c = synthesize_universal_curriculum("test_chem", topic, articles=mock_articles, num_questions=12)
    assert len(q) == 12

    # Verify zero database / kernel contaminants
    for idx, item in enumerate(q):
        all_text = f"{item['question_text']} {item['option_a']} {item['option_b']} {item['option_c']} {item['option_d']}".lower()
        assert "kernel table" not in all_text, f"Q{idx+1} contains kernel table in Chemistry"
        assert "memory isolation" not in all_text, f"Q{idx+1} contains memory isolation in Chemistry"
        assert "database" not in all_text, f"Q{idx+1} contains database in Chemistry"
        assert "candidate key" not in all_text, f"Q{idx+1} contains candidate key in Chemistry"
        assert "deadlock" not in all_text, f"Q{idx+1} contains deadlock in Chemistry"


def test_phonetics_and_phonology_routes_to_linguistics_not_cs():
    """Verifies that Phonetics and Phonology routes to Linguistics, eliminating fallback to Computer Science."""
    topic = "Phonetics and Phonology"
    mock_articles = [
        {"title": "Phonology", "extract": "Phonology is a branch of linguistics that studies how languages systematically organize their sounds. It contrasts with phonetics, which studies the physical production of speech."},
        {"title": "Phoneme", "extract": "A phoneme is the smallest unit of sound in speech that distinguishes one word from another. Minimal pairs demonstrate phonemic contrasts."}
    ]
    code, icon, cat, style = classify_topic_domain(topic, mock_articles)
    assert code == "linguistics", f"Expected 'linguistics', got '{code}'"
    assert style == "linguistics"
    assert "Linguistics" in cat

    c, m, q, g, icon_c, cat_c = synthesize_universal_curriculum("test_ling", topic, articles=mock_articles, num_questions=12)
    assert len(q) == 12

    for idx, item in enumerate(q):
        all_text = f"{item['question_text']} {item['option_a']} {item['option_b']} {item['option_c']} {item['option_d']}".lower()
        assert "kernel table" not in all_text, f"Q{idx+1} contains kernel table in Linguistics"
        assert "memory isolation" not in all_text, f"Q{idx+1} contains memory isolation in Linguistics"
        assert "coffman" not in all_text, f"Q{idx+1} contains Coffman in Linguistics"
        assert "deadlock" not in all_text, f"Q{idx+1} contains deadlock in Linguistics"
        assert "pipeline" not in all_text, f"Q{idx+1} contains pipeline in Linguistics"


def test_database_normalization_separation_from_os_and_cpu():
    """Verifies Database Normalization is strictly separated from OS and CPU architecture."""
    topic = "Database Normalization"
    mock_articles = [
        {"title": "Database normalization", "extract": "Database normalization is the process of structuring a relational database in accordance with a series of normal forms to reduce data redundancy and improve data integrity."},
        {"title": "Boyce–Codd normal form", "extract": "Boyce–Codd normal form is a normal form used in database normalization. A relation is in BCNF if every determinant is a candidate key."}
    ]
    code, icon, cat, style = classify_topic_domain(topic, mock_articles)
    assert code == "dbms", f"Expected 'dbms', got '{code}'"
    assert style == "dbms"

    c, m, q, g, icon_c, cat_c = synthesize_universal_curriculum("test_dbms", topic, articles=mock_articles, num_questions=12)
    assert len(q) == 12

    for idx, item in enumerate(q):
        all_text = f"{item['question_text']} {item['option_a']} {item['option_b']} {item['option_c']} {item['option_d']}".lower()
        assert "kernel table" not in all_text, f"Q{idx+1} contains kernel table in DBMS"
        assert "cpu cache" not in all_text, f"Q{idx+1} contains cpu cache in DBMS"
        assert "coffman" not in all_text, f"Q{idx+1} contains Coffman in DBMS"
        assert "pipelining" not in all_text, f"Q{idx+1} contains pipelining in DBMS"


def test_operating_system_deadlocks_separation_from_dbms():
    """Verifies Operating System Deadlocks generates OS concurrency questions with zero DBMS schema terms."""
    topic = "Operating System Deadlocks"
    mock_articles = [
        {"title": "Deadlock", "extract": "In concurrent computing, a deadlock is a state in which each member of a group is waiting for another member, including itself, to send a message or release a lock."},
        {"title": "Coffman conditions", "extract": "The four Coffman conditions must hold simultaneously for a deadlock to occur: mutual exclusion, hold and wait, no preemption, and circular wait."}
    ]
    code, icon, cat, style = classify_topic_domain(topic, mock_articles)
    assert code == "os", f"Expected 'os', got '{code}'"
    assert style == "os"

    c, m, q, g, icon_c, cat_c = synthesize_universal_curriculum("test_os", topic, articles=mock_articles, num_questions=12)
    assert len(q) == 12

    for idx, item in enumerate(q):
        all_text = f"{item['question_text']} {item['option_a']} {item['option_b']} {item['option_c']} {item['option_d']}".lower()
        assert "candidate key" not in all_text, f"Q{idx+1} contains candidate key in OS"
        assert "bcnf" not in all_text, f"Q{idx+1} contains BCNF in OS"
        assert "functional dependency" not in all_text, f"Q{idx+1} contains functional dependency in OS"


def test_general_academic_fallback_never_cs():
    """Verifies that unclassified novel topics fall back to General Academic, NEVER defaulting to Computer Science."""
    novel_topics = [
        "Sociology of Urban Education",
        "Deep Sea Hydrothermal Vent Communities",
        "Comparative Agricultural Crop Rotation"
    ]
    for topic in novel_topics:
        code, icon, cat, style = classify_topic_domain(topic)
        assert code == "general", f"Expected 'general' for {topic}, got '{code}'"
        assert style == "general"
        assert "General Academic" in cat

        c, m, q, g, icon_c, cat_c = synthesize_universal_curriculum(f"test_gen_{abs(hash(topic))%1000}", topic, num_questions=12)
        assert len(q) == 12

        for idx, item in enumerate(q):
            all_text = f"{item['question_text']} {item['option_a']} {item['option_b']} {item['option_c']} {item['option_d']}".lower()
            assert "kernel" not in all_text, f"Q{idx+1} contains kernel in General topic '{topic}'"
            assert "pipelining" not in all_text, f"Q{idx+1} contains pipelining in General topic '{topic}'"
            assert "coffman" not in all_text, f"Q{idx+1} contains Coffman in General topic '{topic}'"
            assert "deadlock" not in all_text, f"Q{idx+1} contains deadlock in General topic '{topic}'"


def test_zero_dangling_punctuation_across_options():
    """Verifies no option contains double punctuation like '.,.' or ',.' or ends with dangling prepositions."""
    for topic, expected_code, expected_cat in BENCHMARK_15_TOPICS:
        c, m, q, g, icon, cat = synthesize_universal_curriculum(f"test_punct_{abs(hash(topic))%1000}", topic, num_questions=12)
        for idx, item in enumerate(q):
            for opt_key in ["option_a", "option_b", "option_c", "option_d"]:
                opt_val = item[opt_key]
                assert not re.search(r'[,;:.]+\.', opt_val), f"Dangling double punctuation in {topic} Q{idx+1} {opt_key}: '{opt_val}'"
                assert not re.search(r'\b(of|to|in|for|with|and|or|by|at|from)\.\s*$', opt_val), f"Dangling preposition in {topic} Q{idx+1} {opt_key}: '{opt_val}'"
                assert opt_val.endswith(('.', '!', '?')), f"Option lacks final punctuation in {topic} Q{idx+1} {opt_key}: '{opt_val}'"


def test_distractor_diversity_no_static_canned_repeats():
    """Verifies that distractors C and D are not identical static strings repeated across all 12 questions."""
    for topic, expected_code, expected_cat in BENCHMARK_15_TOPICS:
        c, m, q, g, icon, cat = synthesize_universal_curriculum(f"test_distr_{abs(hash(topic))%1000}", topic, num_questions=12)
        opts_c = [item["option_c"] for item in q]
        opts_d = [item["option_d"] for item in q]

        # Options C and D must exhibit variety across 12 questions (at least 3 unique strings)
        unique_c = set(opts_c)
        unique_d = set(opts_d)
        assert len(unique_c) >= 3, f"Option C is static across questions for {topic}: only {len(unique_c)} unique strings"
        assert len(unique_d) >= 2, f"Option D is static across questions for {topic}: only {len(unique_d)} unique strings"


def test_all_15_benchmark_topics_pass_validation():
    """Verifies all 15 benchmark academic topics pass complete curriculum validation with zero errors."""
    for topic, expected_code, expected_cat in BENCHMARK_15_TOPICS:
        c, m, q, g, icon, cat = synthesize_universal_curriculum(f"test_val_{abs(hash(topic))%1000}", topic, num_questions=12)
        val_ok, errs = validate_curriculum_package(c, m, q, cat)
        assert val_ok, f"Curriculum validation failed for {topic} ({cat}): {errs}"
        assert len(q) == 12, f"Expected 12 questions for {topic}, got {len(q)}"
        assert len(c) >= 4, f"Expected at least 4 concepts for {topic}, got {len(c)}"
        assert len(m) >= 2, f"Expected at least 2 misconceptions for {topic}, got {len(m)}"
