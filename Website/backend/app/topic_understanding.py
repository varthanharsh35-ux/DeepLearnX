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
    "transformer": [
        {
            "id": "transformer_deep_learning",
            "title": "Transformer Architecture & Self-Attention (Deep Learning / NLP)",
            "discipline": "Computer Science & AI",
            "subdiscipline": "Deep Learning & NLP",
            "scope": "Multi-head self-attention, positional encoding, encoder-decoder transformers, BERT, GPT, and sequence transduction.",
            "keywords": ["attention", "nlp", "encoder", "decoder", "gpt", "bert", "tokens", "sequence"]
        },
        {
            "id": "transformer_electrical",
            "title": "Electrical Transformers & Electromagnetic Induction (Electrical Engineering / Physics)",
            "discipline": "Engineering & Technology",
            "subdiscipline": "Electrical Engineering",
            "scope": "Mutual induction, Faraday's law, primary and secondary coils, turns ratio, core losses, step-up/step-down transformers, and AC power transmission.",
            "keywords": ["electromagnetic", "induction", "voltage", "turns", "coils", "primary", "secondary", "power", "ac"]
        }
    ],
    "transformers": [
        {
            "id": "transformer_deep_learning",
            "title": "Transformer Architecture & Self-Attention (Deep Learning / NLP)",
            "discipline": "Computer Science & AI",
            "subdiscipline": "Deep Learning & NLP",
            "scope": "Multi-head self-attention, positional encoding, encoder-decoder transformers, BERT, GPT, and sequence transduction.",
            "keywords": ["attention", "nlp", "encoder", "decoder", "gpt", "bert", "tokens", "sequence"]
        },
        {
            "id": "transformer_electrical",
            "title": "Electrical Transformers & Electromagnetic Induction (Electrical Engineering / Physics)",
            "discipline": "Engineering & Technology",
            "subdiscipline": "Electrical Engineering",
            "scope": "Mutual induction, Faraday's law, primary and secondary coils, turns ratio, core losses, step-up/step-down transformers, and AC power transmission.",
            "keywords": ["electromagnetic", "induction", "voltage", "turns", "coils", "primary", "secondary", "power", "ac"]
        }
    ],
    "vector": [
        {
            "id": "vector_math",
            "title": "Vector Spaces & Linear Algebra (Mathematics)",
            "discipline": "Mathematics",
            "subdiscipline": "Linear Algebra",
            "scope": "Vector spaces, linear combinations, basis, dimension, dot product, cross product, and linear transformations."
        },
        {
            "id": "vector_phys",
            "title": "Vector Kinematics & Mechanics (Physics)",
            "discipline": "Physics",
            "subdiscipline": "Classical Mechanics",
            "scope": "Vector quantities, magnitude and direction, vector addition, resolution of forces, velocity, and acceleration."
        },
        {
            "id": "vector_bio",
            "title": "Cloning Vectors & Recombinant DNA (Molecular Biology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Molecular Genetics & Biotechnology",
            "scope": "Plasmids, bacteriophages, viral vectors, multiple cloning sites, selectable markers, and recombinant DNA technology."
        },
        {
            "id": "vector_epid",
            "title": "Disease Vectors & Transmission (Epidemiology)",
            "discipline": "Public Health & Epidemiology",
            "subdiscipline": "Infectious Disease & Parasitology",
            "scope": "Biological and mechanical vectors, arthropod transmission (mosquitoes, ticks), pathogen reservoirs, and vector control."
        }
    ],
    "vectors": [
        {
            "id": "vectors_math",
            "title": "Vector Spaces & Linear Algebra (Mathematics)",
            "discipline": "Mathematics",
            "subdiscipline": "Linear Algebra",
            "scope": "Vector spaces, linear combinations, basis, dimension, dot product, cross product, and linear transformations."
        },
        {
            "id": "vectors_phys",
            "title": "Vector Kinematics & Mechanics (Physics)",
            "discipline": "Physics",
            "subdiscipline": "Classical Mechanics",
            "scope": "Vector quantities, magnitude and direction, vector addition, resolution of forces, velocity, and acceleration."
        },
        {
            "id": "vectors_bio",
            "title": "Cloning Vectors & Recombinant DNA (Molecular Biology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Molecular Genetics & Biotechnology",
            "scope": "Plasmids, bacteriophages, viral vectors, multiple cloning sites, selectable markers, and recombinant DNA technology."
        },
        {
            "id": "vectors_epid",
            "title": "Disease Vectors & Transmission (Epidemiology)",
            "discipline": "Public Health & Epidemiology",
            "subdiscipline": "Infectious Disease & Parasitology",
            "scope": "Biological and mechanical vectors, arthropod transmission (mosquitoes, ticks), pathogen reservoirs, and vector control."
        }
    ],
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
    ],
    "python": [
        {
            "id": "python_cs",
            "title": "Python (High-Level Programming Language & Software Engineering)",
            "discipline": "Computer Science",
            "subdiscipline": "Software Engineering & Data Science",
            "scope": "Python syntax, dynamic typing, memory management, data structures, and standard libraries."
        },
        {
            "id": "python_bio",
            "title": "Python (Constricting Serpents & Herpetology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Zoology & Herpetology",
            "scope": "Pythonidae taxonomy, predatory constricting mechanics, metabolic adaptations, and ecological habitats."
        }
    ],
    "go": [
        {
            "id": "go_cs",
            "title": "Go / Golang (Systems Programming & Concurrency)",
            "discipline": "Computer Science",
            "subdiscipline": "Programming Language Theory",
            "scope": "Goroutines, channels, CSP concurrency, static compilation, and cloud systems software."
        },
        {
            "id": "go_game",
            "title": "Go (Ancient Abstract Strategy Board Game / Weiqi)",
            "discipline": "Games & Cultural History",
            "subdiscipline": "Combinatorial Game Theory",
            "scope": "Grid stone placement, liberties, territory capture, life-and-death tactical patterns, and endgame scoring."
        }
    ],
    "swift": [
        {
            "id": "swift_cs",
            "title": "Swift (Apple Platform Programming & Type Safety)",
            "discipline": "Computer Science",
            "subdiscipline": "Software Engineering",
            "scope": "Swift language protocol-oriented design, ARC memory management, optionals, and iOS/macOS architecture."
        },
        {
            "id": "swift_lit",
            "title": "Jonathan Swift (Satirical Literature & Gulliver's Travels)",
            "discipline": "Literature & Humanities",
            "subdiscipline": "18th-Century Anglo-Irish Literature",
            "scope": "Satirical prose, political allegories, irony, and Enlightenment social critique."
        },
        {
            "id": "swift_bio",
            "title": "Swift Birds (Apodidae & Aerodynamic Avian Biology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Ornithology",
            "scope": "Aerial adaptations of family Apodidae, sustained flight mechanics, nesting biology, and insectivorous foraging."
        }
    ],
    "charge": [
        {
            "id": "charge_phys",
            "title": "Electric Charge (Electromagnetism & Coulomb's Law)",
            "discipline": "Physics",
            "subdiscipline": "Classical Electromagnetism",
            "scope": "Coulombs, electrostatic force, charge quantization, electric fields, and Gauss's law."
        },
        {
            "id": "charge_law",
            "title": "Criminal Charge (Jurisprudence & Indictment)",
            "discipline": "Law & Jurisprudence",
            "subdiscipline": "Criminal Procedure",
            "scope": "Formal accusation, indictment standards, elements of criminal offenses, and due process rights."
        },
        {
            "id": "charge_fin",
            "title": "Financial Charge (Banking & Credit Transactions)",
            "discipline": "Economics & Finance",
            "subdiscipline": "Banking & Consumer Finance",
            "scope": "Transaction debits, interest rates, ledger entries, service fee structures, and credit accounting."
        }
    ],
    "field": [
        {
            "id": "field_math",
            "title": "Field (Abstract Algebra & Galois Theory)",
            "discipline": "Mathematics",
            "subdiscipline": "Abstract Algebra",
            "scope": "Algebraic structures with addition and multiplication, field extensions, Galois theory, and finite fields."
        },
        {
            "id": "field_phys",
            "title": "Field (Classical & Quantum Field Theory)",
            "discipline": "Physics",
            "subdiscipline": "Field Theory & Theoretical Physics",
            "scope": "Continuous physical quantities across space-time, gravitational/electromagnetic fields, and wave equations."
        },
        {
            "id": "field_agri",
            "title": "Agricultural Field (Agronomy & Crop Management)",
            "discipline": "Agricultural Sciences",
            "subdiscipline": "Agronomy & Soil Science",
            "scope": "Crop rotation, soil fertility management, drainage systems, and arable farmland cultivation."
        }
    ],
    "state": [
        {
            "id": "state_poli",
            "title": "Sovereign State (Political Philosophy & Governance)",
            "discipline": "Political Science",
            "subdiscipline": "International Relations & Governance",
            "scope": "Monopoly on legitimate force, sovereignty, constitutional apparatus, and Westphalian state systems."
        },
        {
            "id": "state_phys",
            "title": "States of Matter (Thermodynamics & Phase Transitions)",
            "discipline": "Physics & Chemistry",
            "subdiscipline": "Thermodynamics & Condensed Matter",
            "scope": "Solid, liquid, gas, and plasma phases, latent heat, phase equilibria, and intermolecular forces."
        },
        {
            "id": "state_cs",
            "title": "Program State (Automata & Computational Systems)",
            "discipline": "Computer Science",
            "subdiscipline": "Computation Theory & Software Architecture",
            "scope": "Deterministic finite automata, memory state representations, state machines, and stateless architectures."
        }
    ],
    "revolution": [
        {
            "id": "revolution_hist",
            "title": "Political Revolution (Sociology & Modern History)",
            "discipline": "History & Humanities",
            "subdiscipline": "Comparative Historical Revolutions",
            "scope": "Structural overthrow of political orders (French, American, Russian revolutions), regime transformation, and civil conflict."
        },
        {
            "id": "revolution_astro",
            "title": "Orbital Revolution (Celestial Mechanics & Orbital Physics)",
            "discipline": "Physics & Astronomy",
            "subdiscipline": "Classical Mechanics & Orbital Dynamics",
            "scope": "Keplerian orbital periods, gravitational central-force motion, circular/elliptical orbits, and sidereal periods."
        }
    ],
    "function": [
        {
            "id": "function_math",
            "title": "Mathematical Function (Calculus & Set Theory)",
            "discipline": "Mathematics",
            "subdiscipline": "Mathematical Analysis",
            "scope": "Mappings from domain to codomain, bijective relations, continuous transformations, and function composition."
        },
        {
            "id": "function_cs",
            "title": "Subroutine / Function (Computer Programming)",
            "discipline": "Computer Science",
            "subdiscipline": "Programming Language Paradigms",
            "scope": "Subroutines, pure functions, call stack frames, parameter passing semantics, and lambda calculus."
        },
        {
            "id": "function_bio",
            "title": "Physiological Function (Anatomy & Systemic Biology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Animal & Human Physiology",
            "scope": "Biological organ function, homeostasis maintenance, feedback loops, and physiological adaptations."
        }
    ],
    "mass": [
        {
            "id": "mass_phys",
            "title": "Mass (Newtonian & Relativistic Physics)",
            "discipline": "Physics",
            "subdiscipline": "Classical Mechanics & Relativity",
            "scope": "Inertial vs gravitational mass, kilograms, Newton's second law, relativistic mass-energy equivalence (E=mc²)."
        },
        {
            "id": "mass_relig",
            "title": "The Mass (Eucharistic Liturgy & Ecclesiastical History)",
            "discipline": "Religious Studies & History",
            "subdiscipline": "Christian Liturgical History",
            "scope": "Liturgy of the Eucharist, historical development of the Roman rite, sacramental theology, and choral traditions."
        }
    ],
    "culture": [
        {
            "id": "culture_soc",
            "title": "Culture (Anthropology & Social Sciences)",
            "discipline": "Sociology & Anthropology",
            "subdiscipline": "Cultural Anthropology",
            "scope": "Shared beliefs, norms, semiotics, material culture, linguistic transmission, and societal institutions."
        },
        {
            "id": "culture_bio",
            "title": "Microbiological Culture (Bacteriology & Cell Culture)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Microbiology & Biotechnology",
            "scope": "In vitro microbial propagation, nutrient agar inoculation, aseptic techniques, and colony morphology."
        }
    ]
}

# Cross-disciplinary homonyms and polysemous terms for generalized contextual interpretation
DYNAMIC_POLYSEMY_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
    "crane": [
        {
            "id": "crane_mech",
            "title": "Crane (Heavy Machinery & Construction Rigging)",
            "discipline": "Mechanical & Civil Engineering",
            "subdiscipline": "Construction Machinery",
            "scope": "Hoisting mechanisms, hydraulic booms, load moment indicators, tower cranes, and rigging safety.",
            "keywords": ["hoist", "pulley", "boom", "hydraulic", "rigging", "cable", "load", "construction", "machine", "steel", "tower"]
        },
        {
            "id": "crane_bio",
            "title": "Crane (Avian Biology & Gruidae Ecology)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Ornithology & Conservation Biology",
            "scope": "Gruidae taxonomy, wetland ecology, migratory flight aerodynamics, courtship displays, and habitat conservation.",
            "keywords": ["bird", "gruidae", "feather", "wetland", "migratory", "migration", "whooping", "sandhill", "avian", "nesting", "flock"]
        }
    ],
    "strike": [
        {
            "id": "strike_econ",
            "title": "Labor Strike (Industrial Relations & Collective Bargaining)",
            "discipline": "Economics & Social Sciences",
            "subdiscipline": "Labor Economics",
            "scope": "Work stoppages, union collective bargaining, statutory labor rights, and economic impact of strikes.",
            "keywords": ["labor", "union", "worker", "bargaining", "wage", "walkout", "employment", "industry", "picket"]
        },
        {
            "id": "strike_geol",
            "title": "Strike and Dip (Structural Geology & Fault Analysis)",
            "discipline": "Geological Sciences",
            "subdiscipline": "Structural Geology",
            "scope": "Compass direction of horizontal rock stratum lines, dip angles, fault planes, and tectonic deformation.",
            "keywords": ["geology", "dip", "strata", "fault", "rock", "tectonic", "plane", "horizontal", "bedding", "stratum"]
        }
    ],
    "spring": [
        {
            "id": "spring_phys",
            "title": "Mechanical Spring (Elasticity & Hooke's Law)",
            "discipline": "Physics & Engineering",
            "subdiscipline": "Classical Mechanics",
            "scope": "Restoring forces, Hooke's law, spring constant k, elastic potential energy, and simple harmonic motion.",
            "keywords": ["hooke", "elastic", "restoring", "force", "constant", "oscillation", "harmonic", "stiffness", "coil"]
        },
        {
            "id": "spring_hydro",
            "title": "Natural Spring (Hydrogeology & Geothermal Systems)",
            "discipline": "Earth & Environmental Sciences",
            "subdiscipline": "Hydrogeology",
            "scope": "Groundwater aquifer discharge, water table hydrostatic pressure, mineral karst springs, and geothermal emergence.",
            "keywords": ["water", "aquifer", "hydrogeology", "groundwater", "geothermal", "karst", "artesian", "discharge", "thermal"]
        }
    ],
    "matrix": [
        {
            "id": "matrix_math",
            "title": "Matrix Algebra (Linear Transformations & Determinants)",
            "discipline": "Mathematics",
            "subdiscipline": "Linear Algebra",
            "scope": "Rectangular arrays of numbers, matrix multiplication, determinants, rank, eigenvalues, and eigenvectors.",
            "keywords": ["linear", "algebra", "vector", "multiplication", "determinant", "eigenvalue", "transformation", "rank", "array"]
        },
        {
            "id": "matrix_bio",
            "title": "Extracellular Matrix (Cytology & Tissue Architecture)",
            "discipline": "Biological Sciences",
            "subdiscipline": "Cell Biology & Histology",
            "scope": "Macromolecular network of collagen, proteoglycans, integrins, and cell scaffold communication.",
            "keywords": ["cell", "extracellular", "collagen", "tissue", "integrin", "protein", "histology", "scaffold"]
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


def check_topic_ambiguity(
    topic_normalized: str,
    context: str = "",
    academic_level: str = ""
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]:
    """
    Checks if topic has multiple distinct academic meanings using contextual interpretation
    based on entire topic text, syllabus notes, academic level, and discipline terminology.
    Returns (ambiguity_candidates, resolved_candidate).
    - If unambiguous: returns (None, None).
    - If polysemous but context clearly identifies exactly one meaning: returns (candidates, resolved_candidate).
    - If polysemous and unresolved: returns (candidates, None).
    """
    low = topic_normalized.lower().strip()
    combined = f"{low} {context.lower()} {academic_level.lower()}".strip()
    ctx_words = set(re.findall(r"\b[a-z]{3,}\b", combined))

    # Merge catalogs (catalog takes priority, supplemented by dynamic polysemy patterns)
    merged_catalog: Dict[str, List[Dict[str, Any]]] = {}
    merged_catalog.update(DYNAMIC_POLYSEMY_PATTERNS)
    merged_catalog.update(AMBIGUITY_CATALOG)

    for ambig_key, candidates in merged_catalog.items():
        if re.search(rf"\b{re.escape(ambig_key)}\b", low):
            # Check if user already provided disambiguating keywords in title, context, or notes
            candidate_scores = []
            for cand in candidates:
                cand_text = f"{cand.get('title', '')} {cand.get('discipline', '')} {cand.get('subdiscipline', '')} {cand.get('scope', '')}".lower()
                cand_words = set(re.findall(r"\b[a-z]{3,}\b", cand_text)) - {ambig_key.lower()}
                extra_kw = set(cand.get("keywords", []))
                cand_words.update(extra_kw)

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
                if candidate_scores[0][0] > candidate_scores[1][0] and candidate_scores[0][0] >= 2:
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
        selected_disambiguation: Optional[str] = None,
        academic_level: str = "Introductory"
    ) -> TopicInterpretation:
        """
        Interprets student topic, detecting ambiguities, grounding with evidence,
        and extracting academic objectives and prerequisites.
        """
        clean_topic = normalize_input_topic(topic)
        if not clean_topic:
            clean_topic = "General Academic Studies"

        try:
            from topic_cache import get_topic_cache
        except ImportError:
            try:
                from app.topic_cache import get_topic_cache
            except ImportError:
                from backend.app.topic_cache import get_topic_cache
        _cache = get_topic_cache()
        if not selected_disambiguation and not force_offline:
            _cached = _cache.get_interpretation(clean_topic, syllabus_text)
            if _cached and isinstance(_cached, dict):
                return TopicInterpretation(**_cached)

        # Check for invalid or meaningless input (purely numeric/symbolic, e.g. "5 5 5")
        has_alpha_words = bool(re.search(r'[a-zA-Z]{2,}', clean_topic))
        if not has_alpha_words:
            return TopicInterpretation(
                original_query=topic,
                canonical_title=clean_topic,
                discipline="Invalid Academic Topic",
                subdiscipline="Clarification Required",
                scope=f"'{clean_topic}' does not contain recognizable academic subject terminology. Please enter a valid academic topic.",
                is_ambiguous=True,
                ambiguities=[
                    {"id": "clarify_academic_topic", "title": "Please provide a descriptive academic topic (e.g., Mathematics, Photosynthesis, Computer Science)", "discipline": "Clarification Required", "subdiscipline": "Input Validation", "scope": "Valid academic curriculum requires recognizable disciplinary keywords."}
                ],
                confidence=0.0
            )

        # Check for non-academic gibberish / keyboard smashes (e.g. "asdfghjklqwerty")
        def _check_gibberish(txt: str) -> bool:
            c = re.sub(r'[^a-zA-Z]', '', txt).lower()
            if len(c) >= 6:
                # Consonants strictly excluding y
                consonants_no_y = r'[bcdfghjklmnpqrstvwxz]'
                # Known valid English words with 5+ consonants
                valid_exceptions = {"strength", "strengths", "length", "lengths", "twelfth", "twelfths", "catchphrase", "rhythm", "rhythms", "syzygy"}
                if re.search(consonants_no_y + r'{6,}', c) and not any(v in c for v in valid_exceptions):
                    return True
                vowels = len(re.findall(r'[aeiouy]', c))
                # Very low vowel ratio for a long string
                if (vowels == 0 or (vowels / len(c) < 0.15)) and len(c) >= 7:
                    return True
                # Home-row or top-row keyboard smash
                smash_patterns = ["asdf", "dfgh", "ghjk", "jklq", "qwerty", "zxcv", "xcvb", "cvbn"]
                if any(p in c for p in smash_patterns) and len(c) >= 8:
                    return True
            return False

        if _check_gibberish(clean_topic):
            return TopicInterpretation(
                original_query=topic,
                canonical_title=clean_topic,
                discipline="Invalid Academic Topic",
                subdiscipline="Gibberish Input Rejected",
                scope=f"'{clean_topic}' is not a recognized academic topic. Please enter a valid academic subject.",
                is_ambiguous=True,
                ambiguities=[
                    {"id": "clarify_invalid_gibberish", "title": "Please enter a valid, recognizable academic topic (e.g., Organic Chemistry, Game Design, Operating Systems)", "discipline": "Clarification Required", "subdiscipline": "Input Validation", "scope": "DeepLearnX requires a valid disciplinary subject to construct a curriculum."}
                ],
                confidence=0.0
            )

        # Check for overly broad umbrella disciplines (e.g. "Science", "Engineering")
        broad_low = clean_topic.strip().lower()
        if broad_low in {"science", "sciences", "natural science"}:
            return TopicInterpretation(
                original_query=topic,
                canonical_title="Science (Broad Umbrella Field)",
                discipline="Natural Sciences",
                subdiscipline="Broad Category Clarification",
                scope="'Science' is an umbrella category. Please select a specific scientific branch to assess:",
                is_ambiguous=True,
                ambiguities=[
                    {"id": "science_physics", "title": "Physics (Mechanics, Electromagnetism & Thermodynamics)", "discipline": "Physical Sciences", "subdiscipline": "Physics", "scope": "Classical mechanics, electromagnetism, optics, and thermodynamics."},
                    {"id": "science_chem", "title": "Chemistry (Organic, Inorganic & Physical Chemistry)", "discipline": "Chemical Sciences", "subdiscipline": "Chemistry", "scope": "Chemical bonding, stoichiometry, reaction mechanisms, and thermodynamics."},
                    {"id": "science_bio", "title": "Biology (Cellular Biology, Genetics & Ecology)", "discipline": "Biological Sciences", "subdiscipline": "Biology", "scope": "Cell structure, metabolic pathways, heredity, and ecological food webs."}
                ],
                confidence=0.6
            )
        elif broad_low in {"engineering", "applied science"}:
            return TopicInterpretation(
                original_query=topic,
                canonical_title="Engineering (Broad Umbrella Field)",
                discipline="Engineering & Technology",
                subdiscipline="Broad Category Clarification",
                scope="'Engineering' is an umbrella category. Please select a specific engineering discipline to assess:",
                is_ambiguous=True,
                ambiguities=[
                    {"id": "eng_cs", "title": "Computer Engineering & Systems", "discipline": "Engineering", "subdiscipline": "Computer Engineering", "scope": "Computer architecture, operating systems, digital circuits, and embedded software."},
                    {"id": "eng_mech", "title": "Mechanical Engineering & Fluid Mechanics", "discipline": "Engineering", "subdiscipline": "Mechanical Engineering", "scope": "Statics, dynamics, thermodynamics, fluid mechanics, and machine design."},
                    {"id": "eng_ee", "title": "Electrical & Electronics Engineering", "discipline": "Engineering", "subdiscipline": "Electrical Engineering", "scope": "Circuit analysis, electromagnetic fields, semiconductor devices, and signals."}
                ],
                confidence=0.6
            )

        # 1. Check for polysemous ambiguity unless already resolved by selected_disambiguation
        ambig_candidates, resolved_cand = check_topic_ambiguity(clean_topic, syllabus_text, academic_level)
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

        # 1b. Dynamic LLM Polysemy check for unknown terms when live provider is active
        # Only evaluate bare, unqualified terms (e.g. "Bank", "Terminal", "Pitch", <= 2 words without prepositional phrases)
        is_bare_query = len(clean_topic.split()) <= 2 and not any(kw in clean_topic.lower() for kw in [" in ", " of ", " for ", " and ", ":", "-", "/"])
        active_provider = self.provider_manager.get_active_provider()
        if is_bare_query and not ambig_candidates and not selected_disambiguation and not (syllabus_text and len(syllabus_text) > 20) and active_provider and not force_offline:
            try:
                polysemy_sys = (
                    "You are a linguistic polysemy and academic curriculum analyzer. "
                    "Determine whether the input term has multiple fundamentally different academic meanings across different disciplines "
                    "(e.g., Computer Science vs Biology vs Physics vs History). "
                    "Return JSON with keys: is_ambiguous (bool), ambiguities (list of objects with id, title, discipline, subdiscipline, scope)."
                )
                polysemy_prompt = f"Analyze the topic '{clean_topic}' for cross-disciplinary polysemy."
                p_res = active_provider.generate_structured(schema={}, prompt=polysemy_prompt, system_instruction=polysemy_sys)
                p_data = p_res.content
                if isinstance(p_data, dict) and p_data.get("is_ambiguous") and isinstance(p_data.get("ambiguities"), list) and len(p_data["ambiguities"]) >= 2:
                    return TopicInterpretation(
                        original_query=topic,
                        canonical_title=clean_topic.title(),
                        discipline="Ambiguous Topic",
                        subdiscipline="Multiple Meanings Detected",
                        scope=f"'{clean_topic}' has multiple distinct academic interpretations. Please select the intended scope.",
                        is_ambiguous=True,
                        ambiguities=p_data["ambiguities"],
                        confidence=0.5,
                        generation_mode="live_llm"
                    )
            except Exception as pe:
                logger.debug(f"Dynamic LLM polysemy check skipped/failed: {pe}")

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
        icon, category = detect_domain_meta(clean_topic, evidence_articles, context=f"{syllabus_text} {topic}")

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
                    chosen_disc = selected_cand["discipline"] if selected_cand else data.get("discipline", category)
                    chosen_subdisc = selected_cand["subdiscipline"] if selected_cand else data.get("subdiscipline", category)
                    _llm_interp = TopicInterpretation(
                        original_query=topic,
                        canonical_title=data.get("canonical_title", clean_topic.title()),
                        discipline=chosen_disc,
                        subdiscipline=chosen_subdisc,
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
                    try:
                        _cache.set_interpretation(clean_topic, syllabus_text, _llm_interp.to_dict())
                    except Exception:
                        pass
                    return _llm_interp
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

        _off_interp = TopicInterpretation(
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
        try:
            _cache.set_interpretation(clean_topic, syllabus_text, _off_interp.to_dict())
        except Exception:
            pass
        return _off_interp
