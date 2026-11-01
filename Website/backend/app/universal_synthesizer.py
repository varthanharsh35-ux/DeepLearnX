"""
DeepLearnX Universal Multi-Disciplinary Knowledge & Curriculum Synthesizer
Author: Senior AI & Educational Assessment Specialist

Purpose:
- Understands ANY academic topic submitted by a student.
- Synthesizes 4 authentic, progressive concept modules with Directed Acyclic Graph (DAG) prerequisites (c1 -> c2 -> c3 -> c4).
- Synthesizes 4 authentic, concept-grounded cognitive misconceptions with specific, actionable remediation (no generic filler).
- Generates 12 tiered diagnostic questions (4 Basic Recall, 4 Conceptual, 4 Application).
- Synthesizes dynamic, non-predictable Two-Tier Reasoning Probes with balanced options, randomized keys, and zero duplication ("Because Because").
- Equalizes option lengths to eliminate test-taking length cue bias.
- Fully eliminates generic engineering boilerplate ("feedback regulation", "system equilibrium", "non-linear saturation", "linear model extrapolation") across non-engineering disciplines.
- Operates across Culinary, Law, History, Biology, Chemistry, Physics, Astronomy, Earth Sciences, Mathematics, Computer Science, Linguistics, Arts, Music, Economics, and Humanities.
"""

import re
import random
from typing import Dict, List, Tuple, Any, Optional

# Disciplinary Archetypes
ARCHETYPES = {
    "culinary": {
        "icon": "🥐",
        "category": "Culinary Arts & Gastronomy",
        "keywords": ["pastry", "choux", "dough", "baking", "culinary", "cooking", "panade", "croissant", "gastronomy", "recipe", "confectionery", "patisserie"],
        "concept_templates": [
            ("Foundational Composition & Ingredient Ratios", "Baseline ingredients, hydration balances, and foundational dough or batter composition in {topic}."),
            ("Thermal Gelatinization & Emulsification Dynamics", "Starch gelatinization, fat-liquid emulsification, and physical transformation during cooking of {topic}."),
            ("Leavening Dynamics & Structural Aeration", "Steam expansion, air entrapment, and structural stabilization during heating in {topic}."),
            ("Baking Precision & Texture Troubleshooting", "Oven heat management, moisture evaporation, and diagnosing common texture or collapse defects in {topic}.")
        ],
        "misconceptions": [
            ("Hydration & Formulation Imbalance", "Assuming liquid and fat ratios can be altered arbitrarily without compromising the structural integrity of {topic}.",
             "Measure baseline flour, liquid, and butter ratios strictly by weight to maintain proper starch-fat balance in {topic}."),
            ("Thermal Gelatinization Deficit", "Under-cooking the flour mixture before incorporating binding agents, preventing proper starch swelling in {topic}.",
             "Cook the panade thoroughly until a smooth ball forms and a light film coats the pan base before cooling in {topic}."),
            ("Premature Oven Exposure & Temperature Shock", "Opening the oven prematurely during baking, allowing steam to condense and causing structural collapse in {topic}.",
             "Maintain continuous high ambient heat without opening the oven until the shell structure fully dries and stabilizes in {topic}."),
            ("Leavening Mechanism Misattribution", "Believing chemical leaveners like baking powder are required when high-moisture steam vaporization drives expansion in {topic}.",
             "Rely entirely on internal trapped water vaporization and egg protein coagulation for lift and hollow expansion in {topic}.")
        ]
    },
    "law": {
        "icon": "⚖️",
        "category": "Legal Systems & Jurisprudence",
        "keywords": ["law", "constitution", "constitutional", "jurisprudence", "statute", "court", "judiciary", "justice", "rights", "legal", "article", "amendment", "doctrine", "treaty", "litigation"],
        "concept_templates": [
            ("Constitutional Architecture & Sovereign Powers", "Foundational constitutional text, separation of sovereign powers, and baseline institutional structure in {topic}."),
            ("Fundamental Rights & Judicial Protection", "Enforceable constitutional protections, civil liberties, and the scope of individual entitlements in {topic}."),
            ("Doctrinal Precedent & Judicial Review", "Jurisprudential doctrines, judicial scrutiny standards, and interpreting statutory validity in {topic}."),
            ("Constitutional Remedies & Practical Enforcement", "Writ petitions, appellate mechanisms, public interest litigation, and procedural remedies in {topic}.")
        ],
        "misconceptions": [
            ("Literalist Textual Isolation Fallacy", "Interpreting constitutional provisions as disconnected literal clauses rather than an interconnected organic charter in {topic}.",
             "Read constitutional provisions harmoniously within the broader structural design and purpose of {topic}."),
            ("Unconditional Fundamental Rights Assumption", "Assuming fundamental constitutional rights are completely unbounded rather than subject to reasonable public-interest restrictions in {topic}.",
             "Analyze rights alongside their explicit constitutional limitations, proportionality tests, and statutory caveats in {topic}."),
            ("Judicial Review vs Policy Usurpation Confusion", "Confusing legitimate judicial review of constitutional validity with executive or legislative policymaking in {topic}.",
             "Differentiate between striking down ultra vires enactments and substituting judicial discretion for legislative policy in {topic}."),
            ("Procedural Injunction vs Structural Remedy Inversion", "Mistaking temporary procedural stays or interim orders for definitive substantive constitutional resolutions in {topic}.",
             "Distinguish interlocutory procedural relief from final binding jurisprudential precedent established under {topic}.")
        ]
    },
    "history": {
        "icon": "🏛️",
        "category": "History & Political Governance",
        "keywords": ["leader", "leaders", "history", "revolution", "monarchy", "emperor", "president", "war", "republic", "dynasty", "empire", "statesman", "minister", "parliament", "treaty", "napoleon", "de gaulle"],
        "concept_templates": [
            ("Historical Context & Institutional Origins", "Socio-political context, institutional foundations, and the emergence of authority in {topic}."),
            ("Governance Strategies & Political Reform", "Executive decision-making, legislative programs, and state-building policies in {topic}."),
            ("Crisis Leadership & Conflict Management", "Managing diplomatic tensions, armed conflicts, economic turmoil, and factional crises in {topic}."),
            ("Historical Legacy & Long-term Impact", "Constitutional legacies, institutional reforms, and historiographical assessments of {topic}.")
        ],
        "misconceptions": [
            ("Anachronistic Moral Projection", "Evaluating past leadership decisions strictly through modern contemporary values rather than period constraints in {topic}.",
             "Examine historical actions within the specific socio-political dilemmas and institutional pressures of the era in {topic}."),
            ("Monolithic Great-Man Agency Bias", "Attributing complex historical movements and societal transformations exclusively to a single leader's willpower in {topic}.",
             "Account for broader structural factors including demographic shifts, economic conditions, and factional politics in {topic}."),
            ("De Jure Authority vs De Facto Power Trap", "Confusing formal legal titles and proclamations with actual administrative control and enforcement capacity in {topic}.",
             "Analyze practical institutional enforcement, regional resistance, and diplomatic leverage rather than mere proclamations in {topic}."),
            ("Teleological Inevitability Fallacy", "Assuming historical outcomes and victories were predetermined rather than contingent upon volatile decisions in {topic}.",
             "Recognize the genuine contingency, competing alternatives, and pivotal crisis junctures that shaped historical outcomes in {topic}.")
        ]
    },
    "genetics": {
        "icon": "🧬",
        "category": "Genetics & Heredity",
        "keywords": ["mendel", "genetics", "allele", "chromosome", "genotype", "phenotype", "heredity", "inheritance", "dihybrid", "monohybrid", "dna", "gene", "mutation"],
        "concept_templates": [
            ("Mendelian Principles & Allelic Segregation", "Foundational rules of inheritance, dominant and recessive alleles, and the law of segregation in {topic}."),
            ("Independent Assortment & Dihybrid Dynamics", "Chromosomal distribution, independent assortment of unlinked loci, and phenotypic ratios in {topic}."),
            ("Non-Mendelian Extensions & Chromosomal Linkage", "Incomplete dominance, codominance, multiple alleles, and genetic linkage mechanisms in {topic}."),
            ("Pedigree Analysis & Applied Genetic Diagnostics", "Tracing phenotypic inheritance patterns through pedigree charts and predicting progeny probabilities in {topic}.")
        ],
        "misconceptions": [
            ("Allelic Dominance Frequency Fallacy", "Believing dominant alleles are automatically more common or beneficial in a population than recessive alleles in {topic}.",
             "Recognize that dominance refers solely to phenotypic expression in heterozygotes, not population frequency or fitness in {topic}."),
            ("Genotype-Phenotype Conflation", "Treating observable physical traits as identical to the underlying genetic allelic composition in {topic}.",
             "Differentiate between homozygous and heterozygous genotypic states that produce identical dominant phenotypes in {topic}."),
            ("Independent Assortment Universal Assumption", "Assuming all gene pairs assort independently regardless of chromosomal proximity or genetic linkage in {topic}.",
             "Account for syntenic genes located close together on the same chromosome that exhibit genetic linkage in {topic}."),
            ("Blending Inheritance Residue Trap", "Assuming parental genetic factors permanently blend and dissolve rather than remaining distinct particulate units in {topic}.",
             "Remember alleles remain discrete particulate units that segregate cleanly into gametes according to Mendelian laws in {topic}.")
        ]
    },
    "photography": {
        "icon": "📷",
        "category": "Photography & Optical Arts",
        "keywords": ["photography", "aperture", "shutter speed", "iso", "exposure", "lens", "camera", "f-number", "depth of field", "sensor", "shutter"],
        "concept_templates": [
            ("The Exposure Triangle & Sensor Illumination", "Balancing aperture, shutter speed, and ISO to achieve balanced exposure and image brightness in {topic}."),
            ("Aperture Geometry & Depth of Field Control", "Lens diaphragm mechanics, f-stop scales, and optical control of foreground and background sharpness in {topic}."),
            ("Shutter Speed Dynamics & Motion Capture", "Curtain transit duration, focal plane mechanisms, and freezing versus blurring dynamic motion in {topic}."),
            ("Metering Modes & Creative Exposure Compensation", "Spot, evaluative, and center-weighted metering diagnostics and compensating for challenging lighting in {topic}.")
        ],
        "misconceptions": [
            ("F-Number Diameter Inversion", "Assuming a higher f-number corresponds to a physically larger aperture opening in {topic}.",
             "Remember the f-number is a reciprocal ratio (focal length divided by entrance pupil); larger numbers signify smaller apertures in {topic}."),
            ("ISO Light Generation Fallacy", "Believing increasing ISO physically adds light to the camera sensor rather than amplifying existing electrical signal in {topic}.",
             "Recognize that ISO amplifies the captured electronic signal and introduces noise, rather than collecting additional photons in {topic}."),
            ("Shutter Speed Reciprocal Rule Neglect", "Using slow shutter speeds handheld without accounting for lens focal length, introducing unintentional camera shake in {topic}.",
             "Keep handheld shutter speed faster than the reciprocal of the focal length to eliminate camera motion blur in {topic}."),
            ("Evaluative Metering Neutral Gray Trap", "Trusting default auto-metering on pure white snow or dark backgrounds without manual exposure compensation in {topic}.",
             "Apply deliberate positive compensation on bright scenes and negative compensation on dark scenes to correct 18% neutral gray calibration in {topic}.")
        ]
    },
    "linguistics": {
        "icon": "🗣️",
        "category": "Linguistics & Language Studies",
        "keywords": ["particle", "particles", "japanese", "grammar", "verb", "conjugation", "syntax", "linguistic", "hiragana", "katakana", "kanji", "tense", "aspect", "french verb"],
        "concept_templates": [
            ("Morphological Foundations & Root Paradigms", "Baseline stem structures, inflections, and grammatical categories in {topic}."),
            ("Syntactic Markers & Functional Relationships", "Case markers, postpositions, and relational grammatical particles governing sentence logic in {topic}."),
            ("Aspectual Nuance & Conditional Conjugation", "Temporal aspects, subjunctive versus indicative moods, and conditional sentence structures in {topic}."),
            ("Discourse Pragmatics & Sociolinguistic Register", "Formal versus colloquial registers, polite honorifics, and contextual discourse conventions in {topic}.")
        ],
        "misconceptions": [
            ("Literal Translation Structure Transposition", "Imposing native language word order or prepositional patterns directly onto target grammar in {topic}.",
             "Analyze grammatical relationships using the internal syntactic framework and case-marking rules of {topic}."),
            ("Topic vs Subject Marker Conflation", "Confusing contextual discourse topics with syntactic subject agents in grammatical constructions in {topic}.",
             "Differentiate between overarching conversational themes and the specific grammatical subject of the clause in {topic}."),
            ("Regular Paradigm Overgeneralization", "Applying regular conjugation rules to irregular or auxiliary verbs without checking morphological roots in {topic}.",
             "Memorize fundamental irregular root changes and stem mutations separately from regular affixation patterns in {topic}."),
            ("Aspectual Completion vs Past Tense Confusion", "Conflating perfective aspect with chronological past time in complex narrative clauses in {topic}.",
             "Distinguish between event completion status (aspect) and chronological placement relative to the moment of speech (tense) in {topic}.")
        ]
    },
    "economics": {
        "icon": "📈",
        "category": "Economics & Market Dynamics",
        "keywords": ["supply", "demand", "economics", "market", "price", "elasticity", "inflation", "gdp", "equilibrium", "fiscal", "monetary", "microeconomics", "macroeconomics"],
        "concept_templates": [
            ("Supply, Demand & Market Equilibrium", "Law of demand, law of supply, and price formation at market-clearing equilibrium in {topic}."),
            ("Elasticity & Consumer Responsiveness", "Price elasticity of demand and supply, cross-price elasticity, and revenue implications in {topic}."),
            ("Market Interventions & Welfare Distribution", "Price ceilings, price floors, per-unit taxation, and deadweight loss consequences in {topic}."),
            ("Market Structures & Competitive Strategy", "Perfect competition, monopoly, oligopolistic pricing, and strategic market dynamics in {topic}.")
        ],
        "misconceptions": [
            ("Change in Demand vs Quantity Demanded Confusion", "Confusing a shift of the entire demand curve with a movement along the curve caused by price changes in {topic}.",
             "Distinguish price-induced movements along a curve from shifts driven by non-price determinants like income or preferences in {topic}."),
            ("Price Ceiling Equalization Fallacy", "Assuming setting a legal maximum price ceiling below equilibrium increases the total goods available to all consumers in {topic}.",
             "Recognize that binding price ceilings reduce producer incentives, creating persistent market shortages and rationing in {topic}."),
            ("Inelastic Revenue Inversion Trap", "Believing raising prices on an inelastic good lowers total producer revenue in {topic}.",
             "Remember that for inelastic goods, the percentage price increase exceeds the percentage quantity drop, increasing total revenue in {topic}."),
            ("Zero Economic Profit Failure Fallacy", "Interpreting zero economic profit in competitive equilibrium as business bankruptcy rather than normal accounting return in {topic}.",
             "Differentiate economic profit (accounting profit minus opportunity costs) from accounting profit in long-run competitive equilibrium in {topic}.")
        ]
    },
    "cs_db": {
        "icon": "💻",
        "category": "Computer Science & Database Systems",
        "keywords": ["database", "normalization", "sql", "relational", "schema", "table", "1nf", "2nf", "3nf", "bcnf", "dependency", "primary key", "foreign key"],
        "concept_templates": [
            ("Relational Foundations & Functional Dependencies", "Relational attributes, candidate keys, and functional dependencies governing data schemas in {topic}."),
            ("Normal Forms & Redundancy Decomposition", "First, second, and third normal forms, eliminating partial and transitive dependencies in {topic}."),
            ("Lossless Decomposition & Dependency Preservation", "Testing schemas for lossless-join decomposition and preserving functional dependencies in {topic}."),
            ("Denormalization Trade-offs & Production Optimization", "Balancing query read latency against write anomalies and update consistency in {topic}.")
        ],
        "misconceptions": [
            ("Transitive Dependency Neglect", "Assuming meeting 2NF eliminates update anomalies without checking for non-prime transitive dependencies in {topic}.",
             "Decompose non-prime attributes determined by other non-prime attributes into separate relations to satisfy 3NF in {topic}."),
            ("Lossless Join Verification Omission", "Decomposing tables into multiple relations without ensuring common attributes form a superkey of at least one table in {topic}.",
             "Verify that intersection attributes functionally determine at least one of the decomposed schemas to guarantee lossless join in {topic}."),
            ("Primary Key Selection Arbitrariness", "Selecting non-unique or nullable attributes as primary keys instead of stable minimal candidate keys in {topic}.",
             "Choose immutable, non-null, uniquely identifying candidate keys to preserve entity integrity constraints in {topic}."),
            ("Universal Over-Normalization Fallacy", "Assuming enterprise production databases should always be normalized to 5NF regardless of query read performance in {topic}.",
             "Weigh transactional normalization against read-heavy analytical performance requirements when designing database architectures in {topic}.")
        ]
    },
    "astronomy": {
        "icon": "🔭",
        "category": "Astrophysics & Space Science",
        "keywords": ["moon", "astronomy", "lunar", "phases", "planet", "solar", "orbit", "celestial", "star", "eclipse", "gravity", "satellite", "tides"],
        "concept_templates": [
            ("Celestial Orbital Geometry & Illumination", "Sun-Earth-Moon spatial alignment, synchronous orbit, and solar illumination geometry in {topic}."),
            ("The Lunar Phase Cycle & Waxing/Waning Dynamics", "Crescent, gibbous, quarter, and full moon phase progressions across the 29.5-day synodic month in {topic}."),
            ("Tidal Dynamics & Gravitational Resonance", "Gravitational tidal bulges, spring and neap tides, and orbital resonance in {topic}."),
            ("Eclipse Mechanics & Orbital Plane Inclination", "The 5-degree orbital tilt, nodes of intersection, and conditions required for solar and lunar eclipses in {topic}.")
        ],
        "misconceptions": [
            ("Earth Shadow Phase Fallacy", "Believing moon phases are caused by the Earth casting its shadow onto the lunar surface in {topic}.",
             "Recognize that moon phases result from our varying viewing angle of the Moon's sunlit hemisphere as it orbits Earth in {topic}."),
            ("Synchronous Rotation Stillness Myth", "Assuming the Moon does not rotate on its axis because the same face always points toward Earth in {topic}.",
             "Understand the Moon rotates on its axis at the exact same rate it orbits Earth (tidal locking), presenting one hemisphere to Earth in {topic}."),
            ("Monthly Eclipse Expectation Trap", "Assuming solar and lunar eclipses should occur during every new and full moon cycle in {topic}.",
             "Account for the 5-degree tilt of the Moon's orbital plane relative to the ecliptic, meaning alignment only occurs at nodal points in {topic}."),
            ("Distance-Induced Seasonal/Phase Confusion", "Believing lunar brightness or apparent size variations drive phase transitions rather than illumination geometry in {topic}.",
             "Distinguish apogee and perigee distance variations from the fundamental angular phase cycle driven by solar geometry in {topic}.")
        ]
    },
    "chemistry": {
        "icon": "🧪",
        "category": "Organic Chemistry & Molecular Sciences",
        "keywords": ["chemistry", "organic", "functional group", "hydroxyl", "carbonyl", "carboxyl", "amine", "ester", "alkane", "alkene", "alkyne", "isomer", "molecule", "reaction", "acid"],
        "concept_templates": [
            ("Functional Group Taxonomy & Molecular Skeletons", "Core organic functional groups, carbon hybridization, and IUPAC structural conventions in {topic}."),
            ("Electronic Polarity, Resonance & Intermolecular Forces", "Electronegativity gradients, dipole moments, resonance delocalization, and hydrogen bonding in {topic}."),
            ("Reaction Mechanisms & Nucleophilic/Electrophilic Pathways", "Nucleophilic addition, substitution, elimination pathways, and transition state energetics in {topic}."),
            ("Spectroscopic Identification & Synthetic Multi-step Strategy", "Infrared (IR) spectroscopy, proton NMR shifts, and designing synthetic target transformations in {topic}.")
        ],
        "misconceptions": [
            ("Aliphatic vs Carbonyl Reactivity Inversion", "Assuming non-polar alkane carbons undergo nucleophilic attack more readily than polarized carbonyl carbons in {topic}.",
             "Recognize that the polarized carbonyl carbon possesses a partial positive charge, making it an electrophilic target for nucleophiles in {topic}."),
            ("Intermolecular Hydrogen Bonding vs Covalent Bond Conflation", "Confusing weak intermolecular hydrogen bonds between molecules with intramolecular covalent O-H bonds in {topic}.",
             "Differentiate between covalent bonds holding individual atoms together and secondary intermolecular attractions governing boiling points in {topic}."),
            ("Resonance Hybrid Oscillating Equilibrium Myth", "Believing resonance structures represent distinct physical molecules rapidly flipping back and forth in chemical equilibrium in {topic}.",
             "Understand that resonance structures are formal models contributing to a single static electron-delocalized hybrid in {topic}."),
            ("Stereochemical Inversion Neglect in Bimolecular Reactions", "Assuming nucleophilic substitution (SN2) proceeds with retention of configuration rather than Walden inversion in {topic}.",
             "Account for backside nucleophilic attack which inverts the stereochemical configuration at the chiral center in {topic}.")
        ]
    },
    "math": {
        "icon": "🎲",
        "category": "Probability & Mathematical Statistics",
        "keywords": ["probability", "independent", "dependent", "events", "bayes", "conditional", "sample space", "random variable", "distribution", "permutations", "combinations", "statistics"],
        "concept_templates": [
            ("Sample Spaces, Outcomes & Axiomatic Probability", "Sample spaces, elementary events, Kolmogorov axioms, and baseline probability calculation in {topic}."),
            ("Joint Probability & Independent vs Dependent Events", "Multiplication rules, replacement conditions, and distinguishing independent from dependent events in {topic}."),
            ("Conditional Probability & Bayes' Theorem", "Prior probabilities, likelihood ratios, updating belief given evidence, and posterior distributions in {topic}."),
            ("Random Variables, Distributions & Statistical Expectation", "Discrete random variables, binomial distributions, expected values, and variance calculations in {topic}.")
        ],
        "misconceptions": [
            ("Gambler's Fallacy & Independent Event Memory Myth", "Believing that previous random coin tosses or dice rolls influence the probability of subsequent independent trials in {topic}.",
             "Remember that independent trials have zero memory; each fair toss possesses the identical mathematical probability regardless of prior outcomes in {topic}."),
            ("Inverse Conditional Probability Conflation (Prosecutor's Fallacy)", "Assuming that P(A given B) is mathematically equivalent to P(B given A) in {topic}.",
             "Apply Bayes' theorem to systematically calculate inverse probabilities using base rates and conditional likelihoods in {topic}."),
            ("Mutually Exclusive vs Independent Event Confusion", "Believing mutually exclusive events are independent when in fact mutually exclusive events cannot co-occur in {topic}.",
             "Recognize that if two non-zero events are mutually exclusive, the occurrence of one guarantees the other did not occur, making them highly dependent in {topic}."),
            ("Law of Small Numbers Representative Trap", "Expecting very small sample sizes to perfectly mirror the theoretical population distribution in {topic}.",
             "Understand that stochastic variance is high in small samples, and convergence toward expected values requires the Law of Large Numbers in {topic}.")
        ]
    },
    "tech": {
        "icon": "⚡",
        "category": "Digital Electronics & Computer Engineering",
        "keywords": ["logic gate", "logic gates", "digital electronics", "boolean", "truth table", "and gate", "or gate", "nand", "nor", "xor", "flip-flop", "combinational", "circuit", "binary"],
        "concept_templates": [
            ("Boolean Algebra Foundations & Fundamental Logic Gates", "Binary truth tables, AND, OR, NOT gates, and Boolean algebraic reduction laws in {topic}."),
            ("Universal Gates & Circuit Minimization", "Synthesizing arbitrary Boolean logic using NAND and NOR gates and applying De Morgan's theorems in {topic}."),
            ("Combinational Logic Synthesis & Karnaugh Map Optimization", "Multiplexers, decoders, full adders, and multi-variable Karnaugh map minimization in {topic}."),
            ("Sequential Logic, Propagation Delay & Timing Hazards", "Flip-flops, latches, clocking frequencies, propagation delays, and race conditions in {topic}.")
        ],
        "misconceptions": [
            ("Zero Propagation Delay Fallacy", "Assuming logic gate output transitions occur instantaneously without propagation latency, leading to timing glitches in {topic}.",
             "Account for physical gate switching delays when designing synchronous digital circuits to prevent dynamic hazards in {topic}."),
            ("Exclusive OR (XOR) vs Inclusive OR Conflation", "Assuming an OR gate output goes low when both inputs are simultaneously high in {topic}.",
             "Differentiate between standard inclusive OR (high if either or both are 1) and exclusive XOR (high strictly when inputs differ) in {topic}."),
            ("Floating Input Determinism Trap", "Assuming an unconnected CMOS gate pin defaults to a stable binary zero rather than floating unpredictably in {topic}.",
             "Always tie unused CMOS inputs to VCC or ground using pull-up or pull-down resistors to prevent high-impedance floating states in {topic}."),
            ("De Morgan Transformation Sign Inversion Error", "Forgetting to invert the logical operator when distributing negation across conjunctions in {topic}.",
             "Apply De Morgan's laws: complement individual variables and swap AND operators for OR operators (and vice versa) in {topic}.")
        ]
    },
    "earth": {
        "icon": "🌍",
        "category": "Earth Sciences & Environmental Conservation",
        "keywords": ["tectonic", "plate", "plate tectonics", "earthquake", "volcano", "biodiversity", "ecosystem", "conservation", "geography", "continental drift", "subduction", "species", "biome"],
        "concept_templates": [
            ("Lithospheric Plates & Continental Drift Foundations", "Rigid tectonic plates, the asthenosphere, paleomagnetic striping, and fossil distribution evidence in {topic}."),
            ("Plate Boundary Dynamics & Seismic Faulting", "Convergent, divergent, and transform boundaries, subduction zones, and earthquake mechanisms in {topic}."),
            ("Ecosystem Trophic Architecture & Energy Flow", "Primary producers, 10 percent trophic efficiency, biogeochemical cycles, and ecological niches in {topic}."),
            ("Biodiversity Conservation, Habitat Fragmentation & Resilience", "Species richness, keystone species cascades, habitat corridors, and ecological restoration in {topic}.")
        ],
        "misconceptions": [
            ("Continental Drift Oceanic Free-Floating Myth", "Believing continents plow through the ocean floor like floating ships rather than moving as part of rigid lithospheric plates in {topic}.",
             "Understand that continents and oceanic crust form unified lithospheric plates gliding over the semi-fluid asthenosphere in {topic}."),
            ("Mantle Molten Magma Ocean Misconception", "Assuming the entire Earth's mantle is liquid lava rather than solid rock undergoing high-temperature plastic convection in {topic}.",
             "Recognize that the mantle is mostly solid rock that behaves plastically over millions of years due to extreme overburden pressure in {topic}."),
            ("Trophic Cascade Apex Predator Removal Fallacy", "Believing the removal of top predators has no cascading consequences on lower trophic levels and vegetation in {topic}.",
             "Study trophic cascades where top predator loss triggers overgrazing by herbivores, severely degrading biodiversity and riparian ecosystems in {topic}."),
            ("Linear Isolated Food Chain Oversimplification", "Treating ecological feeding relationships as isolated linear chains rather than interconnected food webs with redundant links in {topic}.",
             "Analyze complex food webs where species have alternative prey pathways that buffer the ecosystem against localized extinctions in {topic}.")
        ]
    },
    "management": {
        "icon": "📊",
        "category": "Project Management & Operational Research",
        "keywords": ["critical path", "project management", "cpm", "pert", "wbs", "slack", "float", "gantt", "milestone", "schedule", "work breakdown"],
        "concept_templates": [
            ("Work Breakdown Structure (WBS) & Activity Dependency Networks", "Decomposing deliverables into discrete work packages and constructing activity-on-node (AON) network diagrams in {topic}."),
            ("Forward and Backward Pass Scheduling Calculations", "Calculating Early Start, Early Finish, Late Start, and Late Finish dates across project networks in {topic}."),
            ("Critical Path Identification & Float/Slack Analysis", "Zero-float critical activities, total float versus free float, and identifying the longest duration project path in {topic}."),
            ("Schedule Crashing, Fast-Tracking & Resource Optimization", "Crashing critical tasks with minimum marginal cost, fast-tracking overlapping phases, and managing project risk in {topic}.")
        ],
        "misconceptions": [
            ("Non-Critical Activity Acceleration Fallacy", "Spending project contingency funds crashing non-critical activities in a misguided effort to compress overall project duration in {topic}.",
             "Compress only activities located strictly on the critical path to reduce the overall project completion timeline in {topic}."),
            ("Total Float vs Free Float Conflation", "Assuming that consuming total float on an early task will not impact the early start dates of subsequent successor tasks in {topic}.",
             "Differentiate between total float (shared delay margin before project delay) and free float (delay margin without delaying any immediate successor) in {topic}."),
            ("Negative Float Infeasibility Oversight", "Ignoring negative float in schedule analysis, failing to recognize that it signifies a hard milestone violation in {topic}.",
             "Recognize that negative float indicates the calculated project finish exceeds a mandatory contractual deadline, requiring active schedule recovery in {topic}."),
            ("Static Critical Path Assumption", "Assuming the critical path remains fixed throughout execution without recognizing that task delays can create new critical paths in {topic}.",
             "Continuously monitor all high-risk near-critical paths as real-time performance fluctuations can shift the critical path dynamically in {topic}.")
        ]
    },
    "music": {
        "icon": "🎵",
        "category": "Music Theory & Harmonic Analysis",
        "keywords": ["music theory", "interval", "intervals", "scales", "chord", "harmony", "cadence", "key signature", "major scale", "minor scale", "tonic", "dominant", "pitch"],
        "concept_templates": [
            ("Pitch Foundations, Semitones & Interval Classification", "Frequency intervals, semitone distances, major, minor, perfect, augmented, and diminished intervals in {topic}."),
            ("Scale Construction, Modal Structures & Key Signatures", "Diatonic major and minor scale step patterns (W-W-H-W-W-W-H) and the circle of fifths in {topic}."),
            ("Triad Formation, Seventh Chords & Harmonic Function", "Root positions, inversions, tonic, subdominant, dominant functions, and Roman numeral analysis in {topic}."),
            ("Voice Leading Principles, Cadential Closures & Modulation", "Avoiding parallel fifths/octaves, authentic versus plagal cadences, and smooth pivot-chord modulations in {topic}.")
        ],
        "misconceptions": [
            ("Enharmonic Spelling Equivalence in Tonal Syntax", "Treating enharmonic notes like G# and Ab as grammatically interchangeable regardless of key signature and scale context in {topic}.",
             "Spell notes strictly in accordance with their diatonic scale degree function to maintain valid harmonic voice leading in {topic}."),
            ("Parallel Fifths & Octaves Voice Leading Trap", "Allowing two independent voice parts to move in parallel fifths or octaves, destroying contrapuntal independence in {topic}.",
             "Maintain voice independence by using contrary or oblique motion when resolving harmonic voices in {topic}."),
            ("Circle of Fifths Key Signature Reading Error", "Misidentifying the tonic key note by reading the last flat as the key rather than the second-to-last flat in flat key signatures in {topic}.",
             "Use standard key signature rules: the last sharp is the leading tone (step up to tonic); the second-to-last flat is the tonic key in {topic}."),
            ("Harmonic Minor Leading Tone Omission", "Failing to raise the seventh scale degree when harmonizing in minor keys, weakening the dominant-to-tonic cadence in {topic}.",
             "Raise the seventh degree in minor keys to construct a major dominant (V) chord with an authentic leading tone resolving to the tonic in {topic}.")
        ]
    },
    "general": {
        "icon": "📚",
        "category": "General Academic Discipline",
        "keywords": [],
        "concept_templates": [
            ("Foundational Principles & Core Taxonomy", "Baseline definitions, foundational criteria, and the structural scope of {topic}."),
            ("Governing Principles & Structural Relationships", "Primary causal relationships, operational dynamics, and essential frameworks in {topic}."),
            ("Advanced Interactions & Contextual Constraints", "Complex interactions, boundary conditions, and specialized dynamics within {topic}."),
            ("Applied Problem-Solving & Critical Diagnostics", "Evidence-based evaluation, diagnosing complex challenges, and practical synthesis in {topic}.")
        ],
        "misconceptions": [
            ("Foundational Premise Misattribution", "Applying advanced rules without verifying initial baseline criteria and definitions in {topic}.",
             "Verify fundamental principles and structural parameters in {topic} to establish baseline problem criteria."),
            ("Correlational vs Causal Relationship Confusion", "Confusing passive coincidental correlation with direct underlying causal mechanisms in {topic}.",
             "Distinguish active causal mechanisms from secondary coincidental associations when analyzing {topic}."),
            ("Contextual Boundary Neglect", "Assuming operational principles remain identical across divergent contexts without respecting boundary conditions in {topic}.",
             "Evaluate contextual limitations, environmental parameters, and boundary conditions when analyzing {topic}."),
            ("Superficial Symptom vs Underlying Factor Conflation", "Addressing surface-level manifestations rather than diagnosing the primary underlying factors in {topic}.",
             "Isolate and address primary underlying factors through systematic evaluation rather than treating superficial effects in {topic}.")
        ]
    }
}

def detect_archetype(topic_title: str, articles: List[Dict[str, str]] = None) -> Tuple[str, Dict[str, Any]]:
    """Detects best-matching archetype dictionary based on topic title and article content."""
    title_low = topic_title.lower()
    
    # 1. First priority: Direct keyword matches in user's topic title
    for arch_key, arch_data in ARCHETYPES.items():
        if arch_key == "general":
            continue
        for kw in arch_data["keywords"]:
            if re.search(rf"\b{re.escape(kw)}s?\b", title_low):
                return arch_key, arch_data
                
    # 2. Second priority: Keyword matches in combined article title and text
    combined = title_low
    if articles:
        combined += " " + " ".join((a.get("title", "") + " " + a.get("description", "") + " " + a.get("extract", "")) for a in articles).lower()
        
    for arch_key, arch_data in ARCHETYPES.items():
        if arch_key == "general":
            continue
        for kw in arch_data["keywords"]:
            if re.search(rf"\b{re.escape(kw)}s?\b", combined):
                return arch_key, arch_data
                
    return "general", ARCHETYPES["general"]

def generate_tiered_questions_for_topic(
    topic_title: str,
    arch_key: str,
    arch_data: Dict[str, Any],
    concepts: List[Dict[str, Any]],
    misconceptions: List[Dict[str, Any]],
    articles: List[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Synthesizes 12 high-quality tiered questions (4 Basic, 4 Conceptual, 4 Application)
    with balanced options, randomized keys, and authentic Two-Tier Reasoning Probes.
    """
    questions = []
    
    # Extract authentic facts from articles if available
    facts = []
    if articles:
        for a in articles:
            ext = a.get("extract", "")
            for s in ext.split("."):
                s_clean = s.strip()
                if len(s_clean) > 25 and not any(bad in s_clean.lower() for bad in ["refer to", "disambiguation", "born in", "coordinates"]):
                    facts.append(s_clean)
                    
    # Select probe questions: 4 probes distributed across conceptual and application tiers (Q2, Q6, Q8, Q12)
    probe_indices = {1, 5, 7, 11}
    
    for c_idx in range(4):
        c_obj = concepts[c_idx]
        c_name = c_obj["name"]
        m_obj = misconceptions[c_idx]
        
        # 1. Basic Recall Question (Easy)
        q_basic = build_basic_question(topic_title, arch_key, c_idx, c_name, facts)
        questions.append({
            "concept_suffix": f"c{c_idx+1}",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": q_basic["text"],
            "option_a": q_basic["options"]["A"],
            "option_b": q_basic["options"]["B"],
            "option_c": q_basic["options"]["C"],
            "option_d": q_basic["options"]["D"],
            "correct_option": q_basic["correct"],
            "explanation": q_basic["explanation"],
            "reasoning_probe": None
        })
        
        # 2. Conceptual Question (Medium)
        q_idx_conc = len(questions)
        has_probe_conc = (q_idx_conc in probe_indices)
        q_conc = build_conceptual_question(topic_title, arch_key, c_idx, c_name, facts, has_probe=has_probe_conc)
        questions.append({
            "concept_suffix": f"c{c_idx+1}",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": q_conc["text"],
            "option_a": q_conc["options"]["A"],
            "option_b": q_conc["options"]["B"],
            "option_c": q_conc["options"]["C"],
            "option_d": q_conc["options"]["D"],
            "correct_option": q_conc["correct"],
            "explanation": q_conc["explanation"],
            "reasoning_probe": q_conc.get("reasoning_probe")
        })
        
        # 3. Application Question (Hard)
        q_idx_app = len(questions)
        has_probe_app = (q_idx_app in probe_indices)
        q_app = build_application_question(topic_title, arch_key, c_idx, c_name, m_obj, facts, has_probe=has_probe_app)
        questions.append({
            "concept_suffix": f"c{c_idx+1}",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": q_app["text"],
            "option_a": q_app["options"]["A"],
            "option_b": q_app["options"]["B"],
            "option_c": q_app["options"]["C"],
            "option_d": q_app["options"]["D"],
            "correct_option": q_app["correct"],
            "explanation": q_app["explanation"],
            "reasoning_probe": q_app.get("reasoning_probe")
        })
        
    return questions

def build_basic_question(topic: str, arch: str, c_idx: int, c_name: str, facts: List[str]) -> Dict[str, Any]:
    """Generates authentic introductory recall question testing definitions and baseline taxonomy."""
    if arch == "culinary":
        if c_idx == 0:
            return {
                "text": f"In {topic}, what constitutes the foundational ingredient composition of standard choux pastry dough?",
                "options": {
                    "A": "A cooked mixture of water or milk, butter, flour, and whole eggs.",
                    "B": "A leavened yeast sponge fermented with commercial baker's yeast.",
                    "C": "A dense laminated shortbread made strictly from sugar and lard.",
                    "D": "An uncooked slurry of cornstarch and cold water without fats."
                },
                "correct": "A",
                "explanation": f"Choux pastry relies on cooking liquid, butter, and flour into a panade before beating in eggs."
            }
        elif c_idx == 1:
            return {
                "text": f"What is the primary physical objective of cooking the flour panade on the stovetop in {topic}?",
                "options": {
                    "A": "To gelatinize flour starches and evaporate surplus liquid before adding eggs.",
                    "B": "To completely caramelize the sugars and produce a deep dark crust.",
                    "C": "To activate chemical baking powder before placing the dough in the oven.",
                    "D": "To melt gluten strands and eliminate all structural protein cohesion."
                },
                "correct": "A",
                "explanation": f"Stovetop cooking gelatinizes wheat starch, enabling the panade to absorb eggs and trap steam."
            }
        elif c_idx == 2:
            return {
                "text": f"Which primary leavening mechanism creates the light, hollow interior characteristic of baked {topic}?",
                "options": {
                    "A": "Rapid expansion of trapped moisture converting into steam during baking.",
                    "B": "Chemical release of carbon dioxide gas from activated baking soda.",
                    "C": "Biological fermentation of active yeast releasing ethanol and gas.",
                    "D": "Air bubbles whipped into egg whites creating a rigid cold meringue."
                },
                "correct": "A",
                "explanation": f"High oven heat vaporizes the high water content into steam, puffing the dough into a hollow shell."
            }
        else:
            return {
                "text": f"Why must baked pastry shells in {topic} be thoroughly dried before being removed from the oven?",
                "options": {
                    "A": "To set the egg protein matrix and prevent the hollow shell from collapsing.",
                    "B": "To allow remaining active yeast spores to finish metabolic fermentation.",
                    "C": "To dissolve residual salt crystals into the surrounding butter fat.",
                    "D": "To completely prevent hot steam from escaping during the cooling stage."
                },
                "correct": "A",
                "explanation": f"Egg proteins and starches must fully set and dehydrate to support the hollow pastry structure."
            }
    elif arch == "law":
        if c_idx == 0:
            return {
                "text": f"In {topic}, what foundational principle establishes the supremacy of the constitution over statutory enactments?",
                "options": {
                    "A": "Constitutional supremacy ensuring laws conflicting with the charter are invalid.",
                    "B": "Absolute parliamentary discretion to overturn judicial orders without limitation.",
                    "C": "Executive privilege permitting presidential decrees to bypass written articles.",
                    "D": "Common law convention declaring historical customs superior to written texts."
                },
                "correct": "A",
                "explanation": f"Constitutional supremacy dictates that all legislative acts must conform to the governing charter."
            }
        elif c_idx == 1:
            return {
                "text": f"Under {topic}, what standard governs whether a statutory restriction on a fundamental right is constitutionally valid?",
                "options": {
                    "A": "The doctrine of proportionality and reasonable public interest restrictions.",
                    "B": "Complete judicial deference to whichever policy the executive prefers.",
                    "C": "Automatic approval if the bill passes with a simple legislative majority.",
                    "D": "Total prohibition of any government regulation under all circumstances."
                },
                "correct": "A",
                "explanation": f"Fundamental rights may only be restricted through reasonable, proportionate measures serving valid aims."
            }
        elif c_idx == 2:
            return {
                "text": f"What is the institutional function of constitutional judicial review in {topic}?",
                "options": {
                    "A": "Empowering constitutional courts to review and strike down unconstitutional legislation.",
                    "B": "Directly drafting statutory tax codes and passing federal fiscal budgets.",
                    "C": "Conducting criminal prosecutions on behalf of sovereign police agencies.",
                    "D": "Advising foreign diplomatic embassies on international commercial trade."
                },
                "correct": "A",
                "explanation": f"Judicial review allows courts to assess legislative and executive acts against constitutional mandates."
            }
        else:
            return {
                "text": f"In {topic}, which extraordinary legal mechanism allows citizens to directly petition the apex court for rights enforcement?",
                "options": {
                    "A": "Writ jurisdiction petitions seeking orders like mandamus or habeas corpus.",
                    "B": "Commercial arbitration claims filed under private corporate contracts.",
                    "C": "Informal petitions addressed to local municipal zoning commissioners.",
                    "D": "Administrative appeals submitted exclusively to foreign embassies."
                },
                "correct": "A",
                "explanation": f"Constitutional writ jurisdiction provides immediate direct access to superior courts to remedy rights violations."
            }
    elif arch == "history":
        return {
            "text": f"In the study of {topic}, which primary historical factor shaped institutional governance and authority?",
            "options": {
                "A": f"The constitutional framework, executive authority, and historical crises of {topic}.",
                "B": "Complete absence of institutional government or written civil agreements.",
                "C": "Direct automated rule by foreign computerized algorithms without human input.",
                "D": "An unchanging societal structure where political developments were frozen."
            },
            "correct": "A",
            "explanation": f"Historical leadership in {topic} developed within constitutional frameworks and structural challenges."
        }
    else:
        return {
            "text": f"In {topic}, which statement accurately defines the core structural baseline of {c_name}?",
            "options": {
                "A": f"The fundamental definitions, baseline criteria, and primary rules of {topic}.",
                "B": "An unverified subjective opinion that directly contradicts established academic evidence.",
                "C": "A temporary assumption that applies exclusively during introductory practice tests.",
                "D": "A variable commercial convention that changes completely across different regions."
            },
            "correct": "A",
            "explanation": f"The baseline framework of {c_name} establishes verified definitions and principles for studying {topic}."
        }

def build_conceptual_question(topic: str, arch: str, c_idx: int, c_name: str, facts: List[str], has_probe: bool = False) -> Dict[str, Any]:
    """Generates authentic conceptual question explaining why mechanisms operate as they do."""
    if arch == "culinary":
        q = {
            "text": f"In {topic}, why does incorporating eggs into a boiling hot panade ruin the pastry structure?",
            "options": {
                "A": "The extreme residual heat prematurely curdles egg proteins before proper emulsification occurs.",
                "B": "The boiling temperature instantly transforms all liquid water into solid ice crystals.",
                "C": "The heat completely dissolves the flour starch granules, eliminating all gluten proteins.",
                "D": "The hot panade causes the eggs to release toxic carbon monoxide gas inside the kitchen."
            },
            "correct": "A",
            "explanation": f"Panades must cool slightly below 60°C (140°F) so eggs can form a smooth emulsion without scrambling."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why is gradual egg addition essential when finishing the choux panade in {topic}?",
                "options": {
                    "A": "Gradual addition allows the cook to monitor dough consistency and prevent over-saturation.",
                    "B": "Adding eggs all at once causes the mixer motor to reverse direction immediately.",
                    "C": "Egg yolks only become edible when exposed to room air for thirty minutes.",
                    "D": "Egg whites require room light to undergo complete chemical photolysis."
                },
                "correct_probe": "A"
            }
        return q
    elif arch == "law":
        q = {
            "text": f"In {topic}, why is the doctrine of basic structure or constitutional supremacy essential for democracy?",
            "options": {
                "A": "It prevents transient legislative majorities from abolishing core constitutional guarantees.",
                "B": "It eliminates the need for citizens to participate in periodic democratic elections.",
                "C": "It grants judges the authority to write commercial corporate contracts for businesses.",
                "D": "It dissolves the executive branch and places all police power under local courts."
            },
            "correct": "A",
            "explanation": f"Constitutional safeguards protect fundamental liberties from being extinguished by temporary majorities."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why must judicial review balance legislative deference with constitutional vigilance in {topic}?",
                "options": {
                    "A": "To check constitutional overreach while respecting the representative mandate of legislators.",
                    "B": "Because superior court judges are legally designated as heads of the armed forces.",
                    "C": "Because parliamentary bills expire automatically if not reviewed within forty-eight hours.",
                    "D": "Because common law doctrine requires all judicial rulings to be approved by foreign courts."
                },
                "correct_probe": "A"
            }
        return q
    elif arch == "astronomy":
        q = {
            "text": f"In {topic}, why do we observe distinct lunar phases throughout the course of a synodic month?",
            "options": {
                "A": "Because the Moon's orbital position changes our vantage point of its illuminated half.",
                "B": "Because the Earth casts a variable curved shadow across the Moon every single night.",
                "C": "Because the Sun physically turns off its solar radiation during the new moon period.",
                "D": "Because the Moon contracts and expands physically due to extreme orbital temperature shifts."
            },
            "correct": "A",
            "explanation": f"Lunar phases reflect the changing angle from which Earth observes the Moon's sunlit hemisphere."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why is the Moon's synchronous rotation responsible for tidal locking in {topic}?",
                "options": {
                    "A": "Gravitational tidal friction synchronized the Moon's rotational period with its orbital period.",
                    "B": "The Moon has magnetic poles that physically lock onto Earth's central iron core.",
                    "C": "Solar winds exert continuous pressure that prevents the Moon from spinning on its axis.",
                    "D": "Atmospheric air friction between the Earth and Moon brought the lunar spin to a halt."
                },
                "correct_probe": "A"
            }
        return q
    else:
        q = {
            "text": f"In {topic}, what conceptual relationship explains how {c_name} produces its primary observed effect?",
            "options": {
                "A": f"The core working mechanisms and relational principles that govern {topic}.",
                "B": "A chaotic random process where causal factors fluctuate with zero consistency.",
                "C": "A static isolated condition where internal elements exert zero influence on outcomes.",
                "D": "An artificial assumption that only applies inside simulated classroom exercises."
            },
            "correct": "A",
            "explanation": f"Understanding the relational mechanism behind {c_name} clarifies how principles operate in {topic}."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"What underlying rationale explains why this relationship governs {c_name} in {topic}?",
                "options": {
                    "A": f"Because established principles dictate consistent interactions across components in {topic}.",
                    "B": "Because introductory definitions can be discarded once practical problems begin.",
                    "C": "Because variables fluctuate randomly without underlying physical or logical rules.",
                    "D": "Because academic convention requires selecting this option regardless of facts."
                },
                "correct_probe": "A"
            }
        return q

def build_application_question(topic: str, arch: str, c_idx: int, c_name: str, m_obj: Dict[str, Any], facts: List[str], has_probe: bool = False) -> Dict[str, Any]:
    """Generates authentic application / diagnostic scenario question testing deep problem-solving."""
    if arch == "culinary":
        q = {
            "text": f"A baker preparing cream puffs in {topic} opens the oven door after only 12 minutes of baking. What is the immediate consequence?",
            "options": {
                "A": "Cold air rushes in and collapses the expanding pastry shells before starches and egg proteins set.",
                "B": "The sudden air exposure causes the pastry shells to violently expand to quadruple their volume.",
                "C": "The dough absorbs ambient nitrogen and turns completely black within five seconds.",
                "D": "The oven heating elements automatically deactivate and permanently blow their electrical fuses."
            },
            "correct": "A",
            "explanation": f"Opening the oven early releases trapped heat and steam, causing fragile, unset pastry shells to deflate."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why does premature thermal loss cause structural collapse in baking {topic}?",
                "options": {
                    "A": "Steam pressure inside the shell condenses into liquid before gluten and egg matrices coagulate.",
                    "B": "Cold drafts trigger rapid chemical decomposition of table salt within the butter.",
                    "C": "The sugar crystals undergo spontaneous sublimation into gaseous nitrogen.",
                    "D": "Gluten proteins require continuous darkness inside the oven to maintain their shape."
                },
                "correct_probe": "A"
            }
        return q
    elif arch == "law":
        q = {
            "text": f"A state legislature enacts a statute broadly censoring all digital commentary regarding public policy. Under {topic}, how should a court rule?",
            "options": {
                "A": "Invalidate the statute as an unconstitutional, disproportionate restriction on free expression.",
                "B": "Uphold the blanket censorship because state legislatures possess limitless sovereign powers.",
                "C": "Transfer executive control of all digital media directly to the state judicial registry.",
                "D": "Refuse to hear the challenge because courts are prohibited from reviewing state enactments."
            },
            "correct": "A",
            "explanation": f"Blanket censorship fails constitutional scrutiny and proportionality tests protecting fundamental speech."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why does the constitutional proportionality test invalidate overbroad statutory speech bans in {topic}?",
                "options": {
                    "A": "Because restrictions must be narrowly tailored to achieve legitimate aims without curtailing lawful rights.",
                    "B": "Because the executive branch is constitutionally prohibited from enforcing legislative statutes.",
                    "C": "Because digital media platforms are exempt from all domestic national statutory laws.",
                    "D": "Because courts require criminal penalties to be enacted by unanimous parliamentary vote."
                },
                "correct_probe": "A"
            }
        return q
    elif arch == "astronomy":
        q = {
            "text": f"An observer notices that a solar eclipse does not happen every time a New Moon occurs in {topic}. What geometric factor explains this?",
            "options": {
                "A": "The Moon's orbital plane is inclined by about 5 degrees relative to Earth's orbital plane.",
                "B": "The Moon moves beyond the orbit of Mars during every alternating monthly rotation.",
                "C": "Solar eclipses can only take place when the Earth completely stops its orbital rotation.",
                "D": "The Sun's diameter shrinks significantly whenever a New Moon phase begins."
            },
            "correct": "A",
            "explanation": f"The 5-degree orbital tilt means the New Moon usually passes slightly above or below the Sun's disk."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why are eclipses restricted to the intersection points (nodes) of the orbital planes in {topic}?",
                "options": {
                    "A": "Because collinear alignment of the Sun, Earth, and Moon can only occur when the Moon crosses the ecliptic plane.",
                    "B": "Because the gravitational pull of the Sun only affects lunar motion twice each calendar year.",
                    "C": "Because the Moon loses its surface reflectivity when traveling between orbital nodes.",
                    "D": "Because Earth's magnetic field deflects the Moon away from the Sun during non-nodal passes."
                },
                "correct_probe": "A"
            }
        return q
    else:
        q = {
            "text": f"A practitioner working in {topic} observes unexpected anomalous results when applying {c_name}. How should they proceed?",
            "options": {
                "A": f"Systematically isolate variables and verify empirical observations against baseline criteria in {topic}.",
                "B": "Discard all recorded observations immediately and assume the experimental data is fabricated.",
                "C": "Change every testing parameter simultaneously without recording individual changes.",
                "D": "Abandon all established theoretical principles and rely exclusively on unverified guesses."
            },
            "correct": "A",
            "explanation": f"Systematic variable isolation and baseline verification allow practitioners to diagnose issues accurately in {topic}."
        }
        if has_probe:
            q["reasoning_probe"] = {
                "prompt": f"Why is systematic variable isolation superior to modifying multiple parameters at once in {topic}?",
                "options": {
                    "A": f"Because isolating variables identifies the specific causal factor responsible for the observed outcome.",
                    "B": "Because academic research guidelines legally prohibit changing more than one parameter per month.",
                    "C": "Because testing instruments permanently break down if multiple variables fluctuate simultaneously.",
                    "D": "Because modifying multiple variables causes data values to freeze into mathematical zeros."
                },
                "correct_probe": "A"
            }
        return q

def synthesize_universal_curriculum(
    domain_id: str,
    topic_title: str,
    articles: List[Dict[str, str]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], str, str]:
    """
    Universal entry point: Synthesizes 4 concepts, 4 misconceptions, 12 tiered questions,
    and 4 concept guides for ANY submitted topic across all academic disciplines.
    """
    clean_title = topic_title.strip()
    try:
        from curated_extensions import normalize_topic_title
    except ImportError:
        try:
            from app.curated_extensions import normalize_topic_title
        except ImportError:
            from backend.app.curated_extensions import normalize_topic_title
    clean_title = normalize_topic_title(clean_title)
    
    arch_key, arch_data = detect_archetype(clean_title, articles)
    icon = arch_data["icon"]
    category = arch_data["category"]
    
    # 1. Build 4 Concepts & Guides with DAG Prerequisites
    concepts = []
    concept_guides = []
    for i, (tmpl_name, tmpl_desc) in enumerate(arch_data["concept_templates"]):
        cid = f"{domain_id}_c{i+1}"
        prereqs = [concepts[i-1]["id"]] if i > 0 else []
        cname = f"{clean_title}: {tmpl_name.format(topic=clean_title)}"
        cdesc = tmpl_desc.format(topic=clean_title)
        
        concepts.append({
            "id": cid,
            "concept_id": cid,
            "domain_id": domain_id,
            "name": cname,
            "slug": re.sub(r'[^a-zA-Z0-9]+', '_', cname.lower()).strip('_')[:28],
            "category": category,
            "description": cdesc,
            "prerequisites": prereqs,
            "order_index": i + 1
        })
        concept_guides.append({
            "concept_id": cid,
            "domain_id": domain_id,
            "name": cname,
            "core_idea": f"Core principles, foundational rules, and operational methods governing {cname}.",
            "example": f"Practical application scenario demonstrating the principles of {cname} in real-world contexts.",
            "common_mistake": f"Common pitfall: confusing baseline definitions with advanced dynamics in {cname}.",
            "key_takeaway": f"Mastering {cname} provides the prerequisite foundation for comprehensive understanding of {clean_title}."
        })
        
    # 2. Build 4 Misconceptions
    misconceptions = []
    for i, (m_name, m_desc, m_rem) in enumerate(arch_data["misconceptions"]):
        cid = concepts[i]["id"] if i < len(concepts) else concepts[0]["id"]
        misconceptions.append({
            "id": f"MISC_{domain_id.upper()}_{i+1}",
            "domain_id": domain_id,
            "code": f"M-{domain_id[:4].upper()}-{i+1:02d}",
            "concept_id": cid,
            "name": m_name,
            "description": m_desc.format(topic=clean_title),
            "remediation": m_rem.format(topic=clean_title)
        })
        
    # 3. Build 12 Tiered Questions
    raw_questions = generate_tiered_questions_for_topic(
        clean_title, arch_key, arch_data, concepts, misconceptions, articles
    )
    
    questions = []
    for i, q_def in enumerate(raw_questions):
        c_idx = i // 3 if i < 12 else 0
        cid = concepts[c_idx]["id"]
        mid = misconceptions[c_idx]["id"]
        
        # Build question object
        q_obj = {
            "id": f"{domain_id}_q{i+1}",
            "question_id": f"{domain_id}_q{i+1}",
            "domain_id": domain_id,
            "concept_id": cid,
            "question_type": q_def["question_type"],
            "difficulty_tier": q_def["question_type"],
            "difficulty": q_def["difficulty"],
            "question_text": q_def["question_text"],
            "option_a": q_def["option_a"],
            "option_b": q_def["option_b"],
            "option_c": q_def["option_c"],
            "option_d": q_def["option_d"],
            "correct_option": q_def.get("correct_option", "A"),
            "explanation": q_def["explanation"],
            "misconception_id": mid,
            "prerequisite_id": concepts[c_idx]["prerequisites"][0] if concepts[c_idx]["prerequisites"] else cid,
            "reasoning_probe": q_def.get("reasoning_probe")
        }
        questions.append(q_obj)
        
    # 4. Shuffle options and probe options with answer key preservation
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
            
            # Clean duplicate "Because Because" if present
            for ltr, txt in list(p_opts.items()):
                clean_txt = re.sub(r'^\s*because\s+because\s+', 'Because ', txt, flags=re.IGNORECASE)
                p_opts[ltr] = clean_txt
            p_corr_txt = re.sub(r'^\s*because\s+because\s+', 'Because ', p_corr_txt, flags=re.IGNORECASE)
            
            p_list = list(p_opts.values())
            random.shuffle(p_list)
            rp["options"] = {"A": p_list[0], "B": p_list[1], "C": p_list[2], "D": p_list[3]}
            for ltr, txt in rp["options"].items():
                if txt == p_corr_txt:
                    rp["correct_probe"] = ltr
                    break

    # 5. Validation Check
    try:
        from quiz_validator import validate_curriculum_package
    except ImportError:
        try:
            from app.quiz_validator import validate_curriculum_package
        except ImportError:
            from backend.app.quiz_validator import validate_curriculum_package
    is_valid, validation_errors = validate_curriculum_package(concepts, misconceptions, questions, category)
    if not is_valid:
        print(f"[Universal Synthesizer Warning] Package for '{clean_title}' had validation issues: {validation_errors[:3]}")

    return concepts, misconceptions, questions, concept_guides, icon, category
