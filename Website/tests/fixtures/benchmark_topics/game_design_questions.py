"""
Authentic Game Design and Development Question Generator
Provides university-grade, domain-specific assessments covering:
1. Core Gameplay Loops & Mechanics-Dynamics-Aesthetics (MDA) Framework
2. Game Rules, State Machines & Emergent Interaction Systems
3. Game Balancing, Dynamic Difficulty Adjustment (DDA) & Economy Loops
4. Level Design, Environmental Storytelling & Player Feedback Systems
"""

from typing import Dict, Any, Optional

def generate_game_design_question(
    c_name: str,
    tier: str,
    q_idx: int,
    has_probe: bool,
    pattern_idx: int = 0
) -> Dict[str, Any]:
    c_low = c_name.lower()

    # 1. Core Gameplay Loops & MDA Framework
    if "loop" in c_low or "mda" in c_low or "mechanics" in c_low and "dynamics" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In the Mechanics-Dynamics-Aesthetics (MDA) framework of game design, how are 'Dynamics' formally defined?"
                opts = {
                    "A": "The run-time behavior of the game mechanics acting upon player inputs and interacting systems over time.",
                    "B": "The pre-rendered 3D cinematic animations and promotional video trailers produced for marketing.",
                    "C": "The compiled binary source code that executes directly on graphics processing hardware.",
                    "D": "The emotional resonance, fun, and psychological satisfaction experienced by the player."
                }
                expl = "Under the MDA framework, Mechanics represent the formal rules and data structures, Dynamics describe the run-time behavioral interactions between mechanics and player input, and Aesthetics describe the player's emotional response."
            else:
                text = "What constitutes the 'Core Gameplay Loop' in interactive game development?"
                opts = {
                    "A": "The primary repeatable cycle of player action, state challenge, feedback, and reward that defines moment-to-moment play.",
                    "B": "The hardware display refresh loop that redraws frame buffers at 60 or 120 Hertz.",
                    "C": "The software licensing agreement verified through cloud digital rights management servers on startup.",
                    "D": "The financial transaction loop that bills player credit cards for recurring subscription fees."
                }
                expl = "A core gameplay loop is the primary cycle of player actions (e.g., Explore -> Combat -> Collect Reward -> Upgrade -> Repeat) that drives player engagement."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why do game designers analyze player engagement from Aesthetics down to Mechanics, whereas developers construct systems from Mechanics up to Aesthetics?"
            opts = {
                "A": "Players perceive a game through its aesthetic feel and emotional feedback first, while developers can only directly manipulate mechanical rules and algorithms to induce those aesthetics.",
                "B": "Game engines prohibit writing mechanics code before final artistic textures and audio assets are rendered.",
                "C": "Aesthetics directly execute on CPU registers, bypassing physics simulation engines entirely.",
                "D": "Players possess source-level debugger access that reveals mechanical algorithms prior to sensory input."
            }
            expl = "The MDA framework highlights this design dichotomy: the designer builds mechanics hoping to produce desired dynamics and aesthetics, while the player directly experiences aesthetics, deduce dynamics, and learns mechanics."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Which design challenge arises when a team attempts to fix an unengaging core loop purely by adding visual polish and particle effects?",
                    "options": {
                        "A": "Cosmetic 'juice' cannot compensate for a lack of meaningful decision-making or sluggish input responsiveness in the underlying mechanics.",
                        "B": "Particle effects reduce player movement speed by automatically doubling gravity variables.",
                        "C": "Audio-visual polish eliminates all physics collisions in modern game engines.",
                        "D": "Visual effects convert single-player titles into turn-based multiplayer games without code changes."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "During playtesting of an action-RPG, players report that combat feels tedious and unrewarding despite having 40 distinct weapon types. How should the systems designer diagnose and resolve this issue?"
            opts = {
                "A": "Analyze the core combat loop's feedback timing, telegraphing, and mechanical differentiation, ensuring weapons produce distinct tactical choices rather than cosmetic stat variations.",
                "B": "Triple the particle emission rates on hit impacts and increase ambient background music volume by 12 decibels.",
                "C": "Remove all player attack capabilities and force players to resolve combat through unskippable dialogue menus.",
                "D": "Require players to restart the entire game from Level 1 whenever a weapon attack misses an enemy."
            }
            expl = "Weapon variety fails when weapons lack distinct dynamics (range, recovery frames, stagger potential). Tightening input responsiveness, telegraphing enemy vulnerabilities, and differentiating attack cadence repairs the core loop."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does differentiating weapon attack frames and stagger potential improve combat feel more effectively than merely altering damage numbers?",
                    "options": {
                        "A": "Frame data and stagger create tangible kinesthetic timing windows and tactical risk-reward decisions for the player.",
                        "B": "Damage numbers alter the 3D polygon count of the character skeleton during animation rendering.",
                        "C": "Frame data eliminates the need for game server network synchronization in online matches.",
                        "D": "Stagger animations prevent the game engine from executing garbage collection routines."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 2. Game Rules, State Machines & Emergent Interaction Systems
    elif "rule" in c_low or "state" in c_low or "interaction" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In game architecture, why are Finite State Machines (FSMs) widely utilized to control enemy character AI and game flow?"
                opts = {
                    "A": "They define explicit, non-overlapping behavioral states (e.g., Patrol, Chase, Attack) with deterministic transitions triggered by game conditions.",
                    "B": "They enable characters to bypass physical obstacles by deleting collision bounding boxes during runtime.",
                    "C": "They automatically generate complete 3D level geometry and lighting maps at compile time.",
                    "D": "They eliminate all memory allocations by executing exclusively inside the GPU vertex cache."
                }
                expl = "Finite State Machines decompose complex entity behavior into distinct discrete states with clear entry, update, and transition conditions based on sensory inputs."
            else:
                text = "What is the primary characteristic of 'Emergent Gameplay' in interactive systems?"
                opts = {
                    "A": "Complex, unscripted player strategies and situations that arise naturally from the interaction of simple, consistent game rules.",
                    "B": "Pre-scripted Quick-Time Events (QTEs) where pressing a highlighted button triggers a fixed cinematic sequence.",
                    "C": "Hardcoded developer cheat codes programmed directly into debugging consoles.",
                    "D": "Random computer crashes triggered by overheating system hardware components."
                }
                expl = "Emergence occurs when simple modular systems (e.g., fire spreads to wooden objects, electricity travels through water) combine dynamically to allow novel player solutions never explicitly scripted by designers."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "How do positive feedback loops differ fundamentally from negative feedback loops in systemic game design?"
            opts = {
                "A": "Positive feedback loops amplify current advantages leading to runaway snowballs, whereas negative feedback loops dampen leads and stabilize the game state.",
                "B": "Positive feedback loops award achievements, while negative feedback loops display game-over screens.",
                "C": "Negative feedback loops double player movement speed, while positive feedback loops lock user input controls.",
                "D": "Positive feedback loops require internet access, while negative feedback loops operate exclusively offline."
            }
            expl = "Positive feedback amplifies deviation (e.g., leader gets bonus resources -> buys stronger units -> expands faster), while negative feedback stabilizes (e.g., Mario Kart rubberbanding, trailing players receiving powerful catch-up items)."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why can an unchecked positive feedback loop destroy player retention in competitive multiplayer games?",
                    "options": {
                        "A": "An early lead becomes insurmountable, rendering the remainder of the match deterministic and discouraging trailing players from competing.",
                        "B": "Positive feedback loops cause server hardware to consume excessive electrical wattage and trip breakers.",
                        "C": "Positive feedback loops randomly reassign player account passwords during matches.",
                        "D": "Positive feedback loops force the game engine to switch from 3D graphics to text mode."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "In a turn-based strategy game, playtesters discover an exploit where spamming a low-tier infantry unit consistently defeats elite end-game armies. How should the designer resolve this state breakdown?"
            opts = {
                "A": "Introduce circular balancing (rock-paper-scissors dynamic) such as area-of-effect splash damage that naturally counters clustered cheap infantry.",
                "B": "Completely remove all infantry units from the game and ban any player who recruited them.",
                "C": "Double the physical screen size of the infantry sprite without altering any underlying combat attributes.",
                "D": "Force the game to terminate and display an error message whenever more than five infantry units are spawned."
            }
            expl = "Dominant strategy exploits collapse emergent gameplay. Adding a natural counter-mechanic (like splash damage artillery) restores circular strategic balance without invalidating the unit entirely."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why is introducing circular counter-play superior to merely increasing the gold cost of the spammed infantry unit?",
                    "options": {
                        "A": "Counter-play preserves strategic depth and tactical adaptation, whereas cost increases often merely delay the dominant strategy without solving it.",
                        "B": "Increasing gold costs causes floating-point roundoff errors in the database ledger.",
                        "C": "Circular counters eliminate all graphics rendering overhead on client machines.",
                        "D": "Cost adjustments require recertifying the game with international rating boards."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 3. Game Balancing, DDA & Economy Loops
    elif "balanc" in c_low or "econom" in c_low or "dda" in c_low or "difficult" in c_low:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In virtual game economies, what is the vital functional distinction between an 'Economy Faucet' and an 'Economy Sink'?"
                opts = {
                    "A": "Faucets inject new currency or resources into the game world, while sinks permanently consume or remove currency to prevent hyperinflation.",
                    "B": "Faucets represent graphics rendering buffers, while sinks handle audio playback mixing.",
                    "C": "Faucets allow players to download updates, while sinks upload crash diagnostic telemetries.",
                    "D": "Faucets manage user login credentials, while sinks handle peer-to-peer network packet encryption."
                }
                expl = "Faucets introduce resources into the economy (quest rewards, loot drops), while sinks remove them (crafting fees, repair costs, consumables) to maintain resource scarcity and purchasing power."
            else:
                text = "What is the primary objective of Dynamic Difficulty Adjustment (DDA) algorithms in modern video games?"
                opts = {
                    "A": "To dynamically modulate encounter parameters in real time to keep the player within their psychological 'Flow Zone' between boredom and anxiety.",
                    "B": "To intentionally frustrate players so they abandon the game and reduce server operating expenses.",
                    "C": "To dynamically adjust monitor refresh rates to conserve handheld console battery life.",
                    "D": "To scramble control bindings randomly every five minutes to test player reaction reflexes."
                }
                expl = "DDA tracks player performance metrics (deaths, health, completion time) and subtly tunes enemy health, item drops, or AI accuracy to maintain optimal challenge and engagement."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "What game balance breakdown occurs when a game features a 'Dominant Strategy'?"
            opts = {
                "A": "One specific choice or build consistently yields strictly superior outcomes regardless of opponent actions, rendering all alternative options strategically obsolete.",
                "B": "The game server prioritizes players with the lowest latency ping over higher-latency participants.",
                "C": "The user interface displays health bars on the right side of the screen rather than the left.",
                "D": "Enemy AI characters refuse to engage in combat when the player approaches within five meters."
            }
            expl = "A dominant strategy is a choice that is always best regardless of what other players or enemies do. When a dominant strategy exists, interesting decision-making disappears."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "How does asymmetrical game design (e.g., Starcraft races, asymmetric multiplayer) maintain competitive balance without homogenizing faction abilities?",
                    "options": {
                        "A": "By giving factions radically different mechanical strengths and vulnerabilities that balance out dynamically over the course of match phases.",
                        "B": "By ensuring every faction shares identical unit models, animations, and weapon damage numbers.",
                        "C": "By forcing the weaker faction to control twice as many units using split-screen keyboards.",
                        "D": "By rolling a twenty-sided die at match start to award victory to one team automatically."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "Six months after launch, an MMO economy suffers from rampant currency hyperinflation where basic consumable prices have multiplied tenfold. How should the lead economy designer systematically correct this?"
            opts = {
                "A": "Audit and throttle high-yield automated faucets while introducing high-value cosmetic, housing, or progression-based currency sinks to drain surplus liquid currency.",
                "B": "Wipe all player character inventories and reset all gold balances to zero without prior announcement.",
                "C": "Increase gold drop rates by 500% from all monster encounters to help poor players catch up.",
                "D": "Remove all merchants, trade systems, and auctions permanently from the game world."
            }
            expl = "Hyperinflation occurs when faucets outpace sinks. Restricting unchecked faucets and providing attractive high-end gold sinks (housing, mounts, vanity titles) drains excess currency supply."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why are cosmetic and convenience sinks generally preferred over mandatory survival repair tax sinks for currency reclamation?",
                    "options": {
                        "A": "Voluntary aspirational sinks feel rewarding and self-directed, whereas excessive mandatory repair taxes punish struggling or novice players disproportionately.",
                        "B": "Mandatory repair taxes crash the physics simulation loop in 64-bit clients.",
                        "C": "Cosmetic sinks reduce network packet sizes transmitted over UDP sockets.",
                        "D": "Novice players cannot access keyboard and mouse peripherals during repair sequences."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

    # 4. Level Design, Environmental Storytelling & Player Feedback
    else:
        if tier == "basic":
            if pattern_idx % 2 == 0:
                text = "In spatial level design, how does 'Visual Signposting' guide player navigation through a 3D environment?"
                opts = {
                    "A": "Using lighting contrast, architectural leading lines, landmark silhouettes, and color coding to intuitively direct player sightlines toward objectives.",
                    "B": "Placing massive floating 2D text billboards that cover half the player's screen at all times.",
                    "C": "Automatically disabling camera controls and rotating the player's view against their input.",
                    "D": "Painting entire map floors bright pink and rendering all wall geometry invisible."
                }
                expl = "Signposting uses environmental cues (bright doorway in a dark corridor, tall landmark tower, contrasting highlight colors) to guide players naturally without immersion-breaking UI markers."
            else:
                text = "What is the purpose of 'Telegraphing' in enemy combat and trap design?"
                opts = {
                    "A": "Providing clear visual, auditory, or animation anticipation cues before an attack lands so players have a fair window to react or evade.",
                    "B": "Sending an automated SMS text message to the player's mobile phone during an encounter.",
                    "C": "Delaying audio sound effects by five seconds after an attack connects with the player model.",
                    "D": "Rendering enemy attacks completely invisible to surprise the player."
                }
                expl = "Telegraphing provides anticipation frames, glowing cues, or sound wind-ups so deaths feel fair and learned rather than cheap and arbitrary."
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": None}

        elif tier == "conceptual":
            text = "Why is trial-and-error level design featuring unpredictable, untelegraphed instant-death hazards widely regarded as poor design practice?"
            opts = {
                "A": "It strips player agency and skill mastery, forcing progress through rote memorization rather than perception, anticipation, and reflexes.",
                "B": "Instant-death hazards permanently corrupt the player's SSD storage sectors.",
                "C": "Unpredictable hazards cause the GPU to render frames in reverse chronological order.",
                "D": "Rote memorization causes video game engines to fail automated code compilation."
            }
            expl = "Fair challenge rewards observational skill and reflexes. When traps kill without warning, players feel cheated because failure was unpreventable on first encounter."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "How does the 'Safe-to-Deadly' rule of introducing mechanics protect player trust in challenging level design?",
                    "options": {
                        "A": "Introduce a new hazardous mechanic first in an environment where failure has minimal penalty, allowing the player to safely learn its behavior before testing them under lethal stakes.",
                        "B": "Ensure all lethal spikes are deactivated during the final boss encounter.",
                        "C": "Award the player maximum level equipment immediately upon entering the first room.",
                        "D": "Remove all enemy AI from the game until the player completes 10 hours of tutorials."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}

        else: # application
            text = "In a stealth action game, level analytics reveal that 65% of players become hopelessly lost in Chapter 3's industrial warehouse district. How should the level designer reconstruct the environment to fix navigation?"
            opts = {
                "A": "Introduce distinct visual landmarks (e.g., a brightly illuminated smokestack), use contrasting warm lighting along primary paths, and eliminate repetitive copy-pasted room architecture.",
                "B": "Reduce the character movement speed by 80% to force players to walk through the warehouse more slowly.",
                "C": "Spawn twenty invincible sniper enemies in the warehouse rafters to eliminate lost players quickly.",
                "D": "Delete Chapter 3 completely and advance all players directly to the ending credits."
            }
            expl = "Getting lost stems from visual homogeneity (lack of distinct landmarks) and poor hierarchy. Distinct silhouettes, purposeful directional lighting, and architectural framing clarify navigational affordance."
            rp = None
            if has_probe:
                rp = {
                    "prompt": "Why does framing a towering landmark through an archway or window immediately re-orient a disoriented player?",
                    "options": {
                        "A": "It establishes a persistent external compass reference point (spatial anchor) that connects local geometry to the macro level layout.",
                        "B": "Framing landmarks disables all physics calculations on nearby dynamic mesh objects.",
                        "C": "Windows and archways force the game client to reconnect to the host multiplayer server.",
                        "D": "External landmarks double the player's maximum ammunition capacity."
                    },
                    "correct_probe": "A"
                }
            return {"text": text, "options": opts, "correct": "A", "explanation": expl, "reasoning_probe": rp}
