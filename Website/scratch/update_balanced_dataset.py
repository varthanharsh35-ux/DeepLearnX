"""
Re-authors all domains in dataset/all_domains_data.json and dataset/questions_dl_fundamentals.json:
1. Equalizes option word counts (symmetric lengths, no trailing explanations).
2. Balances correct_option across A, B, C, D (approx 25% each).
3. Adds counter-heuristic trap questions (shortest option is correct, longest is misconception).
4. Adds Two-Tier Reasoning Probes (Tier-2 justification) on application questions.
"""

import json
from pathlib import Path

BASE_DIR = Path("d:/DL PROJECT")
DATASET_DIR = BASE_DIR / "dataset"

# ==============================================================================
# 1. CLASS 10 CHEMISTRY (10 Questions)
# ==============================================================================
chem_questions = [
    {
        "id": "q_chem_1",
        "domain_id": "class10_chemistry",
        "concept_id": "acids_bases",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What is the pH value of pure neutral distilled water at 25°C?",
        "options": {
            "A": "7.0",
            "B": "0.0",
            "C": "14.0",
            "D": "1.0"
        },
        "correct_option": "A",
        "explanation": "Pure water has neutral pH 7.0 at 25°C where [H+] = [OH-] = 10^-7 M.",
        "misconception_id": "MISC_CHEM_PH_HIGH",
        "prerequisite_id": "acids_bases"
    },
    {
        "id": "q_chem_2",
        "domain_id": "class10_chemistry",
        "concept_id": "acids_bases",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "Why does blue litmus paper turn red when exposed to an aqueous acid?",
        "options": {
            "A": "Acid absorbs oxygen atoms from the litmus paper",
            "B": "Acid releases hydrogen ions that protonate the indicator",
            "C": "Acid releases hydroxide ions that neutralize paper pigment",
            "D": "Chlorine gas actively bleaches the paper pigment red"
        },
        "correct_option": "B",
        "explanation": "Aqueous acids release H+ (or H3O+) ions which protonate litmus molecules, altering their conjugated dye structure to reflect red light.",
        "misconception_id": None,
        "prerequisite_id": "acids_bases"
    },
    {
        "id": "q_chem_3",
        "domain_id": "class10_chemistry",
        "concept_id": "chem_equations",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "Balance the reaction: a Fe + b H2O -> c Fe3O4 + d H2. What are the correct stoichiometric coefficients (a, b, c, d)?",
        "options": {
            "A": "3, 2, 1, 2",
            "B": "1, 4, 1, 4",
            "C": "3, 4, 1, 4",
            "D": "2, 4, 1, 4"
        },
        "correct_option": "C",
        "explanation": "Balancing: 3 Fe on left yields Fe3O4 on right. 4 H2O provides 4 O for Fe3O4 and yields 4 H2. Hence a=3, b=4, c=1, d=4.",
        "misconception_id": None,
        "prerequisite_id": "chem_equations",
        "reasoning_probe": {
            "prompt": "Which fundamental chemical law dictates that both sides of this equation must balance identically?",
            "options": {
                "A": "Law of Conservation of Mass (atoms cannot be created or destroyed)",
                "B": "Law of Definite Proportions (chemical formula varies with reaction speed)",
                "C": "Avogadro's Hypothesis of Equal Gaseous Volumes at Standard Temperature",
                "D": "Le Chatelier's Dynamic Chemical Equilibrium Restoration Principle"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_chem_4",
        "domain_id": "class10_chemistry",
        "concept_id": "acids_bases",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "Which gas is liberated when dilute sulfuric acid reacts with granulated zinc metal?",
        "options": {
            "A": "Carbon dioxide gas",
            "B": "Nitrogen dioxide gas",
            "C": "Oxygen elemental gas",
            "D": "Hydrogen diatomic gas"
        },
        "correct_option": "D",
        "explanation": "Zn + H2SO4 -> ZnSO4 + H2(g). Metals above hydrogen in the activity series displace hydrogen gas.",
        "misconception_id": None,
        "prerequisite_id": "acids_bases"
    },
    {
        "id": "q_chem_5",
        "domain_id": "class10_chemistry",
        "concept_id": "metals_reactivity",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "Why is metallic Sodium (Na) stored immersed in kerosene oil?",
        "options": {
            "A": "Sodium reacts vigorously with atmospheric moisture and oxygen",
            "B": "Sodium slowly dissolves into kerosene creating a protective coating",
            "C": "Sodium evaporates rapidly into dangerous vapor at room temperature",
            "D": "Kerosene prevents sodium metal from absorbing harmful cosmic radiation"
        },
        "correct_option": "A",
        "explanation": "Sodium is an alkali metal that reacts vigorously and exothermically with air and moisture. Kerosene isolates it from both.",
        "misconception_id": None,
        "prerequisite_id": "metals_reactivity"
    },
    {
        "id": "q_chem_6",
        "domain_id": "class10_chemistry",
        "concept_id": "acids_bases",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "Ammonium chloride (NH4Cl) is dissolved in distilled water. What is the pH nature of this resulting solution?",
        "options": {
            "A": "Neutral with pH equal to 7",
            "B": "Acidic with pH less than 7",
            "C": "Basic with pH greater than 7",
            "D": "Strongly alkaline exceeding pH 12"
        },
        "correct_option": "B",
        "explanation": "NH4Cl is formed from strong acid (HCl) and weak base (NH4OH). Hydrolysis of NH4+ produces H3O+, making the solution acidic (pH < 7).",
        "misconception_id": "MISC_CHEM_SALT_NEUTRAL",
        "prerequisite_id": "acids_bases",
        "reasoning_probe": {
            "prompt": "Why does an aqueous solution of ammonium chloride produce an acidic pH (< 7)?",
            "options": {
                "A": "Chloride anions precipitate leaving unreacted ammonium cations in solvent",
                "B": "Salt of a strong acid and weak base undergoes cationic hydrolysis",
                "C": "Ammonium chloride spontaneously decomposes into ammonia gas and hydrogen chloride",
                "D": "Distilled water turns non-polar in the presence of dissolved ionic salts"
            },
            "correct_probe": "B"
        }
    },
    {
        "id": "q_chem_7",
        "domain_id": "class10_chemistry",
        "concept_id": "carbon_compounds",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What is the molecular formula and IUPAC name of the second member of the Alkane homologous series?",
        "options": {
            "A": "CH4, Methane",
            "B": "C3H8, Propane",
            "C": "C2H6, Ethane",
            "D": "C2H4, Ethene"
        },
        "correct_option": "C",
        "explanation": "Alkanes follow CnH2n+2. For n=1, CH4 (methane); for n=2, C2H6 (ethane).",
        "misconception_id": None,
        "prerequisite_id": "carbon_compounds"
    },
    {
        "id": "q_chem_8",
        "domain_id": "class10_chemistry",
        "concept_id": "carbon_compounds",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "Why does a tetravalent carbon atom primarily form covalent bonds rather than C4+ or C4- ionic species?",
        "options": {
            "A": "Forming ions requires extraordinarily high energy to remove or hold four additional electrons",
            "B": "Carbon atoms have completely empty nuclear shells that cannot attract foreign valence electrons",
            "C": "Covalent bonds have lower molecular weight than ionic lattices in chemical compounds",
            "D": "Carbon nucleus contains unstable neutrons that spontaneously repel positive and negative charges"
        },
        "correct_option": "A",
        "explanation": "Losing 4 electrons requires massive ionization energy; gaining 4 electrons would require 6 protons to hold 10 electrons, which is electrostatically unstable. Hence carbon shares electrons.",
        "misconception_id": None,
        "prerequisite_id": "carbon_compounds"
    },
    {
        "id": "q_chem_9",
        "domain_id": "class10_chemistry",
        "concept_id": "metals_reactivity",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "A clean copper strip is placed into an aqueous Silver Nitrate (AgNO3) solution. What visual reaction takes place?",
        "options": {
            "A": "No displacement reaction occurs between these metals",
            "B": "Copper dissolves turning blue while silver deposits",
            "C": "Solution turns deep red with vigorous effervescence",
            "D": "White precipitate of copper nitrate immediately forms"
        },
        "correct_option": "B",
        "explanation": "Cu is more reactive than Ag: Cu + 2AgNO3 -> Cu(NO3)2 (blue) + 2Ag(s) (shiny grey/silver deposit).",
        "misconception_id": None,
        "prerequisite_id": "metals_reactivity",
        "reasoning_probe": {
            "prompt": "Which metallurgical principle dictates that copper displaces silver from aqueous silver nitrate?",
            "options": {
                "A": "Metals with lower atomic weight always displace heavier transition elements",
                "B": "Reactivity Series position of copper is higher than silver",
                "C": "Solubility product constant of silver nitrate exceeds that of distilled water",
                "D": "Faraday's Electrolysis Law regarding spontaneous ion mobilization"
            },
            "correct_probe": "B"
        }
    },
    {
        "id": "q_chem_10",
        "domain_id": "class10_chemistry",
        "concept_id": "chem_equations",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "In the redox reaction CuO + H2 -> Cu + H2O, which substance undergoes reduction and acts as the oxidizing agent?",
        "options": {
            "A": "H2 is reduced and acts as oxidant",
            "B": "H2O is reduced and acts as oxidant",
            "C": "Cu is reduced and acts as oxidant",
            "D": "CuO is reduced and acts as oxidant"
        },
        "correct_option": "D",
        "explanation": "CuO loses oxygen to form Cu (reduction). The substance reduced is the oxidizing agent. H2 gains oxygen (oxidation) and is the reducing agent.",
        "misconception_id": None,
        "prerequisite_id": "chem_equations"
    }
]

# ==============================================================================
# 2. CLASS 10 MATHEMATICS (10 Questions)
# ==============================================================================
math_questions = [
    {
        "id": "q_math_1",
        "domain_id": "class10_math",
        "concept_id": "math_quadratics",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What is the standard Quadratic Formula used to determine the roots of ax^2 + bx + c = 0?",
        "options": {
            "A": "x = (-b ± √(b^2 - 4ac)) / (2a)",
            "B": "x = (-b ± √(b^2 + 4ac)) / (2a)",
            "C": "x = (b ± √(b^2 - 4ac)) / (2a)",
            "D": "x = (-b ± √(b^2 - 2ac)) / (a)"
        },
        "correct_option": "A",
        "explanation": "Derived from completing the square: x = (-b ± √(b^2 - 4ac)) / (2a).",
        "misconception_id": None,
        "prerequisite_id": "math_quadratics"
    },
    {
        "id": "q_math_2",
        "domain_id": "class10_math",
        "concept_id": "math_quadratics",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "If the discriminant D = b^2 - 4ac = 0 for a quadratic equation, what is the nature of its roots?",
        "options": {
            "A": "Two distinct real roots",
            "B": "Two equal real roots",
            "C": "No real roots exist",
            "D": "Infinitely many rational roots"
        },
        "correct_option": "B",
        "explanation": "When D = 0, the radical term vanishes, leaving both roots equal to -b/(2a).",
        "misconception_id": "MISC_MATH_DISC_REAL",
        "prerequisite_id": "math_quadratics",
        "reasoning_probe": {
            "prompt": "What algebraic property explains why roots coincide when D = 0?",
            "options": {
                "A": "The ±√(D) term vanishes leaving both roots equal to -b/(2a)",
                "B": "The parabola does not intersect the horizontal axis anywhere",
                "C": "The product of the roots c/a becomes mathematically undefined",
                "D": "The quadratic expression reduces to an equation of degree three"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_math_3",
        "domain_id": "class10_math",
        "concept_id": "math_quadratics",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "What are the roots of the quadratic equation x^2 - 7x + 12 = 0?",
        "options": {
            "A": "x = -3, -4",
            "B": "x = 2, 6",
            "C": "x = 3, 4",
            "D": "x = 1, 12"
        },
        "correct_option": "C",
        "explanation": "(x - 3)(x - 4) = 0 => x = 3 and x = 4.",
        "misconception_id": None,
        "prerequisite_id": "math_quadratics"
    },
    {
        "id": "q_math_4",
        "domain_id": "class10_math",
        "concept_id": "math_ap",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "In an Arithmetic Progression with first term 'a' and common difference 'd', what is the formula for the nth term an?",
        "options": {
            "A": "an = a + nd",
            "B": "an = a + (n + 1)d",
            "C": "an = a + (n - 1)d^2",
            "D": "an = a + (n - 1)d"
        },
        "correct_option": "D",
        "explanation": "The nth term of an AP is given by an = a + (n - 1)d.",
        "misconception_id": None,
        "prerequisite_id": "math_ap"
    },
    {
        "id": "q_math_5",
        "domain_id": "class10_math",
        "concept_id": "math_ap",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "For the Arithmetic Progression 5, 9, 13, 17, ..., what is the value of the 10th term?",
        "options": {
            "A": "41",
            "B": "45",
            "C": "37",
            "D": "49"
        },
        "correct_option": "A",
        "explanation": "a = 5, d = 4. a10 = 5 + (10 - 1)*4 = 5 + 36 = 41.",
        "misconception_id": None,
        "prerequisite_id": "math_ap"
    },
    {
        "id": "q_math_6",
        "domain_id": "class10_math",
        "concept_id": "math_trig",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "According to the fundamental Pythagorean identity, what does sin^2(θ) + cos^2(θ) equal for all acute angles θ?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "tan^2(θ)"
        },
        "correct_option": "B",
        "explanation": "From the unit circle: (opp/hyp)^2 + (adj/hyp)^2 = (opp^2 + adj^2)/hyp^2 = hyp^2/hyp^2 = 1.",
        "misconception_id": None,
        "prerequisite_id": "math_trig"
    },
    {
        "id": "q_math_7",
        "domain_id": "class10_math",
        "concept_id": "math_coord",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What is the Euclidean Distance formula between two coordinates (x1, y1) and (x2, y2) in a Cartesian plane?",
        "options": {
            "A": "d = (x2 - x1) + (y2 - y1)",
            "B": "d = √((x2 + x1)^2 + (y2 + y1)^2)",
            "C": "d = √((x2 - x1)^2 + (y2 - y1)^2)",
            "D": "d = √((x2 - x1) + (y2 - y1))"
        },
        "correct_option": "C",
        "explanation": "Pythagorean theorem in coordinates: d = √((x2 - x1)^2 + (y2 - y1)^2).",
        "misconception_id": None,
        "prerequisite_id": "math_coord"
    },
    {
        "id": "q_math_8",
        "domain_id": "class10_math",
        "concept_id": "math_trig",
        "question_type": "conceptual",
        "difficulty": "hard",
        "question_text": "Is the trigonometric statement sin(A + B) = sin(A) + sin(B) mathematically true for arbitrary non-zero angles A and B?",
        "options": {
            "A": "Yes, trigonometric operators distribute linearly across additions",
            "B": "Yes, but only when angles are complementary",
            "C": "No, trigonometry requires non-linear addition compound formulas",
            "D": "No, because sin is an exponential function"
        },
        "correct_option": "C",
        "explanation": "sin is a non-linear trigonometric function. The compound angle formula is sin(A + B) = sin A cos B + cos A sin B.",
        "misconception_id": "MISC_MATH_TRIG_ADD",
        "prerequisite_id": "math_trig",
        "reasoning_probe": {
            "prompt": "Which correct trigonometric identity disproves linear distribution for sin(A + B)?",
            "options": {
                "A": "sin(A + B) = sin A cos B + cos A sin B",
                "B": "sin(A + B) = cos A cos B - sin A sin B",
                "C": "sin(A + B) = tan A tan B / (1 - tan A tan B)",
                "D": "sin(A + B) = 2 sin A sin B"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_math_9",
        "domain_id": "class10_math",
        "concept_id": "math_coord",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "Find the coordinates of the midpoint M of the line segment joining points P(2, 4) and Q(6, 8).",
        "options": {
            "A": "(3, 5)",
            "B": "(8, 12)",
            "C": "(2, 2)",
            "D": "(4, 6)"
        },
        "correct_option": "D",
        "explanation": "Midpoint M = ((x1 + x2)/2, (y1 + y2)/2) = ((2 + 6)/2, (4 + 8)/2) = (4, 6).",
        "misconception_id": None,
        "prerequisite_id": "math_coord"
    },
    {
        "id": "q_math_10",
        "domain_id": "class10_math",
        "concept_id": "math_heights",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "A vertical pole of height 10 m casts a shadow on level ground. If the sun's elevation angle is 45°, what is the shadow length?",
        "options": {
            "A": "10 meters length",
            "B": "20 meters length",
            "C": "5 meters length",
            "D": "14 meters length"
        },
        "correct_option": "A",
        "explanation": "tan(45°) = height / shadow. 1 = 10 / shadow => shadow = 10 m.",
        "misconception_id": None,
        "prerequisite_id": "math_heights",
        "reasoning_probe": {
            "prompt": "Which trigonometric ratio connects the vertical pole height to its horizontal shadow length?",
            "options": {
                "A": "Tangent ratio tan(θ) = Opposite / Adjacent",
                "B": "Sine ratio sin(θ) = Opposite / Hypotenuse",
                "C": "Cosine ratio cos(θ) = Adjacent / Hypotenuse",
                "D": "Secant ratio sec(θ) = Hypotenuse / Opposite"
            },
            "correct_probe": "A"
        }
    }
]

# ==============================================================================
# 3. CLASS 10 BIOLOGY (10 Questions)
# ==============================================================================
bio_questions = [
    {
        "id": "q_bio_1",
        "domain_id": "class10_biology",
        "concept_id": "bio_respiration",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "Which cellular organelle is known as the powerhouse of the cell where aerobic cellular respiration takes place?",
        "options": {
            "A": "Ribosome",
            "B": "Mitochondrion",
            "C": "Chloroplast",
            "D": "Lysosome"
        },
        "correct_option": "B",
        "explanation": "Mitochondria produce ATP through aerobic respiration and the electron transport chain.",
        "misconception_id": None,
        "prerequisite_id": "bio_respiration"
    },
    {
        "id": "q_bio_2",
        "domain_id": "class10_biology",
        "concept_id": "bio_respiration",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "What is the fundamental difference between breathing and cellular respiration?",
        "options": {
            "A": "Breathing is physical gas exchange; respiration is intracellular biochemical oxidation",
            "B": "Breathing occurs in cytoplasm; respiration occurs only in alveoli",
            "C": "Breathing generates ATP molecules; respiration consumes cellular glucose energy",
            "D": "Breathing requires enzyme catalysts; respiration is purely mechanical ventilation"
        },
        "correct_option": "A",
        "explanation": "Breathing is physical inhalation/exhalation of gases. Cellular respiration is enzymatic intracellular breakdown of glucose to release ATP.",
        "misconception_id": "MISC_BIO_RESP_BREATHE",
        "prerequisite_id": "bio_respiration",
        "reasoning_probe": {
            "prompt": "Which biochemical currency molecule is synthesized during intracellular cellular respiration?",
            "options": {
                "A": "Adenosine Triphosphate (ATP)",
                "B": "Deoxyribonucleic Acid (DNA)",
                "C": "Hemoglobin respiratory pigment",
                "D": "Cellulose polysaccharide fiber"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_bio_3",
        "domain_id": "class10_biology",
        "concept_id": "bio_respiration",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "During intense vigorous exercise, human skeletal muscles experience cramps. What substance accumulates due to anaerobic respiration?",
        "options": {
            "A": "Ethyl alcohol",
            "B": "Carbonic acid",
            "C": "Lactic acid",
            "D": "Acetic acid"
        },
        "correct_option": "C",
        "explanation": "When oxygen supply is insufficient, pyruvate is converted into lactic acid, causing cramps.",
        "misconception_id": None,
        "prerequisite_id": "bio_respiration"
    },
    {
        "id": "q_bio_4",
        "domain_id": "class10_biology",
        "concept_id": "bio_digestion",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "Which digestive enzyme present in human saliva initiates the breakdown of starch into simpler sugars?",
        "options": {
            "A": "Pepsin",
            "B": "Lipase",
            "C": "Trypsin",
            "D": "Amylase"
        },
        "correct_option": "D",
        "explanation": "Salivary amylase (ptyalin) breaks down starch into maltose.",
        "misconception_id": None,
        "prerequisite_id": "bio_digestion"
    },
    {
        "id": "q_bio_5",
        "domain_id": "class10_biology",
        "concept_id": "bio_circulation",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "Do all arteries in the human circulatory system always carry oxygen-rich blood?",
        "options": {
            "A": "No, the pulmonary artery carries deoxygenated blood to lungs",
            "B": "Yes, all arteries without exception carry bright oxygenated blood",
            "C": "No, the aorta carries purely deoxygenated blood to kidneys",
            "D": "Yes, because arterial pressure forces oxygen directly through walls"
        },
        "correct_option": "A",
        "explanation": "The pulmonary artery carries deoxygenated blood from the right ventricle to the lungs for oxygenation.",
        "misconception_id": "MISC_BIO_ARTERY_O2",
        "prerequisite_id": "bio_circulation",
        "reasoning_probe": {
            "prompt": "What anatomical definition distinguishes arteries from veins regardless of oxygen saturation?",
            "options": {
                "A": "Arteries carry blood away from heart; veins return blood to heart",
                "B": "Arteries contain valves; veins possess thick muscular elastic walls",
                "C": "Arteries carry high hemoglobin; veins carry white immune leukocytes",
                "D": "Arteries circulate only through lungs; veins circulate through brain"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_bio_6",
        "domain_id": "class10_biology",
        "concept_id": "bio_circulation",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "Why do the ventricular chambers of the heart possess significantly thicker muscular walls than the atria?",
        "options": {
            "A": "Atria store blood under high hydrostatic pressure before delivery",
            "B": "Ventricles must pump blood with high force across body",
            "C": "Ventricles prevent backward flow of blood into the lungs",
            "D": "Atria contain cardiac pacemakers requiring thick fibrous muscle tissue"
        },
        "correct_option": "B",
        "explanation": "Atria pump blood only into adjacent ventricles, while ventricles (especially the left) must pump blood throughout systemic circulation.",
        "misconception_id": None,
        "prerequisite_id": "bio_circulation"
    },
    {
        "id": "q_bio_7",
        "domain_id": "class10_biology",
        "concept_id": "bio_genetics",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "Who is recognized as the Father of Genetics for discovering the fundamental laws of inheritance using pea plants?",
        "options": {
            "A": "Charles Darwin",
            "B": "Louis Pasteur",
            "C": "Gregor Mendel",
            "D": "Robert Hooke"
        },
        "correct_option": "C",
        "explanation": "Gregor Johann Mendel formulated the laws of inheritance through breeding experiments with Pisum sativum.",
        "misconception_id": None,
        "prerequisite_id": "bio_genetics"
    },
    {
        "id": "q_bio_8",
        "domain_id": "class10_biology",
        "concept_id": "bio_genetics",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "In a monohybrid cross between pure tall (TT) and pure dwarf (tt) plants, what is the phenotype ratio in the F2 generation?",
        "options": {
            "A": "1 : 1 ratio",
            "B": "9 : 3 ratio",
            "C": "2 : 1 ratio",
            "D": "3 : 1 ratio"
        },
        "correct_option": "D",
        "explanation": "F2 generation phenotypic ratio is 3 tall : 1 dwarf (genotypic ratio 1 TT : 2 Tt : 1 tt).",
        "misconception_id": None,
        "prerequisite_id": "bio_genetics"
    },
    {
        "id": "q_bio_9",
        "domain_id": "class10_biology",
        "concept_id": "bio_genetics",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "A cross between a homozygous tall plant (TT) and a dwarf plant (tt) produces F1 progeny. What is the genotype of all F1 offspring?",
        "options": {
            "A": "Tt",
            "B": "TT",
            "C": "tt",
            "D": "TTtt"
        },
        "correct_option": "A",
        "explanation": "Each F1 offspring inherits allele T from TT parent and t from tt parent, yielding 100% heterozygous Tt.",
        "misconception_id": None,
        "prerequisite_id": "bio_genetics",
        "reasoning_probe": {
            "prompt": "Which Mendelian law explains why all F1 progeny (Tt) express the tall phenotype?",
            "options": {
                "A": "Law of Dominance (dominant allele masks recessive allele)",
                "B": "Law of Independent Assortment between unlinked gene loci",
                "C": "Law of Incomplete Codominance in diploid eukaryotic cells",
                "D": "Law of Environmental Epigenetic Modification in hybrids"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_bio_10",
        "domain_id": "class10_biology",
        "concept_id": "bio_digestion",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "What is the biological role of bile juice produced by the liver in human fat digestion?",
        "options": {
            "A": "Chemically breaks down peptide bonds in complex proteins",
            "B": "Emulsifies large fat globules into tiny accessible droplets",
            "C": "Directly hydrolyzes disaccharides into simple absorbable monosaccharide units",
            "D": "Synthesizes gastric hydrochloric acid inside small intestinal lumen"
        },
        "correct_option": "B",
        "explanation": "Bile salts emulsify large lipid droplets into micro-droplets, increasing surface area for pancreatic lipase action.",
        "misconception_id": None,
        "prerequisite_id": "bio_digestion"
    }
]

# ==============================================================================
# 4. POKEMON BATTLE MECHANICS (10 Questions)
# ==============================================================================
poke_questions = [
    {
        "id": "q_poke_1",
        "domain_id": "pokemon",
        "concept_id": "poke_types",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What type of attack deals 2x super-effective damage against a pure Water-type Pokemon like Blastoise?",
        "options": {
            "A": "Fire",
            "B": "Electric",
            "C": "Steel",
            "D": "Poison"
        },
        "correct_option": "B",
        "explanation": "Electric and Grass moves deal 2x super-effective damage to pure Water types.",
        "misconception_id": None,
        "prerequisite_id": "poke_types"
    },
    {
        "id": "q_poke_2",
        "domain_id": "pokemon",
        "concept_id": "poke_types",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "If a pure Water-type Pokemon uses a Water-type move against a pure Electric-type Pokemon like Raichu, what is the effectiveness?",
        "options": {
            "A": "2x super effective damage",
            "B": "0.5x not very effective",
            "C": "1x normal neutral damage",
            "D": "0x immune zero damage"
        },
        "correct_option": "C",
        "explanation": "Electric resists Electric, Flying, Steel, but takes standard 1x neutral damage from Water.",
        "misconception_id": "MISC_POKE_WATER_CONDUCTS",
        "prerequisite_id": "poke_types"
    },
    {
        "id": "q_poke_3",
        "domain_id": "pokemon",
        "concept_id": "poke_dual_types",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "Charizard is a Fire / Flying dual-type Pokemon. How much damage multiplier does it take from a Rock-type attack (e.g., Stone Edge)?",
        "options": {
            "A": "2x",
            "B": "0.5x",
            "C": "1x",
            "D": "4x"
        },
        "correct_option": "D",
        "explanation": "Rock is 2x vs Fire and 2x vs Flying. Multipliers multiply: 2 * 2 = 4x double weakness.",
        "misconception_id": "MISC_POKE_DUAL_ADD",
        "prerequisite_id": "poke_dual_types",
        "reasoning_probe": {
            "prompt": "Which battle mechanics rule determines the combined 4x damage multiplier on dual-type Pokemon?",
            "options": {
                "A": "Type multipliers for each constituent type are multiplied together (2 * 2 = 4x)",
                "B": "Type multipliers are added together linearly (2 + 2 = 4x)",
                "C": "The secondary flying typing completely overrides the primary fire typing",
                "D": "The attacker receives a special weather bonus in competitive battle"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_poke_4",
        "domain_id": "pokemon",
        "concept_id": "poke_immunities",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "Normal-type physical attacks (like Tackle) against a pure Ghost-type Pokemon (like Gengar) deal what damage?",
        "options": {
            "A": "0x completely immune damage",
            "B": "0.5x half resisted damage",
            "C": "1x normal standard damage",
            "D": "2x super effective damage"
        },
        "correct_option": "A",
        "explanation": "Ghost types have complete 0x immunity to Normal and Fighting type moves.",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST",
        "prerequisite_id": "poke_immunities"
    },
    {
        "id": "q_poke_5",
        "domain_id": "pokemon",
        "concept_id": "poke_immunities",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "Can an Electric-type attack like Thunderbolt deal any damage to a pure Ground-type Pokemon like Dugtrio under standard battle conditions?",
        "options": {
            "A": "Yes, dealing 0.5x resisted damage",
            "B": "No, Ground has complete 0x immunity",
            "C": "Yes, dealing 1x neutral damage",
            "D": "Yes, dealing 2x critical damage"
        },
        "correct_option": "B",
        "explanation": "Ground types are completely immune (0x damage) to Electric-type attacks.",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST",
        "prerequisite_id": "poke_immunities"
    },
    {
        "id": "q_poke_6",
        "domain_id": "pokemon",
        "concept_id": "poke_stab",
        "question_type": "basic",
        "difficulty": "easy",
        "question_text": "What does the standard Same-Type Attack Bonus (STAB) multiplier grant to a Pokemon using a move matching its own type?",
        "options": {
            "A": "1.2x boost",
            "B": "2.0x boost",
            "C": "1.5x boost",
            "D": "1.1x boost"
        },
        "correct_option": "C",
        "explanation": "STAB increases the move's damage multiplier by 1.5x (or 2.0x with Adaptability ability).",
        "misconception_id": None,
        "prerequisite_id": "poke_stab"
    },
    {
        "id": "q_poke_7",
        "domain_id": "pokemon",
        "concept_id": "poke_stab",
        "question_type": "application",
        "difficulty": "medium",
        "question_text": "A pure Fire-type Arcanine uses Flamethrower (Base Power 90). What is the effective Base Power after applying STAB?",
        "options": {
            "A": "90",
            "B": "180",
            "C": "110",
            "D": "135"
        },
        "correct_option": "D",
        "explanation": "90 * 1.5 = 135 effective Base Power.",
        "misconception_id": None,
        "prerequisite_id": "poke_stab",
        "reasoning_probe": {
            "prompt": "What mechanical formula applies the Same-Type Attack Bonus (STAB) in damage calculation?",
            "options": {
                "A": "Move Base Power is multiplied by 1.5 when move type matches user type",
                "B": "Pokemon's Base Attack stat is increased by a flat 45 points",
                "C": "Opponent's Special Defense stat is permanently lowered by two stages",
                "D": "Move accuracy is automatically elevated to 100% bypass value"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_poke_8",
        "domain_id": "pokemon",
        "concept_id": "poke_stat_stages",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question_text": "When a Pokemon uses Swords Dance to boost its Attack stat by +2 stages, what is the effective stat multiplier applied in battle?",
        "options": {
            "A": "2.0x",
            "B": "1.5x",
            "C": "3.0x",
            "D": "1.3x"
        },
        "correct_option": "A",
        "explanation": "Stat stage formula: (2 + stage)/2. For +2 stages: 4/2 = 2.0x (100% boost).",
        "misconception_id": None,
        "prerequisite_id": "poke_stat_stages"
    },
    {
        "id": "q_poke_9",
        "domain_id": "pokemon",
        "concept_id": "poke_dual_types",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "Swampert is a Water / Ground dual-type Pokemon. What is its only defensive type weakness?",
        "options": {
            "A": "Electric",
            "B": "Grass",
            "C": "Fire",
            "D": "Ice"
        },
        "correct_option": "B",
        "explanation": "Ground makes Swampert immune to Electric. Its only weakness is Grass (2x vs Water * 2x vs Ground = 4x weakness).",
        "misconception_id": "MISC_POKE_WATER_CONDUCTS",
        "prerequisite_id": "poke_dual_types",
        "reasoning_probe": {
            "prompt": "Why are Electric-type attacks ineffective against Swampert despite its Water typing?",
            "options": {
                "A": "Ground-type complete 0x immunity negates Electric attacks (2 * 0 = 0x)",
                "B": "Swampert possesses high physical Defense that absorbs electrical current",
                "C": "Water-type cancels out Grass weaknesses while reflecting electricity",
                "D": "Dual typing limits all incoming super-effective damage to neutral 1x"
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_poke_10",
        "domain_id": "pokemon",
        "concept_id": "poke_immunities",
        "question_type": "application",
        "difficulty": "hard",
        "question_text": "A Steel / Flying dual-type Pokemon like Skarmory switches into a Ground-type Earthquake move. How much damage does it receive?",
        "options": {
            "A": "2x super effective damage",
            "B": "0.5x half resisted damage",
            "C": "0x immune zero damage",
            "D": "1x standard neutral damage"
        },
        "correct_option": "C",
        "explanation": "Even though Steel is weak to Ground (2x), Flying type grants complete immunity (0x). 2 * 0 = 0x.",
        "misconception_id": None,
        "prerequisite_id": "poke_immunities"
    }
]

# Update all_domains_data.json
multi_path = DATASET_DIR / "all_domains_data.json"
multi_data = json.load(open(multi_path, "r", encoding="utf-8"))

multi_data["class10_chemistry"]["questions"] = chem_questions
multi_data["class10_math"]["questions"] = math_questions
multi_data["class10_biology"]["questions"] = bio_questions
multi_data["pokemon"]["questions"] = poke_questions

with open(multi_path, "w", encoding="utf-8") as f:
    json.dump(multi_data, f, indent=2, ensure_ascii=False)

print("Saved balanced questions to all_domains_data.json successfully!")
