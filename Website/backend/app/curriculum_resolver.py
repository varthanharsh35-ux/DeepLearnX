"""
DeepLearnX Universal Curriculum & Academic Topic Resolver.

Responsible for:
1. Hierarchical academic identification:
   Education Board -> Class / Grade -> Subject -> Unit -> Chapter -> Topic -> Subtopic.
2. Canonical domain & concept resolution:
   Mapping chapters to domain_id and concept_id when preloaded questions exist,
   preventing cross-subject contamination.
3. Discovering existing custom-generated domains in the SQLite database.
4. Supplying structured curriculum context for intelligent on-demand generation
   when no preloaded questions exist.
"""

import re
import sqlite3
import unicodedata
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Known boards & curricula
BOARDS = {
    "ncert": "NCERT",
    "cbse": "CBSE",
    "icse": "ICSE",
    "isc": "ISC",
    "state board": "State Board",
    "ap": "Advanced Placement (AP)",
    "ib": "International Baccalaureate (IB)",
    "gcse": "GCSE",
    "igcse": "IGCSE",
    "a levels": "A-Levels",
    "a-level": "A-Levels",
    "university": "University",
    "college": "College",
}

# Standard grade/class patterns
GRADE_PATTERN = re.compile(
    r'\b(?:class|grade|standard|std)\s*[:\-]?\s*([0-9]{1,2}(?:th|st|nd|rd)?|[ivxlcdm]+)\b|\b([0-9]{1,2}(?:th|st|nd|rd))\s*(?:class|grade|standard|std)\b',
    re.IGNORECASE
)

# Standard chapter/unit patterns
CHAPTER_PATTERN = re.compile(
    r'\b(?:chapter|unit|ch|module|part|section)\s*[:\-]?\s*([0-9ivxlcdm]+)\s*[:–\.-]*\s*(.*)',
    re.IGNORECASE
)

# Delimiters separating subject from chapter/topic
DELIMITERS = [
    r'\s+[–—]\s+',       # en-dash or em-dash
    r'\s+[-–—]\s+',      # hyphen with spaces
    r'\s*:\s*',          # colon
    r'\s+\|\s+',         # pipe
    r'\s+chapter\s*[:\-]?\s*',
    r'\s+unit\s*[:\-]?\s*',
]


@dataclass
class CurriculumHierarchy:
    """Structured representation of an academic topic."""
    raw_input: str
    board: Optional[str] = None
    grade: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    subtopic: Optional[str] = None
    clean_topic: str = ""
    canonical_domain_id: Optional[str] = None
    matched_concept_ids: List[str] = None
    match_type: str = "unmatched"  # 'canonical_concept', 'canonical_domain', 'unmatched_chapter', 'custom_domain_existing', 'unmatched'
    suggested_action: str = "synthesize_domain"  # 'use_preloaded', 'synthesize_chapter', 'synthesize_domain'
    available_questions: int = 0
    resolution_message: str = ""

    def __post_init__(self):
        if self.matched_concept_ids is None:
            self.matched_concept_ids = []


def normalize_text(text: str) -> str:
    """Normalizes dashes, unicode spaces, and punctuation."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = text.replace('\u2013', ' – ').replace('\u2014', ' — ').replace('\u2212', '-')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_academic_curriculum(raw_input: str) -> CurriculumHierarchy:
    """
    Parses any academic input into its hierarchical components:
    Board -> Grade -> Subject -> Chapter -> Subtopic.
    """
    cleaned = normalize_text(raw_input)
    res = CurriculumHierarchy(raw_input=raw_input)

    # 1. Detect Education Board
    lower = cleaned.lower()
    for b_key, b_name in BOARDS.items():
        pattern = r'\b' + re.escape(b_key) + r'\b'
        if re.search(pattern, lower):
            res.board = b_name
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            break

    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' :–—-')

    # 2. Detect Grade / Class
    grade_match = GRADE_PATTERN.search(cleaned)
    if grade_match:
        g_val = grade_match.group(1) or grade_match.group(2)
        g_num = re.sub(r'[^0-9]', '', g_val)
        if g_num:
            res.grade = f"Class {g_num}"
        else:
            res.grade = f"Class {g_val.upper()}"
        cleaned = GRADE_PATTERN.sub('', cleaned).strip(' :–—-')

    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' :–—-')

    # 3. Detect split between Subject and Chapter/Topic
    split_done = False
    for delim in [r'\s+[–—]\s+', r'\s+[-–—]\s+', r'\s*:\s*', r'\s+\|\s+']:
        parts = re.split(delim, cleaned, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            res.subject = parts[0].strip(' :–—-')
            res.chapter = parts[1].strip(' :–—-')
            split_done = True
            break

    if not split_done:
        ch_match = CHAPTER_PATTERN.search(cleaned)
        if ch_match:
            pre = cleaned[:ch_match.start()].strip(' :–—-')
            post = ch_match.group(2).strip(' :–—-')
            if pre:
                res.subject = pre
            ch_num = ch_match.group(1)
            res.chapter = f"Chapter {ch_num}: {post}" if post else f"Chapter {ch_num}"
            split_done = True

    if not split_done:
        known_subjects = ["chemistry", "biology", "mathematics", "math", "physics", "computer science", "science", "deep learning"]
        cleaned_lower = cleaned.lower()
        for subj in known_subjects:
            match = re.search(r'\b' + re.escape(subj) + r'\b', cleaned_lower)
            if match:
                res.subject = cleaned[match.start():match.end()].title()
                remainder = (cleaned[:match.start()] + " " + cleaned[match.end():]).strip(' :–—-')
                remainder = re.sub(r'\s+', ' ', remainder).strip()
                if remainder:
                    res.chapter = remainder
                split_done = True
                break

    if not split_done:
        res.chapter = cleaned

    parts = []
    if res.grade:
        parts.append(res.grade)
    if res.subject:
        parts.append(res.subject)
    if res.chapter:
        if parts:
            res.clean_topic = f"{' '.join(parts)} - {res.chapter}"
        else:
            res.clean_topic = res.chapter
    else:
        res.clean_topic = " ".join(parts) or raw_input.strip()

    return res


# Concept synonym / chapter topic mappings for canonical domains
CANONICAL_CONCEPT_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "class10_chemistry": {
        "chem_equations": [
            "chemical reaction", "chemical reactions", "chemical equation", "chemical equations",
            "balancing", "balancing equations", "types of reactions", "combination reaction",
            "decomposition reaction", "displacement reaction", "double displacement", "redox",
            "oxidation", "reduction", "corrosion", "rancidity", "exothermic", "endothermic"
        ],
        "acids_bases": [
            "acid", "acids", "base", "bases", "salt", "salts", "ph scale", "litmus",
            "neutralization", "indicators", "chlor-alkali", "bleaching powder",
            "baking soda", "washing soda", "plaster of paris"
        ],
        "metals_reactivity": [
            "metal", "metals", "non-metal", "non-metals", "reactivity series",
            "metallurgy", "corrosion of metals", "ionic compounds", "extraction of metals",
            "calcination", "roasting", "refining", "galvanization"
        ],
        "carbon_compounds": [
            "carbon", "carbon compounds", "covalent bond", "covalent bonding",
            "hydrocarbons", "alkanes", "alkenes", "alkynes", "functional groups",
            "homologous series", "ethanol", "ethanoic acid", "soaps and detergents",
            "saponification", "esterification"
        ]
    },
    "class10_biology": {
        "bio_respiration": [
            "respiration", "cellular respiration", "aerobic", "anaerobic", "atp",
            "glycolysis", "lungs", "alveoli", "trachea", "gas exchange"
        ],
        "bio_digestion": [
            "digestion", "human digestive system", "enzymes", "salivary amylase",
            "pepsin", "trypsin", "alimentary canal", "stomach", "small intestine",
            "villi", "bile", "nutrition", "autotrophic", "heterotrophic"
        ],
        "bio_circulation": [
            "circulation", "blood", "human heart", "blood vessels", "arteries",
            "veins", "capillaries", "double circulation", "platelets", "lymph",
            "transport in plants", "xylem", "phloem", "transpiration"
        ],
        "bio_genetics": [
            "genetics", "heredity", "mendel", "mendelian genetics", "monohybrid",
            "dihybrid", "dna", "chromosomes", "sex determination", "inheritance", "evolution"
        ]
    },
    "class10_math": {
        "math_quadratics": [
            "quadratic", "quadratic equations", "roots", "discriminant",
            "quadratic formula", "factorization of quadratics", "nature of roots"
        ],
        "math_ap": [
            "arithmetic progression", "arithmetic progressions", "ap",
            "common difference", "nth term", "sum of n terms"
        ],
        "math_trig": [
            "trigonometry", "trigonometric ratios", "trigonometric identities",
            "sin", "cos", "tan", "sec", "cosec", "cot", "trigonometric values"
        ],
        "math_coord": [
            "coordinate geometry", "distance formula", "section formula",
            "midpoint formula", "area of triangle", "cartesian plane"
        ],
        "math_heights": [
            "heights and distances", "applications of trigonometry",
            "angle of elevation", "angle of depression", "line of sight"
        ]
    }
}

CANONICAL_DOMAIN_IDS = {"pokemon", "class10_chemistry", "class10_biology", "class10_math", "deep_learning"}


def resolve_curriculum_domain(raw_topic_or_domain: str, db_path: str = "Website/database/deeplearnx.db") -> CurriculumHierarchy:
    """
    Intelligently maps any academic topic, chapter, or domain slug to:
    1. A canonical domain with matching concept(s), OR
    2. An existing custom domain in SQLite, OR
    3. Unmatched hierarchy ready for on-demand synthesis.
    """
    parsed = parse_academic_curriculum(raw_topic_or_domain)
    raw_lower = raw_topic_or_domain.strip().lower()
    clean_topic = parsed.clean_topic or raw_topic_or_domain

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Priority 1: Direct canonical domain ID or canonical name match
        row = cursor.execute("""
            SELECT id, name FROM domains 
            WHERE (id = ? OR LOWER(name) = LOWER(?))
              AND id IN ('pokemon', 'class10_chemistry', 'class10_biology', 'class10_math', 'deep_learning')
        """, (raw_topic_or_domain, raw_topic_or_domain)).fetchone()
        if row:
            parsed.canonical_domain_id = row["id"]
            parsed.match_type = "canonical_domain"
            parsed.suggested_action = "use_preloaded"
            cnt = cursor.execute("SELECT COUNT(*) FROM questions WHERE domain_id = ? AND (is_published = 1 OR is_published IS NULL)", (row["id"],)).fetchone()[0]
            parsed.available_questions = cnt
            parsed.resolution_message = f"Matched canonical domain '{row['name']}' ({row['id']})."
            return parsed

        # Priority 2: Hierarchical Canonical Concept Matching (e.g. "Class 10 NCERT Chemistry – Chemical Reactions")
        cand_domain = None
        subj_str = (parsed.subject or "").lower()
        grade_str = (parsed.grade or "").lower()

        if "10" in grade_str or "class 10" in raw_lower:
            if "chem" in subj_str or "chem" in raw_lower:
                cand_domain = "class10_chemistry"
            elif "bio" in subj_str or "bio" in raw_lower:
                cand_domain = "class10_biology"
            elif "math" in subj_str or "math" in raw_lower:
                cand_domain = "class10_math"
        elif "deep learning" in raw_lower or "neural network" in raw_lower:
            cand_domain = "deep_learning"
        elif "pokemon" in raw_lower:
            cand_domain = "pokemon"

        if cand_domain and cand_domain in CANONICAL_CONCEPT_KEYWORDS:
            concept_rules = CANONICAL_CONCEPT_KEYWORDS[cand_domain]
            matched_concepts = []
            
            search_corpus = f"{parsed.chapter or ''} {parsed.clean_topic} {raw_topic_or_domain}".lower()
            
            # Special case for "Life Processes" in Class 10 Biology (umbrella chapter covering digestion, respiration, circulation)
            if cand_domain == "class10_biology" and "life processes" in search_corpus:
                matched_concepts = ["bio_respiration", "bio_digestion", "bio_circulation"]
            else:
                for c_id, keywords in concept_rules.items():
                    for kw in keywords:
                        if re.search(r'\b' + re.escape(kw) + r'\b', search_corpus):
                            if c_id not in matched_concepts:
                                matched_concepts.append(c_id)
                            break

            if matched_concepts:
                parsed.canonical_domain_id = cand_domain
                parsed.matched_concept_ids = matched_concepts
                parsed.match_type = "canonical_concept"
                parsed.suggested_action = "use_preloaded"
                parsed.resolution_message = (
                    f"Resolved to domain '{cand_domain}' with concept filter {matched_concepts}."
                )
                pl = ",".join("?" for _ in matched_concepts)
                cnt = cursor.execute(
                    f"SELECT COUNT(*) FROM questions WHERE domain_id = ? AND concept_id IN ({pl}) AND (is_published = 1 OR is_published IS NULL)",
                    [cand_domain] + matched_concepts
                ).fetchone()[0]
                parsed.available_questions = cnt
                return parsed
            elif not parsed.chapter or parsed.chapter.strip().lower() in (subj_str, ""):
                # Student asked for the whole subject
                parsed.canonical_domain_id = cand_domain
                parsed.matched_concept_ids = []
                parsed.match_type = "canonical_domain"
                parsed.suggested_action = "use_preloaded"
                parsed.resolution_message = f"Resolved to full domain '{cand_domain}'."
                cnt = cursor.execute("SELECT COUNT(*) FROM questions WHERE domain_id = ? AND (is_published = 1 OR is_published IS NULL)", (cand_domain,)).fetchone()[0]
                parsed.available_questions = cnt
                return parsed
            else:
                # Chapter in Class 10 Chemistry with no preloaded concept (e.g. Periodic Classification)
                parsed.canonical_domain_id = cand_domain
                parsed.matched_concept_ids = []
                parsed.match_type = "unmatched_chapter"
                parsed.suggested_action = "synthesize_chapter"
                parsed.available_questions = 0
                parsed.resolution_message = (
                    f"Identified subject '{cand_domain}', but chapter '{parsed.chapter}' has no preloaded questions."
                )
                return parsed

        # Priority 3: Direct custom domain ID match (e.g. raw input is "custom_photosynthesis_6303b0")
        if raw_topic_or_domain.startswith("custom_"):
            row = cursor.execute("SELECT id, name FROM domains WHERE id = ?", (raw_topic_or_domain,)).fetchone()
            if row:
                parsed.canonical_domain_id = row["id"]
                parsed.match_type = "custom_domain_existing"
                parsed.suggested_action = "use_preloaded"
                cnt = cursor.execute("SELECT COUNT(*) FROM questions WHERE domain_id = ?", (row["id"],)).fetchone()[0]
                parsed.available_questions = cnt
                parsed.resolution_message = f"Matched custom domain '{row['name']}' ({row['id']})."
                return parsed

        # Priority 4: Search existing custom domains in SQLite by name/slug match
        custom_rows = cursor.execute("""
            SELECT id, name FROM domains 
            WHERE id LIKE 'custom_%'
            ORDER BY id DESC
        """).fetchall()

        clean_slug = re.sub(r'[^a-z0-9]', '', clean_topic.lower())
        for cr in custom_rows:
            c_name = cr["name"]
            c_id = cr["id"]
            cr_slug = re.sub(r'[^a-z0-9]', '', c_name.lower())
            if cr_slug and (cr_slug == clean_slug or (len(clean_slug) > 8 and clean_slug in cr_slug)):
                q_cnt = cursor.execute("SELECT COUNT(*) FROM questions WHERE domain_id = ?", (c_id,)).fetchone()[0]
                if q_cnt > 0:
                    parsed.canonical_domain_id = c_id
                    parsed.match_type = "custom_domain_existing"
                    parsed.suggested_action = "use_preloaded"
                    parsed.available_questions = q_cnt
                    parsed.resolution_message = f"Found existing custom-generated domain '{c_name}' ({c_id}) with {q_cnt} questions."
                    return parsed

        # Priority 5: Unmatched -> Return structured curriculum hierarchy for on-demand generation
        parsed.match_type = "unmatched"
        parsed.canonical_domain_id = None
        parsed.matched_concept_ids = []
        parsed.suggested_action = "synthesize_domain"
        parsed.available_questions = 0
        if not parsed.resolution_message:
            parsed.resolution_message = f"No preloaded questions exist for '{clean_topic}'. Automatic synthesis recommended."
        return parsed

    finally:
        conn.close()
