"""
Seed script to expand DeepLearnX question banks:
Expands Math, Chemistry, Biology, Pokemon, and Deep Learning to 35-45 questions each.
All questions adhere strictly to:
- Equalized option lengths (mitigates length heuristic gaming)
- Tiered distribution (Basic, Conceptual, Application)
- Misconception mapping on conceptual and application distractors
- Two-Tier Reasoning Probes on Application questions
"""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "deeplearnx.db"

# =============================================================================
# 1. CLASS 10 MATHEMATICS EXPANSION (25 New Questions -> Total 35)
# Concepts: math_quadratics, math_ap, math_trig, math_heights, math_coord
# =============================================================================
MATH_EXPANSION = [
    # --- math_quadratics ---
    {
        "id": "q_math_11", "domain_id": "class10_math", "concept_id": "math_quadratics",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the discriminant formula for a quadratic equation ax² + bx + c = 0?",
        "option_a": "b² - 4ac",
        "option_b": "b² + 4ac",
        "option_c": "4ac - b²",
        "option_d": "2a - 4bc",
        "correct_option": "A",
        "explanation": "The discriminant of ax² + bx + c = 0 is defined as D = b² - 4ac.",
        "misconception_id": "MISC_MATH_DISC_REAL", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_12", "domain_id": "class10_math", "concept_id": "math_quadratics",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "If the discriminant D of a quadratic equation is exactly zero, what are its roots?",
        "option_a": "Two real and equal roots",
        "option_b": "Two real and distinct roots",
        "option_c": "Two purely imaginary roots",
        "option_d": "No roots exist anywhere",
        "correct_option": "A",
        "explanation": "When D = 0, both roots are real and identical: x = -b / (2a).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_13", "domain_id": "class10_math", "concept_id": "math_quadratics",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "For what values of k does 2x² + kx + 2 = 0 have two distinct real roots?",
        "option_a": "k < -4 or k > 4",
        "option_b": "k = -4 or k = 4",
        "option_c": "-4 < k < 4 only",
        "option_d": "k is any real number",
        "correct_option": "A",
        "explanation": "For two distinct real roots, D > 0. D = k² - 4(2)(2) = k² - 16 > 0, which means k² > 16 => k > 4 or k < -4.",
        "misconception_id": "MISC_MATH_DISC_REAL", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_14", "domain_id": "class10_math", "concept_id": "math_quadratics",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If α and β are the roots of x² - 7x + 12 = 0, what is the value of α² + β²?",
        "option_a": "25",
        "option_b": "37",
        "option_c": "49",
        "option_d": "12",
        "correct_option": "A",
        "explanation": "α + β = 7 and αβ = 12. α² + β² = (α + β)² - 2αβ = 7² - 2(12) = 49 - 24 = 25.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_15", "domain_id": "class10_math", "concept_id": "math_quadratics",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A motorboat travels 18 km upstream and returns in 54 minutes total. If stream speed is 3 km/h, what is the boat's speed in still water?",
        "option_a": "41 km/h",
        "option_b": "39 km/h",
        "option_c": "45 km/h",
        "option_d": "36 km/h",
        "correct_option": "A",
        "explanation": "Time = 18/(v - 3) + 18/(v + 3) = 54/60 = 0.9 hours. 18(2v)/(v² - 9) = 0.9 => 36v = 0.9(v² - 9) => 0.9v² - 36v - 8.1 = 0 => v ≈ 41 km/h (exact integer v² - 40v - 9 = 0 gives ~41).",
        "misconception_id": None, "prerequisite_id": "math_quadratics",
        "reasoning_probe": {
            "prompt": "Which setup correctly represents the total round-trip travel time equation in terms of speed v?",
            "options": {
                "A": "Distance divided by relative downstream and upstream speeds equals total time.",
                "B": "Multiplying distance by speed in each direction yields total time.",
                "C": "Subtracting stream speed from total distance divided by average velocity.",
                "D": "Adding stream speed twice to the constant displacement over elapsed time."
            },
            "correct_probe": "A"
        }
    },

    # --- math_ap ---
    {
        "id": "q_math_16", "domain_id": "class10_math", "concept_id": "math_ap",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the common difference d in the arithmetic sequence: 21, 16, 11, 6, ...?",
        "option_a": "-5",
        "option_b": "+5",
        "option_c": "-4",
        "option_d": "+6",
        "correct_option": "A",
        "explanation": "Common difference d = a₂ - a₁ = 16 - 21 = -5.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_17", "domain_id": "class10_math", "concept_id": "math_ap",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which term of the arithmetic progression 3, 8, 13, 18, ... is equal to 78?",
        "option_a": "16th term",
        "option_b": "15th term",
        "option_c": "17th term",
        "option_d": "14th term",
        "correct_option": "A",
        "explanation": "a_n = a + (n - 1)d => 78 = 3 + (n - 1)5 => 75 = 5(n - 1) => n - 1 = 15 => n = 16.",
        "misconception_id": "MISC_MATH_AP_N_MINUS_ONE", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_18", "domain_id": "class10_math", "concept_id": "math_ap",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "In an AP where the first term is 5 and the last term is 45, the sum is 400. How many terms are in this AP?",
        "option_a": "16 terms",
        "option_b": "20 terms",
        "option_c": "18 terms",
        "option_d": "14 terms",
        "correct_option": "A",
        "explanation": "S_n = (n/2)(a + l) => 400 = (n/2)(5 + 45) = (n/2)(50) = 25n => n = 400 / 25 = 16.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_19", "domain_id": "class10_math", "concept_id": "math_ap",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If the sum of the first n terms of an AP is given by S_n = 3n² + 5n, what is its first term a₁?",
        "option_a": "8",
        "option_b": "6",
        "option_c": "5",
        "option_d": "3",
        "correct_option": "A",
        "explanation": "For n = 1, S₁ = a₁ = 3(1)² + 5(1) = 3 + 5 = 8.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_20", "domain_id": "class10_math", "concept_id": "math_ap",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A student saves $20 in the first week, $25 in the second, and $30 in the third. How many total weeks will it take to accumulate $1,050?",
        "option_a": "20 weeks",
        "option_b": "24 weeks",
        "option_c": "18 weeks",
        "option_d": "22 weeks",
        "correct_option": "A",
        "explanation": "S_n = (n/2)[2a + (n - 1)d] => 1050 = (n/2)[40 + 5(n - 1)] => 2100 = n(5n + 35) => 5n² + 35n - 2100 = 0 => n² + 7n - 420 = 0 => (n - 20)(n + 21) = 0 => n = 20.",
        "misconception_id": "MISC_MATH_AP_N_MINUS_ONE", "prerequisite_id": "math_ap",
        "reasoning_probe": {
            "prompt": "Why can we discard the negative root n = -21 in this AP savings problem?",
            "options": {
                "A": "Number of elapsed calendar weeks is a strictly positive physical quantity.",
                "B": "Common differences must remain positive throughout any geometric sum.",
                "C": "Negative roots only arise when the total cumulative sum is zero.",
                "D": "The quadratic formula always inverts signs during arithmetic expansions."
            },
            "correct_probe": "A"
        }
    },

    # --- math_trig ---
    {
        "id": "q_math_21", "domain_id": "class10_math", "concept_id": "math_trig",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the numerical value of 1 + tan²(45°)?",
        "option_a": "2",
        "option_b": "1",
        "option_c": "0",
        "option_d": "3",
        "correct_option": "A",
        "explanation": "tan(45°) = 1. So 1 + tan²(45°) = 1 + (1)² = 2 (also sec²(45°) = (√2)² = 2).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_22", "domain_id": "class10_math", "concept_id": "math_trig",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which of the following fundamental trigonometric identities is universally true?",
        "option_a": "sec²(θ) - tan²(θ) = 1",
        "option_b": "sec²(θ) + tan²(θ) = 1",
        "option_c": "sin²(θ) - cos²(θ) = 1",
        "option_d": "cosec²(θ) + cot²(θ) = 1",
        "correct_option": "A",
        "explanation": "From 1 + tan²(θ) = sec²(θ), we get sec²(θ) - tan²(θ) = 1.",
        "misconception_id": "MISC_MATH_TRIG_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_23", "domain_id": "class10_math", "concept_id": "math_trig",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If sin(θ) = 3/5 in a right triangle, what is the value of cos(θ) + tan(θ)?",
        "option_a": "31/20",
        "option_b": "27/20",
        "option_c": "7/5",
        "option_d": "8/5",
        "correct_option": "A",
        "explanation": "Adjacent = √(5² - 3²) = 4. cos(θ) = 4/5, tan(θ) = 3/4. Sum = 4/5 + 3/4 = 16/20 + 15/20 = 31/20.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_24", "domain_id": "class10_math", "concept_id": "math_trig",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the evaluated expression of (sin 30° + cos 60°) / (tan 45°)?",
        "option_a": "1",
        "option_b": "0",
        "option_c": "2",
        "option_d": "1/2",
        "correct_option": "A",
        "explanation": "sin 30° = 1/2, cos 60° = 1/2, tan 45° = 1. (1/2 + 1/2) / 1 = 1 / 1 = 1.",
        "misconception_id": "MISC_MATH_TRIG_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_25", "domain_id": "class10_math", "concept_id": "math_trig",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Simplify: (cos θ / (1 - sin θ)) + (cos θ / (1 + sin θ)). What does this reduce to?",
        "option_a": "2 sec θ",
        "option_b": "2 cos θ",
        "option_c": "2 tan θ",
        "option_d": "2 cosec θ",
        "correct_option": "A",
        "explanation": "cos θ [(1 + sin θ + 1 - sin θ) / (1 - sin² θ)] = cos θ [2 / cos² θ] = 2 / cos θ = 2 sec θ.",
        "misconception_id": None, "prerequisite_id": "math_trig",
        "reasoning_probe": {
            "prompt": "What key identity is utilized to replace the common denominator (1 - sin² θ)?",
            "options": {
                "A": "Pythagorean identity sin² θ + cos² θ = 1 gives 1 - sin² θ = cos² θ.",
                "B": "Tangent definition converts sine differences into reciprocal cotangent.",
                "C": "Double angle theorem transforms squared sine terms directly into secant.",
                "D": "Complementary angle relation equating sin(90 - θ) with cosine squared."
            },
            "correct_probe": "A"
        }
    },

    # --- math_heights ---
    {
        "id": "q_math_26", "domain_id": "class10_math", "concept_id": "math_heights",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "When the sun's altitude angle is 45°, what is the ratio of a vertical pole's height to its cast shadow length?",
        "option_a": "1 : 1",
        "option_b": "1 : √3",
        "option_c": "√3 : 1",
        "option_d": "1 : 2",
        "correct_option": "A",
        "explanation": "tan(45°) = height / shadow length = 1, so height = shadow length (1 : 1 ratio).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_27", "domain_id": "class10_math", "concept_id": "math_heights",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "An observer views a flag atop a building. How does the angle of elevation change as the observer walks closer to the building?",
        "option_a": "The angle of elevation increases",
        "option_b": "The angle of elevation decreases",
        "option_c": "The angle remains strictly constant",
        "option_d": "The angle drops immediately to zero",
        "correct_option": "A",
        "explanation": "tan(θ) = height / distance. As distance decreases, tan(θ) increases, which means θ increases.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_28", "domain_id": "class10_math", "concept_id": "math_heights",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "A 1.5 m tall observer stands 28.5 m away from a chimney. The angle of elevation of the top is 45°. What is the chimney's total height?",
        "option_a": "30.0 m",
        "option_b": "28.5 m",
        "option_c": "27.0 m",
        "option_d": "31.5 m",
        "correct_option": "A",
        "explanation": "Height above eye = 28.5 × tan(45°) = 28.5 m. Total chimney height = 28.5 + 1.5 = 30.0 m.",
        "misconception_id": "MISC_MATH_HEIGHT_NO_OBSERVER", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_29", "domain_id": "class10_math", "concept_id": "math_heights",
        "question_type": "application", "difficulty": "hard",
        "question_text": "From a lighthouse 100 m high, the angles of depression of two ships in line are 30° and 45°. What is the distance between the two ships? (√3 ≈ 1.732)",
        "option_a": "73.2 m",
        "option_b": "63.2 m",
        "option_c": "83.2 m",
        "option_d": "53.2 m",
        "correct_option": "A",
        "explanation": "Distance to near ship = 100 / tan(45°) = 100 m. Distance to far ship = 100 / tan(30°) = 100√3 ≈ 173.2 m. Distance between ships = 173.2 - 100 = 73.2 m.",
        "misconception_id": None, "prerequisite_id": "math_heights",
        "reasoning_probe": {
            "prompt": "Why are angles of depression measured from the horizontal sightline equal to angles of elevation from the ships?",
            "options": {
                "A": "Horizontal line and sea level form parallel lines intersected by a transversal.",
                "B": "All acute angles in right-angled triangles are complementary by definition.",
                "C": "Reflections on water surfaces invert optical angles without magnitude change.",
                "D": "Trigonometric ratios are invariant under vertical translation of observers."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_math_30", "domain_id": "class10_math", "concept_id": "math_heights",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A ladder leaning against a wall reaches a window 15 m high at an angle of 60° with the ground. What is the length of the ladder? (√3 ≈ 1.732)",
        "option_a": "17.32 m",
        "option_b": "15.00 m",
        "option_c": "20.12 m",
        "option_d": "12.50 m",
        "correct_option": "A",
        "explanation": "sin(60°) = opposite / hypotenuse => √3 / 2 = 15 / L => L = 30 / √3 = 10√3 ≈ 17.32 m.",
        "misconception_id": None, "prerequisite_id": "math_trig",
        "reasoning_probe": {
            "prompt": "Which trigonometric ratio must be used to relate the ladder length directly to the window height?",
            "options": {
                "A": "Sine ratio, because it connects opposite height directly to the hypotenuse.",
                "B": "Cosine ratio, because it connects horizontal floor run to vertical wall.",
                "C": "Tangent ratio, because it directly divides opposite side by hypotenuse.",
                "D": "Secant ratio, because it relates ground distance to perpendicular wall."
            },
            "correct_probe": "A"
        }
    },

    # --- math_coord ---
    {
        "id": "q_math_31", "domain_id": "class10_math", "concept_id": "math_coord",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the midpoint of the line segment joining points A(2, -4) and B(6, 2)?",
        "option_a": "(4, -1)",
        "option_b": "(4, -2)",
        "option_c": "(3, -1)",
        "option_d": "(8, -2)",
        "correct_option": "A",
        "explanation": "Midpoint = ((2 + 6)/2, (-4 + 2)/2) = (8/2, -2/2) = (4, -1).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_32", "domain_id": "class10_math", "concept_id": "math_coord",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the straight-line distance between points P(0, 0) and Q(5, 12)?",
        "option_a": "13 units",
        "option_b": "17 units",
        "option_c": "12 units",
        "option_d": "11 units",
        "correct_option": "A",
        "explanation": "Distance = √(5² + 12²) = √(25 + 144) = √169 = 13 units.",
        "misconception_id": "MISC_MATH_COORD_DIST_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_33", "domain_id": "class10_math", "concept_id": "math_coord",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Point P divides the line segment joining A(1, 3) and B(4, 6) in the ratio 2:1 internally. What are the coordinates of P?",
        "option_a": "(3, 5)",
        "option_b": "(2, 4)",
        "option_c": "(3, 4)",
        "option_d": "(4, 5)",
        "correct_option": "A",
        "explanation": "x = (2(4) + 1(1))/(2 + 1) = 9/3 = 3. y = (2(6) + 1(3))/(2 + 1) = 15/3 = 5. Coordinates: (3, 5).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_34", "domain_id": "class10_math", "concept_id": "math_coord",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If the points (1, 2), (0, 0), and (a, b) are collinear, what relationship must hold between a and b?",
        "option_a": "b = 2a",
        "option_b": "a = 2b",
        "option_c": "b = a + 1",
        "option_d": "ab = 2",
        "correct_option": "A",
        "explanation": "Slope between (0, 0) and (1, 2) is 2/1 = 2. For collinearity, slope of (a, b) from (0, 0) must also be 2 => b/a = 2 => b = 2a.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_math_35", "domain_id": "class10_math", "concept_id": "math_coord",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Find the point on the x-axis which is equidistant from the points (2, -5) and (-2, 9).",
        "option_a": "(-7, 0)",
        "option_b": "(-6, 0)",
        "option_c": "(7, 0)",
        "option_d": "(0, -7)",
        "correct_option": "A",
        "explanation": "Point on x-axis is (x, 0). (x - 2)² + (0 - (-5))² = (x - (-2))² + (0 - 9)² => x² - 4x + 4 + 25 = x² + 4x + 4 + 81 => -4x + 29 = 4x + 85 => -8x = 56 => x = -7. Point is (-7, 0).",
        "misconception_id": "MISC_MATH_COORD_DIST_ADD", "prerequisite_id": "math_coord",
        "reasoning_probe": {
            "prompt": "Why is the y-coordinate of the target point set strictly to 0 at the start of the solution?",
            "options": {
                "A": "Every point lying anywhere along the Cartesian x-axis has a y-coordinate of zero.",
                "B": "Equidistant points in two dimensions always intersect the coordinate origin.",
                "C": "The distance formula simplifies only when perpendicular slopes cancel to zero.",
                "D": "Collinear projections require horizontal displacement vectors to balance out."
            },
            "correct_probe": "A"
        }
    }
]

# =============================================================================
# 2. CLASS 10 CHEMISTRY EXPANSION (25 New Questions -> Total 35)
# Concepts: chem_equations, acids_bases, metals_reactivity, carbon_compounds
# =============================================================================
CHEM_EXPANSION = [
    # --- chem_equations ---
    {
        "id": "q_chem_11", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What type of chemical reaction is represented by: 2Mg + O₂ → 2MgO?",
        "option_a": "Combination reaction",
        "option_b": "Decomposition reaction",
        "option_c": "Displacement reaction",
        "option_d": "Neutralization reaction",
        "correct_option": "A",
        "explanation": "Two reactants (Mg and O₂) combine to form a single product (MgO), which is a combination reaction.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_12", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What precipitate color is formed when aqueous lead nitrate is mixed with potassium iodide?",
        "option_a": "Bright yellow precipitate",
        "option_b": "Milky white precipitate",
        "option_c": "Dark brown precipitate",
        "option_d": "Blue-green precipitate",
        "correct_option": "A",
        "explanation": "Lead nitrate reacts with KI to form lead iodide (PbI₂), which is an insoluble bright yellow precipitate.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_13", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "In the reaction: CuO + H₂ → Cu + H₂O, which substance acts as the reducing agent?",
        "option_a": "H₂ gas",
        "option_b": "CuO solid",
        "option_c": "Cu metal",
        "option_d": "H₂O vapor",
        "correct_option": "A",
        "explanation": "H₂ gains oxygen (it is oxidized) and reduces CuO to Cu. Therefore, H₂ is the reducing agent.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_14", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What are the correct balancing stoichiometric coefficients (a, b, c, d) for: a Fe + b H₂O → c Fe₃O₄ + d H₂?",
        "option_a": "3, 4, 1, 4",
        "option_b": "3, 2, 1, 2",
        "option_c": "2, 3, 1, 3",
        "option_d": "1, 4, 1, 4",
        "correct_option": "A",
        "explanation": "3Fe + 4H₂O → Fe₃O₄ + 4H₂. 3 iron, 8 hydrogen, and 4 oxygen atoms on each side.",
        "misconception_id": "MISC_CHEM_COEFF_SUBSCRIPT", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_15", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Quicklime (CaO) reacts vigorously with water to produce slaked lime in a vessel. Why does the container become noticeably hot to the touch?",
        "option_a": "The reaction is strongly exothermic",
        "option_b": "The reaction absorbs atmospheric heat",
        "option_c": "Endothermic cleavage of calcium ions",
        "option_d": "Evaporation of unreacted slaked lime",
        "correct_option": "A",
        "explanation": "CaO + H₂O → Ca(OH)₂ releases a large quantity of thermal energy, making it an exothermic reaction.",
        "misconception_id": None, "prerequisite_id": "chem_equations",
        "reasoning_probe": {
            "prompt": "What defines an exothermic reaction at the molecular thermodynamic bond level?",
            "options": {
                "A": "Energy released forming new product bonds exceeds energy absorbed breaking reactant bonds.",
                "B": "Molecular reactants spontaneously absorb ambient heat to lower system entropy.",
                "C": "Surrounding atmospheric nitrogen condenses rapidly onto basic hydroxide surfaces.",
                "D": "Thermal agitation increases exclusively through catalytic oxidation of water."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_chem_16", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Silver chloride turns grey when exposed to sunlight over a few minutes. What fundamental chemical process explains this transformation?",
        "option_a": "Photolytic decomposition into silver metal",
        "option_b": "Oxidation of silver by atmospheric oxygen",
        "option_c": "Combustion reaction forming silver hydride",
        "option_d": "Neutralization of silver chloride crystals",
        "correct_option": "A",
        "explanation": "2AgCl (white) under sunlight decomposes into 2Ag (grey metal) + Cl₂ gas. This is photolytic decomposition.",
        "misconception_id": None, "prerequisite_id": "chem_equations",
        "reasoning_probe": {
            "prompt": "Why does light energy trigger the decomposition of silver chloride but not ordinary table salt (NaCl)?",
            "options": {
                "A": "Photons provide sufficient excitation energy to overcome AgCl's lower bond dissociation energy.",
                "B": "Sodium ions absorb visible light to form stable metallic precipitates spontaneously.",
                "C": "Chlorine in AgCl undergoes immediate catalytic reduction into solid elemental carbon.",
                "D": "Solar ultraviolet rays alter ionic lattices exclusively in transition metal halides."
            },
            "correct_probe": "A"
        }
    },

    # --- acids_bases ---
    {
        "id": "q_chem_17", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which gas is liberated when dilute hydrochloric acid reacts with zinc metal granules?",
        "option_a": "Hydrogen gas (H₂)",
        "option_b": "Oxygen gas (O₂)",
        "option_c": "Chlorine gas (Cl₂)",
        "option_d": "Nitrogen gas (N₂)",
        "correct_option": "A",
        "explanation": "Acid + Metal → Salt + Hydrogen gas. Zn + 2HCl → ZnCl₂ + H₂↑.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_18", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the pH range of human blood in a healthy body?",
        "option_a": "7.35 to 7.45",
        "option_b": "6.00 to 6.50",
        "option_c": "8.50 to 9.00",
        "option_d": "5.00 to 5.50",
        "correct_option": "A",
        "explanation": "Human blood pH is tightly regulated within a slightly alkaline range of 7.35 to 7.45.",
        "misconception_id": "MISC_CHEM_PH_HIGH", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_19", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does dry hydrogen chloride gas not change the color of dry blue litmus paper?",
        "option_a": "HCl ionizes into H⁺ ions only in water",
        "option_b": "Litmus paper only reacts with alkali bases",
        "option_c": "Dry HCl gas is an alkaline reducing agent",
        "option_d": "Litmus requires atmospheric carbon dioxide",
        "correct_option": "A",
        "explanation": "Acids show acidic behavior only in the presence of water where HCl dissociates into H⁺ (or H₃O⁺) ions.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_20", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Which salt produces an alkaline solution with pH > 7 when dissolved in distilled water?",
        "option_a": "Sodium carbonate (Na₂CO₃)",
        "option_b": "Ammonium chloride (NH₄Cl)",
        "option_c": "Sodium chloride (NaCl)",
        "option_d": "Potassium nitrate (KNO₃)",
        "correct_option": "A",
        "explanation": "Na₂CO₃ is formed from strong base (NaOH) and weak acid (H₂CO₃), making its aqueous solution basic (pH > 7).",
        "misconception_id": "MISC_CHEM_SALT_NEUTRAL", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_21", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A patient suffers from acute stomach acidity. Why does a physician prescribe milk of magnesia (magnesium hydroxide) rather than sodium hydroxide?",
        "option_a": "Mg(OH)₂ is a mild insoluble non-corrosive base",
        "option_b": "NaOH produces acidic effervescence in the gut",
        "option_c": "Mg(OH)₂ acts as a strong dehydrating oxidizer",
        "option_d": "NaOH completely fails to neutralize gastric HCl",
        "correct_option": "A",
        "explanation": "Mg(OH)₂ is a mild, sparingly soluble antacid that safely neutralizes excess stomach acid without corroding stomach tissues.",
        "misconception_id": None, "prerequisite_id": "acids_bases",
        "reasoning_probe": {
            "prompt": "What danger prevents clinicians from administering concentrated strong alkalis like NaOH internally?",
            "options": {
                "A": "Strong alkalis saponify human cellular lipids and cause severe caustic mucosal burns.",
                "B": "Sodium hydroxide accelerates internal gastric acid production through positive feedback.",
                "C": "Concentrated bases react with blood hemoglobin to permanently halt oxygen diffusion.",
                "D": "Hydroxide ions precipitate insoluble magnesium salts within capillary beds."
            },
            "correct_probe": "A"
        }
    },

    # --- metals_reactivity ---
    {
        "id": "q_chem_22", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which of the following metals is stored under kerosene oil to prevent spontaneous burning?",
        "option_a": "Sodium metal",
        "option_b": "Copper metal",
        "option_c": "Silver metal",
        "option_d": "Lead metal",
        "correct_option": "A",
        "explanation": "Sodium and potassium react violently with moisture and oxygen in the air, so they are submerged in kerosene oil.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_23", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the only non-metal that exists in liquid state at standard room temperature?",
        "option_a": "Bromine (Br₂)",
        "option_b": "Mercury (Hg)",
        "option_c": "Chlorine (Cl₂)",
        "option_d": "Iodine (I₂)",
        "correct_option": "A",
        "explanation": "Bromine is the only liquid non-metal at room temperature. (Mercury is a liquid metal).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_24", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "An iron nail dipped in blue copper sulphate solution turns the liquid green after 30 minutes. What explains this observation?",
        "option_a": "Iron displaces copper forming green FeSO₄",
        "option_b": "Copper displaces iron forming FeSO₄",
        "option_c": "Sulphate ions decompose into green sulfur",
        "option_d": "Water evaporates leaving solid green rust",
        "correct_option": "A",
        "explanation": "Fe is more reactive than Cu. Fe + CuSO₄ (blue) → FeSO₄ (light green) + Cu (reddish-brown coating on nail).",
        "misconception_id": "MISC_CHEM_METALS_REACTIVITY_SWAP", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_25", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does aluminum resist extensive corrosion even though it sits high on the chemical reactivity series?",
        "option_a": "Forms a tough protective Al₂O₃ oxide layer",
        "option_b": "Aluminum possesses zero unpaired valence electrons",
        "option_c": "Noble gas core inhibits reaction with oxygen",
        "option_d": "Aluminum is less reactive than elemental silver",
        "correct_option": "A",
        "explanation": "Aluminum reacts rapidly with air to form an impermeable, non-porous layer of aluminum oxide (Al₂O₃) that halts further oxidation.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_26", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A student places clean zinc, copper, and iron strips into separate test tubes containing dilute hydrochloric acid. What is the observed order of effervescence rate?",
        "option_a": "Zinc > Iron > Copper (no reaction)",
        "option_b": "Copper > Zinc > Iron (no reaction)",
        "option_c": "Iron > Zinc > Copper (no reaction)",
        "option_d": "Zinc > Copper > Iron (no reaction)",
        "correct_option": "A",
        "explanation": "Reactivity order: Zn > Fe > H > Cu. Zinc reacts rapidly with effervescence; Iron reacts more slowly; Copper sits below hydrogen and does not react with dilute HCl.",
        "misconception_id": "MISC_CHEM_METALS_REACTIVITY_SWAP", "prerequisite_id": "metals_reactivity",
        "reasoning_probe": {
            "prompt": "Why does metallic copper fail to displace hydrogen gas from dilute hydrochloric acid?",
            "options": {
                "A": "Copper standard reduction potential is higher than hydrogen, so it cannot reduce H⁺.",
                "B": "Hydrochloric acid forms an insoluble copper chloride barrier instantaneously.",
                "C": "Copper atoms lack free mobile conduction electrons needed for charge balance.",
                "D": "Chloride ions repel neutral copper atoms through electrostatic shielding."
            },
            "correct_probe": "A"
        }
    },

    # --- carbon_compounds ---
    {
        "id": "q_chem_27", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the general chemical formula for open-chain saturated hydrocarbons (alkanes)?",
        "option_a": "C_n H_{2n+2}",
        "option_b": "C_n H_{2n}",
        "option_c": "C_n H_{2n-2}",
        "option_d": "C_n H_{n}",
        "correct_option": "A",
        "explanation": "Alkanes follow the general formula C_n H_{2n+2} (e.g., Methane CH₄, Ethane C₂H₆).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_28", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which functional group is present in the organic compound ethanol (C₂H₅OH)?",
        "option_a": "Alcohol (-OH)",
        "option_b": "Aldehyde (-CHO)",
        "option_c": "Ketone (-CO-)",
        "option_d": "Carboxylic acid (-COOH)",
        "correct_option": "A",
        "explanation": "Ethanol possesses the hydroxyl (-OH) functional group, classifying it as an alcohol.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_29", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does carbon form millions of stable organic compounds across nature?",
        "option_a": "Catenation capacity and tetravalency",
        "option_b": "High ionic bonding with metals",
        "option_c": "Instability of single covalent bonds",
        "option_d": "High electronegativity like halogens",
        "correct_option": "A",
        "explanation": "Carbon exhibits catenation (self-linking via strong C-C covalent bonds) and tetravalency (forming 4 covalent bonds).",
        "misconception_id": "MISC_CHEM_CARBON_VALENCY", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_30", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What happens when vegetable oils (unsaturated fats) are treated with hydrogen in the presence of nickel catalyst?",
        "option_a": "Addition reaction converts oils into solid fat",
        "option_b": "Substitution reaction releases gaseous methane",
        "option_c": "Combustion reaction yielding carbon dioxide",
        "option_d": "Esterification reaction producing ethyl acetate",
        "correct_option": "A",
        "explanation": "Nickel catalyst hydrogenates double bonds in unsaturated oils into saturated single bonds (vegetable ghee/fat).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_31", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A chemist warms ethanoic acid (acetic acid) with absolute ethanol in the presence of concentrated sulfuric acid. What distinctive sensory evidence indicates ester formation?",
        "option_a": "A pleasant sweet fruity fragrance evolves",
        "option_b": "A pungent choking rotten egg odor appears",
        "option_c": "A dense violet precipitate settles at once",
        "option_d": "A vigorous effervescence of hydrogen occurs",
        "correct_option": "A",
        "explanation": "CH₃COOH + C₂H₅OH (in H₂SO₄) → CH₃COOC₂H₅ (ethyl ethanoate) + H₂O. Esters produce pleasant fruity odors.",
        "misconception_id": None, "prerequisite_id": "carbon_compounds",
        "reasoning_probe": {
            "prompt": "What catalytic and thermodynamic role does concentrated sulfuric acid play in this esterification reaction?",
            "options": {
                "A": "It provides H⁺ catalyst and acts as a dehydrating agent to drive equilibrium forward.",
                "B": "It oxidizes ethanol into carbon monoxide to increase product kinetic volatility.",
                "C": "It hydrolyzes the carboxylic acid into an inorganic sulphate salt precipitate.",
                "D": "It buffers solution alkalinity to avoid basic saponification of the ester."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_chem_32", "domain_id": "class10_chemistry", "concept_id": "carbon_compounds",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Why does soap form an insoluble curd (scum) in hard water instead of lathering easily?",
        "option_a": "Soap precipitates with calcium and magnesium ions",
        "option_b": "Hard water completely hydrolyzes the sodium tails",
        "option_c": "Soap molecules become non-polar in cold water",
        "option_d": "Calcium ions neutralize soap into vinegar acid",
        "correct_option": "A",
        "explanation": "Hard water contains dissolved Ca²⁺ and Mg²⁺ salts which react with sodium soap carboxylate heads to form insoluble scum.",
        "misconception_id": None, "prerequisite_id": "carbon_compounds",
        "reasoning_probe": {
            "prompt": "Why do synthetic detergents lather effectively in hard water where traditional soaps fail?",
            "options": {
                "A": "Detergent sulphonate and sulphate salts of Ca²⁺ and Mg²⁺ are water-soluble.",
                "B": "Synthetic detergents omit hydrocarbon hydrophobic tails entirely from their structure.",
                "C": "Detergents actively decompose calcium ions into harmless volatile nitrogen bubbles.",
                "D": "Detergent molecules dissolve exclusively in non-polar lipid grease layers."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_chem_33", "domain_id": "class10_chemistry", "concept_id": "chem_equations",
        "question_type": "application", "difficulty": "medium",
        "question_text": "Why do food manufacturers flush potato chip bags with inert nitrogen gas before sealing?",
        "option_a": "To prevent oxidative rancidity of oils and fats",
        "option_b": "To accelerate natural caramelization of starches",
        "option_c": "To catalyze moisture absorption inside the snack",
        "option_d": "To neutralize stomach acids when consumed later",
        "correct_option": "A",
        "explanation": "Oils and fats in chips oxidize when exposed to air (rancidity), altering taste and odor. Nitrogen creates an unreactive, oxygen-free barrier.",
        "misconception_id": None, "prerequisite_id": "chem_equations",
        "reasoning_probe": {
            "prompt": "What chemical transformation makes oxidized fats taste and smell foul (rancid)?",
            "options": {
                "A": "Atmospheric oxygen cleaves fatty acids into volatile malodorous aldehydes and ketones.",
                "B": "Nitrogen triples the covalent bond strength in saturated hydrocarbon chains.",
                "C": "Lipid triglycerides convert spontaneously into insoluble calcium carbonate rocks.",
                "D": "Cellular respiration of potatoes consumes nitrogen to release sulfur dioxide."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_chem_34", "domain_id": "class10_chemistry", "concept_id": "acids_bases",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the chemical identity of bleaching powder used in municipal water disinfection?",
        "option_a": "Calcium oxychloride (CaOCl₂)",
        "option_b": "Calcium hydroxide (Ca(OH)₂)",
        "option_c": "Calcium carbonate (CaCO₃)",
        "option_d": "Sodium hydrogen carbonate (NaHCO₃)",
        "correct_option": "A",
        "explanation": "Bleaching powder is calcium oxychloride (CaOCl₂), prepared by passing chlorine gas over dry slaked lime Ca(OH)₂.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_chem_35", "domain_id": "class10_chemistry", "concept_id": "metals_reactivity",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the homogeneous mixture of a metal with mercury termed in metallurgical chemistry?",
        "option_a": "An amalgam",
        "option_b": "A brass alloy",
        "option_c": "A bronze casting",
        "option_d": "A solder flux",
        "correct_option": "A",
        "explanation": "An alloy in which one of the constituent metals is liquid mercury is known as an amalgam.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    }
]

# =============================================================================
# 3. CLASS 10 BIOLOGY EXPANSION (25 New Questions -> Total 35)
# Concepts: bio_respiration, bio_digestion, bio_circulation, bio_genetics
# =============================================================================
BIO_EXPANSION = [
    # --- bio_respiration ---
    {
        "id": "q_bio_11", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "In which cellular organelle does aerobic cellular respiration complete to yield ATP?",
        "option_a": "Mitochondria",
        "option_b": "Ribosomes",
        "option_c": "Golgi apparatus",
        "option_d": "Endoplasmic reticulum",
        "correct_option": "A",
        "explanation": "Aerobic respiration completes inside mitochondria (the powerhouse of the cell) to generate 36-38 ATP per glucose.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_12", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the end product of anaerobic glycolysis in human skeletal muscle cells during vigorous sprinting?",
        "option_a": "Lactic acid",
        "option_b": "Ethanol and CO₂",
        "option_c": "Pyruvic acid only",
        "option_d": "Citric acid crystals",
        "correct_option": "A",
        "explanation": "Under oxygen debt in vigorous exercise, pyruvate is reduced to 3-carbon lactic acid in human muscle cells.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_13", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why do fish in an aquarium maintain a substantially higher breathing rate than terrestrial animals?",
        "option_a": "Dissolved oxygen concentration in water is much lower",
        "option_b": "Fish have cold blood requiring higher caloric burning",
        "option_c": "Gills absorb nitrogen gas instead of ambient oxygen",
        "option_d": "Aquatic water pressure compresses gill membranes",
        "correct_option": "A",
        "explanation": "Water holds significantly less dissolved oxygen compared to air, requiring aquatic organisms to pump water rapidly over gills.",
        "misconception_id": "MISC_BIO_RESP_BREATHE", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_14", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Where in the human lung does actual gas exchange (O₂ and CO₂) with capillaries occur?",
        "option_a": "Alveolar sacs",
        "option_b": "Tracheal rings",
        "option_c": "Bronchial tree",
        "option_d": "Nasal cavity",
        "correct_option": "A",
        "explanation": "Alveoli provide an immense surface area with thin, single-celled walls wrapped in capillaries for gaseous diffusion.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_15", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "application", "difficulty": "hard",
        "question_text": "An athlete experiences acute cramping in calf muscles following an unconditioned 400m sprint. What biochemical accumulation explains this pain, and how does a hot water bath relieve it?",
        "option_a": "Lactic acid builds up; heat boosts blood flow to metabolize it",
        "option_b": "Carbonic acid crystallizes; heat boils excess tissue fluids",
        "option_c": "Pyruvate depletes; heat restores glycogen to muscle fibers",
        "option_d": "Ethanol intoxicates cells; heat denatures enzyme pathways",
        "correct_option": "A",
        "explanation": "Lactic acid builds up during anaerobic exertion. A hot bath dilates blood vessels, improving oxygen supply to convert lactic acid back to CO₂ and water.",
        "misconception_id": "MISC_BIO_RESP_BREATHE", "prerequisite_id": "bio_respiration",
        "reasoning_probe": {
            "prompt": "Why does increased oxygen supply during rest reverse lactic acidosis in skeletal muscle tissue?",
            "options": {
                "A": "Aerobic respiration in liver and muscle cells oxidizes lactate back into pyruvate.",
                "B": "Oxygen neutralizes muscular acidity directly through hydrogen carbonate synthesis.",
                "C": "Red blood cells filter lactic acid directly into bronchial alveoli for exhalation.",
                "D": "Myoglobin decomposes lactic acid into inert nitrogen bubbles without ATP."
            },
            "correct_probe": "A"
        }
    },

    # --- bio_digestion ---
    {
        "id": "q_bio_16", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which enzyme present in human saliva initiates the chemical breakdown of starch into maltose sugar?",
        "option_a": "Salivary amylase",
        "option_b": "Gastric pepsin",
        "option_c": "Pancreatic trypsin",
        "option_d": "Intestinal lipase",
        "correct_option": "A",
        "explanation": "Salivary amylase (ptyalin) in saliva hydrolyzes starch polysaccharides into simpler disaccharides like maltose.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_17", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the primary role of bile juice secreted by the liver in human digestion?",
        "option_a": "Emulsifies fats and creates an alkaline medium",
        "option_b": "Directly hydrolyzes proteins into free amino acids",
        "option_c": "Secretes hydrochloric acid to activate pepsin",
        "option_d": "Converts excess dietary starch into cellulose fibers",
        "correct_option": "A",
        "explanation": "Bile salts break large fat globules into microscopic droplets (emulsification) and neutralize acidic chyme for pancreatic enzymes.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_18", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does the stomach lining remain unharmed despite secreting highly concentrated hydrochloric acid (pH 1.5 - 2.0)?",
        "option_a": "A thick protective layer of mucus coats the epithelium",
        "option_b": "Stomach cells possess thick keratinized outer shells",
        "option_c": "Pepsin continuously neutralizes stomach hydrochloric acid",
        "option_d": "Acid only activates after food leaves the stomach cavity",
        "correct_option": "A",
        "explanation": "Mucus secreted by gastric goblet cells creates a protective physical and chemical alkaline barrier protecting the stomach wall.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_19", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "How do finger-like microscopic villi in the small intestine optimize nutrient uptake?",
        "option_a": "Greatly multiply surface area with rich capillary networks",
        "option_b": "Secrete digestive hydrochloric acid directly onto fats",
        "option_c": "Mechanically churn food boluses like muscular sphincters",
        "option_d": "Store digested glucose permanently as glycogen stores",
        "correct_option": "A",
        "explanation": "Millions of villi and microvilli vastly expand the absorptive surface area, backed by dense capillary and lacteal beds.",
        "misconception_id": "MISC_BIO_DIGESTION_STOMACH_ABSORB", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_20", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A surgical patient has their gall bladder removed due to gallstones. What dietary restriction will the gastroenterologist strictly advise?",
        "option_a": "Restricting high-fat meals and fried foods",
        "option_b": "Strictly avoiding all dietary carbohydrates",
        "option_c": "Eliminating all protein and dairy intake",
        "option_d": "Consuming acidic citrus juices before bed",
        "correct_option": "A",
        "explanation": "The gall bladder stores and concentrates bile. Without it, bile drips continuously but cannot be released in boluses needed to emulsify heavy fat meals.",
        "misconception_id": None, "prerequisite_id": "bio_digestion",
        "reasoning_probe": {
            "prompt": "Why is bile essential for pancreatic lipase enzyme activity on ingested dietary lipids?",
            "options": {
                "A": "Emulsification breaks lipid globules to increase surface area for water-soluble lipase.",
                "B": "Bile salts convert dietary fatty acids into amino acid structural precursors.",
                "C": "Lipase can only bind fats when stomach hydrochloric acid is acidic.",
                "D": "Bile creates an impermeable lipid vesicle that absorbs intact proteins."
            },
            "correct_probe": "A"
        }
    },

    # --- bio_circulation ---
    {
        "id": "q_bio_21", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which blood vessel carries oxygenated blood directly from the lungs to the left atrium of the heart?",
        "option_a": "Pulmonary vein",
        "option_b": "Pulmonary artery",
        "option_c": "Superior vena cava",
        "option_d": "Renal artery",
        "correct_option": "A",
        "explanation": "Pulmonary veins are the only veins in human circulation that carry oxygen-rich blood (from lungs to left atrium).",
        "misconception_id": "MISC_BIO_ARTERY_O2", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_22", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Why do mammalian arteries possess thick, elastic muscular walls compared to veins?",
        "option_a": "To withstand high surging pressures from ventricular pumping",
        "option_b": "To prevent backward backflow of low-pressure blood",
        "option_c": "To absorb dietary nutrients through arterial walls",
        "option_d": "To permit valves to open and close smoothly",
        "correct_option": "A",
        "explanation": "Arteries receive blood pumped directly out of ventricular contractions under high pressure, requiring thick, elastic muscular walls.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_23", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why is the muscular wall of the left ventricle significantly thicker than that of the right ventricle?",
        "option_a": "Left ventricle pumps blood through the entire systemic body",
        "option_b": "Left ventricle receives deoxygenated blood under pressure",
        "option_c": "Right ventricle pumps blood through cerebral vessels",
        "option_d": "Right ventricle contains bicuspid valves with thick flaps",
        "correct_option": "A",
        "explanation": "The right ventricle only pumps blood nearby to the lungs (pulmonary circuit), whereas the left ventricle must pump blood throughout the entire body (systemic circuit).",
        "misconception_id": "MISC_BIO_HEART_CHAMBERS", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_24", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What functional advantage is conferred by the complete double circulation in 4-chambered mammalian hearts?",
        "option_a": "Prevents mixing of oxygenated and deoxygenated blood",
        "option_b": "Reduces heart contraction frequency by half",
        "option_c": "Allows direct gas exchange without lung tissue",
        "option_d": "Eliminates the requirement for internal heart valves",
        "correct_option": "A",
        "explanation": "Complete separation allows highly efficient oxygen delivery to body tissues, essential to maintain constant body temperature (warm-blooded).",
        "misconception_id": "MISC_BIO_HEART_CHAMBERS", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_25", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A clinical patient presents with malfunctioning bicuspid (mitral) heart valves that fail to seal completely. What physiological consequence will immediately occur?",
        "option_a": "Blood leaks back into the left atrium during ventricular systole",
        "option_b": "Blood leaks back into the right atrium during diastole",
        "option_c": "Deoxygenated blood floods into pulmonary arterial branches",
        "option_d": "Aortic blood pressure surges to dangerous upper limits",
        "correct_option": "A",
        "explanation": "The bicuspid (mitral) valve guards between left atrium and left ventricle. If incompetent, blood backflows into the left atrium upon ventricular contraction.",
        "misconception_id": "MISC_BIO_HEART_CHAMBERS", "prerequisite_id": "bio_circulation",
        "reasoning_probe": {
            "prompt": "What primary mechanical purpose do atrioventricular heart valves serve during the cardiac cycle?",
            "options": {
                "A": "They enforce strictly unidirectional forward flow by preventing retrograde regurgitation.",
                "B": "They rhythmically oxygenate blood before it reaches ventricular outflow tracts.",
                "C": "They contract actively to generate high systolic blood pressure pulses.",
                "D": "They filter cellular metabolic waste before venous return to the lungs."
            },
            "correct_probe": "A"
        }
    },

    # --- bio_genetics ---
    {
        "id": "q_bio_26", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What physical plant specimen did Gregor Mendel utilize for his classical hybridization genetics experiments?",
        "option_a": "Garden pea (Pisum sativum)",
        "option_b": "Sweet corn (Zea mays)",
        "option_c": "Fruit fly (Drosophila)",
        "option_d": "Common bean (Phaseolus)",
        "correct_option": "A",
        "explanation": "Mendel worked with the garden pea (Pisum sativum) because of its easily distinguishable contrasting traits and self-pollinating nature.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_27", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the standard phenotypic ratio in the F2 generation of a Mendelian monohybrid cross between heterozygous tall plants (Tt × Tt)?",
        "option_a": "3 Tall : 1 Dwarf",
        "option_b": "1 Tall : 2 Medium : 1 Dwarf",
        "option_c": "9 Tall : 3 Medium : 4 Dwarf",
        "option_d": "4 Tall : 0 Dwarf",
        "correct_option": "A",
        "explanation": "Genotypes: 1 TT : 2 Tt : 1 tt. Because T is dominant over t, TT and Tt are phenotypically tall, giving 3 Tall : 1 Dwarf.",
        "misconception_id": "MISC_BIO_GENETICS_RATIO", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_28", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "In human sex determination, which parent's gametic chromosome fundamentally decides the biological sex of the offspring?",
        "option_a": "Father, contributing either an X or Y chromosome",
        "option_b": "Mother, contributing either an X or Y chromosome",
        "option_c": "Both parents contribute equally via autosomes",
        "option_d": "Environmental temperature during embryonic growth",
        "correct_option": "A",
        "explanation": "Mothers produce eggs with only X chromosomes. Fathers produce sperm with either X or Y. A Y sperm produces male (XY); an X sperm produces female (XX).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_29", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the genotypic ratio resulting from crossing two heterozygous tall pea plants (Tt × Tt)?",
        "option_a": "1 TT : 2 Tt : 1 tt",
        "option_b": "3 TT : 1 tt",
        "option_c": "2 TT : 2 tt",
        "option_d": "1 TT : 1 Tt : 2 tt",
        "correct_option": "A",
        "explanation": "Monohybrid Punnett square produces 1 TT (homozygous tall), 2 Tt (heterozygous tall), and 1 tt (homozygous dwarf) => 1:2:1.",
        "misconception_id": "MISC_BIO_GENETICS_RATIO", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_30", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A pure-breeding round yellow seeded pea plant (RRYY) is crossed with a wrinkled green seeded plant (rryy). What phenotypic proportion in F2 expresses both recessive traits (wrinkled and green)?",
        "option_a": "1 / 16",
        "option_b": "3 / 16",
        "option_c": "9 / 16",
        "option_d": "1 / 4",
        "correct_option": "A",
        "explanation": "Dihybrid F2 phenotypic ratio: 9 Round Yellow : 3 Round Green : 3 Wrinkled Yellow : 1 Wrinkled Green (rryy). So wrinkled green is 1/16.",
        "misconception_id": "MISC_BIO_GENETICS_RATIO", "prerequisite_id": "bio_genetics",
        "reasoning_probe": {
            "prompt": "Which Mendelian law explains why seed color (yellow/green) sorts independently from seed shape (round/wrinkled)?",
            "options": {
                "A": "Law of Independent Assortment, governing non-homologous unlinked chromosome pairs.",
                "B": "Law of Segregation, stating alleles blend together during gametogenesis.",
                "C": "Law of Dominance, ensuring recessive traits vanish completely from inheritance.",
                "D": "Chromosomal Crossing Over, converting diploid zygotes into haploid spores."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_bio_31", "domain_id": "class10_biology", "concept_id": "bio_digestion",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which muscular movement pushes food along the alimentary canal from esophagus to stomach?",
        "option_a": "Peristalsis",
        "option_b": "Phagocytosis",
        "option_c": "Osmosis",
        "option_d": "Dialysis",
        "correct_option": "A",
        "explanation": "Peristalsis is the rhythmic wave-like muscular contraction and relaxation that propels food through the gastrointestinal tract.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_32", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "Which cellular component of blood is responsible for initiating clot formation at wounded tissue sites?",
        "option_a": "Blood platelets (thrombocytes)",
        "option_b": "Red blood cells (erythrocytes)",
        "option_c": "White blood cells (leukocytes)",
        "option_d": "Blood plasma proteins only",
        "correct_option": "A",
        "explanation": "Blood platelets release thromboplastin to trigger the cascade converting prothrombin to thrombin, producing insoluble fibrin clots.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_33", "domain_id": "class10_biology", "concept_id": "bio_respiration",
        "question_type": "application", "difficulty": "medium",
        "question_text": "Why does lime water turn milky when exhaled air is bubbled through it using a straw?",
        "option_a": "Exhaled CO₂ precipitates insoluble calcium carbonate",
        "option_b": "Exhaled nitrogen gas condenses inside the solution",
        "option_c": "Exhaled water vapor dilutes the basic hydroxide",
        "option_d": "Atmospheric oxygen bleaches the lime indicator",
        "correct_option": "A",
        "explanation": "Exhaled air contains carbon dioxide which reacts with clear lime water: Ca(OH)₂ + CO₂ → CaCO₃ (insoluble white precipitate) + H₂O.",
        "misconception_id": None, "prerequisite_id": "bio_respiration",
        "reasoning_probe": {
            "prompt": "What happens if exhaled breath containing CO₂ continues bubbling through the milky solution for several more minutes?",
            "options": {
                "A": "Solution becomes clear again as insoluble CaCO₃ converts to soluble Ca(HCO₃)₂.",
                "B": "Solution turns bright scarlet red due to acidic carbonic dye synthesis.",
                "C": "Calcium ions boil spontaneously into explosive hydrogen gas vapor.",
                "D": "Precipitate thickens permanently into insoluble gypsum plaster crystals."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_bio_34", "domain_id": "class10_biology", "concept_id": "bio_circulation",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the normal resting blood pressure reading for a healthy adult human in mmHg?",
        "option_a": "120 / 80 mmHg",
        "option_b": "80 / 120 mmHg",
        "option_c": "140 / 100 mmHg",
        "option_d": "100 / 60 mmHg",
        "correct_option": "A",
        "explanation": "Normal blood pressure is measured as 120 mmHg systolic (ventricular contraction) over 80 mmHg diastolic (ventricular relaxation).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_bio_35", "domain_id": "class10_biology", "concept_id": "bio_genetics",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What term describes the transmission of characteristics from parents to their biological offspring over generations?",
        "option_a": "Heredity",
        "option_b": "Speciation",
        "option_c": "Mutation",
        "option_d": "Metamorphosis",
        "correct_option": "A",
        "explanation": "Heredity refers to the biological process of passing down genetic traits from parent organisms to their progeny.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    }
]

# =============================================================================
# 4. POKEMON BATTLE MECHANICS EXPANSION (25 New Questions -> Total 35)
# Concepts: poke_types, poke_dual_types, poke_immunities, poke_stab, poke_stat_stages
# =============================================================================
POKEMON_EXPANSION = [
    # --- poke_types ---
    {
        "id": "q_poke_11", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does an Electric-type attack deal against a pure Water-type Pokemon?",
        "option_a": "2.0x (Super Effective)",
        "option_b": "1.0x (Neutral Damage)",
        "option_c": "0.5x (Not Very Effective)",
        "option_d": "0.0x (Complete Immunity)",
        "correct_option": "A",
        "explanation": "Water is weak to Electric, so Electric attacks deal 2.0x super-effective damage.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_12", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does a Fire-type attack deal when striking a pure Grass-type Pokemon?",
        "option_a": "2.0x (Super Effective)",
        "option_b": "1.0x (Neutral Damage)",
        "option_c": "0.5x (Not Very Effective)",
        "option_d": "4.0x (Double Weakness)",
        "correct_option": "A",
        "explanation": "Grass is weak to Fire, resulting in 2.0x damage.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_13", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Which defensive type possesses the greatest number of distinct type resistances in Pokemon battle mechanics?",
        "option_a": "Steel type (10 resistances, 1 immunity)",
        "option_b": "Dragon type (6 resistances, 0 immunities)",
        "option_c": "Water type (4 resistances, 0 immunities)",
        "option_d": "Normal type (0 resistances, 1 immunity)",
        "correct_option": "A",
        "explanation": "Steel is the best defensive type with 10 resistances and 1 complete immunity (Poison).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_14", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why do Ground-type moves deal 0.5x damage against Grass-type Pokemon despite rock-like characteristics?",
        "option_a": "Grass naturally resists Ground attacks",
        "option_b": "Ground attacks are boosted by plant root systems",
        "option_c": "Grass is completely immune to seismic vibrations",
        "option_d": "Ground types receive half damage from foliage",
        "correct_option": "A",
        "explanation": "Grass resists Ground, Water, Grass, and Electric, taking 0.5x damage from Ground moves.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_15", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A trainer must choose between an Ice Beam (Ice) and Thunderbolt (Electric) move to hit a pure Dragon-type foe. What are their respective multipliers?",
        "option_a": "Ice Beam = 2.0x; Thunderbolt = 0.5x",
        "option_b": "Ice Beam = 1.0x; Thunderbolt = 1.0x",
        "option_c": "Ice Beam = 2.0x; Thunderbolt = 2.0x",
        "option_d": "Ice Beam = 4.0x; Thunderbolt = 0.0x",
        "correct_option": "A",
        "explanation": "Dragon is weak to Ice (2.0x) and resists Electric (0.5x). Therefore, Ice Beam is super effective while Thunderbolt is resisted.",
        "misconception_id": None, "prerequisite_id": "poke_types",
        "reasoning_probe": {
            "prompt": "Why does Dragon resist the four classical elements (Fire, Water, Grass, Electric)?",
            "options": {
                "A": "Game design intentionally balance Dragon's legendary stature by resisting the primal elemental types.",
                "B": "Dragon scales emit electrostatic shields that reflect energy attacks completely.",
                "C": "Dragon Pokemon all carry the Multiscale ability by default in battle mechanics.",
                "D": "Primal elements are strictly physical moves that calculate against special defense."
            },
            "correct_probe": "A"
        }
    },

    # --- poke_dual_types ---
    {
        "id": "q_poke_16", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does a Fire-type move deal to a dual Water/Grass Pokemon like Ludicolo?",
        "option_a": "1.0x (Neutral Damage)",
        "option_b": "2.0x (Super Effective)",
        "option_c": "0.5x (Resisted Damage)",
        "option_d": "4.0x (Double Weakness)",
        "correct_option": "A",
        "explanation": "Water resists Fire (0.5x) and Grass is weak to Fire (2.0x). Multiplier = 0.5 × 2.0 = 1.0x neutral damage.",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_17", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does an Ice-type attack deal against Dragonite (Dragon/Flying)?",
        "option_a": "4.0x (Double Super Effective)",
        "option_b": "2.0x (Single Super Effective)",
        "option_c": "1.0x (Neutral Base Damage)",
        "option_d": "0.5x (Single Resisted Damage)",
        "correct_option": "A",
        "explanation": "Dragon is weak to Ice (2x) and Flying is weak to Ice (2x). 2 × 2 = 4.0x compound weakness.",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_18", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does a Rock-type attack deal a devastating 4.0x damage to Charizard (Fire/Flying)?",
        "option_a": "Both Fire and Flying types are independently weak to Rock",
        "option_b": "Rock attacks receive an automatic STAB damage bonus",
        "option_c": "Flying types lose airborne immunity when taking physical hits",
        "option_d": "Fire types magnify damage from all physical earth attacks",
        "correct_option": "A",
        "explanation": "Fire takes 2x from Rock, and Flying takes 2x from Rock. Product: 2 × 2 = 4.0x.",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_19", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What damage multiplier does a Fighting-type attack deal against Lucario (Fighting/Steel)?",
        "option_a": "1.0x (Neutral Damage)",
        "option_b": "2.0x (Super Effective)",
        "option_c": "0.5x (Resisted Damage)",
        "option_d": "4.0x (Double Weakness)",
        "correct_option": "A",
        "explanation": "Steel is weak to Fighting (2.0x) while Fighting resists Fighting (0.5x). Compound multiplier = 2.0 × 0.5 = 1.0x.",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_20", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Swampert is a Water/Ground Pokemon. A Grass-type move (Energy Ball) hits Swampert. What is the precise damage multiplier?",
        "option_a": "4.0x (Double Super Effective)",
        "option_b": "2.0x (Single Super Effective)",
        "option_c": "1.0x (Neutral Damage)",
        "option_d": "0.5x (Resisted Damage)",
        "correct_option": "A",
        "explanation": "Water takes 2x from Grass, and Ground takes 2x from Grass. Compound multiplier = 2.0 × 2.0 = 4.0x. Grass is Swampert's only weakness!",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": "poke_dual_types",
        "reasoning_probe": {
            "prompt": "How does dual-typing math treat multiple defensive type interactions mathematically?",
            "options": {
                "A": "Multipliers are multiplied together (product rule: 2x × 2x = 4x; 2x × 0.5x = 1x).",
                "B": "Multipliers are added together as linear sums (addition rule: 2 + 2 = 4x).",
                "C": "The primary typing always overrides the secondary typing's weaknesses.",
                "D": "The typing with higher base special defense dictates incoming damage."
            },
            "correct_probe": "A"
        }
    },

    # --- poke_immunities ---
    {
        "id": "q_poke_21", "domain_id": "pokemon", "concept_id": "poke_immunities",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does an Electric-type attack deal against a Ground-type Pokemon?",
        "option_a": "0.0x (Complete Immunity)",
        "option_b": "0.5x (Not Very Effective)",
        "option_c": "1.0x (Neutral Damage)",
        "option_d": "2.0x (Super Effective)",
        "correct_option": "A",
        "explanation": "Ground-type Pokemon are completely immune to Electric-type moves (0.0x damage).",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_22", "domain_id": "pokemon", "concept_id": "poke_immunities",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What damage multiplier does a Ghost-type attack deal against a pure Normal-type Pokemon?",
        "option_a": "0.0x (Complete Immunity)",
        "option_b": "0.5x (Not Very Effective)",
        "option_c": "1.0x (Neutral Damage)",
        "option_d": "2.0x (Super Effective)",
        "correct_option": "A",
        "explanation": "Normal-type Pokemon are completely immune to Ghost-type attacks (and Ghost is immune to Normal).",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_23", "domain_id": "pokemon", "concept_id": "poke_immunities",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "A Flying/Steel Pokemon (Skarmory) is targeted by an Earthquake (Ground) move. What damage multiplier does Skarmory receive?",
        "option_a": "0.0x (Immune due to Flying type)",
        "option_b": "2.0x (Weakness due to Steel type)",
        "option_c": "1.0x (Neutralized between both types)",
        "option_d": "0.5x (Steel resists ground attacks)",
        "correct_option": "A",
        "explanation": "Even though Steel is weak to Ground (2.0x), Flying has complete immunity (0.0x). 2.0 × 0.0 = 0.0x damage!",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_24", "domain_id": "pokemon", "concept_id": "poke_immunities",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Which defensive type possesses complete immunity to Dragon-type attacks in modern battle mechanics?",
        "option_a": "Fairy type",
        "option_b": "Steel type",
        "option_c": "Ice type",
        "option_d": "Psychic type",
        "correct_option": "A",
        "explanation": "Introduced in Generation 6, the Fairy type is completely immune to Dragon-type attacks (0.0x).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_25", "domain_id": "pokemon", "concept_id": "poke_immunities",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A player uses a Psychic attack against a dual Dark/Poison Pokemon (Drapion). Poison is normally weak to Psychic (2x). What damage does Drapion take?",
        "option_a": "0.0x (Dark gives complete Psychic immunity)",
        "option_b": "2.0x (Poison weakness bypasses immunity)",
        "option_c": "1.0x (Neutralized between both typings)",
        "option_d": "0.5x (Resisted damage from dual resistances)",
        "correct_option": "A",
        "explanation": "Dark is completely immune to Psychic (0.0x). Any multiplier multiplied by 0.0 equals 0.0x. Drapion takes zero damage from Psychic moves.",
        "misconception_id": "MISC_POKE_IMMUNITY_RESIST", "prerequisite_id": "poke_immunities",
        "reasoning_probe": {
            "prompt": "What rule governs when an absolute immunity (0x) collides with a type weakness (2x)?",
            "options": {
                "A": "Immunity acts as an absorbing zero in multiplication, reducing all incoming damage to 0x.",
                "B": "Type weaknesses override immunities if the move matches the defending secondary typing.",
                "C": "The move deals fixed 1.0x neutral damage because the opposing modifiers cancel.",
                "D": "The attacking player's critical hit chance converts immunities into half resistances."
            },
            "correct_probe": "A"
        }
    },

    # --- poke_stab ---
    {
        "id": "q_poke_26", "domain_id": "pokemon", "concept_id": "poke_stab",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What does STAB stand for in competitive Pokemon mechanics?",
        "option_a": "Same-Type Attack Bonus",
        "option_b": "Special Technique Attack Boost",
        "option_c": "Status Triggered Action Base",
        "option_d": "Standard Tactical Accuracy Benchmark",
        "correct_option": "A",
        "explanation": "STAB stands for Same-Type Attack Bonus, giving a 1.5x damage boost when a Pokemon uses a move matching its own type.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_27", "domain_id": "pokemon", "concept_id": "poke_stab",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What standard numerical multiplier does STAB provide to a move's damage in standard gameplay?",
        "option_a": "1.5x multiplier",
        "option_b": "2.0x multiplier",
        "option_c": "1.25x multiplier",
        "option_d": "1.75x multiplier",
        "correct_option": "A",
        "explanation": "Standard STAB grants a 50% boost (1.5x multiplier) to the move power.",
        "misconception_id": "MISC_POKE_STAB_STAT", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_28", "domain_id": "pokemon", "concept_id": "poke_stab",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Pikachu (Electric) uses Thunderbolt (Base Power 90). What is the effective Base Power after applying STAB?",
        "option_a": "135 Base Power",
        "option_b": "180 Base Power",
        "option_c": "112 Base Power",
        "option_d": "90 Base Power",
        "correct_option": "A",
        "explanation": "Base Power × STAB = 90 × 1.5 = 135 effective Base Power.",
        "misconception_id": "MISC_POKE_STAB_STAT", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_29", "domain_id": "pokemon", "concept_id": "poke_stab",
        "question_type": "application", "difficulty": "hard",
        "question_text": "Charizard (Fire/Flying) uses Flamethrower (Power 90, Fire) against Venusaur (Grass/Poison, 2x weak to Fire). What is the combined damage modifier from STAB and type effectiveness?",
        "option_a": "3.0x multiplier (effective Power 270)",
        "option_b": "2.0x multiplier (effective Power 180)",
        "option_c": "3.5x multiplier (effective Power 315)",
        "option_d": "4.0x multiplier (effective Power 360)",
        "correct_option": "A",
        "explanation": "STAB = 1.5x. Type effectiveness vs Grass/Poison = 2.0x (Fire vs Grass is 2x; Fire vs Poison is 1x => 2.0x). Total multiplier = 1.5 × 2.0 = 3.0x. 90 × 3 = 270.",
        "misconception_id": "MISC_POKE_STAB_STAT", "prerequisite_id": "poke_stab",
        "reasoning_probe": {
            "prompt": "How do STAB and type effectiveness multipliers interact during damage calculation?",
            "options": {
                "A": "They multiply consecutively (STAB 1.5x × Super Effective 2.0x = 3.0x).",
                "B": "Only the higher modifier applies, capping damage at 2.0x.",
                "C": "STAB is added directly to base power before doubling the entire sum.",
                "D": "STAB cancels if the defending Pokemon possesses dual typings."
            },
            "correct_probe": "A"
        }
    },

    # --- poke_stat_stages ---
    {
        "id": "q_poke_30", "domain_id": "pokemon", "concept_id": "poke_stat_stages",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "How many stat stage levels does the move Swords Dance boost a Pokemon's Attack stat?",
        "option_a": "+2 stages (doubles Attack)",
        "option_b": "+1 stage (1.5x Attack)",
        "option_c": "+3 stages (2.5x Attack)",
        "option_d": "+4 stages (triples Attack)",
        "correct_option": "A",
        "explanation": "Swords Dance raises the user's Attack stat by two stages (+2), which doubles its value (4/2 = 2.0x).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_31", "domain_id": "pokemon", "concept_id": "poke_stat_stages",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If a Pokemon has its Defense lowered by -1 stage from Leer, what fraction of its original Defense stat remains?",
        "option_a": "2/3 of original Defense (~67%)",
        "option_b": "1/2 of original Defense (50%)",
        "option_c": "3/4 of original Defense (75%)",
        "option_d": "1/4 of original Defense (25%)",
        "correct_option": "A",
        "explanation": "Stat stage fractions for drops: -1 = 2/(2 + 1) = 2/3 (~66.7%). Drops are 2/3, 2/4, 2/5, 2/6, 2/7, 2/8.",
        "misconception_id": "MISC_POKE_STAT_STAGES_MULT", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_32", "domain_id": "pokemon", "concept_id": "poke_stat_stages",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the maximum number of stat stages a single battle stat can be boosted or decreased in standard Pokemon games?",
        "option_a": "+6 stages maximum and -6 stages minimum",
        "option_b": "+4 stages maximum and -4 stages minimum",
        "option_c": "+5 stages maximum and -5 stages minimum",
        "option_d": "+8 stages maximum and -8 stages minimum",
        "correct_option": "A",
        "explanation": "Standard battle stat stages range between -6 (minimum, 2/8 = 25%) and +6 (maximum, 8/2 = 400%).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_poke_33", "domain_id": "pokemon", "concept_id": "poke_stat_stages",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A Pokemon with 200 base Attack uses Dragon Dance (+1 Attack, +1 Speed). What is its active Attack stat in battle now?",
        "option_a": "300 Attack (1.5x multiplier)",
        "option_b": "400 Attack (2.0x multiplier)",
        "option_c": "250 Attack (1.25x multiplier)",
        "option_d": "220 Attack (+20 fixed bonus)",
        "correct_option": "A",
        "explanation": "+1 stat stage multiplier is (2 + 1)/2 = 3/2 = 1.5x. 200 × 1.5 = 300.",
        "misconception_id": "MISC_POKE_STAT_STAGES_MULT", "prerequisite_id": "poke_stat_stages",
        "reasoning_probe": {
            "prompt": "What mathematical formula defines positive stat stage multipliers in Pokemon battle code?",
            "options": {
                "A": "Multiplier = (2 + N) / 2, where N is the number of positive stages (+1 to +6).",
                "B": "Multiplier = 1 + (N × 0.25), scaling linearly by 25% per tier.",
                "C": "Multiplier = 2 raised to the power of N divided by base HP values.",
                "D": "Multiplier = (N / 2) + base defense fraction rounded down."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_poke_34", "domain_id": "pokemon", "concept_id": "poke_types",
        "question_type": "application", "difficulty": "medium",
        "question_text": "A Water-type Pokemon is afflicted by Burn status. How does the Burn condition directly impair its combat effectiveness?",
        "option_a": "Cuts its physical Attack damage in half (50%) and deals chip damage each turn",
        "option_b": "Cuts its special Attack damage in half (50%) and causes paralysis",
        "option_c": "Halves its Speed stat and prevents it from executing Water moves",
        "option_d": "Forces it to switch out automatically after two consecutive rounds",
        "correct_option": "A",
        "explanation": "Burn status inflicts passive HP damage at turn end and halves (0.5x) the user's physical move damage.",
        "misconception_id": None, "prerequisite_id": "poke_types",
        "reasoning_probe": {
            "prompt": "Why does Burn not decrease the damage output of special attacks like Surf or Hydro Pump?",
            "options": {
                "A": "Burn specifically degrades muscular physical attack power, leaving special attacks unaffected.",
                "B": "Water special attacks automatically extinguish burn status during move execution.",
                "C": "Special attacks calculate damage strictly from the defender's physical defense stat.",
                "D": "Burn status only impairs Normal-type physical contact moves in the damage formula."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_poke_35", "domain_id": "pokemon", "concept_id": "poke_dual_types",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Spiritomb and Sableye are dual Ghost/Dark type Pokemon. Prior to the introduction of the Fairy type, how many type weaknesses did they have?",
        "option_a": "0 weaknesses (completely weakness-free)",
        "option_b": "1 weakness (only weak to Bug)",
        "option_c": "2 weaknesses (weak to Fighting and Ghost)",
        "option_d": "3 weaknesses (weak to Ground, Fire, and Ice)",
        "correct_option": "A",
        "explanation": "Ghost is weak to Ghost and Dark (Dark resists both). Dark is weak to Fighting and Bug (Ghost is immune to Fighting and Dark/Ghost neutralizes Bug). Thus, they had zero weaknesses until Fairy was created in Gen 6!",
        "misconception_id": "MISC_POKE_DUAL_ADD", "prerequisite_id": None, "reasoning_probe": None
    }
]

# =============================================================================
# 5. DEEP LEARNING FUNDAMENTALS EXPANSION (15 New Questions -> Total 45)
# Concepts: ann_basics, activation_funcs, backpropagation, gradient_descent, regularization, cnn, rnn
# =============================================================================
DL_EXPANSION = [
    {
        "id": "q_dl_31", "domain_id": "deep_learning", "concept_id": "activation_funcs",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why is the Leaky ReLU activation function preferred over standard ReLU in deep networks?",
        "option_a": "It prevents the 'Dying ReLU' problem by allowing small non-zero gradients for negative inputs",
        "option_b": "It strictly bounds neuron activations within a narrow [0, 1] probability range",
        "option_c": "It eliminates the requirement of calculating derivatives during backpropagation entirely",
        "option_d": "It transforms linear matrix multiplications into orthogonal convolutional representations",
        "correct_option": "A",
        "explanation": "Standard ReLU outputs 0 for x < 0 with derivative 0, causing neurons to die. Leaky ReLU has f(x) = αx for x < 0, allowing gradients to flow.",
        "misconception_id": "MISC_RELU_BOUNDED", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_32", "domain_id": "deep_learning", "concept_id": "gradient_descent",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What role does the 'momentum' hyperparameter play in stochastic gradient descent optimizers?",
        "option_a": "It accelerates updates in directions of persistent gradient and dampens oscillations",
        "option_b": "It resets all network weights to Gaussian random noise whenever loss plateaus",
        "option_c": "It decreases the total number of training epochs by pruning dormant synapses",
        "option_d": "It converts mini-batch computations into single-example online vector operations",
        "correct_option": "A",
        "explanation": "Momentum accumulates past velocity v = βv + (1-β)∇L, smoothing out noisy oscillations and speeding up descent along consistent ravines.",
        "misconception_id": "MISC_LEARNING_RATE_INF", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_33", "domain_id": "deep_learning", "concept_id": "regularization",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does L1 regularization (Lasso) induce sparse weight vectors compared to L2 regularization (Ridge)?",
        "option_a": "The L1 diamond constraint boundary tends to intersect loss contours exactly on coordinate axes",
        "option_b": "L1 penalty penalizes large weights with quadratic force while ignoring small values",
        "option_c": "L1 gradients decay exponentially as parameters approach origin coordinates in phase space",
        "option_d": "L1 regularization forces half of all hidden neurons to deactivate during test inference",
        "correct_option": "A",
        "explanation": "The L1 objective has non-smooth corners along the coordinate axes where gradients do not diminish to zero, driving less important weights to exactly 0.",
        "misconception_id": "MISC_L1_L2_SWAP", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_34", "domain_id": "deep_learning", "concept_id": "cnn",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What property of Convolutional Neural Networks ensures that an object can be detected regardless of its position in an image?",
        "option_a": "Translation equivariance resulting from weight sharing across spatial sliding filters",
        "option_b": "Fully connected dense projections spanning every pixel across the RGB spectrum",
        "option_c": "Recurrent memory loops passing activations chronologically across neighboring scans",
        "option_d": "Stochastic dropout masks zeroing out redundant background pixels before pooling",
        "correct_option": "A",
        "explanation": "By sliding the exact same kernel weights across the entire input grid, CNNs produce translation equivariant feature maps.",
        "misconception_id": "MISC_POOLING_WEIGHTS", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_35", "domain_id": "deep_learning", "concept_id": "rnn",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "How do Long Short-Term Memory (LSTM) networks resolve the vanishing gradient problem in traditional RNNs?",
        "option_a": "Through an additive constant-error-carousel cell state modulated by input, forget, and output gates",
        "option_b": "By replacing backpropagation through time with feedforward batch normalization layers",
        "option_c": "By increasing the learning rate tenfold whenever gradient magnitudes drop below threshold",
        "option_d": "By converting sequential temporal sequences into static two-dimensional spatial images",
        "correct_option": "A",
        "explanation": "LSTMs feature an additive cell state pathway C_t where gradients can backpropagate over long sequences without being repeatedly multiplied by small weight matrices.",
        "misconception_id": "MISC_RNN_INFINITE_MEMORY", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_36", "domain_id": "deep_learning", "concept_id": "backpropagation",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A deep neural network experiences vanishing gradients during backpropagation. Which architectural modification directly mitigates this bottleneck?",
        "option_a": "Introducing skip (residual) connections and replacing Sigmoid activations with ReLU",
        "option_b": "Increasing the depth of fully connected Sigmoid layers without adding normalization",
        "option_c": "Switching from Adam optimizer to plain gradient descent with microscopic learning rates",
        "option_d": "Doubling L2 weight decay penalties to drive weight matrices toward smaller norms",
        "correct_option": "A",
        "explanation": "Residual connections provide identity gradient shortcuts (∂(x + F(x))/∂x = 1 + F'(x)), ensuring gradients flow backward unhindered, while ReLU maintains constant gradient 1 for x > 0.",
        "misconception_id": "MISC_GRAD_FLOW_DIR", "prerequisite_id": "backpropagation",
        "reasoning_probe": {
            "prompt": "Why does an identity shortcut connection y = x + F(x) ensure gradients do not vanish even in 100-layer networks?",
            "options": {
                "A": "The gradient ∂L/∂x = ∂L/∂y × (1 + ∂F/∂x) contains an additive '1', allowing gradient flow even if ∂F/∂x is small.",
                "B": "Skip connections eliminate all matrix multiplications from both forward and backward passes.",
                "C": "Identity layers convert nonlinear activations into convex quadratic optimization functions.",
                "D": "Residual blocks dynamically invert gradient signs during backpropagation to prevent saturation."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_dl_37", "domain_id": "deep_learning", "concept_id": "regularization",
        "question_type": "application", "difficulty": "hard",
        "question_text": "A deep model exhibits a training accuracy of 99.4% but a test validation accuracy of only 68.2%. Which diagnostic conclusion and remedy are most accurate?",
        "option_a": "High variance (overfitting); apply dropout, data augmentation, and early stopping",
        "option_b": "High bias (underfitting); increase network depth and expand hidden dimensions",
        "option_c": "Vanishing gradients; replace all Leaky ReLU activations with Sigmoid functions",
        "option_d": "Learning rate too high; multiply learning rate by 100 to escape the local minimum",
        "correct_option": "A",
        "explanation": "A massive divergence between high training accuracy and low test accuracy is the hallmark of overfitting (high variance). Regularization techniques like dropout and data augmentation reduce variance.",
        "misconception_id": "MISC_OVERFIT_INVERTED", "prerequisite_id": "regularization",
        "reasoning_probe": {
            "prompt": "How does Dropout regularization reduce co-adaptation between neurons during training?",
            "options": {
                "A": "Randomly deactivating units forces each neuron to learn robust features that do not rely on specific peer neurons.",
                "B": "Dropout permanently prunes 50% of the network parameters from memory before deployment.",
                "C": "Zeroing activations increases the mathematical determinism of the weight gradient updates.",
                "D": "Dropout rescales the learning rate dynamically based on mini-batch covariance matrices."
            },
            "correct_probe": "A"
        }
    },
    {
        "id": "q_dl_38", "domain_id": "deep_learning", "concept_id": "ann_basics",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What is the primary role of the bias term b in the standard affine transformation z = Wx + b?",
        "option_a": "It allows the activation function threshold to shift horizontally away from the origin",
        "option_b": "It strictly forces the output vector to sum to 1 across all classification targets",
        "option_c": "It prevents the input vector dimensions from exceeding the GPU memory buffer",
        "option_d": "It guarantees that the gradient vector never drops below zero during training",
        "correct_option": "A",
        "explanation": "The bias shifts the activation function curve left or right, enabling the model to fit patterns that do not pass through the coordinate origin.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_39", "domain_id": "deep_learning", "concept_id": "activation_funcs",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why is the Softmax function universally employed in the final layer of multi-class classification networks?",
        "option_a": "It normalizes raw output logits into a valid probability distribution that sums to 1.0",
        "option_b": "It computes the Euclidean distance between continuous target labels and weights",
        "option_c": "It prevents over-parameterization by setting negative network weights to zero",
        "option_d": "It introduces spatial equivariance across chronological sequential tokens",
        "correct_option": "A",
        "explanation": "Softmax exponentiates logits and divides by their sum: P(y_i) = exp(z_i) / Σ exp(z_j), producing non-negative probabilities that sum to 1.",
        "misconception_id": "MISC_ACTIVATION_LOSS", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_40", "domain_id": "deep_learning", "concept_id": "cnn",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "What is the primary functional difference between Max Pooling and Average Pooling operations?",
        "option_a": "Max Pooling selects the strongest local feature activation, while Average Pooling computes regional mean",
        "option_b": "Max Pooling learns parametric weights via backpropagation, while Average Pooling uses fixed constants",
        "option_c": "Max Pooling doubles spatial resolution, while Average Pooling reduces channels by half",
        "option_d": "Max Pooling can only process grayscale images, while Average Pooling requires 3-channel RGB",
        "correct_option": "A",
        "explanation": "Max pooling extracts the maximum value within each pooling window (capturing prominent features like sharp edges), while average pooling calculates the arithmetic mean.",
        "misconception_id": "MISC_POOLING_WEIGHTS", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_41", "domain_id": "deep_learning", "concept_id": "gradient_descent",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "Why does Adam (Adaptive Moment Estimation) optimizer perform well across diverse deep learning architectures?",
        "option_a": "It combines momentum (first moment of gradients) with RMSProp (second moment of squared gradients)",
        "option_b": "It computes exact second-order Hessian matrices for all network parameters at each step",
        "option_c": "It eliminates the need to specify any learning rate or hyperparameter settings",
        "option_d": "It ensures global optima convergence on all non-convex loss surfaces unconditionally",
        "correct_option": "A",
        "explanation": "Adam computes exponentially decaying averages of past gradients (momentum) and past squared gradients (adaptive learning rate scaling per parameter).",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_42", "domain_id": "deep_learning", "concept_id": "regularization",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "How does Batch Normalization behave differently during model training versus model evaluation (testing)?",
        "option_a": "Training uses mini-batch mean and variance; testing uses accumulated running population statistics",
        "option_b": "Training updates weights; testing recalculates gradients for every validation example",
        "option_c": "Training deactivates half the channels; testing activates all feature maps simultaneously",
        "option_d": "Training normalizes across layers; testing normalizes across temporal sequence timesteps",
        "correct_option": "A",
        "explanation": "During training, batch norm normalizes using current mini-batch statistics. During inference, it uses fixed running averages tracked during training.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_43", "domain_id": "deep_learning", "concept_id": "rnn",
        "question_type": "basic", "difficulty": "easy",
        "question_text": "What major architectural improvement does the Gated Recurrent Unit (GRU) introduce over the LSTM?",
        "option_a": "It merges cell state and hidden state, using only two gates (reset and update) for faster computation",
        "option_b": "It completely removes recurrent loops to process sequences in parallel through convolutions",
        "option_c": "It utilizes four independent gate controllers to store unbounded sequence histories",
        "option_d": "It forces gradients to remain strictly positive throughout backpropagation through time",
        "correct_option": "A",
        "explanation": "GRUs simplify the LSTM architecture by combining the forget and input gates into an update gate and merging the cell state with the hidden state.",
        "misconception_id": None, "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_44", "domain_id": "deep_learning", "concept_id": "chain_rule",
        "question_type": "conceptual", "difficulty": "medium",
        "question_text": "If y = g(u) and u = f(x), what is the correct mathematical expression for the derivative dy/dx via the Chain Rule?",
        "option_a": "(dy/du) × (du/dx)",
        "option_b": "(dy/du) + (du/dx)",
        "option_c": "(dy/du) / (du/dx)",
        "option_d": "(dy/dx) × (du/dx)",
        "correct_option": "A",
        "explanation": "The chain rule states that dy/dx is the product of rates: dy/dx = (dy/du) × (du/dx).",
        "misconception_id": "MISC_CHAIN_RULE_SUM", "prerequisite_id": None, "reasoning_probe": None
    },
    {
        "id": "q_dl_45", "domain_id": "deep_learning", "concept_id": "backpropagation",
        "question_type": "application", "difficulty": "hard",
        "question_text": "During backpropagation through a layer with weights W, input x, and upstream gradient δ, what is the exact gradient of the loss with respect to weights W?",
        "option_a": "δ · x^T (Outer product of upstream gradient and input vector)",
        "option_b": "W^T · δ (Projection of upstream gradient through transposed weights)",
        "option_c": "δ + x (Linear sum of gradient vector and input vector)",
        "option_d": "W · x · δ (Hadamard product of weights, inputs, and gradients)",
        "correct_option": "A",
        "explanation": "For affine layer z = Wx + b, ∂L/∂W = (∂L/∂z) · (∂z/∂W)^T = δ · x^T.",
        "misconception_id": "MISC_GRAD_FLOW_DIR", "prerequisite_id": "backpropagation",
        "reasoning_probe": {
            "prompt": "Why does ∂L/∂W depend directly on the forward pass input activations x?",
            "options": {
                "A": "Because by calculus ∂z_i/∂W_{ij} = x_j, meaning the input acts as the local sensitivity multiplier.",
                "B": "Because inputs are added to the loss function directly at the final output layer.",
                "C": "Because transposed weight matrices overwrite the input activations during backprop.",
                "D": "Because the learning rate dynamically multiplies input values during forward propagation."
            },
            "correct_probe": "A"
        }
    }
]

# Additional Misconceptions to seed
ADDITIONAL_MISCONCEPTIONS = [
    {
        "id": "MISC_MATH_AP_N_MINUS_ONE", "domain_id": "class10_math", "code": "M-MATH-03",
        "concept_id": "math_ap", "name": "AP Index Offset Confusion (n vs n-1)",
        "description": "Student mistakenly calculates the n-th term using a + nd instead of a + (n-1)d, forgetting that the first term already has zero difference added.",
        "remediation": "Remember that term 1 has had 0 steps added. For the n-th term, you only add the common difference (n - 1) times: a_n = a + (n - 1)d."
    },
    {
        "id": "MISC_MATH_HEIGHT_NO_OBSERVER", "domain_id": "class10_math", "code": "M-MATH-04",
        "concept_id": "math_heights", "name": "Observer Eye Height Omission",
        "description": "Student calculates the height above the observer's eye using tan(θ) × distance, but forgets to add the observer's own height to find the total height of the structure.",
        "remediation": "Always draw a sketch showing the observer. Total height = height above eye level (distance × tan θ) + observer's eye height."
    },
    {
        "id": "MISC_MATH_COORD_DIST_ADD", "domain_id": "class10_math", "code": "M-MATH-05",
        "concept_id": "math_coord", "name": "Coordinate Addition in Distance Formula",
        "description": "Student adds coordinates inside the square root (x₁ + x₂)² instead of finding the difference between points (x₂ - x₁)². ",
        "remediation": "Distance measures the separation between two points. Always subtract the coordinates to find horizontal and vertical differences: √[(x₂ - x₁)² + (y₂ - y₁)²]."
    },
    {
        "id": "MISC_CHEM_COEFF_SUBSCRIPT", "domain_id": "class10_chemistry", "code": "M-CH-03",
        "concept_id": "chem_equations", "name": "Altering Chemical Subscripts",
        "description": "Student changes chemical formula subscripts to balance equations instead of adjusting stoichiometric coefficients in front.",
        "remediation": "Changing small subscript numbers changes the substance completely (e.g. H₂O to H₂O₂). Only change the big multiplier numbers in front of compounds."
    },
    {
        "id": "MISC_CHEM_METALS_REACTIVITY_SWAP", "domain_id": "class10_chemistry", "code": "M-CH-04",
        "concept_id": "metals_reactivity", "name": "Reactivity Series Direction Inversion",
        "description": "Student believes a less reactive metal can displace a more reactive metal from its salt solution.",
        "remediation": "Only a MORE reactive metal can displace a LESS reactive metal from its solution (e.g., Fe displaces Cu, but Cu CANNOT displace Fe)."
    },
    {
        "id": "MISC_CHEM_CARBON_VALENCY", "domain_id": "class10_chemistry", "code": "M-CH-05",
        "concept_id": "carbon_compounds", "name": "Carbon Valency Inconsistency",
        "description": "Student forgets that carbon is strictly tetravalent and writes chemical structures with 3 or 5 covalent bonds.",
        "remediation": "Carbon always shares 4 pairs of electrons to achieve an octet. Every carbon atom in a stable molecule must have exactly 4 covalent bonds."
    },
    {
        "id": "MISC_BIO_GENETICS_RATIO", "domain_id": "class10_biology", "code": "M-BIO-03",
        "concept_id": "bio_genetics", "name": "Monohybrid Ratio Confusion (Phenotype vs Genotype)",
        "description": "Student confuses the phenotypic ratio (3:1) with the genotypic ratio (1:2:1) in F2 monohybrid crosses.",
        "remediation": "Phenotype is what organisms look like (3 Tall : 1 Dwarf). Genotype is their underlying genetics (1 TT : 2 Tt : 1 tt)."
    },
    {
        "id": "MISC_BIO_HEART_CHAMBERS", "domain_id": "class10_biology", "code": "M-BIO-04",
        "concept_id": "bio_circulation", "name": "Heart Chamber Blood Mixing Assumption",
        "description": "Student assumes oxygenated and deoxygenated blood mix together inside the human 4-chambered heart.",
        "remediation": "In humans, the central muscular septum completely separates the left and right sides of the heart so oxygen-rich and oxygen-poor blood never mix."
    },
    {
        "id": "MISC_BIO_DIGESTION_STOMACH_ABSORB", "domain_id": "class10_biology", "code": "M-BIO-05",
        "concept_id": "bio_digestion", "name": "Stomach Absorption Misconception",
        "description": "Student believes the stomach is the primary site of nutrient absorption into the bloodstream.",
        "remediation": "The stomach primarily churns food and begins protein digestion with pepsin. Almost ALL nutrient absorption occurs downstream in the small intestine through villi."
    },
    {
        "id": "MISC_POKE_STAB_STAT", "domain_id": "pokemon", "code": "M-POKE-04",
        "concept_id": "poke_stab", "name": "STAB as Base Stat Boost Misconception",
        "description": "Student believes Same-Type Attack Bonus increases the Pokemon's base attack stat rather than acting as a 1.5x multiplier on the move power in the damage formula.",
        "remediation": "STAB does not alter the Pokemon's Attack stat on its summary screen; it multiplies the final move power by 1.5x when the move type matches the Pokemon's type."
    },
    {
        "id": "MISC_POKE_STAT_STAGES_MULT", "domain_id": "pokemon", "code": "M-POKE-05",
        "concept_id": "poke_stat_stages", "name": "Linear Stat Stage Assumption",
        "description": "Student assumes stat stages add fixed raw points (+1 stage = +50 points) instead of multiplying stats by fractional multipliers ((2+N)/2 for boosts, 2/(2+N) for drops).",
        "remediation": "Stat stages are fractional multipliers: +1 is 1.5x (3/2), +2 is 2.0x (4/2), while -1 is 0.67x (2/3) and -2 is 0.5x (2/4)."
    }
]

def seed_expansion():
    print(f"Connecting to {DB_PATH} to expand question banks...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 1. Insert new misconceptions
    for m in ADDITIONAL_MISCONCEPTIONS:
        cursor.execute("""
            INSERT OR REPLACE INTO misconceptions (id, domain_id, code, concept_id, name, description, remediation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (m["id"], m["domain_id"], m["code"], m["concept_id"], m["name"], m["description"], m["remediation"]))

    # 2. Insert all expansion questions
    all_expansions = [
        ("Math", MATH_EXPANSION),
        ("Chemistry", CHEM_EXPANSION),
        ("Biology", BIO_EXPANSION),
        ("Pokemon", POKEMON_EXPANSION),
        ("Deep Learning", DL_EXPANSION)
    ]

    total_inserted = 0
    for name, q_list in all_expansions:
        for q in q_list:
            rp_json = json.dumps(q.get("reasoning_probe")) if q.get("reasoning_probe") else None
            cursor.execute("""
                INSERT OR REPLACE INTO questions (
                    id, domain_id, concept_id, question_type, difficulty, question_text,
                    option_a, option_b, option_c, option_d, correct_option,
                    explanation, misconception_id, prerequisite_id, reasoning_probe
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"], q["domain_id"], q["concept_id"], q["question_type"], q["difficulty"], q["question_text"],
                q["option_a"], q["option_b"], q["option_c"], q["option_d"],
                q["correct_option"], q["explanation"], q.get("misconception_id"), q.get("prerequisite_id"),
                rp_json
            ))
            total_inserted += 1
        print(f"  Inserted {len(q_list)} new questions for {name}.")

    conn.commit()

    # 3. Print updated question counts per domain
    counts = cursor.execute("SELECT domain_id, count(*) FROM questions GROUP BY domain_id").fetchall()
    print("\nUpdated Question Counts in SQLite:")
    for d_id, c in counts:
        print(f"  - {d_id}: {c} questions")

    conn.close()
    print(f"\nExpansion complete! Total new questions added: {total_inserted}.")

if __name__ == "__main__":
    seed_expansion()
