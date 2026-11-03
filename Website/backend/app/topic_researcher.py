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
    "wrestler", "record producer", "comic book", "fictional character",
    "video game character", "video game series",
    "born 19", "born 20", "lawyer (born", "diplomat (born"
]

MILITARY_CONFLICT_TERMS = [
    "war", "battle", "military conflict", "armed conflict", "military intervention",
    "naval blockade", "military campaign", "invasion"
]

LISTICLE_PATTERNS = [
    "list of", "lists of", "comparison of", "timeline of", "usage share of",
    "outline of", "index of", "glossary of"
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
            try:
                from backend.app.curated_extensions import normalize_topic_title
            except ImportError:
                from Website.backend.app.curated_extensions import normalize_topic_title
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
                if any(lp in title_low for lp in LISTICLE_PATTERNS):
                    continue
                # If non-military topic, skip military conflict articles (e.g. Pastry War when searching French Pastry)
                if not is_military_topic and any(m in title_low for m in ["war", "battle of", "siege of", "invasion of"]):
                    continue
                # If searching general broad topic like plants, skip Latin binomial species (e.g. Solidago canadensis)
                if "plant" in search_term.lower() and re.search(r'^[A-Z][a-z]+\s+[a-z]+$', title) and "plant" not in title_low:
                    continue
                results.append(title)
                if len(results) >= 10:
                    break
    except Exception as e:
        print(f"[Topic Researcher] Wikipedia search failed: {e}")
        return []

    def _fetch_article_summaries(candidate_titles: List[str], current_articles: List[Dict[str, str]]) -> List[Dict[str, str]]:
        collected_titles = {a["title"].lower() for a in current_articles}
        for title in candidate_titles:
            if title.lower() in collected_titles:
                continue
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
            req_sum = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req_sum, timeout=5) as resp:
                    d = json.loads(resp.read().decode())
                    desc = (d.get("description") or "").lower()
                    
                    # Exclude biographical entries
                    if any(term in desc for term in BIOGRAPHICAL_DISALLOW):
                        continue
                        
                    # Exclude military conflicts for non-military topics
                    if not is_military_topic and any(term in desc for term in MILITARY_CONFLICT_TERMS):
                        continue
                        
                    extract = d.get("extract", "")
                    if extract and len(extract) > 60:
                        current_articles.append({
                            "title": title,
                            "description": d.get("description", ""),
                            "extract": extract
                        })
                        collected_titles.add(title.lower())
                        if len(current_articles) >= 4:
                            break
            except Exception:
                pass
        return current_articles

    articles = _fetch_article_summaries(results, [])

    # If fewer than 4 distinct articles, attempt secondary expansion search
    if len(articles) < 4:
        for suffix in ["concepts", "fundamentals", "mechanisms"]:
            exp_term = f"{search_term} {suffix}"
            exp_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(exp_term)}&format=json"
            try:
                exp_req = urllib.request.Request(exp_url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(exp_req, timeout=5) as resp:
                    exp_data = json.loads(resp.read().decode())
                    exp_items = exp_data.get("query", {}).get("search", [])
                    exp_titles = [
                        it["title"] for it in exp_items
                        if not any(k in it["title"].lower() for k in ["disambiguation", "film", "album", "song", "band", "character", "tv series", "discography"])
                        and not any(lp in it["title"].lower() for lp in LISTICLE_PATTERNS)
                    ]
                    articles = _fetch_article_summaries(exp_titles, articles)
                    if len(articles) >= 4:
                        break
            except Exception:
                pass

    return articles


def fetch_crossref_knowledge(topic: str, max_results: int = 2) -> List[Dict[str, Any]]:
    """Fetches peer-reviewed academic publications and abstracts from CrossRef API with substantive evidence extraction."""
    clean_topic = topic.strip()
    encoded = urllib.parse.quote(clean_topic)
    headers = {"User-Agent": "DeepLearnX/2.0 (CognitiveEducationalResearch; mailto:research@deeplearnx.edu)"}
    scholarly_items = []
    
    # Try querying with has-abstract:true first for deep scientific abstracts
    urls = [
        f"https://api.crossref.org/works?query={encoded}&filter=has-abstract:true&rows={max_results}",
        f"https://api.crossref.org/works?query={encoded}&rows={max_results}"
    ]
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("message", {}).get("items", [])
                for it in items:
                    title_list = it.get("title", [])
                    title = title_list[0] if title_list else ""
                    doi_url = it.get("URL") or f"https://doi.org/{it.get('DOI', '')}"
                    abstract = it.get("abstract") or ""
                    # Clean JATS XML tags and HTML entities from abstract
                    abstract_clean = re.sub(r'<[^>]+>', '', abstract).strip()
                    abstract_clean = re.sub(r'&[a-z]+;', ' ', abstract_clean).strip()
                    if not abstract_clean:
                        container = it.get("container-title", [""])[0] if it.get("container-title") else ""
                        abstract_clean = f"Scholarly peer-reviewed research analyzing {title} in {container}."
                    if title and not any(s["title"].lower() == title.lower() for s in scholarly_items):
                        scholarly_items.append({
                            "title": title,
                            "url": doi_url,
                            "source_type": "peer_reviewed_literature",
                            "description": f"Peer-reviewed academic research from CrossRef on {title}.",
                            "extract": abstract_clean
                        })
                if scholarly_items:
                    break
        except Exception:
            continue
            
    return scholarly_items


def fetch_multisource_academic_knowledge(topic: str) -> Dict[str, Any]:
    """
    Multi-source scholarly research pipeline.
    Combines:
    1. Wikipedia REST API (encyclopedic foundation, taxonomy & concept definitions)
    2. CrossRef Academic API (peer-reviewed journal papers, DOIs & scholarly abstracts)
    Returns structured evidence package with provenance tracking and extracted factual claims.
    Caches successful results to eliminate redundant API calls and rate-limiting.
    """
    try:
        from topic_cache import get_topic_cache
    except ImportError:
        try:
            from app.topic_cache import get_topic_cache
        except ImportError:
            from backend.app.topic_cache import get_topic_cache
    _cache = get_topic_cache()
    _cached = _cache.get_research(topic)
    if _cached:
        return _cached

    import datetime
    retrieval_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # 1. Primary encyclopedic retrieval
    wiki_articles = fetch_wikipedia_knowledge(topic)
    
    # 2. Secondary scholarly literature retrieval
    scholarly_articles = fetch_crossref_knowledge(topic, max_results=2)
    
    # Combined sources with full provenance
    all_sources = []
    for a in wiki_articles:
        all_sources.append({
            "title": a["title"],
            "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(a['title'].replace(' ', '_'))}",
            "retrieval_date": retrieval_date,
            "source_type": "encyclopedic_reference",
            "relevant_passages": a.get("extract", "")[:350],
            "description": a.get("description", "")
        })
        
    for s in scholarly_articles:
        all_sources.append({
            "title": s["title"],
            "url": s["url"],
            "retrieval_date": retrieval_date,
            "source_type": s["source_type"],
            "relevant_passages": s.get("extract", "")[:350],
            "description": s.get("description", "")
        })

    # Combined articles list for curriculum synthesizers
    combined_articles = list(wiki_articles)
    for s in scholarly_articles:
        if len(combined_articles) < 5 and not any(a["title"].lower() == s["title"].lower() for a in combined_articles):
            combined_articles.append({
                "title": s["title"],
                "description": s["description"],
                "extract": s["extract"]
            })

    # Extract clean factual claims from all retrieved passages
    extracted_facts = []
    for src in all_sources:
        passages = src.get("relevant_passages", "")
        for sent in passages.split("."):
            cs = sent.strip()
            if 35 < len(cs) < 220 and not any(bad in cs.lower() for bad in ["refer to", "disambiguation", "born in", "coordinates"]):
                extracted_facts.append(cs)

    res_pkg = {
        "topic": topic,
        "articles": combined_articles,
        "sources": all_sources,
        "extracted_facts": extracted_facts,
        "provenance": {
            "wikipedia_count": len(wiki_articles),
            "crossref_count": len(scholarly_articles),
            "total_sources": len(all_sources),
            "retrieval_timestamp": retrieval_date
        }
    }
    try:
        _cache.set_research(topic, res_pkg)
    except Exception:
        pass
    return res_pkg

def _matches_any(text: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if re.search(r'\b' + re.escape(pat) + r's?\b', text, re.IGNORECASE):
            return True
    return False

DOMAIN_DEFINITIONS: List[Tuple[str, str, List[str]]] = [
    ("🕷️", "Zoology & Animal Biology", ["spider", "arachnid", "insect", "entomology", "arthropod", "animal", "zoology", "reptile", "amphibian", "bird", "mammal", "ichthyology", "fish", "largemouth", "scales", "integument"]),
    ("🌿", "Botanical & Plant Sciences", ["plant", "botany", "horticulture", "crop", "tree", "flora", "flower", "seed", "leaf", "photosynthesis", "chloroplast"]),
    ("🧬", "Genetics & Heredity", ["mendelian", "allele", "genotype", "phenotype", "heredity", "inheritance", "chromosome"]),
    ("🧬", "Cellular & Molecular Biology", ["cell", "dna", "rna", "protein", "organelle", "membrane", "biology", "mitochondria", "epidermal", "keratin", "cuticle", "morphology", "anatomy"]),
    ("💻", "Computer Science & Databases", ["database", "sql", "normalization", "relational", "schema", "table", "foreign key", "primary key", "indexing"]),
    ("💻", "Computer Science & Systems", ["unix", "linux", "bash", "shell", "terminal", "command line", "operating system", "software", "compiler", "programming"]),
    ("✈️", "Transportation & Logistics", ["airport", "runway", "aviation", "airline", "railway", "freight", "transport", "transportation", "logistics", "passenger", "cargo", "mass transit", "rapid transit", "infrastructure", "fleet"]),
    ("🌌", "Astronomy & Astrophysics", ["astronomy", "astrophysics", "exoplanet", "planet", "stellar", "star", "galaxy", "telescope", "photometry", "radial velocity", "orbit", "solar system", "cosmology", "celestial", "space science", "light curve", "barycenter", "spectroscopy"]),
    ("📷", "Photography & Visual Arts", ["photography", "aperture", "shutter speed", "iso", "exposure", "lens", "camera", "sensor"]),
    ("🗣️", "Linguistics & Language Studies", ["japanese", "hiragana", "katakana", "kanji", "grammatical particle", "grammar", "linguistic", "syntax"]),
    ("🌋", "Earth & Geological Sciences", ["volcano", "earthquake", "geology", "tectonic", "mineral", "rock", "fossil", "magma", "river", "hydrology", "fluvial", "sediment", "geomorphology", "floodplain"]),
    ("🔐", "Quantum Science & Cryptography", ["quantum", "quark", "gluon", "hadron", "chromodynamics", "cryptography", "cipher", "encryption", "no-cloning", "entanglement", "qubit", "subatomic", "particle physics"]),
    ("💧", "Fluid Mechanics & Hydraulics", ["fluid", "viscosity", "hydraulics", "bernoulli", "aerodynamic", "pipe flow"]),
    ("📐", "Engineering Graphics & Design", ["engineering graphics", "orthographic", "isometric", "autocad", "drafting", "projection"]),
    ("🍞", "Food Science & Microbiology", ["fermentation", "sourdough", "yeast", "bacteria", "food science", "baking", "microbiology"]),
    ("⚖️", "Legal Systems & Jurisprudence", ["roman law", "constitution", "statute", "legal", "jurisprudence", "court", "legislation"]),
    ("🏛️", "History & Humanities", ["history", "revolution", "empire", "civilization", "ancient", "medieval", "dynasty", "war"]),
    ("🎵", "Music Theory & Fine Arts", ["music", "harmony", "chord", "melody", "rhythm", "instrument", "tempo", "clef", "tonality", "pentatonic", "chromatic", "solfege"]),
    ("🔊", "Acoustics & Sound Physics", ["acoustics", "sound wave", "frequency", "hertz", "auditory", "decibel", "resonance", "vibration", "pitch"]),
    ("⚾", "Sports Science & Athletics", ["baseball", "athletics", "cricket", "football", "strike zone", "pitching", "fastball"]),
    ("📡", "Media & Communication Studies", ["communication theory", "mass media", "journalism", "broadcasting", "publishing"]),
    ("📈", "Economics & Business", ["economics", "market", "inflation", "gdp", "supply", "demand", "monetary", "fiscal", "banking", "finance"]),
]

def detect_domain_meta(topic: str, articles: List[Dict[str, str]], context: str = "") -> Tuple[str, str]:
    """Detects clean category name and emoji icon based on weighted keyword matching against topic, context, and articles."""
    art_titles = " ".join(a.get("title", "") for a in articles)
    art_extracts = " ".join(a.get("extract", "") for a in articles)

    best_score = 0
    best_match = ("📚", "General Academic Discipline")

    for icon, name, patterns in DOMAIN_DEFINITIONS:
        score = 0
        for pat in patterns:
            rx = rf"\b{re.escape(pat)}s?\b"
            if re.search(rx, topic, re.IGNORECASE):
                score += 10
            if context and re.search(rx, context, re.IGNORECASE):
                score += 5
            if re.search(rx, art_titles, re.IGNORECASE):
                score += 3
            if re.search(rx, art_extracts, re.IGNORECASE):
                score += 1

        if score > best_score:
            best_score = score
            best_match = (icon, name)

    return best_match

def synthesize_authentic_curriculum(
    domain_id: str,
    topic_title: str,
    articles: List[Dict[str, str]] = None,
    num_questions: int = 12,
    dag_type: Optional[str] = None,
    seed_offset: int = 0
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
            try:
                from backend.app.universal_synthesizer import synthesize_universal_curriculum
            except ImportError:
                from Website.backend.app.universal_synthesizer import synthesize_universal_curriculum

    if articles is None:
        try:
            articles = fetch_wikipedia_knowledge(topic_title)
        except Exception:
            articles = []

    return synthesize_universal_curriculum(
        domain_id,
        topic_title,
        articles=articles,
        num_questions=num_questions,
        dag_type=dag_type,
        seed_offset=seed_offset
    )

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
        try:
            from backend.app.quiz_validator import balance_sentence as _balance_sentence
        except ImportError:
            from Website.backend.app.quiz_validator import balance_sentence as _balance_sentence
