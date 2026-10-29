"""
DeepLearnX Universal Domain Assessment & Question Generation Engine
Provides authentic, pedagogically rigorous, non-repeating diagnostic questions
and Directed Acyclic Graph (DAG) curricula for ANY topic in the world.
Guarantees:
- 12 completely distinct, non-repeating questions across 4 cognitive concepts.
- 4 Easy Basic, 4 Medium Conceptual, and 4 Hard Application questions.
- Randomized Two-Tier Reasoning Probe placement across the quiz (non-predictable).
- Disciplinary archetype matching across 14 academic domains.
- Universal Academic Multi-Disciplinary Framework for any arbitrary or novel topic.
- Zero engineering jargon anomalies in non-engineering topics.
"""

import re
import random
from typing import Dict, List, Tuple, Any

def disc_match(patterns: List[str], text: str) -> bool:
    """Matches keywords using word boundaries to avoid false substring matches."""
    for pat in patterns:
        if re.search(rf"\b{re.escape(pat)}s?\b", text, re.IGNORECASE):
            return True
    return False

def generate_curriculum_for_topic(
    domain_id: str,
    topic_title: str,
    syllabus_text: str = ""
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], str, str]:
    combined = f"{topic_title} {syllabus_text}".lower()

    # 1. Detect archetype with word boundary safety
    if disc_match([
        "engineering graphic", "engineering drawing", "technical drawing", "autocad", "cad",
        "orthographic", "isometric projection", "isometric drawing", "drafting", "dimensioning",
        "projection plane", "blueprint", "solidworks", "geometric dimensioning", "gd&t"
    ], combined):
        arch = "graphics"
        icon, cat = "📐", "Engineering Graphics & Design"

    elif disc_match([
        "fluid mechanic", "fluid dynamic", "fluid flow", "hydrodynamic", "hydraulics",
        "bernoulli", "navier stokes", "viscosity", "laminar", "turbulent", "pipe flow",
        "reynolds number", "aerodynamic", "boundary layer", "pump cavitation", "venturi"
    ], combined):
        arch = "fluid"
        icon, cat = "💧", "Fluid Mechanics & Hydraulics"

    elif disc_match([
        "spider", "arachnid", "insect", "animal", "zoology", "biology", "biological",
        "cell biology", "genetics", "dna", "rna", "ecology", "evolution", "anatomy",
        "physiology", "immunology", "pathology", "medicine", "pharmacology", "neuroscience",
        "virology", "microbiology", "photosynthesis", "organism", "mammal", "bird", "reptile",
        "amphibian", "arthropod", "marine biology", "botany", "flora", "fauna", "biodiversity",
        "taxonomy", "speciation", "wildlife"
    ], combined):
        arch = "bio"
        icon, cat = "🧬", "Biological & Life Sciences"

    elif disc_match([
        "chemistry", "chemical", "molecule", "reaction kinetics", "stoichiometry",
        "acid base", "catalyst", "polymer", "chemical synthesis", "covalent bond",
        "ionic bond", "periodic table", "electrochemistry", "organic chemistry", "inorganic"
    ], combined):
        arch = "chem"
        icon, cat = "🧪", "Chemical Sciences & Materials"

    elif disc_match([
        "physics", "quantum mechanics", "optics", "gravity", "general relativity",
        "electromagnetism", "nuclear physics", "astronomy", "astrophysics", "cosmology",
        "thermodynamics", "laser physics", "particle physics"
    ], combined) and not disc_match(["fluid", "mechanic"], combined):
        arch = "physics"
        icon, cat = "🔭", "Physics & Space Sciences"

    elif disc_match([
        "software engineering", "programming", "algorithm", "data structure", "database",
        "operating system", "computer network", "compiler", "cybersecurity", "cloud computing",
        "full stack", "web development", "react", "node", "sql", "api", "python code", "java"
    ], combined) and not disc_match(["graphics", "drawing", "drafting", "fluid", "mechanic"], combined):
        arch = "tech"
        icon, cat = "💻", "Computer Science & Software"

    elif disc_match([
        "horticulture", "agriculture", "pomology", "olericulture", "floriculture",
        "agronomy", "crop science", "soil science", "plant propagation", "pest management",
        "farming", "greenhouse", "fertilizer", "irrigation", "entomology"
    ], combined):
        arch = "agri"
        icon, cat = "🌿", "Agricultural & Plant Sciences"

    elif disc_match([
        "structural", "mechanics of materials", "strength of materials", "statics",
        "kinematics", "beam deflection", "truss", "stress strain", "machine design",
        "vibration", "civil engineering", "concrete structure", "geotechnical"
    ], combined):
        arch = "civil_mech"
        icon, cat = "⚙️", "Mechanical & Structural Engineering"

    elif disc_match([
        "mathematics", "calculus", "linear algebra", "geometry", "statistics",
        "probability", "matrix algebra", "trigonometry", "differential equation",
        "discrete mathematics", "numerical methods"
    ], combined):
        arch = "math"
        icon, cat = "📐", "Mathematics & Quantitative Methods"

    elif disc_match([
        "economics", "microeconomics", "macroeconomics", "finance", "marketing",
        "supply chain", "accounting", "business management", "banking", "inflation",
        "price elasticity", "gross domestic product", "gdp", "market equilibrium"
    ], combined):
        arch = "econ"
        icon, cat = "📈", "Economics & Business Management"

    elif disc_match([
        "law", "legal system", "constitution", "jurisprudence", "judiciary",
        "statutory interpretation", "human rights", "criminal law", "tort law",
        "contract law", "constitutional law", "governance", "court precedent"
    ], combined):
        arch = "law"
        icon, cat = "⚖️", "Law & Political Science"

    elif disc_match([
        "history", "historical", "revolution", "civilization", "empire",
        "archaeology", "medieval", "ancient history", "world war", "dynasty",
        "colonialism", "historiography"
    ], combined):
        arch = "history"
        icon, cat = "🏛️", "History & Humanities"

    elif disc_match([
        "music theory", "harmony", "melody", "rhythm", "literature", "poetry",
        "novel", "theatre", "linguistics", "musical composition", "musical scale", "creative arts"
    ], combined):
        arch = "arts"
        icon, cat = "🎵", "Arts, Music & Literature"

    else:
        arch = "universal"
        icon, cat = "📚", "General Academic Discipline"

    # 2. Build 4 Progressive Concepts
    if arch == "graphics":
        concept_defs = [
            (f"{topic_title}: Orthographic Projections & Principal Planes",
             "Reference planes (HP, VP, PP), first-angle vs third-angle standards, and principal view alignment."),
            (f"{topic_title}: Isometric Projections & Spatial Visualization",
             "Isometric axes (30° inclination), isometric scale ratio (0.816), and the box construction method."),
            (f"{topic_title}: Sections of Solids & Internal Features",
             "Cutting plane placement, standard 45° section hatching, and conventions for unhatched fasteners."),
            (f"{topic_title}: Dimensioning Rules, Tolerances & Assembly Fits",
             "Baseline datum dimensioning, tolerance classes (clearance, transition, interference), and stack-up.")
        ]
    elif arch == "fluid":
        concept_defs = [
            (f"{topic_title}: Fluid Properties & Hydrostatic Pressure",
             "Newtonian viscosity, shear stress gradients, isotropic static pressure, and hydrostatic head."),
            (f"{topic_title}: Continuity & Conservation Principles",
             "Conservation of mass, steady incompressible continuity, and velocity-pressure trade-offs."),
            (f"{topic_title}: Flow Regimes, Reynolds Number & Boundary Layers",
             "Laminar vs turbulent regimes, critical Reynolds thresholds, and viscous boundary layer drag."),
            (f"{topic_title}: Frictional Losses & Dynamic Hydraulic Machinery",
             "Darcy-Weisbach pipe friction, pump performance curves, and suction cavitation diagnosis.")
        ]
    elif arch == "bio":
        concept_defs = [
            (f"{topic_title}: Cellular Structure & Biological Foundations",
             "Cell membrane permeability, organelle compartmentalization, and fundamental anatomical organization."),
            (f"{topic_title}: Metabolic Pathways & Physiological Regulation",
             "Enzyme-catalyzed reactions, biochemical transformation mechanisms, and metabolic energy balance."),
            (f"{topic_title}: Homeostatic Balance & Environmental Limits",
             "Negative feedback loops, osmotic and thermal equilibrium, and physiological tolerance limits."),
            (f"{topic_title}: Diagnostic Assays & Empirical Evaluation",
             "Specific biological assays, identifying structural adaptations, and diagnostic problem solving.")
        ]
    elif arch == "chem":
        concept_defs = [
            (f"{topic_title}: Atomic Structure & Chemical Bonding",
             "Valence electron configurations, ionic vs covalent bonding forces, and molecular geometries."),
            (f"{topic_title}: Reaction Kinetics & Collision Dynamics",
             "Activation energy barriers, molecular collision frequency, and catalytic acceleration mechanisms."),
            (f"{topic_title}: Dynamic Equilibrium & Systemic Constraints",
             "Reversible reaction dynamics, Le Chatelier's equilibrium shifts, and concentration-temperature balance."),
            (f"{topic_title}: Chemical Analysis & Diagnostic Evaluation",
             "Titration protocols, spectrophotometric assays, and troubleshooting impure chemical yields.")
        ]
    elif arch == "physics":
        concept_defs = [
            (f"{topic_title}: Fundamental Laws & Conservation Principles",
             "Newton's laws of motion, conservation of momentum and energy, and invariant physical reference frames."),
            (f"{topic_title}: Dynamic Forces & Field Interactions",
             "Gravitational, electromagnetic, and contact forces governing trajectories and potential fields."),
            (f"{topic_title}: Energy Transformations & Boundary Conditions",
             "Mechanical energy conversion, wave propagation boundaries, and thermodynamic entropy limits."),
            (f"{topic_title}: Empirical Diagnostics & Measurement Analysis",
             "Experimental uncertainty propagation, systematic vs random error tracing, and sensor calibration.")
        ]
    elif arch == "tech":
        concept_defs = [
            (f"{topic_title}: Core Architecture & Data Structures",
             "Memory layout, spatial data structures, algorithmic complexity, and asymptotic efficiency bounds."),
            (f"{topic_title}: Algorithmic Logic & Execution Flow",
             "Conditional branch resolution, iterative vs recursive transformations, and state transition graphs."),
            (f"{topic_title}: Concurrency, Latency & Capacity Limits",
             "Thread synchronization, race condition prevention, deadlock avoidance, and network throughput boundaries."),
            (f"{topic_title}: System Troubleshooting & Fault Isolation",
             "Systematic debugging, stack trace analysis, memory leak isolation, and edge-case handling.")
        ]
    elif arch == "agri":
        concept_defs = [
            (f"{topic_title}: Soil Nutrition & Root Uptake Physiology",
             "Essential macronutrients, soil pH bioavailability, cation exchange, and osmotic root absorption."),
            (f"{topic_title}: Plant Growth & Propagation Mechanisms",
             "Photosynthetic carbon fixation, transpiration dynamics, cambial graft union, and plant hormones."),
            (f"{topic_title}: Pest Vectors & Environmental Constraints",
             "Integrated pest management (IPM), economic injury thresholds, pathogen transmission, and drought."),
            (f"{topic_title}: Harvest Quality & Diagnostic Remediation",
             "Ethylene-mediated fruit ripening, post-harvest respiration control, and foliar deficiency diagnosis.")
        ]
    elif arch == "civil_mech":
        concept_defs = [
            (f"{topic_title}: Stress-Strain & Material Elasticity",
             "Hooke's law, elastic modulus, shear stress, and fundamental mechanical load response."),
            (f"{topic_title}: Structural Equilibrium & Force Resolution",
             "Statics equations, free-body diagram equilibrium, shear force, and bending moment distributions."),
            (f"{topic_title}: Yield Limits, Buckling & Safety Margins",
             "Euler buckling criteria, factor of safety conventions, and plastic deformation thresholds."),
            (f"{topic_title}: Non-Destructive Testing & Failure Analysis",
             "Fatigue crack propagation, ultrasonic defect detection, and structural integrity diagnosis.")
        ]
    elif arch == "math":
        concept_defs = [
            (f"{topic_title}: Foundational Definitions & Axiomatic Baselines",
             "Formal definitions, domain and range constraints, and structural baseline conditions."),
            (f"{topic_title}: Functional Transformations & Analytical Operations",
             "Derivatives as instantaneous rates of change, integrals as continuous sums, and linear mapping."),
            (f"{topic_title}: Boundary Invariants, Convergence & Limits",
             "Asymptotic behavior, series convergence tests, matrix singularity thresholds, and domain limits."),
            (f"{topic_title}: Analytical Proofs & Edge-Case Verification",
             "Rigorous deductive verification, proof by counterexample, and resolving extraneous solutions.")
        ]
    elif arch == "econ":
        concept_defs = [
            (f"{topic_title}: Scarcity, Consumer Choice & Opportunity Cost",
             "Resource constraints, marginal utility trade-offs, and baseline budget allocation decisions."),
            (f"{topic_title}: Supply, Demand & Market Price Formation",
             "Price mechanism dynamics, price elasticity of demand, and competitive market clearing equilibrium."),
            (f"{topic_title}: Market Distortions & Regulatory Boundaries",
             "Externalities, price ceilings and floors, deadweight welfare losses, and monopoly pricing power."),
            (f"{topic_title}: Economic Diagnostics & Policy Evaluation",
             "Macroeconomic indicators (inflation, GDP growth), monetary policy adjustments, and empirical market data.")
        ]
    elif arch == "law":
        concept_defs = [
            (f"{topic_title}: Constitutional Foundations & Statutory Authority",
             "Sovereign legal authority, separation of constitutional powers, and supremacy of statutory enactments."),
            (f"{topic_title}: Statutory Construction & Judicial Precedent",
             "Doctrine of stare decisis, canons of statutory interpretation, and reconciling conflicting case holdings."),
            (f"{topic_title}: Due Process & Jurisdictional Boundaries",
             "Procedural fairness standards, constitutional scrutiny tests, and regulatory jurisdictional limits."),
            (f"{topic_title}: Applied Case Analysis & Legal Remedies",
             "Applying legal rules to fact patterns, burden of proof standards, and crafting equitable remedies.")
        ]
    elif arch == "history":
        concept_defs = [
            (f"{topic_title}: Preconditions, Social Strata & Baseline Context",
             "Underlying socioeconomic conditions, demographic pressures, and institutional structures preceding events."),
            (f"{topic_title}: Catalysts, Mobilization & Pivotal Decisions",
             "Immediate trigger events, strategic leadership decisions, and competing ideological factions."),
            (f"{topic_title}: Institutional Reforms & Systemic Consequences",
             "Long-term structural transformations, redistribution of political power, and enduring legal legacies."),
            (f"{topic_title}: Historical Evidence & Archival Corroboration",
             "Cross-referencing conflicting primary source accounts, identifying witness biases, and empirical evaluation.")
        ]
    elif arch == "arts":
        concept_defs = [
            (f"{topic_title}: Foundational Elements, Tonal Scales & Meters",
             "Pitch intervals, scale structures, rhythmic notation, and baseline structural units of composition."),
            (f"{topic_title}: Harmonic Progressions & Narrative Movement",
             "Chord syntax, functional harmonic movement, and dynamic narrative pacing across structural phrases."),
            (f"{topic_title}: Aesthetic Tension, Dissonance & Resolution",
             "Interplay of tension and consonance, motif variation, and structural balance across contrasting themes."),
            (f"{topic_title}: Critical Analysis & Compositional Troubleshooting",
             "Diagnosing faulty voice-leading cadences, stylistic critique, and resolving structural inconsistencies.")
        ]
    else:  # UNIVERSAL MULTI-DISCIPLINARY FRAMEWORK
        concept_defs = [
            (f"{topic_title}: Foundational Principles & Core Taxonomy",
             f"Baseline definitions, structural criteria, and the foundational taxonomy of {topic_title}."),
            (f"{topic_title}: Governing Mechanisms & Causal Interactions",
             f"Direct causal pathways, interaction dynamics, and governing processes in {topic_title}."),
            (f"{topic_title}: Boundary Invariants & Systemic Trade-offs",
             f"Essential constraints, conservation principles, and boundary thresholds in {topic_title}."),
            (f"{topic_title}: Diagnostic Evaluation & Empirical Verification",
             f"Systematic problem solving, distinguishing symptoms from causes, and practical verification in {topic_title}.")
        ]

    # Build concepts & concept guides
    concepts = []
    concept_guides = []
    for i, (cname, cdesc) in enumerate(concept_defs):
        cid = f"{domain_id}_c{i+1}"
        prereqs = [concepts[i-1]["id"]] if i > 0 else []
        concepts.append({
            "id": cid,
            "domain_id": domain_id,
            "name": cname,
            "slug": re.sub(r'[^a-zA-Z0-9]+', '_', cname.lower()).strip('_')[:28],
            "category": cat,
            "description": cdesc,
            "prerequisites": prereqs,
            "order_index": i + 1
        })
        concept_guides.append({
            "concept_id": cid,
            "domain_id": domain_id,
            "name": cname,
            "core_idea": f"Core principles, governing laws, and operational methods of {cname}.",
            "example": f"Practical application scenario demonstrating the principles of {cname}.",
            "common_mistake": f"Common error: bypassing foundational prerequisites or confusing symptoms with causes in {cname}.",
            "key_takeaway": f"Mastering {cname} is essential for accurate problem solving and rigorous diagnosis in {topic_title}."
        })

    # Build 4 precise cognitive misconceptions
    misconceptions = []
    misc_titles = [
        ("Foundational Premise Inversion", "Assuming advanced operational rules apply without verifying initial baseline definitions."),
        ("Directional Causality Trap", "Confusing active driving mechanisms with passive secondary correlations or symptoms."),
        ("Boundary Limit Neglect", "Failing to account for critical capacity limits or non-linear behavior beyond thresholds."),
        ("Symptom vs. Root Cause Confusion", "Addressing surface-level symptoms rather than diagnosing the underlying causal malfunction.")
    ]
    for i, (mtitle, mdesc) in enumerate(misc_titles):
        mid = f"MISC_{domain_id.upper()}_{i+1}"
        c = concepts[i]
        c_short = c["name"].split(":", 1)[1].strip() if ":" in c["name"] else c["name"]
        misconceptions.append({
            "id": mid,
            "domain_id": domain_id,
            "code": f"M-GEN-{i+1:02d}",
            "concept_id": c["id"],
            "name": f"{mtitle} in {c_short}",
            "description": f"{mdesc} Occurs frequently when analyzing {c_short}.",
            "remediation": f"Review baseline definitions and trace causal dependencies carefully in {c_short}."
        })

    # 3. Generate questions for the detected archetype
    raw_questions = []

    for c_idx in range(4):
        c = concepts[c_idx]
        cid = c["id"]
        misc_id = misconceptions[c_idx]["id"]
        c_label = c["name"].split(":", 1)[1].strip() if ":" in c["name"] else c["name"]

        # Questions per archetype
        if arch == "graphics":
            if c_idx == 0:
                q_b = {
                    "text": f"In {topic_title}, which three mutually perpendicular reference planes construct principal orthographic projections?",
                    "a": "Horizontal Plane (HP), Vertical Plane (VP), and Profile Plane (PP).",
                    "b": "Diagonal Plane, Incline Plane, and Polar Coordinate Axis.",
                    "c": "Surface Plane, Boundary Plane, and Tangent Coordinate Axis.",
                    "d": "Central Plane, Auxiliary Plane, and Linear Reference Grid.",
                    "expl": "Orthographic projection uses Horizontal (top), Vertical (front), and Profile (side) planes."
                }
                q_c = {
                    "text": f"In {topic_title}, why must the top view always align directly in vertical alignment with the front view?",
                    "a": "Because both views share the exact same horizontal width dimensions along common projection rays.",
                    "b": "Because drafting rules require all drawing views to be enclosed within a single rectangular border.",
                    "c": "Because placing views in random locations eliminates the need to measure component depth dimensions.",
                    "d": "Because horizontal view alignment is only necessary when creating freehand artistic sketches.",
                    "expl": "In orthographic projection, projector lines connecting front and top views share identical horizontal width coordinates.",
                    "prompt": "Why is vertical alignment between front and top views mandatory in orthographic drafting?",
                    "probe_opts": {
                        "A": "Because projection rays pass perpendicularly through the object, ensuring horizontal coordinates remain identical.",
                        "B": "Because drawing sheets cannot physically support non-aligned view placements.",
                        "C": "Because auxiliary views are legally required to occupy the lower-left corner of all blueprints.",
                        "D": "Because rotating views independently makes computer storage of CAD files impossible."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a drafter projects an inclined planar surface that slopes at 45 degrees to the horizontal plane. What is observed in the top view?",
                    "a": "The inclined surface appears foreshortened in length rather than its true physical shape.",
                    "b": "The inclined surface appears in its true physical shape and full manufactured dimensions.",
                    "c": "The inclined surface appears as a single dimensionless point on the horizontal plane.",
                    "d": "The inclined surface completely disappears from the top orthographic projection.",
                    "expl": "Any surface inclined to a projection plane projects with foreshortened dimensions rather than its true shape.",
                    "prompt": "Why does an inclined surface appear foreshortened on a principal projection plane?",
                    "probe_opts": {
                        "A": "Because projection rays intersect the angled plane obliquely rather than perpendicular to its surface.",
                        "B": "Because projection planes absorb optical light waves that diminish true physical object dimensions.",
                        "C": "Because drafting scales automatically shrink any feature drawn on the horizontal plane.",
                        "D": "Because inclined surfaces lose physical length whenever placed in an orthographic drafting environment."
                    }
                }
            elif c_idx == 1:
                q_b = {
                    "text": f"In {topic_title}, at what angle are the two receding horizontal axes drawn relative to the baseline in an isometric drawing?",
                    "a": "At 30 degrees to the horizontal line on both sides of the vertical axis.",
                    "b": "At 45 degrees to the horizontal line on both sides of the vertical axis.",
                    "c": "At 60 degrees to the horizontal line on both sides of the vertical axis.",
                    "d": "At 90 degrees to the horizontal line on both sides of the vertical axis.",
                    "expl": "Isometric drawing axes consist of one vertical axis and two receding axes inclined at 30 degrees to the horizontal."
                }
                q_c = {
                    "text": f"In {topic_title}, why do circular holes appear as ellipses rather than true circles when drawn on isometric planes?",
                    "a": "Because the circular perimeter is projected obliquely across foreshortened isometric axes.",
                    "b": "Because cylindrical holes physically deform when viewed from an angled perspective.",
                    "c": "Because drafting compasses cannot construct circles on standard drawing sheets.",
                    "d": "Because isometric projection completely eliminates curvature from geometric drafting.",
                    "expl": "A circle inscribed in an isometric square projects as an ellipse due to equal 30-degree axis foreshortening.",
                    "prompt": "Why do true circles project as ellipses in isometric views?",
                    "probe_opts": {
                        "A": "Because viewing the circle at an angle foreshortens one diameter while preserving the conjugate diameter.",
                        "B": "Because isometric planes are physically curved rather than flat drawing surfaces.",
                        "C": "Because drawing standards require all curves to be approximated by straight lines.",
                        "D": "Because isometric scales only function when measuring rectangular prisms."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a draftsman needs to draw a non-isometric inclined pyramid edge in an isometric projection. Which procedure is correct?",
                    "a": "Enclose the object in an isometric box, locate the endpoint coordinates, and connect them.",
                    "b": "Measure the angled line directly with an ordinary linear scale along its inclined orientation.",
                    "c": "Rotate the drawing sheet by 45 degrees and draw the inclined line as a vertical axis.",
                    "d": "Scale the angled line down by fifty percent and align it parallel to the isometric baseline.",
                    "expl": "Non-isometric lines do not foreshorten equally; they must be drawn by plotting endpoint coordinates using the box method.",
                    "prompt": "Why cannot non-isometric lines be measured directly with an isometric scale?",
                    "probe_opts": {
                        "A": "Because only lines parallel to the three principal isometric axes undergo uniform foreshortening.",
                        "B": "Because isometric scales are legally prohibited from measuring non-horizontal lines.",
                        "C": "Because non-isometric lines expand infinitely when transferred onto an isometric plane.",
                        "D": "Because drafting tools cannot measure dimensions that exceed ten centimeters in length."
                    }
                }
            elif c_idx == 2:
                q_b = {
                    "text": f"In {topic_title}, which drafting convention indicates solid material that has been sliced by a cutting plane in a sectional view?",
                    "a": "Thin continuous parallel hatching lines drawn at an angle of 45 degrees.",
                    "b": "Thick solid black shading covering the entire cross-sectional surface.",
                    "c": "Dashed hidden lines spaced at random intervals across the sliced plane.",
                    "d": "Alternating long and short chain lines drawn across the outer perimeter.",
                    "expl": "Standard sectional hatching uses continuous thin lines inclined at 45 degrees to the main view outline."
                }
                q_c = {
                    "text": f"In {topic_title}, why are standard fasteners such as solid shafts, bolts, keys, and ribs left unhatched when sliced longitudinally?",
                    "a": "Because hatching them gives a false impression of internal thickness and obscures functional assembly clarity.",
                    "b": "Because standard fasteners are made of non-metallic materials that cannot be hatched.",
                    "c": "Because cutting planes are physically unable to slice through hardened steel components.",
                    "d": "Because unhatched components reduce ink usage on commercial manufacturing blueprints.",
                    "expl": "Engineering drawing standards leave longitudinal cuts of solid shafts, bolts, ribs, and pins unhatched to preserve clarity.",
                    "prompt": "Why do drafting standards prohibit hatching longitudinal cuts of solid pins and shafts?",
                    "probe_opts": {
                        "A": "Because hatching solid cylindrical shafts makes them appear hollow, confusing manufacturing technicians.",
                        "B": "Because standard fasteners do not possess cross-sectional thickness.",
                        "C": "Because sectional hatching can only be applied to plastic or rubber components.",
                        "D": "Because cutting planes automatically bounce off cylindrical steel surfaces."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a component is completely symmetrical and possesses intricate external contours and internal stepped bores. Which sectional view is best?",
                    "a": "A half-section view, showing one half in exterior elevation and the other half in interior section.",
                    "b": "A revolved section placed entirely outside the boundaries of the principal projection view.",
                    "c": "A broken-out section that removes ninety percent of the external surface features.",
                    "d": "An auxiliary section drawn perpendicular to the baseline ground reference plane.",
                    "expl": "A half-section view is the ideal standard for symmetrical components because it reveals both internal and external features simultaneously.",
                    "prompt": "Why is a half-section particularly effective for symmetrical mechanical housings?",
                    "probe_opts": {
                        "A": "It simultaneously displays internal cavity geometry and external surface features on a single view.",
                        "B": "It cuts drafting time in half by requiring only half of the projection rays to be plotted.",
                        "C": "It eliminates the requirement to specify manufacturing tolerances on mating surfaces.",
                        "D": "It replaces orthographic front and top views with a single perspective artistic sketch."
                    }
                }
            else:  # c_idx == 3
                q_b = {
                    "text": f"In {topic_title}, what distinguishes aligned dimensioning from unidirectional dimensioning on engineering drawings?",
                    "a": "Aligned dimensions follow dimension lines; unidirectional dimensions are all read horizontally from the bottom.",
                    "b": "Aligned dimensions use metric units; unidirectional dimensions strictly use imperial units.",
                    "c": "Aligned dimensions are placed only on hidden lines; unidirectional dimensions appear on outlines.",
                    "d": "Aligned dimensions are written in cursive; unidirectional dimensions use uppercase block text.",
                    "expl": "In aligned dimensioning, text runs parallel to dimension lines; in unidirectional, all text reads horizontally from the drawing bottom."
                }
                q_c = {
                    "text": f"In {topic_title}, what characterizes a clearance fit between a manufactured shaft and hole across all tolerance limits?",
                    "a": "The minimum hole diameter is strictly larger than the maximum permissible shaft diameter.",
                    "b": "The shaft diameter is identical to the hole diameter with zero dimensional variation.",
                    "c": "The minimum shaft diameter exceeds the maximum hole diameter by at least five millimeters.",
                    "d": "The shaft and hole are welded together permanently without any assembly gap.",
                    "expl": "A clearance fit guarantees a positive gap between mating parts under all allowable manufacturing tolerance conditions.",
                    "prompt": "Why does a clearance fit guarantee free rotational or sliding movement under all conditions?",
                    "probe_opts": {
                        "A": "Because the maximum material condition of the shaft is smaller than the maximum material condition of the hole.",
                        "B": "Because clearance fits eliminate all manufacturing tolerances and friction forces.",
                        "C": "Because shafts in clearance fits expand when subjected to frictional heat.",
                        "D": "Because mating parts in clearance fits do not touch the surrounding atmosphere."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a pin of 25 mm with tolerance ±0.02 mm fails to enter a hole of 25 mm with tolerance +0.04/+0.01 mm. What caused this assembly failure?",
                    "a": "The pin was manufactured at its upper limit (25.02 mm), exceeding the hole's minimum size (25.01 mm).",
                    "b": "The hole contracted due to negative thermal expansion while resting in ambient room conditions.",
                    "c": "Dimensional tolerances are theoretical labels that have zero relevance during physical assembly.",
                    "d": "The pin accumulated additional metal atoms spontaneously during transport between workbenches.",
                    "expl": "When tolerance limits overlap, worst-case boundary conditions produce interference (pin 25.02 mm > hole 25.01 mm).",
                    "prompt": "Why did the manufactured pin jam inside the hole despite both parts meeting individual blueprint specs?",
                    "probe_opts": {
                        "A": "Because the tolerance zones overlap, creating an interference condition under worst-case boundary limits.",
                        "B": "Because cylindrical holes always contract by ten percent immediately following machining operations.",
                        "C": "Because manufacturing blueprints only guarantee fit when parts are assembled in a vacuum chamber.",
                        "D": "Because tolerance ranges only apply to the overall length of the pin rather than its diameter."
                    }
                }

        elif arch == "fluid":
            if c_idx == 0:
                q_b = {
                    "text": f"In {topic_title}, which core fluid property describes a fluid's internal resistance to shear flow under applied force?",
                    "a": "Dynamic viscosity, which relates shear stress linearly to velocity gradient in Newtonian fluids.",
                    "b": "Specific gravity, which measures how rapidly fluid molecules disintegrate into vapor.",
                    "c": "Surface tension, which causes fluids to expand infinitely across open containers.",
                    "d": "Thermal conductivity, which eliminates all internal frictional drag in moving liquids.",
                    "expl": "Viscosity measures fluid shear resistance, defined by Newton's law of viscosity (tau = mu * du/dy)."
                }
                q_c = {
                    "text": f"In {topic_title}, why does static fluid pressure at depth act equally in all directions at a single point (Pascal's law)?",
                    "a": "Because fluids cannot support static shear stresses and transmit normal compressive forces isotropically.",
                    "b": "Because gravitational attraction only pulls downward on fluid surfaces without affecting depth.",
                    "c": "Because fluid pressure drops to absolute zero whenever a liquid comes to rest.",
                    "d": "Because atmospheric pressure cancels all hydrostatic pressures in liquid reservoirs.",
                    "expl": "At rest, fluids have no shear stress; normal stresses in all directions are identical, which is Pascal's law.",
                    "prompt": "Why must pressure at a point in a static fluid be isotropic in all directions?",
                    "probe_opts": {
                        "A": "Because an infinitesimal fluid element at equilibrium has zero shear stresses, requiring equal normal forces to balance.",
                        "B": "Because liquids are composed of spherical atoms that only bounce horizontally.",
                        "C": "Because gravity only affects solid objects and has zero influence on fluids.",
                        "D": "Because static fluids lose all mass and density until motion resumes."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a U-tube manometer measures pressure difference between two points in a water pipe. What determines fluid column height difference?",
                    "a": "The static pressure difference divided by the specific weight difference of the fluids.",
                    "b": "The total volume of manometer fluid regardless of fluid density or pipe pressure.",
                    "c": "The atmospheric room temperature regardless of fluid density or velocity.",
                    "d": "The diameter of the glass manometer tube regardless of static pressure head.",
                    "expl": "Manometer fluid differential height is governed by hydrostatic balance: delta_P = delta_rho * g * delta_h.",
                    "prompt": "Why do fluid levels in a U-tube manometer remain stable during steady pressure measurement?",
                    "probe_opts": {
                        "A": "Because hydrostatic pressure at any continuous horizontal datum line within the same fluid must be equal.",
                        "B": "Because glass manometer tubes exert magnetic forces that lock liquid columns into fixed heights.",
                        "C": "Because liquids in manometers lose all weight and density once enclosed inside glass tubing.",
                        "D": "Because moving fluids inside pipelines exert zero static pressure on adjoining pressure taps."
                    }
                }
            elif c_idx == 1:
                q_b = {
                    "text": f"In {topic_title}, which fundamental conservation law is mathematically expressed by the continuity equation (A1*v1 = A2*v2)?",
                    "a": "Conservation of mass, stating that mass flow rate remains constant in steady incompressible flow.",
                    "b": "Conservation of momentum, stating that fluid particles accelerate without applied forces.",
                    "c": "Conservation of thermal energy, stating that fluid temperature never fluctuates during flow.",
                    "d": "Conservation of electrical charge, stating that neutral fluids generate magnetic fields.",
                    "expl": "The continuity equation A1*v1 = A2*v2 is the direct mathematical formulation of conservation of mass for incompressible flow."
                }
                q_c = {
                    "text": f"In {topic_title}, why does static pressure decrease when an incompressible fluid speeds up through a pipe constriction (Venturi effect)?",
                    "a": "Because internal pressure energy is converted into kinetic energy to preserve total mechanical energy.",
                    "b": "Because fluid mass is destroyed as liquid molecules pass through the narrow constriction.",
                    "c": "Because pipe walls absorb fluid energy and convert it into nuclear radiation.",
                    "d": "Because friction with pipe walls completely stops fluid movement inside narrow nozzles.",
                    "expl": "Bernoulli's principle states that along a streamline, an increase in velocity (kinetic energy) must be balanced by a decrease in static pressure.",
                    "prompt": "Why does accelerated fluid velocity result in reduced static pressure?",
                    "probe_opts": {
                        "A": "Because conservation of mechanical energy requires static pressure head to drop as velocity head increases.",
                        "B": "Because faster fluids lose all internal mass and become light gases.",
                        "C": "Because pipe friction absorbs fluid pressure and releases it as radio waves.",
                        "D": "Because static pressure only exists when fluids are completely motionless."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, water flows through a horizontal pipe that narrows from 40 cm to 20 cm in diameter. What happens to water velocity and static pressure?",
                    "a": "Velocity increases by a factor of four, and static pressure decreases significantly.",
                    "b": "Velocity decreases by half, and static pressure doubles inside the constriction.",
                    "c": "Velocity and static pressure remain completely identical across both pipe sections.",
                    "d": "Velocity drops to zero, and static pressure rises to infinite magnitude.",
                    "expl": "Area is proportional to diameter squared; halving diameter cuts area to 1/4, quadrupling velocity and dropping pressure.",
                    "prompt": "Why does velocity quadruple when the pipe diameter is reduced by half in incompressible flow?",
                    "probe_opts": {
                        "A": "Because cross-sectional area is proportional to the square of diameter (A = pi*D^2/4), requiring 4x speed for equal mass flow.",
                        "B": "Because narrower pipes generate gravitational acceleration that pushes water molecules four times faster.",
                        "C": "Because fluid density increases fourfold when passing through narrower cross-sectional geometries.",
                        "D": "Because pipe friction accelerates liquids whenever wall contact surface area decreases."
                    }
                }
            elif c_idx == 2:
                q_b = {
                    "text": f"In {topic_title}, which dimensionless parameter is used to predict whether fluid flow in a pipe is laminar or turbulent?",
                    "a": "Reynolds number, which quantifies the ratio of inertial forces to viscous damping forces.",
                    "b": "Froude number, which measures the ratio of electromagnetic force to capillary surface tension.",
                    "c": "Mach number, which compares fluid velocity to the speed of light in vacuum.",
                    "d": "Prandtl number, which measures the chemical reaction speed between fluid molecules.",
                    "expl": "The Reynolds number (Re = rho*v*D/mu) determines flow regime by comparing inertial forces to viscous damping forces."
                }
                q_c = {
                    "text": f"In {topic_title}, why does turbulent pipe flow cause much higher frictional pressure loss than laminar flow at identical flow rates?",
                    "a": "Because chaotic turbulent eddies cause cross-stream momentum exchange and steep velocity gradients at walls.",
                    "b": "Because turbulent fluids freeze along pipe walls and block liquid passage.",
                    "c": "Because laminar flow generates zero friction and experiences zero pressure drop.",
                    "d": "Because turbulent flow causes fluid molecules to escape through solid pipe walls.",
                    "expl": "Turbulence creates intense mixing and chaotic vortex motion, which dissipates mechanical energy through high turbulent shear stress.",
                    "prompt": "Why does cross-stream eddy mixing produce severe energy dissipation in turbulent flows?",
                    "probe_opts": {
                        "A": "Because chaotic macroscopic vortices transfer high-velocity fluid to walls, dramatically steepening shear gradients.",
                        "B": "Because turbulent eddies chemically react with water to form heavy solid minerals.",
                        "C": "Because turbulent fluids generate internal magnetic friction that stops flow.",
                        "D": "Because laminar layers generate negative friction that accelerates fluids."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an oil pipeline operating in laminar flow (Re = 1200) has its pumping flow rate tripled. What happens to the flow regime?",
                    "a": "The Reynolds number increases to 3600, entering the transitional/turbulent flow regime.",
                    "b": "The flow remains permanently laminar because oil viscosity prevents turbulent eddy formation.",
                    "c": "The Reynolds number drops to 400 because faster liquids experience lower internal inertia.",
                    "d": "The oil separates into gas and solid phases due to increased pumping velocity.",
                    "expl": "Tripling velocity triples Re (from 1200 to 3600), pushing the flow past the laminar boundary (Re ~ 2000) into turbulence.",
                    "prompt": "Why does tripling flow velocity cause the fluid flow to transition into turbulence?",
                    "probe_opts": {
                        "A": "Because inertial forces scale directly with velocity and overcome the stabilizing damping effect of viscous forces.",
                        "B": "Because faster fluids lose all internal viscosity and become completely frictionless substances.",
                        "C": "Because pipe walls contract inward when fluid velocity increases beyond critical thresholds.",
                        "D": "Because higher flow rates cause gravity to act horizontally along the pipeline axis."
                    }
                }
            else:  # c_idx == 3
                q_b = {
                    "text": f"In {topic_title}, which equation is universally used to calculate major frictional head loss in circular pipe flow?",
                    "a": "The Darcy-Weisbach equation, relating head loss to friction factor, pipe length, diameter, and velocity.",
                    "b": "The Ideal Gas equation, relating pressure and volume to absolute Kelvin temperature.",
                    "c": "The Pythagorean theorem, calculating geometric distance across perpendicular coordinates.",
                    "d": "The Coulomb equation, calculating electrostatic attraction between opposing electrical charges.",
                    "expl": "The Darcy-Weisbach equation (hf = f * (L/D) * (v^2 / 2g)) calculates frictional pipe head loss."
                }
                q_c = {
                    "text": f"In {topic_title}, what is the physical root cause of pump cavitation in hydraulic pumping systems?",
                    "a": "Local static pressure dropping below the liquid saturation vapor pressure, forming vapor bubbles that collapse violently.",
                    "b": "Air entering through exhaust valves and cooling pump impellers to sub-zero temperatures.",
                    "c": "Electrical currents from the motor melting the metal casing of the pump.",
                    "d": "Solid sand particles dissolving in water and neutralizing fluid viscosity.",
                    "expl": "Cavitation occurs when suction pressure drops below vapor pressure (Pv), forming bubbles that implode violently in high-pressure regions.",
                    "prompt": "Why does dropping below vapor pressure trigger destructive cavitation in hydraulic pumps?",
                    "probe_opts": {
                        "A": "Because liquid flashes into vapor pockets that collapse catastrophically when entering higher pressure impeller zones.",
                        "B": "Because water molecules chemically dissolve into oxygen gas and burn the impeller metal.",
                        "C": "Because low pressure causes pipe walls to freeze into brittle ice sheets.",
                        "D": "Because pump motors spin in reverse whenever suction pressure decreases."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a centrifugal pump emits loud rattling noises like pumping gravel, accompanied by severe vibration and head loss. What is the diagnosis?",
                    "a": "Cavitation occurring in the pump impeller due to inadequate Net Positive Suction Head (NPSH).",
                    "b": "The electric motor is running in reverse and converting liquid water into steam.",
                    "c": "The pipeline has developed infinite friction that prevents water molecules from moving.",
                    "d": "The water has lost all surface tension due to excessive discharge valve throttling.",
                    "expl": "Loud rattling noise, vibration, and performance drop are textbook diagnostic symptoms of suction cavitation in centrifugal pumps.",
                    "prompt": "Why does cavitation produce loud rattling noise and severe mechanical pitting damage inside pumps?",
                    "probe_opts": {
                        "A": "Because vapor bubbles collapse violently upon reaching higher pressure zones, generating localized shock waves exceeding 1000 MPa.",
                        "B": "Because gravel and metal fragments are spontaneously synthesized inside the pump impeller eye.",
                        "C": "Because the pump motor vibrates against the concrete foundation when pumping cold fluids.",
                        "D": "Because water molecules chemically react with stainless steel impellers to release hydrogen gas."
                    }
                }

        elif arch == "bio":
            if c_idx == 0:
                q_b = {
                    "text": f"In {topic_title}, which structural component regulates selective passage of nutrients and ions into living cells?",
                    "a": "The phospholipid bilayer membrane embedded with selective transport proteins and channel complexes.",
                    "b": "A solid calcium carbonate shell that permanently isolates the cell from all external fluids.",
                    "c": "A magnetic mineral lattice that repels all dissolved organic molecules unconditionally.",
                    "d": "An impermeable wax layer that prevents any exchange of moisture, gases, or electrolytes.",
                    "expl": "The selectively permeable plasma membrane controls cellular influx and efflux using embedded protein channels and pumps."
                }
                q_c = {
                    "text": f"In {topic_title}, why do specialized mitochondria maintain an internal electrochemical proton gradient across their inner membrane?",
                    "a": "To drive chemiosmotic ATP synthase rotation, producing adenosine triphosphate (ATP) for cellular work.",
                    "b": "To generate high-voltage electricity that electrocutes invading bacterial microorganisms directly.",
                    "c": "To convert ambient liquid water into solid structural cellulose fibers inside animal tissues.",
                    "d": "To eliminate the need for organic carbon nutrients and oxygen in cellular respiration.",
                    "expl": "Proton pumping into the intermembrane space establishes a proton-motive force that powers ATP synthase (chemiosmosis).",
                    "prompt": "Why is the inner mitochondrial membrane's selective proton impermeability essential for ATP generation?",
                    "probe_opts": {
                        "A": "Because uncontrolled proton leakage would dissipate the proton-motive force without driving ATP synthase rotation.",
                        "B": "Because protons are toxic chemicals that dissolve cellular organelles upon contact.",
                        "C": "Because mitochondria only function when their internal pH reaches absolute zero.",
                        "D": "Because ATP synthase requires complete electrical insulation from all chemical ions."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a biologist treats tissue cells with an uncoupling agent that renders the inner mitochondrial membrane permeable to protons. What occurs?",
                    "a": "Oxygen consumption continues, but ATP synthesis collapses while metabolic energy is dissipated as heat.",
                    "b": "ATP synthesis increases tenfold while cellular oxygen consumption drops to zero.",
                    "c": "The cell membrane immediately turns into solid bone tissue within seconds.",
                    "d": "The cell ceases all metabolic activity and transforms into an inorganic mineral crystal.",
                    "expl": "Uncouplers allow protons to bypass ATP synthase, destroying the proton gradient; fuel oxidation continues but releases heat instead of ATP.",
                    "prompt": "Why does dissipating the mitochondrial proton gradient without ATP synthesis generate excessive body heat?",
                    "probe_opts": {
                        "A": "Because the free energy released from nutrient oxidation cannot be captured as chemical bonds and is lost as thermal energy.",
                        "B": "Because uncoupling agents ignite chemical fires within the lipid bilayer.",
                        "C": "Because oxygen molecules explode when coming into contact with cellular cytoplasm.",
                        "D": "Because mitochondria reverse their cooling cycle and absorb ambient refrigeration."
                    }
                }
            elif c_idx == 1:
                q_b = {
                    "text": f"In {topic_title}, how do biological enzymes accelerate metabolic chemical reactions inside living organisms?",
                    "a": "By binding substrates at active sites and lowering the activation energy barrier for transition states.",
                    "b": "By raising cellular temperature to several hundred degrees Celsius during reaction catalysis.",
                    "c": "By altering the overall thermodynamic equilibrium constant (Keq) to favor non-spontaneous products.",
                    "d": "By converting all surrounding water molecules into pure reactive hydrogen gas.",
                    "expl": "Enzymes are biological catalysts that lower activation energy without shifting the reaction's equilibrium constant."
                }
                q_c = {
                    "text": f"In {topic_title}, why is allosteric feedback inhibition essential for regulating metabolic synthesis pathways?",
                    "a": "It prevents wasteful overproduction of end-products by inhibiting early pathway enzymes when product levels are sufficient.",
                    "b": "It destroys all cellular enzymes permanently as soon as a single reaction is completed.",
                    "c": "It forces metabolic reactions to run in reverse, converting complex proteins back into carbon dioxide.",
                    "d": "It eliminates the need for genetic transcription and translation of metabolic proteins.",
                    "expl": "Feedback inhibition is an efficient homeostatic control where the pathway's final product allosterically inhibits the commitment-step enzyme.",
                    "prompt": "Why is allosteric regulation advantageous over competitive active-site inhibition in metabolic pathways?",
                    "probe_opts": {
                        "A": "Because the end-product can regulate the enzyme without structurally mimicking the initial substrate molecule.",
                        "B": "Because allosteric inhibitors permanently denature the enzyme, preventing any future activity.",
                        "C": "Because competitive inhibitors require higher operating temperatures than living cells can survive.",
                        "D": "Because allosteric enzymes operate independently of cellular gene regulation mechanisms."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an enzymatic assay shows that increasing substrate concentration overcomes the effect of an inhibitor, restoring Vmax. What inhibitor type is this?",
                    "a": "A competitive inhibitor that reversibly binds to the enzyme's catalytic active site.",
                    "b": "An irreversible covalent poison that permanently destroys the enzyme's tertiary structure.",
                    "c": "A non-competitive inhibitor that reduces Vmax regardless of substrate concentration.",
                    "d": "An uncompetitive inhibitor that binds exclusively to the enzyme-substrate complex.",
                    "expl": "Competitive inhibitors compete with substrate for the active site; high substrate concentrations outcompete the inhibitor and reach full Vmax.",
                    "prompt": "Why can high substrate concentration overcome competitive inhibition but not non-competitive inhibition?",
                    "probe_opts": {
                        "A": "Because substrate and competitive inhibitor compete for the same active site, whereas non-competitive inhibitors bind elsewhere.",
                        "B": "Because competitive inhibitors chemically dissolve whenever exposed to water molecules.",
                        "C": "Because non-competitive inhibitors increase the number of available active sites on the enzyme.",
                        "D": "Because substrate molecules only react with enzymes when inhibitors are absent from the entire room."
                    }
                }
            elif c_idx == 2:
                q_b = {
                    "text": f"In {topic_title}, which physiological mechanism maintains internal stability when external environmental conditions fluctuate?",
                    "a": "Negative feedback loops that sense deviations from a homeostatic set-point and trigger counteractive responses.",
                    "b": "Positive feedback cascades that perpetually amplify all environmental disturbances without limit.",
                    "c": "Immediate permanent cessation of all metabolic processes until external variables return to normal.",
                    "d": "Random metabolic mutations that alter the organism's genetic code every few hours.",
                    "expl": "Homeostasis relies on negative feedback loops (sensor, integrator, effector) that counteract deviations to maintain set-points."
                }
                q_c = {
                    "text": f"In {topic_title}, what occurs to animal red blood cells placed into a severely hypotonic (low solute) aqueous solution?",
                    "a": "Water rushes into the cells down its osmotic potential gradient, causing swelling and osmotic lysis (bursting).",
                    "b": "Water rushes out of the cells, causing extreme crenation and shriveling of the cellular membrane.",
                    "c": "The cells spontaneously develop rigid cellulose cell walls to resist internal hydrostatic pressure.",
                    "d": "The cells absorb salt from the ambient water and transform into photosynthetic plant cells.",
                    "expl": "Animal cells lack rigid cell walls; in hypotonic environments, net water influx causes them to swell and burst (lysis).",
                    "prompt": "Why do plant cells tolerate hypotonic environments without bursting, whereas animal cells lyse?",
                    "probe_opts": {
                        "A": "Because rigid peptidoglycan/cellulose cell walls exert turgor pressure that counteracts osmotic water influx.",
                        "B": "Because plant cells have active vacuum pumps that expel all internal water molecules.",
                        "C": "Because animal cell membranes are permeable to all proteins and dissolved minerals.",
                        "D": "Because plant cells do not contain cytoplasm or intracellular solute molecules."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an investigator tests an organism exposed to prolonged extreme heat and observes sudden cellular dysfunction. What molecular change caused this?",
                    "a": "Thermal denaturation of proteins, disrupting tertiary hydrogen bonds and inactivating metabolic enzymes.",
                    "b": "Cellular DNA spontaneously converting into atmospheric nitrogen gas.",
                    "c": "The cell membrane solidifying into an impenetrable block of crystalline ice.",
                    "d": "The organism's blood pressure dropping to absolute zero due to loss of gravity.",
                    "expl": "High temperatures disrupt non-covalent bonds (hydrogen, ionic, hydrophobic) maintaining protein tertiary structure, causing denaturation.",
                    "prompt": "Why does thermal denaturation of enzymes lead to rapid systemic biological failure?",
                    "probe_opts": {
                        "A": "Because unfolding the specific 3D conformation of active sites abolishes catalytic activity across essential pathways.",
                        "B": "Because denatured enzymes begin synthesizing toxic radioactive isotopes inside the cytoplasm.",
                        "C": "Because heat causes cellular ribosomes to stop accepting amino acid building blocks.",
                        "D": "Because denatured proteins consume all intracellular ATP through reverse phosphorylation."
                    }
                }
            else:  # c_idx == 3
                q_b = {
                    "text": f"In {topic_title}, which analytical assay uses antibody-antigen binding specificity to quantify target proteins or pathogens?",
                    "a": "Enzyme-Linked Immunosorbent Assay (ELISA), utilizing enzyme-conjugated detection antibodies.",
                    "b": "Gram staining of inorganic metallic alloys to test electrical conductivity.",
                    "c": "Paper chromatography used exclusively to measure planetary atmospheric pressure.",
                    "d": "Simple visual inspection without chemical reagents or optical magnification.",
                    "expl": "ELISA uses specific antibodies coupled with enzymatic colorimetric detection to identify and quantify antigens or antibodies."
                }
                q_c = {
                    "text": f"In {topic_title}, why must biological diagnostic assays include both positive and negative control samples in every test run?",
                    "a": "To verify assay sensitivity and rule out false positives from contamination or false negatives from reagent decay.",
                    "b": "To intentionally double the financial cost and time duration of the clinical laboratory procedure.",
                    "c": "Because diagnostic instruments cannot record readings unless control tubes are physically present in the tray.",
                    "d": "To ensure that all patient test specimens produce positive diagnoses regardless of health status.",
                    "expl": "Controls validate assay integrity: negative controls detect non-specific binding/contamination; positive controls verify reagent reactivity.",
                    "prompt": "Why would an assay without negative controls produce dangerous clinical diagnostic errors?",
                    "probe_opts": {
                        "A": "Because non-specific background binding or reagent contamination could produce false-positive diagnoses.",
                        "B": "Because the assay detection enzyme would be unable to produce any optical color change.",
                        "C": "Because patient antibodies only bind to antigens when negative controls are placed in adjacent wells.",
                        "D": "Because laboratory safety protocols require negative controls to neutralize acidic waste."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a patient sample tests positive on an antibody serology assay but negative on a PCR nucleic acid test. What is the interpretation?",
                    "a": "The patient experienced a past resolved infection and retains circulating antibodies, but has no active replicating pathogen.",
                    "b": "The PCR machine converted the patient's genetic sequence into inorganic plastic fibers.",
                    "c": "The patient's immune system has completely failed to recognize the foreign pathogen.",
                    "d": "The pathogen has integrated into red blood cells where nucleic acids cannot be detected.",
                    "expl": "Antibodies persist for months or years after an infection is cleared; PCR detects active pathogen genetic material during current infection.",
                    "prompt": "Why does PCR nucleic acid testing distinguish active infection from past historical exposure more accurately than serology?",
                    "probe_opts": {
                        "A": "Because PCR amplifies active viral or bacterial genetic material, which disappears shortly after pathogen clearance.",
                        "B": "Because PCR tests only function when the patient has zero circulating immune antibodies.",
                        "C": "Because antibodies are short-lived proteins that degrade within five minutes of exposure.",
                        "D": "Because genetic material can only be isolated from patients who have never been vaccinated."
                    }
                }

        elif arch == "history":
            if c_idx == 0:
                q_b = {
                    "text": f"In {topic_title}, what primary socioeconomic condition formed the baseline precondition for systemic historical transformation?",
                    "a": "Structural fiscal crises, entrenched social stratification, and institutional paralysis within governing bodies.",
                    "b": "Unanimous social harmony with zero economic, legal, or religious grievances among all classes.",
                    "c": "Complete absence of economic trade, taxation systems, or written legal codes across the realm.",
                    "d": "Spontaneous unanimous abdication of all ruling monarchs without underlying socioeconomic pressures.",
                    "expl": "Historical turning points emerge from systemic preconditions: severe fiscal distress, rigid social hierarchy, and institutional failure."
                }
                q_c = {
                    "text": f"In {topic_title}, why do historians analyze underlying institutional structures rather than attributing major events solely to individual leaders?",
                    "a": "Because individual actions are shaped and constrained by broader economic realities, legal frameworks, and class interests.",
                    "b": "Because historical leaders possessed zero personal influence over political or military decisions.",
                    "c": "Because written historical records never mention the names or decisions of individual political figures.",
                    "d": "Because economic forces operate completely independently of any human decision-making.",
                    "expl": "Systemic historical analysis examines how institutional, economic, and demographic conditions channel and constrain individual choices.",
                    "prompt": "Why does structural historical analysis provide deeper explanatory power than the 'Great Man' theory alone?",
                    "probe_opts": {
                        "A": "Because political decisions succeed or fail based on structural material capacity, social alignment, and institutional leverage.",
                        "B": "Because historical leaders were legally required to submit all speeches to modern academic historians.",
                        "C": "Because institutional structures operate without any participation by living human beings.",
                        "D": "Because biographical records from previous centuries are universally classified as fictional literature."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an escalating economic crisis coincides with widespread institutional discontent among urban and rural populations. What historical dynamic unfolds?",
                    "a": "Popular grievances coalesce into organized political demands, forcing institutional reform or revolutionary confrontation.",
                    "b": "All social classes voluntarily surrender their legal rights to preserve existing feudal monopolies.",
                    "c": "Economic grievances dissipate instantly without leaving any documentation in administrative archives.",
                    "d": "The governing authority achieves perpetual stability by ignoring public deficits and food shortages.",
                    "expl": "Unresolved structural deficits and widespread popular distress create revolutionary pressures that compel systemic political reorganization.",
                    "prompt": "Why does the convergence of fiscal crisis and social stratification trigger systemic political confrontation?",
                    "probe_opts": {
                        "A": "Because institutional rigidity prevents peaceful reform, leaving radical political mobilization as the primary avenue for redress.",
                        "B": "Because economic crises automatically eliminate all ideological disagreements among competing factions.",
                        "C": "Because ancient legal codes required popular revolts to occur every twenty-five calendar years.",
                        "D": "Because urban populations always support absolute monarchical authority during times of economic distress."
                    }
                }
            elif c_idx == 1:
                q_b = {
                    "text": f"In {topic_title}, what characterises a critical historical turning point during a period of national or regional transformation?",
                    "a": "A pivotal decision, military clash, or legislative act that irreversibly shifts the balance of political power.",
                    "b": "A prolonged period of total stasis during which zero political or military developments take place.",
                    "c": "A secret agreement that has zero impact on public laws, governance structures, or social relations.",
                    "d": "A routine administrative decree that confirms existing monarchical privileges without opposition.",
                    "expl": "Historical turning points are decisive events that rupture the status quo and establish new trajectories of power."
                }
                q_c = {
                    "text": f"In {topic_title}, why do moderate political factions often struggle to maintain control during acute revolutionary crises?",
                    "a": "Because escalating polarization between reactionary defenders of the old order and radical grass-roots reformers fractures the center.",
                    "b": "Because centrist political groups are constitutionally barred from holding public office during emergencies.",
                    "c": "Because moderate politicians refuse to read written legislation or participate in parliamentary debate.",
                    "d": "Because economic crises only affect radical political groups while sparing the general population.",
                    "expl": "Crisis polarization squeezes the center: concessions satisfy neither counter-revolutionaries seeking restoration nor radicals demanding structural overhaul.",
                    "prompt": "Why do centrist political compromises often collapse during acute revolutionary upheaval?",
                    "probe_opts": {
                        "A": "Because moderate reforms fail to resolve fundamental material distress while alienating traditional elite power bases.",
                        "B": "Because historical actors were legally bound to join extremist political organizations.",
                        "C": "Because moderate political parties were prohibited from publishing newspapers or holding public assemblies.",
                        "D": "Because revolutionary periods automatically double the cost of constitutional governance."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a moderate reform faction attempts to compromise with an entrenched ruling elite during a severe national crisis. What predictable historical tension arises?",
                    "a": "The compromise is rejected by radical grassroots factions demanding structural overhaul, fracturing the reform coalition.",
                    "b": "All competing political parties immediately unite into a single harmonious governing council.",
                    "c": "The public loses all interest in political governance and ceases following national events.",
                    "d": "The entrenched elite voluntarily cedes all property and administrative power without resistance.",
                    "expl": "Moderate compromises during revolutionary crises frequently collapse when grassroots pressure outpaces elite willingness to reform.",
                    "prompt": "Why do centrist political compromises often fail during acute revolutionary crises?",
                    "probe_opts": {
                        "A": "Because moderate solutions fail to resolve the core structural grievances animating popular mobilization while alienating elite defenders of the old order.",
                        "B": "Because historical participants are legally prohibited from supporting moderate political platforms during revolutions.",
                        "C": "Because ruling elites always welcome rapid democratization and voluntary wealth redistribution.",
                        "D": "Because political moderation requires higher financial expenditure than military confrontation."
                    }
                }
            elif c_idx == 2:
                q_b = {
                    "text": f"In {topic_title}, which structural legacy represents the most enduring outcome of systemic institutional reform?",
                    "a": "The codification of unified legal principles, reorganization of administrative power, and redistribution of property rights.",
                    "b": "The immediate restoration of all pre-crisis feudal privileges and aristocratic tax exemptions.",
                    "c": "The permanent prohibition of all future legislative debates, elections, and written statutes.",
                    "d": "The total erasure of all legal documentation, administrative boundaries, and currency systems.",
                    "expl": "Enduring historical legacies manifest as codified legal codes, centralized administrative systems, and transformed social rights."
                }
                q_c = {
                    "text": f"In {topic_title}, why do legal and institutional codifications often outlast the specific regimes that enacted them?",
                    "a": "Because standardized legal equality, property protection, and administrative efficiency provide lasting utility across successive governments.",
                    "b": "Because subsequent governments are constitutionally forbidden from amending or repealing ancient statutes.",
                    "c": "Because written legal codes become sacred religious artifacts that cannot be physically altered.",
                    "d": "Because administrative civil servants refuse to recognize any change in national political leadership.",
                    "expl": "Institutional reforms that streamline administration, establish uniform commercial law, and guarantee basic rights persist because of practical utility.",
                    "prompt": "Why did legal codifications like the Napoleonic Code persist across changing 19th-century regimes?",
                    "probe_opts": {
                        "A": "Because rational legal uniformity, enforceable property rights, and commercial predictability served the economic interests of the rising middle class.",
                        "B": "Because military decrees from fallen emperors remain legally binding under international maritime treaties.",
                        "C": "Because subsequent monarchs were illiterate and unable to draft new statutory legislation.",
                        "D": "Because the original legal parchment was made of indestructible gold foil."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a post-crisis government seeks to stabilize society after years of upheaval while preserving core reforms. Which strategy proves most durable?",
                    "a": "Establishing a centralized legal code that cements equality before the law while reconciling with moderate social institutions.",
                    "b": "Executing all former government officials and burning all national tax and land ownership registries.",
                    "c": "Reinstating all medieval feudal obligations and revoking all civil rights granted during the upheaval.",
                    "d": "Outlawing all commercial trade and returning to an exclusively local agrarian barter economy.",
                    "expl": "Durable post-revolutionary stabilization balances institutional order with the preservation of core civil and legal advancements.",
                    "prompt": "Why does institutional codification provide greater long-term stability than arbitrary executive decree?",
                    "probe_opts": {
                        "A": "Because predictable, codified laws establish widespread institutional legitimacy, economic certainty, and enforceable civil expectations.",
                        "B": "Because written legal codes eliminate the need for judges, lawyers, or law enforcement agencies.",
                        "C": "Because executive decrees are physically unable to be communicated beyond the capital city.",
                        "D": "Because citizens prefer authoritarian uncertainty over transparent statutory guidelines."
                    }
                }
            else:  # c_idx == 3
                q_b = {
                    "text": f"In {topic_title}, what is the foundational methodology historians use to evaluate the credibility of historical claims?",
                    "a": "Cross-referencing multiple conflicting primary sources against independent archival, material, and administrative records.",
                    "b": "Accepting the official monarchical proclamation as absolute unvarnished truth without verification.",
                    "c": "Assuming that all written historical records were intentionally fabricated by ancient propagandists.",
                    "d": "Relying exclusively on modern historical fiction novels rather than period archival documents.",
                    "expl": "Rigorous historiography requires cross-examining diverse primary sources to detect bias, omissions, and corroborate empirical facts."
                }
                q_c = {
                    "text": f"In {topic_title}, why must historians critically scrutinize the social status and political affiliation of primary source authors?",
                    "a": "Because eyewitnesses write from specific ideological perspectives that influence which events they observe, emphasize, or omit.",
                    "b": "Because historical actors were legally required to misrepresent historical casualty figures in personal letters.",
                    "c": "Because common citizens lacked the physical ability to witness major historical events directly.",
                    "d": "Because political affiliation has zero influence on how individuals interpret or describe events.",
                    "expl": "Primary sources reflect the author's social vantage point, personal motives, and intended audience; identifying perspective reveals underlying biases.",
                    "prompt": "Why cannot any single eyewitness primary source be treated as an objective, complete historical record?",
                    "probe_opts": {
                        "A": "Because individual observers have geographically limited vantage points and are filtered through personal ideological biases.",
                        "B": "Because ancient ink degraded so quickly that written words reversed their meaning over time.",
                        "C": "Because eyewitness testimony is legally prohibited in modern academic historical research publications.",
                        "D": "Because historical witnesses only recorded events that occurred during daylight hours."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a researcher examining a pivotal battle finds official military dispatches reporting a glorious triumph, but private soldiers' diaries describe panicked retreat and heavy losses. How should the historian determine the truth?",
                    "a": "Corroborate both accounts with independent logistical supply records, hospital casualty manifests, and territorial control maps.",
                    "b": "Discard the soldiers' diaries immediately because low-ranking participants possess zero historical value.",
                    "c": "Accept the official military dispatch uncritically because official government documents are prohibited from distortion.",
                    "d": "Conclude that the battle never took place and remove all references to it from the historical record.",
                    "expl": "Historians reconcile conflicting accounts by cross-referencing logistical, medical, and spatial evidence to establish empirical reality.",
                    "prompt": "Why is cross-referencing administrative and logistical data necessary when reconciling conflicting primary accounts?",
                    "probe_opts": {
                        "A": "Because operational records such as supply tallies and casualty logs are recorded for functional utility rather than political propaganda, providing an objective empirical anchor.",
                        "B": "Because administrative civil servants were completely isolated from the political pressures of their era.",
                        "C": "Because personal diaries are legally inadmissible in modern academic historical research publications.",
                        "D": "Because military leaders were required by ancient chivalric codes to report exact battlefield casualty tallies."
                    }
                }

        else:
            # UNIVERSAL ACADEMIC MULTI-DISCIPLINARY FRAMEWORK
            # Tailored cleanly to ANY topic title in the world without jargon anomalies
            if c_idx == 0:
                q_b = {
                    "text": f"In {topic_title}, what foundational definition or core taxonomy establishes how {c_label} is classified?",
                    "a": f"Established structural criteria and baseline principles that define valid relationships in {topic_title}.",
                    "b": f"Arbitrary heuristics that operate with zero rules, definitions, or predictable analytical boundaries.",
                    "c": f"Replacing systematic analysis with subjective opinion that contradicts empirical evidence.",
                    "d": f"Assuming all systems behave identically regardless of initial parameters or environmental context.",
                    "expl": f"{c_label} provides the foundational premises, operational taxonomy, and baseline definitions required to study {topic_title}."
                }
                q_c = {
                    "text": f"In {topic_title}, why must foundational baseline criteria in {c_label} be verified before drawing analytical conclusions?",
                    "a": f"Because operational rules in {topic_title} are only valid when their prerequisite baseline assumptions are fully satisfied.",
                    "b": f"Because verifying foundational baselines automatically solves all downstream problems without further calculation.",
                    "c": f"Because advanced principles apply universally across all contexts even when foundational assumptions are broken.",
                    "d": f"Because baseline conditions are merely decorative labels that have no influence on real-world outcomes.",
                    "expl": f"Higher-level conclusions depend on prerequisite conditions being met; bypassing foundational validation leads to false deductions.",
                    "prompt": f"Why does validating prerequisite baseline conditions prevent false deductions in {c_label}?",
                    "probe_opts": {
                        "A": f"Because higher-order principles are derived under specific boundary conditions; violating baselines renders subsequent theorems inapplicable.",
                        "B": f"Because baseline conditions automatically double the computational speed of all subsequent calculations.",
                        "C": f"Because prerequisite rules are legally binding statutes established by international educational committees.",
                        "D": f"Because empirical investigations cannot proceed unless all variables are set to zero."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, a practitioner attempts to apply an advanced method from {c_label} to a case where foundational premises are unmet. What is the predictable outcome?",
                    "a": f"The method produces invalid conclusions or systemic failure because core prerequisite assumptions were bypassed.",
                    "b": f"The method automatically adapts and guarantees flawless performance regardless of prerequisite violations.",
                    "c": f"The system enters a perpetual equilibrium state that eliminates all sources of analytical error.",
                    "d": f"The governing rules of {topic_title} cease to operate across the entire academic discipline.",
                    "expl": f"Applying specialized techniques without validating initial premises in {c_label} leads directly to erroneous conclusions.",
                    "prompt": f"Why does bypassing initial baseline validation in {c_label} invalidate subsequent conclusions?",
                    "probe_opts": {
                        "A": f"Because analytical models in {topic_title} are logically derived under specific boundary premises that dictate their applicability.",
                        "B": f"Because baseline premises alter universal constants rather than defining specific system boundaries.",
                        "C": f"Because analytical models always perform with higher accuracy when foundational definitions are ignored.",
                        "D": f"Because baseline conditions only apply to historical case studies rather than active problem solving."
                    }
                }
            elif c_idx == 1:
                q_b = {
                    "text": f"In {topic_title}, which driving mechanism regulates active dynamic processes in {c_label}?",
                    "a": f"Direct causal pathways that govern how inputs are transformed into measurable outputs.",
                    "b": f"Completely random fluctuations that occur without any logical or governing mechanism.",
                    "c": f"Passive historical correlations that exert zero active influence on ongoing operations.",
                    "d": f"Spontaneous equilibrium states that generate infinite capacity without consuming resources.",
                    "expl": f"{c_label} is driven by active causal mechanisms that dictate how inputs are processed into systemic outcomes."
                }
                q_c = {
                    "text": f"In {topic_title}, when analyzing {c_label}, how does altering a key input parameter impact overall system output?",
                    "a": f"It propagates through the governing mechanism, shifting output in accordance with system sensitivity.",
                    "b": f"It produces completely random outputs that bear no relationship to the input alteration.",
                    "c": f"It has zero effect because system outputs remain completely frozen under all conditions.",
                    "d": f"It immediately resets all internal system parameters back to zero regardless of mechanism.",
                    "expl": f"Dynamic mechanisms dictate parameter sensitivity: changes in inputs propagate systematically through internal causal chains.",
                    "prompt": f"Why does understanding causal sensitivity allow accurate prediction of system behavior in {c_label}?",
                    "probe_opts": {
                        "A": f"Because mapping governing functional dependencies allows one to calculate output trajectories from input perturbations.",
                        "B": "Because dynamic systems eliminate all mathematical uncertainty when inputs are varied.",
                        "C": "Because sensitive parameters only operate when systems are completely isolated from the environment.",
                        "D": "Because input alterations are prohibited from affecting systemic outcomes in rigorous academic models."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, two parameters in {c_label} appear strongly correlated during testing. How should a researcher determine true causation?",
                    "a": f"Isolate and manipulate one parameter while holding others constant to observe direct output changes.",
                    "b": f"Assume that whichever parameter occurred first in time is the guaranteed sole cause.",
                    "c": f"Discard all experimental measurements and rely entirely on unverified intuition.",
                    "d": f"Conclude that correlation always guarantees direct causation without further testing.",
                    "expl": f"True causality in {c_label} requires controlled experimentation: isolating one factor while holding confounding variables constant.",
                    "prompt": f"Why does observing correlation alone fail to establish a direct causal mechanism in {c_label}?",
                    "probe_opts": {
                        "A": f"Because two variables may correlate due to an unobserved third factor or coincidental alignment rather than direct causation.",
                        "B": f"Because direct causes in {topic_title} are legally prohibited from correlating with their effects.",
                        "C": f"Because controlled testing introduces artificial distortions that hide true relationships.",
                        "D": f"Because all measurable variables in {topic_title} operate in complete isolation from one another."
                    }
                }
            elif c_idx == 2:
                q_b = {
                    "text": f"In {topic_title}, what defines the governing boundary constraints and conservation limits in {c_label}?",
                    "a": f"Fundamental structural, conservation, or physical thresholds beyond which standard behavior degrades or alters.",
                    "b": f"Arbitrary suggestions that have zero influence on real-world functional validity or outcomes.",
                    "c": f"Infinite capacity bounds that permit unbounded expansion without consuming energy or resources.",
                    "d": f"Static conventions that apply only when the subject is completely deactivated or unobserved.",
                    "expl": f"{c_label} establishes the critical operational boundaries, conservation invariants, and threshold limits of the subject."
                }
                q_c = {
                    "text": f"In {topic_title}, what is the inherent trade-off when optimizing a specific parameter near its boundary limit in {c_label}?",
                    "a": f"Maximizing one desired property typically narrows margins of safety or compromises other coupled attributes.",
                    "b": f"Pushing performance higher automatically eliminates all friction, costs, vulnerabilities, and risks.",
                    "c": f"Parameters operating near critical thresholds require zero oversight or continuous monitoring.",
                    "d": f"Optimizing performance causes all external resource and energy requirements to drop to zero.",
                    "expl": f"System trade-offs dictate that optimizing one metric toward boundary thresholds inherently stresses coupled constraints.",
                    "prompt": f"Why does pushing a parameter toward its boundary threshold compromise coupled attributes in {c_label}?",
                    "probe_opts": {
                        "A": f"Because conservation laws dictate that shifting resources or capacity toward one objective diminishes reserves available for others.",
                        "B": "Because boundary thresholds generate negative gravity that destabilizes surrounding components.",
                        "C": "Because optimized systems lose the ability to interact with atmospheric air.",
                        "D": "Because coupled constraints only exist in purely theoretical mathematical models."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an analyst extrapolates a linear model in {c_label} far beyond its validated empirical threshold. What occurs?",
                    "a": f"The model breaks down because non-linear saturation, threshold effects, or systemic instability take over.",
                    "b": f"The model maintains perfect 100% predictive accuracy across all infinite parameter regimes.",
                    "c": f"The underlying real-world phenomena reshape themselves to match the linear mathematical formula.",
                    "d": f"All mathematical calculations automatically yield zero with zero residual error.",
                    "expl": f"Extrapolating beyond validated boundaries in {c_label} fails because non-linear dynamics emerge past critical thresholds.",
                    "prompt": f"Why does linear extrapolation fail beyond critical threshold boundaries in {c_label}?",
                    "probe_opts": {
                        "A": f"Because systems exhibit non-linear state transitions, saturation, or damping breakdown once threshold limits are exceeded.",
                        "B": "Because linear equations are legally invalid in modern academic research publications.",
                        "C": "Because physical systems expand into additional dimensions beyond threshold points.",
                        "D": "Because threshold limits cause all mathematical variables to freeze into constants."
                    }
                }
            else:  # c_idx == 3
                q_b = {
                    "text": f"In {topic_title}, what is the standard empirical methodology for conducting rigorous diagnostic evaluation in {c_label}?",
                    "a": f"Systematic verification of observations against baseline standards using variable isolation and corroborating evidence.",
                    "b": f"Changing all testing conditions simultaneously without recording experimental modifications.",
                    "c": f"Assuming that every anomalous observation is a permanent law that invalidates all prior knowledge.",
                    "d": f"Rejecting measurable data and relying entirely on unverified personal intuition.",
                    "expl": f"{c_label} relies on disciplined diagnostic evaluation: isolating variables and comparing observations against baseline benchmarks."
                }
                q_c = {
                    "text": f"In {topic_title}, why is distinguishing surface symptoms from underlying root causes critical during evaluation in {c_label}?",
                    "a": f"Because treating surface symptoms leaves the underlying causal mechanism active, leading to recurring issues.",
                    "b": f"Because surface symptoms are always identical to the underlying root cause in every scenario.",
                    "c": f"Because root causes resolve spontaneously as soon as superficial symptoms are addressed.",
                    "d": f"Because diagnostic instruments can only detect root causes and cannot measure surface effects.",
                    "expl": f"Addressing symptoms provides only temporary masking; resolving fundamental issues in {c_label} requires identifying the root cause.",
                    "prompt": f"Why does addressing root causes produce permanent resolution compared to treating symptoms in {c_label}?",
                    "probe_opts": {
                        "A": f"Because symptoms are secondary cascading consequences; terminating the primary causal trigger halts the entire sequence.",
                        "B": "Because primary causes have lower magnitude than secondary observational symptoms.",
                        "C": "Because surface symptoms always disappear automatically without intervention.",
                        "D": "Because diagnostic protocols require root causes to be resolved before symptoms appear."
                    }
                }
                q_a = {
                    "text": f"In {topic_title}, an investigator observes multiple conflicting anomalous indications in {c_label} simultaneously. How should they proceed?",
                    "a": f"Trace symptom dependencies back to initial triggering factors and test hypotheses sequentially through controlled isolation.",
                    "b": f"Discard all anomalous observations immediately and declare the investigation completely resolved.",
                    "c": f"Replace all theoretical models simultaneously without validating which assumption failed.",
                    "d": f"Assume the observations are impossible and cease all further investigation.",
                    "expl": f"Complex investigations require tracing symptoms back to the initiating trigger and testing hypotheses one by one.",
                    "prompt": f"Why is tracing the initiating trigger superior to addressing secondary symptoms in {c_label}?",
                    "probe_opts": {
                        "A": f"Because secondary symptoms are cascading consequences of the primary fault; fixing the primary fault resolves the cascade.",
                        "B": f"Because primary trigger events have lower severity than secondary consequence symptoms.",
                        "C": f"Because secondary symptoms are always false readings generated by defective instruments.",
                        "D": f"Because diagnostic standards require secondary symptoms to be resolved in reverse alphabetical order."
                    }
                }

        # Collect raw questions
        raw_questions.append({
            "concept_idx": c_idx, "type": "basic", "diff": "easy",
            "q": q_b
        })
        raw_questions.append({
            "concept_idx": c_idx, "type": "conceptual", "diff": "medium",
            "q": q_c
        })
        raw_questions.append({
            "concept_idx": c_idx, "type": "application", "diff": "hard",
            "q": q_a
        })

    # RANDOMIZE TWO-TIER REASONING PROBES ACROSS THE QUIZ
    # Avoid predictable 3, 6, 9, 12! Select 4 distinct questions from eligible conceptual and application questions.
    eligible_indices = [i for i, item in enumerate(raw_questions) if "prompt" in item["q"] and "probe_opts" in item["q"]]
    selected_probe_indices = set(random.sample(eligible_indices, min(4, len(eligible_indices))))

    questions = []
    for i, item in enumerate(raw_questions):
        c_idx = item["concept_idx"]
        cid = concepts[c_idx]["id"]
        misc_id = misconceptions[c_idx]["id"]
        q_def = item["q"]

        rp = None
        if i in selected_probe_indices:
            rp = {
                "prompt": q_def["prompt"],
                "options": q_def["probe_opts"],
                "correct_probe": "A"
            }

        questions.append({
            "id": f"{domain_id}_q{i+1}",
            "domain_id": domain_id,
            "concept_id": cid,
            "question_type": item["type"],
            "difficulty": item["diff"],
            "question_text": q_def["text"],
            "option_a": q_def["a"],
            "option_b": q_def["b"],
            "option_c": q_def["c"],
            "option_d": q_def["d"],
            "correct_option": "A",
            "explanation": q_def["expl"],
            "misconception_id": misc_id,
            "prerequisite_id": concepts[c_idx]["prerequisites"][0] if concepts[c_idx]["prerequisites"] else cid,
            "reasoning_probe": rp
        })

    # Shuffle options for questions and reasoning probes to distribute correct answers evenly across A, B, C, D
    for q in questions:
        orig_correct = q.get("correct_option", "A").upper().strip()
        raw_opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        idx_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        correct_text = raw_opts[idx_map.get(orig_correct, 0)]
        random.shuffle(raw_opts)
        q["option_a"] = raw_opts[0]
        q["option_b"] = raw_opts[1]
        q["option_c"] = raw_opts[2]
        q["option_d"] = raw_opts[3]
        for ltr, txt in [("A", raw_opts[0]), ("B", raw_opts[1]), ("C", raw_opts[2]), ("D", raw_opts[3])]:
            if txt == correct_text:
                q["correct_option"] = ltr
                break

        rp = q.get("reasoning_probe")
        if rp and "options" in rp and "correct_probe" in rp:
            p_opts = rp["options"]
            orig_p_corr = rp.get("correct_probe", "A").upper().strip()
            p_corr_txt = p_opts.get(orig_p_corr, p_opts.get("A", ""))
            p_txts = list(p_opts.values())
            random.shuffle(p_txts)
            rp["options"] = {"A": p_txts[0], "B": p_txts[1], "C": p_txts[2], "D": p_txts[3]}
            for ltr, txt in rp["options"].items():
                if txt == p_corr_txt:
                    rp["correct_probe"] = ltr
                    break

    return concepts, misconceptions, questions, concept_guides, icon, cat
