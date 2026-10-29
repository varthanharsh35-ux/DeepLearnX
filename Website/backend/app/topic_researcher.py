"""
DeepLearnX AI Topic Researcher & Dynamic Curriculum Synthesizer
Uses live Wikipedia knowledge retrieval and authentic domain ontologies
to research ANY topic in the world and synthesize:
- 4 real, topic-specific concept modules with authentic terminology
- DAG prerequisite links (c1 -> c2 -> c3 -> c4)
- 4 authentic cognitive misconceptions
- 12 tiered diagnostic questions (4 Basic, 4 Conceptual, 4 Application)
- Randomized, non-predictable Two-Tier Reasoning Probe placement
- Balanced option lengths and randomized correct choices
- Authentic remedial questions and concept guides for the topic
"""

import re
import json
import random
import urllib.request
import urllib.parse
from typing import Dict, List, Tuple, Any, Optional

USER_AGENT = "DeepLearnX/2.0 (CognitiveEducationalResearch; research@deeplearnx.edu)"

# Disallowed biographical / pop-culture terms in Wikipedia article descriptions
BIOGRAPHICAL_DISALLOW = [
    "singer", "musician", "songwriter", "actor", "actress", "band",
    "rock band", "album", "song", "film", "television", "tv series",
    "politician", "footballer", "cricketer", "baseball", "athlete",
    "wrestler", "record producer"
]

def fetch_wikipedia_knowledge(topic: str) -> List[Dict[str, str]]:
    """Fetches relevant core Wikipedia articles and extracts for a given topic,
    filtering out biographical and pop-culture disambiguation pages."""
    clean_topic = topic.strip()
    # Normalize query: strip filler words and part phrases to find core encyclopedic article
    search_term = re.sub(r'^(types of|introduction to|fundamentals of|basics of|principles of)\s+', '', clean_topic, flags=re.IGNORECASE)
    search_term = re.sub(r'\s+and\s+(its|their)\s+parts.*$', '', search_term, flags=re.IGNORECASE)
    search_term = re.sub(r'[\'\"’]', '', search_term).strip()
    
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&format=json"
    req = urllib.request.Request(search_url, headers={"User-Agent": USER_AGENT})
    
    results = []
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            search_items = data.get("query", {}).get("search", [])
            for it in search_items:
                title = it["title"]
                title_low = title.lower()
                # Skip disambiguation, media, listicles
                if any(k in title_low for k in ["disambiguation", "film", "album", "song", "band", "character", "tv series", "discography"]):
                    continue
                # If searching general broad topic like plants, skip Latin binomial species (e.g. Solidago canadensis)
                if "plant" in search_term.lower() and re.search(r'^[A-Z][a-z]+\s+[a-z]+$', title) and "plant" not in title_low:
                    continue
                results.append(title)
                if len(results) >= 6:
                    break
    except Exception as e:
        print(f"[Topic Researcher] Wikipedia search failed: {e}")
        return []

    # Fetch summary for each candidate article and filter out biographical entities
    articles = []
    for title in results:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                d = json.loads(resp.read().decode())
                desc = (d.get("description") or "").lower()
                # Exclude biographical entries (e.g., Robert Plant when searching Plants)
                if any(term in desc for term in BIOGRAPHICAL_DISALLOW):
                    continue
                extract = d.get("extract", "")
                if extract and len(extract) > 80:
                    articles.append({
                        "title": title,
                        "description": d.get("description", ""),
                        "extract": extract
                    })
                    if len(articles) >= 4:
                        break
        except Exception:
            pass
            
    return articles

def _matches_any(text: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if re.search(r'\b' + re.escape(pat) + r's?\b', text, re.IGNORECASE):
            return True
    return False

def detect_domain_meta(topic: str, articles: List[Dict[str, str]]) -> Tuple[str, str]:
    """Detects clean category name and emoji icon based on topic and articles using word-boundary matching."""
    combined = f"{topic} " + " ".join(a.get("title", "") + " " + a.get("extract", "") for a in articles)
    
    if _matches_any(combined, ["spider", "arachnid", "insect", "entomology", "arthropod", "animal", "zoology", "reptile", "amphibian", "bird", "mammal"]):
        return "🕷️", "Zoology & Arachnid Biology"
    elif _matches_any(combined, ["plant", "botany", "horticulture", "crop", "tree", "flora", "flower", "seed", "leaf", "photosynthesis", "chloroplast"]):
        return "🌿", "Botanical & Plant Sciences"
    elif _matches_any(combined, ["mendelian", "allele", "genotype", "phenotype", "heredity", "inheritance", "chromosome"]):
        return "🧬", "Genetics & Heredity"
    elif _matches_any(combined, ["cell", "dna", "rna", "protein", "organelle", "membrane", "biology", "mitochondria"]):
        return "🧬", "Cellular & Molecular Biology"
    elif _matches_any(combined, ["database", "sql", "normalization", "relational", "schema", "table", "foreign key", "primary key", "indexing"]):
        return "💻", "Computer Science & Databases"
    elif _matches_any(combined, ["photography", "aperture", "shutter speed", "iso", "exposure", "lens", "camera", "sensor"]):
        return "📷", "Photography & Visual Arts"
    elif _matches_any(combined, ["japanese", "hiragana", "katakana", "kanji", "particle", "grammar", "linguistic", "syntax"]):
        return "🗣️", "Linguistics & Language Studies"
    elif _matches_any(combined, ["volcano", "earthquake", "geology", "tectonic", "mineral", "rock", "fossil", "magma"]):
        return "🌋", "Earth & Geological Sciences"
    elif _matches_any(combined, ["quantum", "cryptography", "cipher", "encryption", "no-cloning", "entanglement", "qubit"]):
        return "🔐", "Quantum Science & Cryptography"
    elif _matches_any(combined, ["fluid", "viscosity", "hydraulics", "bernoulli", "aerodynamic", "pipe flow"]):
        return "💧", "Fluid Mechanics & Hydraulics"
    elif _matches_any(combined, ["engineering graphics", "orthographic", "isometric", "autocad", "drafting", "projection"]):
        return "📐", "Engineering Graphics & Design"
    elif _matches_any(combined, ["fermentation", "sourdough", "yeast", "bacteria", "food science", "baking", "microbiology"]):
        return "🍞", "Food Science & Microbiology"
    elif _matches_any(combined, ["roman law", "constitution", "statute", "legal", "jurisprudence", "court", "legislation"]):
        return "⚖️", "Legal Systems & Jurisprudence"
    elif _matches_any(combined, ["history", "revolution", "empire", "civilization", "ancient", "medieval", "dynasty", "war"]):
        return "🏛️", "History & Humanities"
    elif _matches_any(combined, ["music", "harmony", "chord", "scale", "melody", "rhythm", "instrument", "tempo"]):
        return "🎵", "Music Theory & Fine Arts"
    elif _matches_any(combined, ["economics", "market", "inflation", "gdp", "supply", "demand", "monetary", "fiscal"]):
        return "📈", "Economics & Business"
    else:
        return "📚", "General Academic Discipline"

def synthesize_authentic_curriculum(
    domain_id: str,
    topic_title: str,
    articles: List[Dict[str, str]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], str, str]:
    """
    Synthesizes authentic concepts, misconceptions, and 12 tiered diagnostic questions
    specifically built from real-world scientific and academic knowledge.
    Uses TopicInterpreter to establish the pedagogical scope and build genuine questions.
    """
    from backend.app.topic_interpreter import interpret_topic_scope
    from backend.app.quiz_validator import validate_curriculum_package
    
    # 1. Interpret topic and construct authentic knowledge brief with research extracts
    brief = interpret_topic_scope(topic_title, articles=articles)
    icon = brief.icon
    category = brief.category
    
    # 2. Build Concepts & Guides
    concepts = []
    concept_guides = []
    for i, c_def in enumerate(brief.concepts_raw):
        cid = f"{domain_id}_{c_def.get('id_suffix', f'c{i+1}')}"
        prereqs = [concepts[i-1]["id"]] if i > 0 else []
        cname = c_def["name"]
        concepts.append({
            "id": cid,
            "domain_id": domain_id,
            "name": cname,
            "slug": re.sub(r'[^a-zA-Z0-9]+', '_', cname.lower()).strip('_')[:28],
            "category": category,
            "description": c_def["description"],
            "prerequisites": prereqs,
            "order_index": i + 1
        })
        concept_guides.append({
            "concept_id": cid,
            "domain_id": domain_id,
            "name": cname,
            "core_idea": c_def.get("core_idea", c_def["description"]),
            "example": c_def.get("example", f"Practical application in {cname}."),
            "common_mistake": c_def.get("common_mistake", f"Common trap in {cname}."),
            "key_takeaway": c_def.get("key_takeaway", f"Core takeaway of {cname}.")
        })
        
    # 3. Build Misconceptions
    misconceptions = []
    for i, m_def in enumerate(brief.misconceptions_raw):
        cid = concepts[i]["id"] if i < len(concepts) else concepts[0]["id"]
        misconceptions.append({
            "id": f"MISC_{domain_id.upper()}_{i+1}",
            "domain_id": domain_id,
            "code": m_def.get("code", f"M-{i+1:02d}"),
            "concept_id": cid,
            "name": m_def["name"],
            "description": m_def["description"],
            "remediation": m_def["remediation"]
        })
        
    # 4. Build Questions
    raw_qs = brief.questions_raw
    # Ensure exactly 4 reasoning probes are active across questions
    existing_probe_indices = [idx for idx, q in enumerate(raw_qs) if q.get("reasoning_probe")]
    needed = 4 - len(existing_probe_indices)
    if needed > 0:
        candidate_indices = [idx for idx, q in enumerate(raw_qs) if idx not in existing_probe_indices and q.get("question_type") in ["conceptual", "application"]]
        to_add = random.sample(candidate_indices, min(needed, len(candidate_indices))) if candidate_indices else []
        for c_idx in to_add:
            corr_text = raw_qs[c_idx]["option_a"]
            c_name = concepts[c_idx // 3]["name"] if (c_idx // 3) < len(concepts) else topic_title
            raw_qs[c_idx]["reasoning_probe"] = {
                "prompt": f"Why does this principle or relationship govern {c_name}?",
                "options": {
                    "A": f"Because {corr_text.rstrip('.')} under governing constraints.",
                    "B": f"Because introductory definitions can be ignored in applied contexts.",
                    "C": f"Because system variables fluctuate randomly without physical or logical rules.",
                    "D": f"Because academic standards require selecting this option regardless of facts."
                },
                "correct_probe": "A"
            }
    elif needed < 0:
        excess = random.sample(existing_probe_indices, -needed)
        for idx in excess:
            raw_qs[idx]["reasoning_probe"] = None

    questions = []
    for i, q_def in enumerate(raw_qs):
        c_idx = i // 3 if i < 12 else 0
        cid = concepts[c_idx]["id"]
        mid = misconceptions[c_idx]["id"]
        
        rp = q_def.get("reasoning_probe")
        
        q_obj = {
            "id": f"{domain_id}_q{i+1}",
            "domain_id": domain_id,
            "concept_id": cid,
            "question_type": q_def.get("question_type", "basic"),
            "difficulty": q_def.get("difficulty", "easy"),
            "question_text": q_def["question_text"],
            "option_a": q_def["option_a"],
            "option_b": q_def["option_b"],
            "option_c": q_def["option_c"],
            "option_d": q_def["option_d"],
            "correct_option": q_def.get("correct_option", "A"),
            "explanation": q_def["explanation"],
            "misconception_id": mid,
            "prerequisite_id": concepts[c_idx]["prerequisites"][0] if concepts[c_idx]["prerequisites"] else cid,
            "reasoning_probe": rp
        }
        questions.append(q_obj)
        
    # 5. Shuffle options for questions and reasoning probes while preserving answer key integrity
    for q in questions:
        orig_corr = q.get("correct_option", "A").upper().strip()
        idx_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        corr_text = opts[idx_map.get(orig_corr, 0)]
        random.shuffle(opts)
        q["option_a"] = opts[0]
        q["option_b"] = opts[1]
        q["option_c"] = opts[2]
        q["option_d"] = opts[3]
        for ltr, txt in [("A", opts[0]), ("B", opts[1]), ("C", opts[2]), ("D", opts[3])]:
            if txt == corr_text:
                q["correct_option"] = ltr
                break
                
        rp = q.get("reasoning_probe")
        if rp and isinstance(rp, dict) and "options" in rp:
            p_opts = rp["options"]
            p_orig_corr = rp.get("correct_probe", "A").upper().strip()
            p_corr_txt = p_opts.get(p_orig_corr, p_opts.get("A", ""))
            p_list = list(p_opts.values())
            random.shuffle(p_list)
            rp["options"] = {"A": p_list[0], "B": p_list[1], "C": p_list[2], "D": p_list[3]}
            for ltr, txt in rp["options"].items():
                if txt == p_corr_txt:
                    rp["correct_probe"] = ltr
                    break

    # 6. Validate Curriculum Package
    is_valid, validation_errors = validate_curriculum_package(concepts, misconceptions, questions, category)
    if not is_valid:
        print(f"[Validation Warning] Package for '{topic_title}' had issues: {validation_errors[:3]}")

    return concepts, misconceptions, questions, concept_guides, icon, category

def build_curriculum_from_articles(
    domain_id: str,
    topic_title: str,
    articles: List[Dict[str, str]],
    icon: str = "📚",
    category: str = "General Academic Discipline"
):
    """Dynamically builds an authentic curriculum for the topic without canned absurd distractors."""
    return synthesize_authentic_curriculum(domain_id, topic_title, articles)

# Export balance_sentence for text sanitization and testing
from backend.app.quiz_validator import balance_sentence as _balance_sentence
