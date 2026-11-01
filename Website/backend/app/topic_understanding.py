"""
DeepLearnX Universal Topic Understanding & Ambiguity Engine.

Responsible for:
- Input normalization and intent preservation.
- Canonical title, academic discipline, subdiscipline, and learning scope interpretation.
- Active ambiguity detection and structured clarification alternatives.
- Multi-source factual evidence grounding.
- Seamless bridge between live LLM providers and authentic offline synthesis.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

try:
    from .topic_researcher import fetch_wikipedia_knowledge, detect_domain_meta
    from .providers.manager import get_provider_manager
except (ImportError, ValueError):
    try:
        from topic_researcher import fetch_wikipedia_knowledge, detect_domain_meta
        from providers.manager import get_provider_manager
    except ImportError:
        try:
            from app.topic_researcher import fetch_wikipedia_knowledge, detect_domain_meta
            from app.providers.manager import get_provider_manager
        except ImportError:
            try:
                from backend.app.topic_researcher import fetch_wikipedia_knowledge, detect_domain_meta
                from backend.app.providers.manager import get_provider_manager
            except ImportError:
                from Website.backend.app.topic_researcher import fetch_wikipedia_knowledge, detect_domain_meta
                from Website.backend.app.providers.manager import get_provider_manager

logger = logging.getLogger("deeplearnx.topic_understanding")

# Polysemous topics requiring clarification unless disambiguated by context or notes
AMBIGUITY_CATALOG = {
    "java": [
        {
            "id": "java_cs",
            "title": "Java (Programming Language & Object-Oriented Software)",
            "discipline": "Computer Science",
            "subdiscipline": "Software Engineering & Languages",
            "scope": "Java language syntax, JVM architecture, OOP principles, and standard class libraries."
        },
        {
            "id": "java_geo",
            "title": "Java (Island Geography & Indonesian History)",
            "discipline": "Geography & History",
            "subdiscipline": "Southeast Asian Studies",
            "scope": "Physical geography of Java island, volcanic landscape, population centers, and cultural history."
        },
        {
            "id": "java_coffee",
            "title": "Java Coffee (Agricultural Cultivation & Trade)",
            "discipline": "Agricultural Sciences",
            "subdiscipline": "Agronomy & Food Systems",
            "scope": "Coffea arabica cultivation, processing methods, harvest cycles, and historical coffee trade."
        }
    ],
    "mercury": [
        {
            "id": "mercury_astro",
            "title": "Mercury (Terrestrial Planet & Solar System)",
            "discipline": "Astronomy & Astrophysics",
            "subdiscipline": "Planetary Science",
            "scope": "Orbital dynamics, surface geology, extreme temperature variations, and magnetic field of planet Mercury."
        },
        {
            "id": "mercury_chem",
            "title": "Mercury (Transition Metal & Chemical Properties)",
            "discipline": "Chemistry",
            "subdiscipline": "Inorganic Chemistry",
            "scope": "Atomic structure of Hg, liquid metal properties, amalgam formation, and toxicity."
        },
        {
            "id": "mercury_myth",
            "title": "Mercury (Roman Deity & Classical Mythology)",
            "discipline": "Classical Studies & Mythology",
            "subdiscipline": "Ancient Roman Religion",
            "scope": "Attributes of god Mercury, psychopomp role, Roman pantheon relations, and iconography."
        }
    ],
    "apple": [
        {
            "id": "apple_hort",
            "title": "Apple (Malus domestica & Pomological Science)",
            "discipline": "Agricultural Sciences",
            "subdiscipline": "Horticulture & Pomology",
            "scope": "Botanical structure of pome fruits, orchard grafting, cultivar genetics, and harvest storage."
        },
        {
            "id": "apple_tech",
            "title": "Apple Inc. (Corporate History & Personal Computing)",
            "discipline": "Business & Technology Studies",
            "subdiscipline": "Computing History",
            "scope": "Evolution of Apple personal computers, GUI operating systems, hardware design, and consumer ecosystem."
        }
    ],
    "vector": [
        {
            "id": "vector_math",
            "title": "Vector (Euclidean Vector & Linear Algebra)",
            "discipline": "Mathematics",
            "subdiscipline": "Linear Algebra & Geometry",
            "scope": "Magnitude and direction, vector spaces, dot products, cross products, and linear combinations."
        },
        {
            "id": "vector_bio",
            "title": "Disease Vector (Epidemiology & Parasitology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Epidemiology & Vector Biology",
            "scope": "Biological vectors (mosquitoes, ticks), pathogen transmission mechanisms, and vector control."
        },
        {
            "id": "vector_cs",
            "title": "Dynamic Array Vector (Computer Science Data Structures)",
            "discipline": "Computer Science",
            "subdiscipline": "Data Structures & Algorithms",
            "scope": "Contiguous memory arrays, geometric reallocation, amortized complexity, and iterator invalidation."
        }
    ],
    "french leaders": [
        {
            "id": "french_leaders_rev",
            "title": "Leaders of the French Revolution (1789–1799)",
            "discipline": "History & Humanities",
            "subdiscipline": "Modern European History",
            "scope": "Key figures of the French Revolution (Robespierre, Danton, Marat, Sieyès), factional politics, and Reign of Terror."
        },
        {
            "id": "french_leaders_modern",
            "title": "Presidents of the French Fifth Republic (1958–Present)",
            "discipline": "Political Science",
            "subdiscipline": "Comparative Government",
            "scope": "Semi-presidential executive powers under the 1958 constitution, from de Gaulle to contemporary presidents."
        }
    ],
    "rust": [
        {
            "id": "rust_chem",
            "title": "Rust (Iron Oxide Corrosion & Metallurgy)",
            "discipline": "Chemistry & Materials Science",
            "subdiscipline": "Corrosion Chemistry",
            "scope": "Electrochemical oxidation of iron, hydration reactions, galvanic corrosion, and anti-corrosion coatings."
        },
        {
            "id": "rust_cs",
            "title": "Rust (Systems Programming Language)",
            "discipline": "Computer Science",
            "subdiscipline": "Programming Language Theory",
            "scope": "Affine type system, ownership and borrowing, compile-time memory safety, and concurrency."
        },
        {
            "id": "rust_plant",
            "title": "Rust Fungi (Pucciniales & Plant Pathology)",
            "discipline": "Agricultural Biology",
            "subdiscipline": "Plant Pathology & Mycology",
            "scope": "Obligate biotrophic fungi, life cycles on host crops (cereal rust), and agricultural mitigation."
        }
    ],
    "cell": [
        {
            "id": "cell_bio",
            "title": "Biological Cell (Cytology & Cell Biology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Cell Biology",
            "scope": "Membrane structure, organelles, protein synthesis, mitosis, and metabolic pathways."
        },
        {
            "id": "cell_electro",
            "title": "Electrochemical Cell (Batteries & Galvanic Systems)",
            "discipline": "Chemistry & Physics",
            "subdiscipline": "Electrochemistry",
            "scope": "Anode and cathode redox reactions, standard reduction potentials, electrolytes, and battery discharge."
        }
    ],
    "virus": [
        {
            "id": "virus_bio",
            "title": "Biological Virus (Microbiology & Virology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Virology",
            "scope": "Viral capsid structure, genetic material (DNA/RNA), replication cycles, and host cell entry."
        },
        {
            "id": "virus_cs",
            "title": "Computer Virus (Malware & Cybersecurity)",
            "discipline": "Computer Science",
            "subdiscipline": "Cybersecurity",
            "scope": "Self-replicating malicious code, infection vectors, executable payload execution, and signature detection."
        }
    ]
}


@dataclass
class TopicInterpretation:
    """Normalized structured understanding of a student-submitted topic."""
    original_query: str
    canonical_title: str
    discipline: str
    subdiscipline: str
    scope: str
    academic_level: str = "Introductory"
    learning_objectives: List[str] = field(default_factory=list)
    prerequisite_areas: List[str] = field(default_factory=list)
    core_areas: List[str] = field(default_factory=list)
    important_terms: List[str] = field(default_factory=list)
    ambiguities: List[Dict[str, Any]] = field(default_factory=list)
    is_ambiguous: bool = False
    exclusions: List[str] = field(default_factory=list)
    confidence: float = 0.95
    evidence_sources: List[Dict[str, Any]] = field(default_factory=list)
    icon: str = "📚"
    category: str = "General Academic Subject"
    generation_mode: str = "offline_knowledge_synthesis"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_input_topic(topic: str) -> str:
    """Safely normalizes topic title without corrupting technical meaning or creating double suffixes."""
    if not topic:
        return ""
    t = topic.strip()
    # Strip common filler prefixes
    t = re.sub(r'^(types of|introduction to|fundamentals of|basics of|principles of)\s+', '', t, flags=re.IGNORECASE)
    # Normalize punctuation and quotes
    t = re.sub(r'[\'\"’]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def check_topic_ambiguity(topic_normalized: str, context: str = "") -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]:
    """
    Checks if topic has multiple distinct academic meanings.
    Returns (ambiguity_candidates, resolved_candidate).
    - If not in catalog: returns (None, None).
    - If in catalog but context clearly identifies exactly one meaning: returns (candidates, resolved_candidate).
    - If in catalog and unresolved: returns (candidates, None).
    """
    low = topic_normalized.lower().strip()
    combined = f"{low} {context.lower()}".strip()
    ctx_words = set(re.findall(r"\b[a-z]{3,}\b", combined))

    for ambig_key, candidates in AMBIGUITY_CATALOG.items():
        if re.search(rf"\b{re.escape(ambig_key)}\b", low):
            # Check if user already provided disambiguating keywords in title or context
            candidate_scores = []
            for cand in candidates:
                cand_text = f"{cand.get('title', '')} {cand.get('discipline', '')} {cand.get('subdiscipline', '')} {cand.get('scope', '')}".lower()
                cand_words = set(re.findall(r"\b[a-z]{3,}\b", cand_text)) - {ambig_key.lower()}
                overlap = cand_words & ctx_words
                if overlap:
                    candidate_scores.append((len(overlap), cand))

            if len(candidate_scores) == 1:
                # Exactly one candidate matched distinct context keywords -> resolved!
                return candidates, candidate_scores[0][1]
            elif len(candidate_scores) > 1:
                candidate_scores.sort(key=lambda x: x[0], reverse=True)
                if candidate_scores[0][0] >= 2 and candidate_scores[0][0] > candidate_scores[1][0]:
                    return candidates, candidate_scores[0][1]
                return candidates, None
            else:
                return candidates, None

    return None, None


class TopicUnderstandingEngine:
    """Universal academic topic interpreter."""

    def __init__(self):
        self.provider_manager = get_provider_manager()

    def interpret(
        self,
        topic: str,
        syllabus_text: str = "",
        force_offline: bool = False,
        selected_disambiguation: Optional[str] = None
    ) -> TopicInterpretation:
        """
        Interprets student topic, detecting ambiguities, grounding with evidence,
        and extracting academic objectives and prerequisites.
        """
        clean_topic = normalize_input_topic(topic)
        if not clean_topic:
            clean_topic = "General Academic Studies"

        # 1. Check for polysemous ambiguity unless already resolved by selected_disambiguation
        ambig_candidates, resolved_cand = check_topic_ambiguity(clean_topic, syllabus_text)
        if ambig_candidates and not selected_disambiguation and not resolved_cand:
            return TopicInterpretation(
                original_query=topic,
                canonical_title=clean_topic.title(),
                discipline="Ambiguous Topic",
                subdiscipline="Multiple Meanings Detected",
                scope=f"'{clean_topic}' has multiple distinct academic interpretations. Please select the intended scope.",
                is_ambiguous=True,
                ambiguities=ambig_candidates,
                confidence=0.5
            )

        # If a specific disambiguation was chosen from the ambiguity modal or resolved by context
        selected_cand = resolved_cand
        if selected_disambiguation and ambig_candidates:
            for c in ambig_candidates:
                if c.get("id") == selected_disambiguation:
                    selected_cand = c
                    clean_topic = c["title"].split("(")[0].strip()
                    break
        elif selected_cand:
            clean_topic = selected_cand["title"].split("(")[0].strip()

        # 2. Retrieve encyclopedic evidence
        evidence_articles = []
        try:
            evidence_articles = fetch_wikipedia_knowledge(clean_topic)
        except Exception as e:
            logger.warning(f"Evidence retrieval failed: {e}")

        # 3. Detect domain metadata & icon
        icon, category = detect_domain_meta(clean_topic, evidence_articles)

        # 4. Attempt live LLM structured interpretation if provider ready
        active_provider = self.provider_manager.get_active_provider()
        if active_provider and not force_offline:
            try:
                system_instruction = (
                    "You are the DeepLearnX Universal Academic Topic Interpreter. "
                    "Analyze the submitted topic, establish a rigorous yet accessible introductory learning scope, "
                    "identify primary learning objectives and prerequisite concepts, and return strictly valid JSON."
                )
                prompt = (
                    f"Topic: {clean_topic}\n"
                    f"Syllabus / Context: {syllabus_text}\n"
                    f"Evidence Summary: {' '.join(a.get('extract', '')[:200] for a in evidence_articles[:2])}\n"
                    f"Produce a structured JSON topic analysis with keys: "
                    f"canonical_title, discipline, subdiscipline, scope, academic_level, "
                    f"learning_objectives (list of 3-4), prerequisite_areas (list of 2-3), "
                    f"core_areas (list of 3-4), important_terms (list of 4-6), exclusions (list of 2-3)."
                )
                res = active_provider.generate_structured(schema={}, prompt=prompt, system_instruction=system_instruction)
                data = res.content
                if isinstance(data, dict) and "discipline" in data:
                    return TopicInterpretation(
                        original_query=topic,
                        canonical_title=data.get("canonical_title", clean_topic.title()),
                        discipline=data.get("discipline", category),
                        subdiscipline=data.get("subdiscipline", category),
                        scope=data.get("scope", f"Introductory academic study of {clean_topic}."),
                        academic_level=data.get("academic_level", "Introductory"),
                        learning_objectives=data.get("learning_objectives", [
                            f"Understand foundational principles of {clean_topic}.",
                            f"Analyze key mechanisms and structures in {clean_topic}.",
                            f"Apply core principles to solve introductory problems."
                        ]),
                        prerequisite_areas=data.get("prerequisite_areas", ["Basic scientific/academic literacy"]),
                        core_areas=data.get("core_areas", [f"{clean_topic} Fundamentals", f"{clean_topic} Applications"]),
                        important_terms=data.get("important_terms", []),
                        exclusions=data.get("exclusions", []),
                        confidence=0.98,
                        evidence_sources=evidence_articles,
                        icon=icon,
                        category=category,
                        generation_mode="live_llm"
                    )
            except Exception as e:
                logger.warning(f"Live LLM topic interpretation failed ({e}); falling back to offline interpretation.")

        # 5. Authentic Offline Interpretation Fallback
        discipline = selected_cand["discipline"] if selected_cand else category
        subdiscipline = selected_cand["subdiscipline"] if selected_cand else category
        scope = selected_cand["scope"] if selected_cand else (
            f"Introductory academic study of {clean_topic}: foundational definitions, operational mechanisms, core constraints, and introductory applications."
        )

        learning_objectives = [
            f"Identify and define the core concepts and terminology of {clean_topic}.",
            f"Explain the primary mechanisms, structures, and theoretical principles of {clean_topic}.",
            f"Distinguish between valid principles and common misconceptions in {clean_topic}.",
            f"Apply foundational principles to solve realistic introductory problems."
        ]

        prerequisite_areas = [
            f"Basic foundational knowledge of {discipline.split('&')[0].strip()}",
            "Introductory scientific or qualitative reasoning capabilities"
        ]

        core_areas = [
            f"{clean_topic} Foundational Terminology & Definitions",
            f"{clean_topic} Primary Mechanisms & Core Laws",
            f"{clean_topic} Structural Relationships & Interactions",
            f"{clean_topic} Practical Applications & Problem Solving"
        ]

        # Extract terms from encyclopedic extracts
        terms = []
        for art in evidence_articles:
            words = re.findall(r'\b[A-Z][a-z]{3,}\b', art.get("extract", ""))
            for w in words:
                if w.lower() not in [clean_topic.lower(), "wikipedia", "english"] and w not in terms:
                    terms.append(w)
                if len(terms) >= 6:
                    break

        return TopicInterpretation(
            original_query=topic,
            canonical_title=clean_topic.title(),
            discipline=discipline,
            subdiscipline=subdiscipline,
            scope=scope,
            academic_level="Introductory",
            learning_objectives=learning_objectives,
            prerequisite_areas=prerequisite_areas,
            core_areas=core_areas,
            important_terms=terms,
            confidence=0.92,
            evidence_sources=evidence_articles,
            icon=icon,
            category=category,
            generation_mode="offline_knowledge_synthesis"
        )
