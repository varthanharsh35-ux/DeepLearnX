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

# Disallowed biographical / pop-culture / tangential terms in Wikipedia article descriptions
BIOGRAPHICAL_DISALLOW = [
    "singer", "musician", "songwriter", "actor", "actress", "band",
    "rock band", "album", "song", "film", "television", "tv series",
    "politician", "footballer", "cricketer", "baseball", "athlete",
    "wrestler", "record producer", "video game", "comic book", "fictional character",
    "born 19", "born 20", "lawyer (born", "diplomat (born"
]

MILITARY_CONFLICT_TERMS = [
    "war", "battle", "military conflict", "armed conflict", "military intervention",
    "naval blockade", "military campaign", "invasion"
]

def fetch_wikipedia_knowledge(topic: str) -> List[Dict[str, str]]:
    """Fetches relevant core Wikipedia articles and extracts for a given topic,
    filtering out biographical, military war puns, and pop-culture disambiguation pages."""
    clean_topic = topic.strip()
    try:
        from curated_extensions import normalize_topic_title
    except ImportError:
        try:
            from app.curated_extensions import normalize_topic_title
        except ImportError:
            from backend.app.curated_extensions import normalize_topic_title
    clean_topic = normalize_topic_title(clean_topic)
    
    # Check if user topic is genuinely military or history of warfare
    is_military_topic = any(k in clean_topic.lower() for k in ["war", "battle", "military", "conflict", "invasion", "revolution"])
    
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
                # If non-military topic, skip military conflict articles (e.g. Pastry War when searching French Pastry)
                if not is_military_topic and any(m in title_low for m in ["war", "battle of", "siege of", "invasion of"]):
                    continue
                # If searching general broad topic like plants, skip Latin binomial species (e.g. Solidago canadensis)
                if "plant" in search_term.lower() and re.search(r'^[A-Z][a-z]+\s+[a-z]+$', title) and "plant" not in title_low:
                    continue
                results.append(title)
                if len(results) >= 8:
                    break
    except Exception as e:
        print(f"[Topic Researcher] Wikipedia search failed: {e}")
        return []

    # Fetch summary for each candidate article and filter out biographical and irrelevant entities
    articles = []
    for title in results:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                d = json.loads(resp.read().decode())
                desc = (d.get("description") or "").lower()
                
                # Exclude biographical entries
                if any(term in desc for term in BIOGRAPHICAL_DISALLOW):
                    continue
                    
                # Exclude military conflicts for non-military topics
                if not is_military_topic and any(term in desc for term in MILITARY_CONFLICT_TERMS):
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
    articles: List[Dict[str, str]] = None,
    num_questions: int = 12
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], str, str]:
    """
    Synthesizes authentic concepts, misconceptions, and tiered diagnostic questions
    specifically built from real-world scientific and academic knowledge.
    Routes to the universal educational intelligence synthesizer for non-linear DAGs,
    authentic concepts, and balanced questions.
    """
    try:
        from universal_synthesizer import synthesize_universal_curriculum
    except ImportError:
        try:
            from app.universal_synthesizer import synthesize_universal_curriculum
        except ImportError:
            from backend.app.universal_synthesizer import synthesize_universal_curriculum

    if articles is None:
        try:
            articles = fetch_wikipedia_knowledge(topic_title)
        except Exception:
            articles = []

    return synthesize_universal_curriculum(domain_id, topic_title, articles=articles, num_questions=num_questions)

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
try:
    from quiz_validator import balance_sentence as _balance_sentence
except ImportError:
    try:
        from app.quiz_validator import balance_sentence as _balance_sentence
    except ImportError:
        from backend.app.quiz_validator import balance_sentence as _balance_sentence
