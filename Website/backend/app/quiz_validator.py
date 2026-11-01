"""
DeepLearnX Quiz Quality Validator and Auto-Revision Engine
Implements strict pedagogical validation rules to eliminate:
- Cross-domain distractor contamination (metallic wires, boiling hydrocarbons in biology)
- Incomplete / truncated answers (sentences sliced mid-phrase, e.g. "in other parts of.")
- Robotic, repetitive question stems ("what primary governing mechanism characterizes...")
- Option length bias (correct option significantly longer than distractors)
- Contradictory Two-Tier reasoning checks
- Missing or generic remedial lessons
"""

import re
from typing import Dict, List, Tuple, Any, Optional

# Generic engineering boilerplate terms that must NEVER appear in non-engineering disciplines
GENERIC_ENGINEERING_CONTAMINANTS = [
    "feedback regulation",
    "system equilibrium",
    "non-linear saturation",
    "critical threshold",
    "governing mechanism",
    "fluctuating operational",
    "foundational premise inversion",
    "directional causality trap",
    "boundary limit neglect",
    "symptom vs. root cause confusion",
    "an analyst extrapolates",
    "an engineer extrapolates",
    "governing boundary constraints",
    "operational boundaries",
    "linear model extrapolation",
    "damping breakdown"
]

# Prohibited cross-domain contamination terms by category
FORBIDDEN_CONTAMINANTS = {
    "biology": [
        "metallic wire", "electrical current through metal", "hydrocarbon solvent",
        "silicate mineral", "operating system kernel", "compiler pass",
        "packet routing", "monarchical decree", "feudal estate", "harmonic cadence"
    ],
    "history": [
        "organelle", "mitochondria", "chloroplast", "hydrocarbon", "compiler",
        "operating system", "packet header", "fluid viscosity", "reynolds number"
    ],
    "music": [
        "hydrocarbon", "mitochondria", "compiler", "operating system",
        "parliamentary decree", "french revolution", "reynolds number", "cavitation"
    ],
    "math": [
        "mitochondria", "monarchical decree", "chloroplast", "hydrocarbon solvent",
        "bastille", "harmonic cadence"
    ],
    "law": [
        "chloroplast", "mitochondria", "hydrocarbon", "reynolds number",
        "compiler pass", "quantum entanglement"
    ],
    "culinary": [
        "operating system", "compiler pass", "packet routing", "quantum entanglement",
        "hydraulic pressure", "reynolds number", "parliamentary decree", "linear extrapolation"
    ]
}

# Incomplete sentence endings that indicate destructive truncation
DANGLING_ENDINGS = [
    r'\bof\.\s*$', r'\bto\.\s*$', r'\bin\.\s*$', r'\bfor\.\s*$', r'\bwith\.\s*$',
    r'\band\.\s*$', r'\bor\.\s*$', r'\bby\.\s*$', r'\bat\.\s*$', r'\bfrom\.\s*$',
    r'\bthat\.\s*$', r'\bwhich\.\s*$', r'\bparts of\.\s*$', r'\bsuch as\.\s*$',
    r'\bincluding\.\s*$', r'\bbecause\.\s*$'
]

# Robotic boilerplate stems that must not be used on academic topics
ROBOTIC_STEMS = [
    r'what primary governing mechanism or functional role characterizes',
    r'what core analytical principle must be applied',
    r'according to academic classification, which statement accurately defines',
    r'what defines the governing boundary constraints and conservation limits',
    r'how do governing mechanisms maintain stability under fluctuating operational conditions',
    r'extrapolates a linear model.*far beyond its empirically validated threshold'
]


def check_topic_name_integrity(name: str) -> Tuple[bool, str]:
    """Ensures topic name does not have corruptions, typos like 'Lawss', or duplication."""
    if not name or len(name.strip()) < 2:
        return False, "Topic name is empty or too short."
    cleaned = name.strip()
    # Check for corruptions like 'Lawss' (double 's' at end of word not in standard double-s words)
    standard_ss = {"pass", "class", "grass", "glass", "brass", "mass", "bass", "compass", "bypass",
                   "loss", "boss", "moss", "cross", "gloss", "dross",
                   "kiss", "miss", "hiss", "bliss", "abyss",
                   "fuss", "muss", "truss",
                   "stress", "process", "access", "success", "excess", "progress", "recess", "address",
                   "express", "impress", "press", "business", "illness", "fitness", "darkness", "witness"}
    for word in cleaned.split():
        w_low = word.lower().strip(".,!?:;-()")
        if w_low.endswith("ss") and w_low not in standard_ss and len(w_low) > 3:
            return False, f"Corrupted topic name detected with invalid double 's': '{word}'"
    return True, "Valid"


def check_sentence_completeness(text: str) -> Tuple[bool, str]:
    """Ensures text is a complete, well-formed sentence or phrase."""
    if not text or len(text.strip()) < 8:
        return False, "Text is empty or too short."
    
    cleaned = text.strip()
    
    # Check for dangling prepositions/conjunctions before period
    for pat in DANGLING_ENDINGS:
        if re.search(pat, cleaned, re.IGNORECASE):
            return False, f"Dangling ending matching pattern '{pat}': '{cleaned[-25:]}'"
            
    # Check that it ends with valid terminal punctuation (handling closing quotes and brackets)
    stripped = cleaned.rstrip("'\"’”)]}")
    if not stripped or stripped[-1] not in '.?!':
        if cleaned[-1] not in '.?!':
            return False, f"Missing terminal punctuation: '{cleaned[-20:]}'"
        
    return True, "Complete"


def check_distractor_contamination(options: List[str], category: str) -> Tuple[bool, str]:
    """Checks for absurd cross-domain contamination and generic engineering jargon in option strings."""
    cat_low = category.lower()
    
    # Determine which forbidden list applies
    active_forbidden = []
    is_engineering = any(k in cat_low for k in ["engineering graphics", "fluid mechanics", "control system", "mechanical engineering"])
    
    # For non-engineering categories, strictly forbid generic engineering contaminants
    if not is_engineering:
        active_forbidden.extend(GENERIC_ENGINEERING_CONTAMINANTS)
        
    if any(k in cat_low for k in ["biolog", "plant", "botan", "zoolog", "spider", "insect", "medic"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["biology"])
    elif any(k in cat_low for k in ["history", "humanit", "revolution", "leader"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["history"])
    elif any(k in cat_low for k in ["music", "art"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["music"])
    elif any(k in cat_low for k in ["math", "fraction", "arithmetic", "probability"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["math"])
    elif any(k in cat_low for k in ["law", "constitution", "legal"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["law"])
    elif any(k in cat_low for k in ["culinary", "pastry", "baking", "food"]):
        active_forbidden.extend(FORBIDDEN_CONTAMINANTS["culinary"])
        
    for opt in options:
        opt_low = opt.lower()
        for forbidden in active_forbidden:
            if forbidden.lower() in opt_low:
                return False, f"Found forbidden cross-domain contamination '{forbidden}' in option: '{opt[:60]}...'"
                
    return True, "Clean"


def check_distinct_options(options: List[str]) -> Tuple[bool, str]:
    """Ensures all 4 options are distinct strings."""
    norm = [re.sub(r'\s+', ' ', o.strip().lower()) for o in options]
    if len(set(norm)) != len(options):
        return False, "Duplicate options found."
    return True, "Distinct"


def check_option_length_balance(options: List[str], correct_idx: int) -> Tuple[bool, float]:
    """
    Checks if options are reasonably balanced.
    Returns (is_acceptable, length_ratio).
    """
    lengths = [len(o.split()) for o in options]
    max_len = max(lengths)
    min_len = max(min(lengths), 1)
    ratio = max_len / float(min_len)
    
    # Flag only if correct option is conspicuously longer (> 2.5x the shortest)
    is_biased = (lengths[correct_idx] == max_len and ratio > 2.5 and lengths[correct_idx] > min_len + 12)
    return not is_biased, ratio


def validate_question(q: Dict[str, Any], category: str = "") -> Tuple[bool, List[str]]:
    """
    Validates a single question against all quality criteria.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    # 1. Text presence and robotic stem rejection
    q_text = q.get("question_text", "").strip()
    if not q_text or len(q_text) < 15:
        errors.append("Question text missing or too short.")
    else:
        q_low = q_text.lower()
        for stem in ROBOTIC_STEMS:
            if re.search(stem, q_low, re.IGNORECASE):
                errors.append(f"Robotic boilerplate stem detected: '{stem}'")
        
    # 2. Options completeness
    opts = [
        q.get("option_a", ""),
        q.get("option_b", ""),
        q.get("option_c", ""),
        q.get("option_d", "")
    ]
    for idx, opt in enumerate(opts):
        comp_ok, comp_err = check_sentence_completeness(opt)
        if not comp_ok:
            errors.append(f"Option {chr(65+idx)} incomplete: {comp_err}")
            
    # 3. Distinct options
    dist_ok, dist_err = check_distinct_options(opts)
    if not dist_ok:
        errors.append(dist_err)
        
    # 4. Correct option valid
    corr = str(q.get("correct_option", "A")).strip().upper()
    if corr not in ["A", "B", "C", "D"]:
        errors.append(f"Invalid correct_option: {corr}")
        
    # 5. Distractor contamination
    contam_ok, contam_err = check_distractor_contamination(opts, category)
    if not contam_ok:
        errors.append(contam_err)
        
    # 6. Explanation
    expl = q.get("explanation", "").strip()
    if not expl or len(expl) < 15:
        errors.append("Explanation missing or too brief.")
        
    # 7. Two-Tier Reasoning Probe validation (if present)
    rp = q.get("reasoning_probe")
    if rp and isinstance(rp, dict):
        p_prompt = rp.get("prompt", "").strip()
        p_opts = rp.get("options", {})
        p_corr = str(rp.get("correct_probe", "A")).strip().upper()
        if not p_prompt or len(p_prompt) < 12:
            errors.append("Reasoning probe prompt missing or too short.")
        if len(p_opts) != 4 or any(k not in p_opts for k in ["A", "B", "C", "D"]):
            errors.append("Reasoning probe must have 4 options (A, B, C, D).")
        else:
            p_opt_list = [p_opts["A"], p_opts["B"], p_opts["C"], p_opts["D"]]
            p_dist_ok, _ = check_distinct_options(p_opt_list)
            if not p_dist_ok:
                errors.append("Reasoning probe has duplicate options.")
            for p_ltr, p_txt in p_opts.items():
                p_comp_ok, p_comp_err = check_sentence_completeness(p_txt)
                if not p_comp_ok:
                    errors.append(f"Probe option {p_ltr} incomplete: {p_comp_err}")
                if re.search(r'\bbecause\s+because\b', p_txt, re.IGNORECASE):
                    errors.append(f"Probe option {p_ltr} contains duplicate 'Because Because'")
        if p_corr not in ["A", "B", "C", "D"]:
            errors.append(f"Invalid probe correct_probe: {p_corr}")
            
    return len(errors) == 0, errors


def validate_curriculum_package(
    concepts: List[Dict[str, Any]],
    misconceptions: List[Dict[str, Any]],
    questions: List[Dict[str, Any]],
    category: str = ""
) -> Tuple[bool, List[str]]:
    """
    Validates a complete curriculum package before persisting to database.
    """
    errors = []
    
    # Concepts count
    if len(concepts) != 4:
        errors.append(f"Expected exactly 4 concepts, got {len(concepts)}.")
        
    # Questions count
    if len(questions) != 12:
        errors.append(f"Expected exactly 12 questions, got {len(questions)}.")
        
    # Misconceptions count
    if len(misconceptions) != 4:
        errors.append(f"Expected exactly 4 misconceptions, got {len(misconceptions)}.")
        
    # Check each question
    for idx, q in enumerate(questions):
        ok, q_errs = validate_question(q, category)
        if not ok:
            for e in q_errs:
                errors.append(f"Q{idx+1}: {e}")
                
    # Reasoning probes count: must be between 3 and 5
    probes_count = sum(1 for q in questions if q.get("reasoning_probe"))
    if probes_count < 3 or probes_count > 5:
        errors.append(f"Expected between 3 and 5 reasoning probes, got {probes_count}.")
        
    # Remediation quality check on misconceptions: must NOT be generic filler
    generic_fillers = [
        "review fundamental definitions and empirical dependencies carefully",
        "before evaluating complex scenarios",
        "without verifying initial baseline definitions"
    ]
    for m in misconceptions:
        rem = (m.get("remediation") or "").lower()
        for gf in generic_fillers:
            if gf in rem:
                errors.append(f"Generic remediation filler detected in misconception: '{m.get('name')}'")
            
    return len(errors) == 0, errors

def balance_sentence(text: str, target_min: int = 85, target_max: int = 108, fallback_context: str = "") -> str:
    """Sanitize and balance extract sentences without destructive truncation or dangling prepositions."""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\([^)]*\)', '', text)  # remove parenthetical clauses
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Check if text ends cleanly with punctuation
    if not text.endswith(('.', '!', '?')):
        text = f"{text}."
        
    # Check for dangling endings: never leave dangling prepositions or conjunctions
    for pat in DANGLING_ENDINGS:
        if re.search(pat, text, re.IGNORECASE):
            text = re.sub(pat, '.', text).strip()
            if fallback_context:
                text = f"{text.rstrip('.')} {fallback_context.strip()}."

    return text if text.endswith(('.', '!', '?')) else f"{text}."
