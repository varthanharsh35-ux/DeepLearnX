"""
DeepLearnX Concept Remediation & Learning Guide
Comprehensive, simple-English conceptual explanations, relatable real-world examples,
and common traps to avoid across all 5 subjects.
"""

CONCEPT_GUIDE = {
    # =========================================================================
    # 1. CLASS 10 MATHEMATICS
    # =========================================================================
    "math_quadratics": {
        "concept_id": "math_quadratics",
        "domain_id": "class10_math",
        "name": "Quadratic Equations & Roots",
        "core_idea": "A quadratic equation is any equation where the highest power of x is 2, written in standard form as ax² + bx + c = 0. The discriminant D = b² - 4ac acts like a preview: if D > 0 you get two different real answers; if D = 0 both answers are identical; if D < 0 there are no real answers.",
        "example": "Throwing a ball into the air: its height over time follows h = -5t² + 20t. Setting h = 0 lets you find the two times the ball touches the ground: t = 0s (launch) and t = 4s (landing).",
        "common_mistake": "When solving x² = 25, students often say the answer is only 5. Remember that (-5)² is also 25, so x = +5 and -5.",
        "key_takeaway": "Always write the equation in standard form ax² + bx + c = 0 first, and check D = b² - 4ac before solving."
    },
    "math_ap": {
        "concept_id": "math_ap",
        "domain_id": "class10_math",
        "name": "Arithmetic Progressions (AP)",
        "core_idea": "An Arithmetic Progression is a sequence of numbers where you add or subtract the exact same amount at each step, called the common difference (d). The formula for any term is a_n = a + (n - 1)d.",
        "example": "If you save $10 in week 1, $15 in week 2, and $20 in week 3, the starting amount is a = $10 and common difference is d = $5. In week 10, you save a₁₀ = 10 + (10 - 1) × 5 = $55.",
        "common_mistake": "Multiplying by n instead of (n - 1). The first term has had zero additions, so the 10th term only adds the difference 9 times.",
        "key_takeaway": "The n-th term is always a + (n - 1)d, and the sum of n terms is (n/2) × [2a + (n - 1)d]."
    },
    "math_trig": {
        "concept_id": "math_trig",
        "domain_id": "class10_math",
        "name": "Trigonometry & Key Identities",
        "core_idea": "Trigonometry connects angles inside a right-angled triangle to the lengths of its sides. Sin is Opposite/Hypotenuse, Cos is Adjacent/Hypotenuse, and Tan is Opposite/Adjacent. The golden rule is sin²(θ) + cos²(θ) = 1.",
        "example": "A 5-meter ladder leans against a wall at a 30° angle. The height reached on the wall is 5 × sin(30°) = 5 × 0.5 = 2.5 meters.",
        "common_mistake": "Confusing sin(30°) and cos(30°). Remember: sin(30°) = 1/2 = 0.5, while cos(30°) = √3/2 ≈ 0.866.",
        "key_takeaway": "Remember SOH-CAH-TOA and the identity sin²(θ) + cos²(θ) = 1."
    },
    "math_heights": {
        "concept_id": "math_heights",
        "domain_id": "class10_math",
        "name": "Heights & Distances (Applications of Trigonometry)",
        "core_idea": "You can measure the height of tall buildings, trees, or mountains without climbing them by measuring your distance from the base and the angle looking up (angle of elevation) or looking down (angle of depression).",
        "example": "If you stand 40 meters away from a tower and look up at the top at a 45° angle, because tan(45°) = 1, the tower height above your eye is 40 × tan(45°) = 40 meters.",
        "common_mistake": "Forgetting to add the observer's eye height to the calculated height when the problem gives the observer's height.",
        "key_takeaway": "Angle of elevation equals angle of depression (alternate interior angles), and tan(θ) = height / distance."
    },
    "math_coord": {
        "concept_id": "math_coord",
        "domain_id": "class10_math",
        "name": "Coordinate Geometry",
        "core_idea": "Points are located on a flat grid using (x, y) coordinates. The distance formula √[(x₂ - x₁)² + (y₂ - y₁)²] uses the Pythagorean theorem, and the midpoint is simply the average of the two points.",
        "example": "The distance between your house at (0, 0) and the school at (3, 4) is √[(3 - 0)² + (4 - 0)²] = √(9 + 16) = √25 = 5 units.",
        "common_mistake": "Mixing up x and y values in the formula or adding instead of subtracting coordinates inside the brackets.",
        "key_takeaway": "Distance is the straight-line hypotenuse: √[Δx² + Δy²]."
    },

    # =========================================================================
    # 2. CLASS 10 CHEMISTRY
    # =========================================================================
    "chem_equations": {
        "concept_id": "chem_equations",
        "domain_id": "class10_chemistry",
        "name": "Chemical Reactions & Balancing Equations",
        "core_idea": "Atoms cannot appear or vanish out of thin air (Law of Conservation of Mass). Every type of atom on the left (reactants) must equal the exact number of atoms on the right (products).",
        "example": "Burning hydrogen gas in oxygen: 2H₂ + O₂ → 2H₂O. There are 4 hydrogen atoms and 2 oxygen atoms on both the left and right sides.",
        "common_mistake": "Changing the small subscript numbers (like changing H₂O to H₂O₂). You can only change the big coefficient numbers in front of compounds!",
        "key_takeaway": "Only balance equations by placing multipliers in front of formulas, never by altering chemical formulas."
    },
    "acids_bases": {
        "concept_id": "acids_bases",
        "domain_id": "class10_chemistry",
        "name": "Acids, Bases & The pH Scale",
        "core_idea": "Acids release hydrogen ions (H⁺) in water and have a pH below 7 (turns blue litmus red). Bases release hydroxide ions (OH⁻) and have a pH above 7 (turns red litmus blue). Pure water is neutral at pH 7.",
        "example": "Lemon juice has a pH of about 2 (acidic). Baking soda dissolved in water has a pH around 9 (mildly basic). When you combine an acid and a base, they neutralize into salt and water.",
        "common_mistake": "Thinking all salts are neutral. A salt made from a strong acid and weak base (like ammonium chloride NH₄Cl) is slightly acidic with pH < 7.",
        "key_takeaway": "pH < 7 is acidic (rich in H⁺), pH = 7 is neutral, and pH > 7 is basic (rich in OH⁻)."
    },
    "metals_reactivity": {
        "concept_id": "metals_reactivity",
        "domain_id": "class10_chemistry",
        "name": "Metals & The Reactivity Series",
        "core_idea": "Metals are ranked in order of how eagerly they react and give away electrons. A more active metal will displace (kick out) a less active metal from its dissolved compound.",
        "example": "If you put a clean iron nail into blue copper sulfate solution (CuSO₄), iron is more reactive than copper: iron dissolves into the solution (turning it greenish) and pure reddish copper settles onto the nail.",
        "common_mistake": "Thinking copper can displace iron. Because copper is lower down the reactivity ladder, dropping copper into iron sulfate causes zero reaction.",
        "key_takeaway": "A metal can only displace metals that sit below it in the reactivity series (K > Na > Ca > Mg > Al > Zn > Fe > Cu > Ag > Au)."
    },
    "carbon_compounds": {
        "concept_id": "carbon_compounds",
        "domain_id": "class10_chemistry",
        "name": "Carbon & Its Covalent Compounds",
        "core_idea": "Carbon has 4 outer electrons. Gaining 4 electrons takes too much nuclear charge to hold, and losing 4 takes massive ionization energy. Therefore, carbon always shares electrons (covalent bonding) and can form endless chains with other carbon atoms (catenation).",
        "example": "Cooking gas (methane CH₄): 1 carbon atom shares a pair of electrons with each of 4 hydrogen atoms, creating 4 strong covalent bonds.",
        "common_mistake": "Thinking carbon forms ionic bonds like table salt. Carbon compounds are covalent with lower melting points and do not conduct electricity.",
        "key_takeaway": "Carbon is tetravalent (forms 4 shared covalent bonds) and links with itself to form straight, branched, and ring structures."
    },

    # =========================================================================
    # 3. CLASS 10 BIOLOGY
    # =========================================================================
    "bio_respiration": {
        "concept_id": "bio_respiration",
        "domain_id": "class10_biology",
        "name": "Cellular Respiration & Energy (ATP)",
        "core_idea": "Respiration is the cellular process of breaking down food (glucose) to release energy packaged into ATP molecules. Aerobic respiration (with oxygen in mitochondria) produces 36–38 ATP, while anaerobic respiration (without oxygen) only gives 2 ATP and produces lactic acid or alcohol.",
        "example": "During a fast sprint, your muscles need energy faster than your lungs can supply oxygen. Muscle cells temporarily switch to anaerobic respiration, producing lactic acid which causes muscle soreness.",
        "common_mistake": "Confusing breathing with respiration. Breathing is just air moving in and out of the lungs; respiration is the chemical breakdown of glucose inside living cells.",
        "key_takeaway": "Oxygen-rich cellular respiration takes place inside mitochondria and produces maximum energy (ATP)."
    },
    "bio_digestion": {
        "concept_id": "bio_digestion",
        "domain_id": "class10_biology",
        "name": "Human Digestion & Enzymes",
        "core_idea": "The digestive system breaks large food molecules into tiny nutrients that can enter the bloodstream using specific biological catalysts called enzymes: amylase in saliva breaks starches, pepsin in stomach acid digests proteins, and bile from the liver breaks fat into tiny droplets.",
        "example": "Bile acts just like dishwashing soap on greasy plates: it breaks giant clumps of fat into microscopic droplets (emulsification) so lipase enzymes can quickly digest them.",
        "common_mistake": "Assuming bile contains digestive enzymes. Bile contains no enzymes; its job is purely mechanical emulsification and neutralizing stomach acid.",
        "key_takeaway": "Different enzymes need different pH environments: pepsin works in acidic stomach fluid, while intestinal enzymes need an alkaline fluid."
    },
    "bio_circulation": {
        "concept_id": "bio_circulation",
        "domain_id": "class10_biology",
        "name": "Circulation & The Human Heart",
        "core_idea": "Humans have double circulation: blood passes through the 4-chambered heart twice in each complete loop. The right side pumps oxygen-poor blood to the lungs, and the muscular left side pumps oxygen-rich blood out to the whole body.",
        "example": "Arteries are thick-walled pipes that carry blood away from the heart under high pressure. Veins have thinner walls and built-in one-way valves so blood doesn't flow backwards under low pressure.",
        "common_mistake": "Saying all arteries carry oxygenated blood. The pulmonary artery is the one exception: it carries deoxygenated blood to the lungs.",
        "key_takeaway": "Arteries carry blood away from the heart; veins return blood to the heart; double circulation keeps oxygenated and deoxygenated blood completely separate."
    },
    "bio_genetics": {
        "concept_id": "bio_genetics",
        "domain_id": "class10_biology",
        "name": "Heredity & Mendelian Genetics",
        "core_idea": "Inherited traits are controlled by gene pairs (alleles). A dominant allele (like T for tall) completely masks a recessive allele (like t for short). In a cross between two hybrid parents (Tt × Tt), the offspring show a 3:1 ratio of dominant to recessive traits.",
        "example": "Brown eye color (B) is dominant over blue eyes (b). If both parents carry a hidden blue gene (Bb), there is a 25% chance (1 in 4) their child inherits bb and has blue eyes.",
        "common_mistake": "Confusing phenotype with genotype. Phenotype is what you visibly see (e.g. 3 Tall : 1 Short); genotype is the exact genetic code (1 TT : 2 Tt : 1 tt).",
        "key_takeaway": "Dominant traits show up even with one copy; recessive traits only appear when both copies are identical."
    },

    # =========================================================================
    # 4. POKEMON BATTLE MECHANICS
    # =========================================================================
    "poke_types": {
        "concept_id": "poke_types",
        "domain_id": "pokemon",
        "name": "Type Matchups & Single Weaknesses",
        "core_idea": "Every Pokemon attack and defender has an elemental type. Super-effective moves deal double damage (2×), not-very-effective moves deal half damage (0.5×), and normal hits deal standard damage (1×).",
        "example": "Using Water Gun (Water) against Charmander (Fire) deals 2× damage, while using Ember (Fire) against Squirtle (Water) only deals 0.5× damage.",
        "common_mistake": "Thinking Rock and Ground are the same type. Ground is immune to Electric and weak to Water/Grass/Ice; Rock is weak to Fighting/Ground/Steel/Water/Grass and has no electric immunity.",
        "key_takeaway": "Pay attention to the elemental wheel: Fire beats Grass, Grass beats Water, Water beats Fire."
    },
    "poke_dual_types": {
        "concept_id": "poke_dual_types",
        "domain_id": "pokemon",
        "name": "Dual-Type Multipliers",
        "core_idea": "When a Pokemon has two types, the damage multipliers from each type multiply together. If an attack is super effective against both types, it deals 2 × 2 = 4× damage (quadruple weakness). If resisted by both, it deals 0.5 × 0.5 = 0.25× damage.",
        "example": "Swampert is Water and Ground. Grass is super effective against Water (2×) and super effective against Ground (2×), resulting in 2 × 2 = 4× damage!",
        "common_mistake": "Adding the multipliers instead of multiplying them. 2 × 2 = 4× (quadruple damage), not 2 + 2.",
        "key_takeaway": "Always multiply both type multipliers together: 2 × 2 = 4×, 2 × 0.5 = 1× (neutral), 0.5 × 0.5 = 0.25×."
    },
    "poke_immunities": {
        "concept_id": "poke_immunities",
        "domain_id": "pokemon",
        "name": "Type Immunities (0× Damage)",
        "core_idea": "Some type combinations take zero damage (0×) from certain attacks, regardless of the attacker's level or stats.",
        "example": "Ground-type Pokemon take 0× damage from Electric attacks (Thunderbolt completely fails), and Ghost-types take 0× damage from Normal and Fighting moves.",
        "common_mistake": "Assuming Flying-type Pokemon are immune to all ground hazard or weather effects. Flying is immune to Ground-type moves, but takes 2× damage from Rock and Electric moves.",
        "key_takeaway": "An immunity turns the entire multiplier to 0× immediately, overriding other stats."
    },
    "poke_stab": {
        "concept_id": "poke_stab",
        "domain_id": "pokemon",
        "name": "STAB (Same-Type Attack Bonus)",
        "core_idea": "When a Pokemon uses an attack that matches its own elemental type, it earns a free +50% damage bonus (1.5× multiplier).",
        "example": "Pikachu (Electric) using Thunderbolt (90 base power) deals 90 × 1.5 = 135 effective power because of STAB. A Snorlax using Thunderbolt gets no bonus (stays at 90).",
        "common_mistake": "Thinking STAB depends on what type the opponent is. STAB only depends on whether the attacker's type matches the attack's type.",
        "key_takeaway": "Matching your Pokemon's type to its moves gives a free 1.5× damage boost on every hit."
    },
    "poke_stat_stages": {
        "concept_id": "poke_stat_stages",
        "domain_id": "pokemon",
        "name": "Stat Stages & Battle Stat Buffs",
        "core_idea": "Certain moves raise or lower combat stats in stages from -6 up to +6. A +1 boost increases the stat by +50% (1.5×), and a +2 boost doubles the stat (2.0×).",
        "example": "Using Swords Dance gives +2 Attack stages, instantly doubling the Pokemon's physical attack power for all future physical hits.",
        "common_mistake": "Thinking stat boosts stay when switching. When a Pokemon is swapped out to the bench, all stat stage boosts reset back to 0.",
        "key_takeaway": "Setup moves like Swords Dance or Dragon Dance multiply damage output quickly."
    },

    # =========================================================================
    # 5. DEEP LEARNING FUNDAMENTALS
    # =========================================================================
    "derivatives": {
        "concept_id": "derivatives",
        "domain_id": "deep_learning",
        "name": "Calculus & Derivatives",
        "core_idea": "A derivative dy/dx tells you the instantaneous slope or rate of change: if you nudge the input x forward by a tiny amount, how much does the output y change?",
        "example": "If a car's distance formula is s(t) = t², the derivative is 2t. At second 3, the instantaneous speedometer reading is 2 × 3 = 6 m/s.",
        "common_mistake": "Thinking the derivative of a constant number has value. The derivative of any constant (like 5 or 100) is always 0 because constants do not change.",
        "key_takeaway": "Derivatives show direction and steepness: positive means rising, negative means falling, zero means flat (peak or valley)."
    },
    "chain_rule": {
        "concept_id": "chain_rule",
        "domain_id": "deep_learning",
        "name": "The Calculus Chain Rule",
        "core_idea": "When mathematical functions are nested inside each other like Russian dolls y = f(g(x)), you find the total rate of change by multiplying the individual rates of change: dy/dx = (dy/dg) × (dg/dx).",
        "example": "Currency conversion: If 1 Euro = 1.10 US Dollars, and 1 US Dollar = 83 Indian Rupees, then 1 Euro = 1.10 × 83 = 91.3 Rupees. You multiply rates of change, never add them!",
        "common_mistake": "Adding derivative rates instead of multiplying them. dy/dx is NOT (dy/du + du/dx); rates of change scale multiplicatively.",
        "key_takeaway": "The Chain Rule multiplies gradients backwards along the computational path."
    },
    "ann_basics": {
        "concept_id": "ann_basics",
        "domain_id": "deep_learning",
        "name": "Artificial Neural Networks (ANN)",
        "core_idea": "An artificial neuron takes several numbers (inputs), multiplies each by an importance weight (w), adds a bias adjustment (b), and passes the total sum z = Σ wᵢxᵢ + b through an activation function.",
        "example": "Predicting apartment rent: input x₁ is square feet, x₂ is number of bedrooms. The model learns weights w₁ and w₂ that indicate how much each feature affects rent.",
        "common_mistake": "Believing stacking multiple linear layers without activation functions creates a deep network. Without non-linear activation functions, 100 linear layers collapse into a single basic linear formula.",
        "key_takeaway": "A neuron computes a weighted sum plus bias, followed by a non-linear activation function."
    },
    "activation_funcs": {
        "concept_id": "activation_funcs",
        "domain_id": "deep_learning",
        "name": "Activation Functions (ReLU, Sigmoid, Softmax)",
        "core_idea": "Activation functions introduce curved, non-linear boundaries so the neural network can learn complex shapes instead of just flat lines. ReLU (max(0, x)) is the most widely used because it computes quickly and does not squash large gradients.",
        "example": "Sigmoid squashes any input number between 0 and 1, making it perfect for predicting a probability. ReLU turns all negative inputs to 0 and passes positive inputs straight through.",
        "common_mistake": "Assuming ReLU is capped at 1 like Sigmoid. ReLU has no upper limit: for positive numbers, output = input.",
        "key_takeaway": "ReLU is standard for hidden layers because it avoids the vanishing gradient problem; Sigmoid/Softmax are used for output probability layers."
    },
    "forward_prop": {
        "concept_id": "forward_prop",
        "domain_id": "deep_learning",
        "name": "Forward Propagation & Loss Functions",
        "core_idea": "Forward propagation is the step where input data travels from left to right through the network to generate a guess. The loss function compares this guess against the actual truth to calculate an error score.",
        "example": "A cat detector looks at an image, produces a guess (e.g. 70% cat), and compares it to the real label (100% cat). The difference is measured using Cross-Entropy Loss.",
        "common_mistake": "Using Mean Squared Error (MSE) for multi-class classification. Cross-entropy loss is much better suited for probability outputs because it penalizes confident wrong guesses heavily.",
        "key_takeaway": "Forward propagation produces predictions; the loss function measures how far off the prediction was."
    },
    "backpropagation": {
        "concept_id": "backpropagation",
        "domain_id": "deep_learning",
        "name": "Backpropagation & Gradient Flow",
        "core_idea": "Backpropagation is how the network learns from its mistakes. It sends error signals backwards from the output layer to earlier layers using the Chain Rule, calculating exactly how much each weight contributed to the error.",
        "example": "If a network guesses that a dog photo is a bus, backprop traces backwards: 'Neuron 4 was too aggressive, reduce its weight; Neuron 2 was helpful, increase its weight'.",
        "common_mistake": "Thinking gradients flow forward with the data. Gradients always travel in reverse, from the final loss backwards to the earliest weights.",
        "key_takeaway": "Backpropagation uses the Chain Rule to calculate gradients for every single learnable parameter in the network."
    },
    "gradient_descent": {
        "concept_id": "gradient_descent",
        "domain_id": "deep_learning",
        "name": "Gradient Descent & Learning Rate",
        "core_idea": "Gradient descent is the optimization rule that updates weights to reduce prediction error: w_new = w_old - (learning_rate × gradient). It takes small steps in the downward direction of the error hill.",
        "example": "Walking down a foggy hill to reach the valley: you feel the slope under your feet and take small steps downhill until you reach the lowest point.",
        "common_mistake": "Setting the learning rate too high causes the model to jump back and forth over the valley and never learn. Setting it too small makes training take days.",
        "key_takeaway": "Weights are updated by taking steps in the opposite direction of the gradient, scaled by the learning rate."
    },
    "overfitting": {
        "concept_id": "overfitting",
        "domain_id": "deep_learning",
        "name": "Overfitting & Generalization",
        "core_idea": "Overfitting happens when a model memorizes the training data (including accidental noise) so thoroughly that it fails when given brand-new test questions.",
        "example": "A student who memorizes the exact numbers and answers from practice exams. When the actual exam changes the numbers slightly, they get confused and fail.",
        "common_mistake": "Assuming 100% training accuracy means a perfect model. If validation accuracy is low while training accuracy is 100%, the model has overfitted.",
        "key_takeaway": "A good model generalizes well to new, unseen data rather than just memorizing training examples."
    },
    "regularization": {
        "concept_id": "regularization",
        "domain_id": "deep_learning",
        "name": "Regularization Techniques (Dropout & Weight Decay)",
        "core_idea": "Regularization prevents overfitting by stopping neurons from depending too heavily on one another. Dropout randomly turns off a percentage of neurons during each training step, forcing the network to learn robust features.",
        "example": "Sports team training: the coach randomly benches star players in practice drills so every teammate learns to handle the ball independently, making the team stronger overall.",
        "common_mistake": "Leaving Dropout on during testing or evaluation. Dropout is only used during training; during inference, all neurons are active.",
        "key_takeaway": "Dropout and weight decay keep weights small and distributed, preventing memorization."
    },
    "cnn": {
        "concept_id": "cnn",
        "domain_id": "deep_learning",
        "name": "Convolutional Neural Networks (CNN)",
        "core_idea": "CNNs are neural networks designed for images and spatial patterns. They slide small filters (kernels) across images to spot edges, textures, and shapes regardless of where they appear on the screen.",
        "example": "Face recognition: the first layers spot simple light and dark lines, middle layers combine them into noses and eyes, and final layers recognize the complete face.",
        "common_mistake": "Thinking max pooling contains learnable weights. Max pooling is a fixed operation that simply keeps the highest number in each small region to downsample the image.",
        "key_takeaway": "Convolutional filters extract spatial patterns, and pooling layers shrink the image dimensions."
    },
    "rnn": {
        "concept_id": "rnn",
        "domain_id": "deep_learning",
        "name": "Recurrent Neural Networks (RNN)",
        "core_idea": "RNNs are designed for sequential data like sentences, speech, or stock prices over time. They have a recurrent hidden memory that passes information from previous words forward into the next step.",
        "example": "Predicting the next word in a sentence: 'The clouds are in the ___'. The network needs memory of the word 'clouds' earlier in the sentence to predict 'sky'.",
        "common_mistake": "Basic RNNs suffer from vanishing gradients on long paragraphs (they forget early sentences). LSTMs and GRUs solve this with memory gates.",
        "key_takeaway": "RNNs maintain internal hidden state memory to process chronological, sequential data."
    }
}

import sqlite3

def register_concept_guide(guide: dict):
    """Registers or updates a concept guide entry dynamically."""
    if not guide or "concept_id" not in guide:
        return
    CONCEPT_GUIDE[guide["concept_id"]] = guide

def get_concept_guide(concept_id: str, domain_id: str = None) -> dict:
    """Returns detailed concept explanation, example, and common traps."""
    if concept_id in CONCEPT_GUIDE:
        return CONCEPT_GUIDE[concept_id]
        
    # Check SQLite custom_concept_guides table if available
    db_file = Path(__file__).resolve().parents[2] / "database" / "deeplearnx.db"
    if db_file.exists():
        try:
            conn = sqlite3.connect(str(db_file))
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM custom_concept_guides WHERE concept_id = ?", (concept_id,)).fetchone()
            conn.close()
            if row:
                guide_data = {
                    "concept_id": row["concept_id"],
                    "domain_id": row["domain_id"],
                    "name": row["name"],
                    "core_idea": row["core_idea"],
                    "example": row["example"],
                    "common_mistake": row["common_mistake"],
                    "key_takeaway": row["key_takeaway"]
                }
                CONCEPT_GUIDE[concept_id] = guide_data
                return guide_data
        except Exception:
            pass

    # Fallback default
    clean_name = concept_id.replace("_", " ").title()
    return {
        "concept_id": concept_id,
        "domain_id": domain_id or "general",
        "name": clean_name,
        "core_idea": f"{clean_name} is an important foundation in this subject. Reviewing its key rules and formulas will help you solve application problems confidently.",
        "example": f"Look for everyday situations where {clean_name} governs the outcome, and practice step-by-step problem calculations.",
        "common_mistake": "Skipping fundamental steps or applying formulas without checking the problem conditions.",
        "key_takeaway": "Focus on understanding the core principle behind the formula before attempting practice questions."
    }

