"""
Authentic Photosynthesis Question Generator
Provides university-grade, domain-specific assessments covering:
1. Chloroplast Ultrastructure, Pigment Absorption Spectra & Photolysis
2. Light-Dependent Reactions, Electron Transport Chain & Photophosphorylation
3. Calvin Cycle (C3 Pathway), RuBisCO Carboxylase & G3P Triose Synthesis
4. Photorespiration Inefficiency, C4 Kranz Anatomy & CAM Temporal Separation
"""

from typing import Dict, Any, Optional

def generate_photosynthesis_question(
    c_name: str,
    tier: str,
    q_idx: int,
    has_probe: bool,
    pattern_idx: int = 0
) -> Dict[str, Any]:
    c_low = c_name.lower()

    # 1. Chloroplast Ultrastructure, Pigment Absorption & Photolysis
    if "chloroplast" in c_low or "pigment" in c_low or "photolysis" in c_low or "light capture" in c_low or "ultrastructure" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In oxygenic photosynthesis, what is the precise chemical origin of the molecular oxygen (O2) released into the atmosphere?"
                opts = {
                    "A": "The enzymatic photolysis (splitting) of water molecules (H2O) at the oxygen-evolving complex of Photosystem II.",
                    "B": "The breakdown of carbon dioxide (CO2) during carbon fixation in the stroma.",
                    "C": "The cleavage of glucose during mitochondrial cellular respiration.",
                    "D": "The reduction of atmospheric nitrogen gas by symbiotic root bacteria."
                }
                expl = "Ruben, Kamen, and Van Niel isotopic tracer experiments using H2(18)O definitively proved that all O2 released originates from water photolysis at Photosystem II (2H2O -> O2 + 4H+ + 4e-), not from carbon dioxide."
            else:
                text = "Which wavelengths of electromagnetic radiation are most strongly absorbed by Chlorophyll a and b pigments?"
                opts = {
                    "A": "Blue-violet (~430-450 nm) and red-orange (~640-660 nm) wavelengths, while reflecting green light (~500-550 nm).",
                    "B": "Green light (~520 nm) and yellow light (~580 nm) exclusively.",
                    "C": "Invisible infrared thermal radiation (>800 nm) and radio frequency waves.",
                    "D": "High-energy gamma rays and cosmic particle radiation."
                }
                expl = "Chlorophyll absorption spectra show distinct peaks in the blue and red regions. Green light is largely unabsorbed and reflected, which gives green plant tissues their characteristic color."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why do leaves appear green to the human eye, and why is the assumption that 'plants thrive best under pure green light' scientifically false?"
            opts = {
                "A": "Chlorophyll pigments reflect rather than absorb green wavelengths; illuminating plants with pure green light yields minimal photosynthetic electron transport and severely stunts growth.",
                "B": "Green light has such high photon energy that it incinerates thylakoid membrane lipids upon contact.",
                "C": "Green wavelengths are absorbed exclusively by cell wall cellulose rather than chloroplasts.",
                "D": "Plants only reflect green light when they are dead or completely devoid of chloroplasts."
            }
            expl = "The action spectrum of photosynthesis drops precipitously in the green spectrum because chlorophylls a and b lack significant absorption bands between 500-550 nm, reflecting most green photons."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "What role do accessory pigments like Carotenoids (beta-carotene, lutein) play in the light-harvesting antenna complex?",
                    "options": {
                        "A": "They absorb intermediate blue-green wavelengths and provide non-photochemical quenching to dissipate excess photon energy safely as heat, preventing photo-oxidative damage.",
                        "B": "They convert carbon dioxide directly into starch granules without light activation.",
                        "C": "They transport sucrose from root xylem vessels up to developing leaf buds.",
                        "D": "They eliminate all water requirements by generating synthetic moisture from oxygen."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "In an experiment, plants are supplied with water enriched with oxygen-18 isotope (H2(18)O) and standard atmospheric carbon dioxide (C(16)O2). After 4 hours of intense illumination, where will the heavy oxygen-18 isotope be detected?"
            opts = {
                "A": "Exclusively in the evolved gaseous molecular oxygen (18-O2) released into the air.",
                "B": "Exclusively within the synthesized glucose (C6H12(18)O6) stored in the plant roots.",
                "C": "Exclusively within the ATP synthase enzyme molecules bound to the thylakoid membrane.",
                "D": "Heavy isotopes cannot be incorporated into biological macromolecules due to atomic mass barriers."
            }
            expl = "Water is split in Photosystem II to replace electrons lost by P680 reaction centers. The oxygen atoms from H2O combine to form O2 gas, proving evolved oxygen originates from water."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "If the experiment is reversed, supplying C(18)O2 and standard H2(16)O, where will the oxygen-18 isotope appear?",
                    "options": {
                        "A": "In synthesized triose sugars (G3P/glucose) and newly formed metabolic water molecules.",
                        "B": "In the evolved oxygen gas bubbled out from stomatal pores.",
                        "C": "In the thylakoid lumen proton reservoir.",
                        "D": "In the nitrogen gas expelled by mitochondrial ribosomes."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 2. Light-Dependent Reactions & Photophosphorylation
    elif "light-dependent" in c_low or "electron transport" in c_low or "photophosphorylation" in c_low or "chemiosmosis" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the primary driving mechanism of ATP synthesis across the thylakoid membrane during the light reactions?"
                opts = {
                    "A": "Chemiosmosis driven by a proton electrochemical gradient (high H+ concentration in the thylakoid lumen relative to the stroma) powering ATP Synthase.",
                    "B": "Direct combustion of atmospheric glucose molecules in the thylakoid stroma.",
                    "C": "Gravitational kinetic energy generated by cytoplasmic streaming in plant cells.",
                    "D": "Static electrical discharges jumping between adjacent grana stacks."
                }
                expl = "Peter Mitchell's chemiosmotic hypothesis: electron transport pumps H+ from the stroma into the thylakoid lumen. Protons flow back into the stroma through ATP synthase, driving photophosphorylation."
            else:
                text = "What are the two primary energy-rich chemical products generated by non-cyclic light reactions that directly fuel the Calvin cycle?"
                opts = {
                    "A": "Adenosine Triphosphate (ATP) and reduced Nicotinamide Adenine Dinucleotide Phosphate (NADPH).",
                    "B": "Glucose and atmospheric nitrogen gas.",
                    "C": "Lactic acid and ethyl alcohol.",
                    "D": "Sodium chloride and hydrochloric acid."
                }
                expl = "Non-cyclic photophosphorylation generates ATP (energy carrier) and NADPH (reducing agent), which are exported to the stroma to power the enzymatic reactions of the Calvin cycle."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Under what physiological conditions do chloroplasts switch from non-cyclic to cyclic photophosphorylation, and what is the outcome?"
            opts = {
                "A": "When the ratio of NADPH to NADP+ is very high and ATP demand exceeds supply; electrons cycle through Photosystem I and cytochrome b6f to pump protons, generating ATP without producing NADPH or O2.",
                "B": "When ambient temperature drops below freezing, converting chloroplasts into cellular heating units.",
                "C": "When plants enter winter dormancy and lose all green foliage.",
                "D": "Cyclic photophosphorylation occurs exclusively in deep-sea volcanic hydrothermal vent bacteria."
            }
            expl = "The Calvin cycle consumes 9 ATP for every 6 NADPH (a 3:2 ratio). Non-cyclic flow produces ATP and NADPH in roughly equal ratios; cyclic flow around PSI supplies the extra ATP needed without generating excess NADPH."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does cyclic photophosphorylation produce zero molecular oxygen (O2)?",
                    "options": {
                        "A": "Photosystem II and its water-splitting complex are bypassed entirely in cyclic electron flow; electrons originate from and return to Photosystem I.",
                        "B": "Oxygen atoms are destroyed by high-voltage electric fields inside cytochrome b6f.",
                        "C": "Cyclic photophosphorylation consumes all available atmospheric oxygen to synthesize carbon dioxide.",
                        "D": "Oxygen molecules are converted into nitrogen atoms during cyclic electron transport."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "The agricultural herbicide DCMU (Diuron) blocks the plastoquinone (PQ) binding site on Photosystem II, preventing electron transfer to the plastoquinone pool. What immediate downstream biochemical effect will be observed in treated crop weeds?"
            opts = {
                "A": "Electron transport from PSII ceases, stopping proton accumulation in the thylakoid lumen, halting non-cyclic ATP and NADPH synthesis, and starving the Calvin cycle.",
                "B": "Photosynthetic rate increases by 400% as electrons are diverted directly into glucose synthesis.",
                "C": "RuBisCO begins fixing atmospheric argon gas into amino acids.",
                "D": "The plant immediately switches to anaerobic fermentation inside the chloroplast stroma."
            }
            expl = "By blocking PQ reduction, DCMU interrupts linear electron flow: PSII cannot unload electrons, water splitting stops, and without electron transfer to PSI, NADPH and proton-driven ATP production collapse."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does adding an artificial electron donor capable of feeding electrons directly to Photosystem I restore ATP synthesis in DCMU-inhibited chloroplasts?",
                    "options": {
                        "A": "It bypasses the blocked PSII-to-PQ step, enabling PSI-dependent cyclic photophosphorylation to resume pumping protons for ATP synthase.",
                        "B": "The artificial donor dissolves the chloroplast double membrane.",
                        "C": "It converts DCMU into a nitrogen-rich agricultural fertilizer.",
                        "D": "Artificial donors eliminate the requirement for light energy during photophosphorylation."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 3. Calvin Cycle (C3 Pathway), RuBisCO & G3P Triose Synthesis
    elif "calvin" in c_low or "rubisco" in c_low or "carbon fixation" in c_low or "c3" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is the primary enzymatic catalyst responsible for fixing inorganic carbon dioxide (CO2) onto ribulose-1,5-bisphosphate (RuBP) in the Calvin cycle?"
                opts = {
                    "A": "RuBisCO (Ribulose-1,5-bisphosphate carboxylase-oxygenase).",
                    "B": "DNA Polymerase III.",
                    "C": "Mitochondrial Cytochrome c Oxidase.",
                    "D": "Pancreatic Trypsin."
                }
                expl = "RuBisCO is the primary carbon-fixing enzyme on Earth, catalyzing the carboxylation of RuBP to produce an unstable 6-carbon intermediate that immediately splits into two 3-phosphoglycerate (3-PGA) molecules."
            else:
                text = "What is the direct, net three-carbon sugar output exported from the Calvin cycle to synthesize glucose and other carbohydrates?"
                opts = {
                    "A": "Glyceraldehyde-3-phosphate (G3P / PGAL).",
                    "B": "Pure crystalline sucrose.",
                    "C": "L-Glutamic acid.",
                    "D": "Ethyl alcohol."
                }
                expl = "The Calvin cycle does not directly export glucose; for every 3 CO2 fixed, 6 G3P are produced, of which 5 are recycled to regenerate RuBP and 1 net G3P is exported to form hexose sugars."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why is the common textbook terminology 'Dark Reactions' a misleading name for the Calvin cycle?"
            opts = {
                "A": "The Calvin cycle relies directly on ATP and NADPH generated by light, and key Calvin cycle enzymes (e.g., FBPase, RuBisCO activase) are actively stimulated by light-driven ferredoxin-thioredoxin systems; it halts in the dark.",
                "B": "The Calvin cycle takes place inside deep underground fungal networks that never see sunlight.",
                "C": "The reactions produce flashes of bioluminescent green light visible to the naked eye.",
                "D": "The Calvin cycle requires darkness to prevent photon radiation from evaporating water molecules."
            }
            expl = "The 'dark reactions' do not require darkness; rather, they do not directly absorb photons. In reality, they depend on continuous light reaction products and light-dependent stroma alkalinization (Mg2+ influx and pH increase) to remain active."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "What happens to the Calvin cycle if an illuminated plant is suddenly plunged into complete darkness?",
                    "options": {
                        "A": "Within minutes, ATP and NADPH pools deplete, stromal pH drops, thioredoxin inactivation occurs, and carbon fixation halts completely.",
                        "B": "Carbon fixation increases exponentially because sunlight was inhibiting RuBisCO.",
                        "C": "The chloroplast immediately begins releasing large quantities of methane gas.",
                        "D": "The plant converts its leaves into root tissues to escape the dark."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "In Melvin Calvin's classic lollipop experiment, green algae (Chlorella) were exposed to radioactive carbon-14 dioxide ((14)CO2) and killed in boiling alcohol after just 5 seconds of illumination. Which molecule was identified as the very first stable radioactive intermediate?"
            opts = {
                "A": "3-Phosphoglycerate (3-PGA), a 3-carbon organic acid.",
                "B": "A 6-carbon glucose molecule.",
                "C": "Ribulose-1,5-bisphosphate (RuBP).",
                "D": "Carbonic acid in the liquid nutrient broth."
            }
            expl = "Chromatography and autoradiography revealed 3-PGA as the first labeled compound formed within seconds, proving that RuBP (5C) accepts CO2 (1C) to yield two 3-PGA (3C) molecules."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "If the illumination is maintained but the CO2 concentration is suddenly dropped to zero, what will happen to the relative concentrations of RuBP and 3-PGA?",
                    "options": {
                        "A": "RuBP accumulates because it cannot be carboxylated, while 3-PGA plummets as it continues to be converted to G3P by remaining ATP/NADPH.",
                        "B": "Both RuBP and 3-PGA double in concentration simultaneously.",
                        "C": "3-PGA accumulates while RuBP drops to zero.",
                        "D": "Both molecules decompose into pure elemental carbon powder."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 4. Photorespiration, C4 & CAM Adaptations
    else:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "What is Photorespiration (C2 cycle), and why is it considered a major bioenergetic inefficiency in C3 plants?"
                opts = {
                    "A": "RuBisCO binds oxygen (O2) instead of carbon dioxide (CO2), producing 2-phosphoglycolate which consumes ATP and releases previously fixed carbon without producing sugar.",
                    "B": "Mitochondria shut down cellular respiration whenever chloroplasts are exposed to bright sunlight.",
                    "C": "Plants absorb excessive water vapor through open stomata during heavy rainstorms.",
                    "D": "Chloroplasts consume glucose to synthesize structural cellulose in tree bark."
                }
                expl = "RuBisCO is bifunctional: under high temperature and elevated O2:CO2 ratios, its oxygenase activity binds O2, yielding 3-PGA and toxic 2-phosphoglycolate, wasting up to 25-40% of fixed energy during glycolate salvage."
            else:
                text = "How does C4 plant anatomy (Kranz anatomy) structurally protect RuBisCO from photorespiration?"
                opts = {
                    "A": "Initial CO2 fixation occurs in mesophyll cells via PEP carboxylase, and concentrated CO2 is transported to bundle sheath cells where RuBisCO is isolated from high O2 levels.",
                    "B": "Bundle sheath cells contain zero chlorophyll pigments and operate exclusively in total darkness.",
                    "C": "Mesophyll cells convert leaf surfaces into reflective mirrors that bounce away all oxygen molecules.",
                    "D": "C4 plants lack stomata and absorb carbon dioxide through deep root systems."
                }
                expl = "C4 plants spatially separate carbon capture and the Calvin cycle: PEP carboxylase fixes CO2 into 4-carbon malate in mesophyll cells; malate is decarboxylated in bundle sheath cells, bathing RuBisCO in high CO2 concentrations."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How does Crassulacean Acid Metabolism (CAM) differ from C4 photosynthesis in solving the transpiration-versus-photosynthesis trade-off in arid environments?"
            opts = {
                "A": "CAM separates carbon capture and the Calvin cycle temporally (opening stomata at night to store CO2 as malic acid; closing stomata by day to run Calvin cycle using light energy), whereas C4 separates them spatially between cell types.",
                "B": "CAM plants do not require water or light to synthesize carbohydrates.",
                "C": "CAM plants fix nitrogen gas instead of carbon dioxide to build sugars.",
                "D": "CAM photosynthesis only operates when air temperature exceeds 65 degrees Celsius."
            }
            expl = "CAM plants (cacti, pineapples, agaves) open stomata in cool, humid nights, drastically reducing water transpiration while fixing CO2 into vacuolar malic acid. During hot days, stomata remain sealed and malic acid is decarboxylated internally."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why can PEP Carboxylase fix carbon dioxide efficiently even when stomata are nearly closed, whereas RuBisCO cannot?",
                    "options": {
                        "A": "PEP Carboxylase has a much higher affinity for bicarbonate/CO2 than RuBisCO and possesses zero oxygenase affinity for O2, preventing competitive inhibition.",
                        "B": "PEP Carboxylase generates atmospheric water vapor from carbon dioxide.",
                        "C": "PEP Carboxylase operates exclusively in frozen ice crystals.",
                        "D": "PEP Carboxylase uses nuclear radiation instead of chemical bond energy."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "A greenhouse crop researcher measures net photosynthetic rates in wheat (a C3 crop) and maize (a C4 crop) across a temperature gradient from 20°C to 42°C under full sunlight. What performance divergence will occur and what biochemical mechanism explains it?"
            opts = {
                "A": "Maize photosynthetic efficiency remains high or increases at high temperatures, whereas wheat efficiency collapses due to increased RuBisCO oxygenase affinity and stomatal closure driving photorespiration.",
                "B": "Wheat efficiency quadruples while maize cells undergo thermal lysis and burst.",
                "C": "Both crops switch to anaerobic lactic acid fermentation above 25°C.",
                "D": "Maize stops fixing carbon because PEP carboxylase denatures at 22°C."
            }
            expl = "At high temperatures, CO2 solubility decreases faster than O2 solubility, and RuBisCO's thermal kinetic properties favor oxygenase activity. C4 maize suppresses photorespiration by concentrating CO2 around RuBisCO, outperforming C3 wheat in hot climates."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does C3 wheat outperform C4 maize in cool, temperate climates (e.g., 15°C) under ambient CO2 levels?",
                    "options": {
                        "A": "Photorespiration is minimal at cool temperatures, meaning C3 plants avoid the additional ATP metabolic cost (2 ATP per CO2 fixed) required by the C4 PEP regeneration pathway.",
                        "B": "C4 maize leaves lose all cell membranes at temperatures below 18°C.",
                        "C": "C3 wheat does not require ATP to run the Calvin cycle.",
                        "D": "Cold temperatures convert C3 wheat into a carnivorous plant."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}
