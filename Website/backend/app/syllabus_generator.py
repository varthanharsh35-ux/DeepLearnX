"""
DeepLearnX Syllabus & Custom Topic Question Bank Generator Engine
With Dual-Mode Generation:
1. AI Model API Integration (Google Gemini & OpenAI / OpenRouter):
   - Accepts user-provided API key from UI or environment (.env).
   - Generates authentic, rigorous cognitive assessments for ANY curriculum or syllabus.
   - Enforces pedagogical constraints: equalized option lengths, multi-tier distribution,
     and Two-Tier Reasoning Probes on application questions to detect false mastery.
2. Domain-Aware Semantic Taxonomy Offline Fallback:
   - Recognizes academic fields (History, Biology, Chemistry, Physics, Economics, Math, CS).
   - Generates authentic domain concepts and questions (e.g., French Revolution discusses
     the Three Estates, Bastille, and Reign of Terror rather than software debugging).
"""

import os
import re
import json
import time
import uuid
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

import httpx

try:
    from concept_guide import register_concept_guide
except ImportError:
    try:
        from app.concept_guide import register_concept_guide
    except ImportError:
        from backend.app.concept_guide import register_concept_guide

try:
    from curated_extensions import (
        HORTICULTURE_CURRICULUM,
        FULL_STACK_CURRICULUM,
        FLUID_MECHANICS_CURRICULUM,
        ENGINEERING_GRAPHICS_CURRICULUM,
        normalize_topic_title,
        extract_concepts_from_syllabus
    )
except ImportError:
    try:
        from app.curated_extensions import (
            HORTICULTURE_CURRICULUM,
            FULL_STACK_CURRICULUM,
            FLUID_MECHANICS_CURRICULUM,
            ENGINEERING_GRAPHICS_CURRICULUM,
            normalize_topic_title,
            extract_concepts_from_syllabus
        )
    except ImportError:
        from backend.app.curated_extensions import (
            HORTICULTURE_CURRICULUM,
            FULL_STACK_CURRICULUM,
            FLUID_MECHANICS_CURRICULUM,
            ENGINEERING_GRAPHICS_CURRICULUM,
            normalize_topic_title,
            extract_concepts_from_syllabus
        )

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "deeplearnx.db"

# Domain icon selection heuristics based on subject keywords
THEME_ICONS = [
    (["horticulture", "horticultural", "pomology", "olericulture", "floriculture", "plant propagation", "garden", "gardening"], "🌿", "Agricultural & Plant Sciences"),
    (["engineering graphics", "engineering drawing", "technical drawing", "autocad", "cad", "orthographic", "isometric projection", "drafting", "dimensioning"], "📐", "Engineering Graphics & Design"),
    (["neuroscience", "neuro", "brain", "sleep", "psychology", "cognitive", "psychiatry", "neurology", "synapse"], "🧠", "Neuroscience & Cognitive Sciences"),
    (["music", "harmony", "melody", "rhythm", "chords", "scale", "composition", "tempo", "pitch"], "🎵", "Music & Creative Arts"),
    (["aviation", "flight", "aerodynamics", "aircraft", "airplane", "airfoil", "thrust", "lift"], "✈️", "Aerospace & Aviation"),
    (["marine", "ocean", "coral", "reef", "aquatic", "sea", "fishery"], "🌊", "Marine & Ocean Sciences"),
    (["astronomy", "astrophysics", "stellar", "galaxy", "planet", "telescope", "star", "solar"], "🔭", "Astrophysics & Space Science"),
    (["architecture", "pyramid", "pharaoh", "archaeology", "egyptian", "monument", "temple"], "🏛️", "Architecture & Archaeology"),
    (["full stack", "fullstack", "fsd", "web development", "react", "node", "mern", "mean", "24csi013"], "💻", "Computer Science & Web Architecture"),
    (["french revolution", "history", "revolution", "empire", "war", "civilization", "ancient", "medieval", "bastille", "monarchy"], "🏛️", "History & Humanities"),
    (["types of pests", "type of pest", "pest", "pests", "entomology", "weevil", "aphid", "locust", "borer", "termite", "whitefly"], "🐛", "Agricultural Biology & Applied Entomology"),
    (["pesticide", "pesticides", "crop", "agriculture", "soil", "farming", "insecticide", "herbicide", "fungicide"], "🌾", "Agricultural & Environmental Sciences"),
    (["earthquake", "tectonic", "geology", "plate", "crust", "volcano", "seismic", "fault", "earth science"], "🌍", "Earth & Environmental Sciences"),
    (["medicine", "disease", "pharmacology", "pathology", "immune", "virus", "bacteria", "clinical"], "🩺", "Medical & Health Sciences"),
    (["constitution", "law", "politics", "legal", "rights", "judiciary", "government", "parliament"], "⚖️", "Law & Political Science"),
    (["literature", "poetry", "grammar", "novel", "drama", "linguistics", "author", "metaphor"], "📖", "Literature & Linguistics"),
    (["network", "tcp", "ip", "packet", "protocol", "osi", "internet", "routing"], "🌐", "Computer Science"),
    (["os", "operating system", "process", "thread", "kernel", "deadlock", "memory"], "💻", "Computer Science"),
    (["database", "sql", "dbms", "relational", "nosql", "query", "acid"], "🗄️", "Computer Science"),
    (["algorithm", "data structure", "tree", "graph", "sorting", "hash", "array"], "🌲", "Computer Science"),
    (["python", "java", "c++", "programming", "software", "code", "oop"], "🐍", "Computer Science"),
    (["physics", "mechanics", "thermodynamics", "optics", "quantum", "electromagnetism", "fluid", "gravity"], "⚡", "Physics"),
    (["chemistry", "organic", "polymer", "acid", "reaction", "bond", "periodic", "inorganic", "equilibrium"], "🧪", "Chemistry"),
    (["biology", "cell", "genetics", "dna", "ecology", "evolution", "anatomy", "respiration", "photosynthesis"], "🧬", "Biology"),
    (["math", "calculus", "algebra", "geometry", "statistics", "matrix", "probability", "trigonometry"], "📐", "Mathematics"),
    (["economics", "micro", "macro", "inflation", "market", "finance", "gdp", "supply", "demand", "elasticity"], "📈", "Economics & Business"),
    (["ai", "machine learning", "neural", "deep learning", "nlp", "computer vision", "unsupervised", "autoencoder"], "🤖", "Artificial Intelligence & Data Science")
]

def pick_icon_and_category(topic_title: str, text: str = "") -> tuple:
    combined = f"{topic_title} {text}".lower()
    for keywords, icon, cat in THEME_ICONS:
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}s?\b", combined):
                return icon, cat
    return "📚", "General Academic Subject"

def slugify(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', text.strip().lower()).strip('_')
    return cleaned[:28] if cleaned else "topic"

# =============================================================================
# 1. AI MODEL API CALLER (GEMINI & OPENAI)
# =============================================================================

def build_llm_system_prompt(topic_title: str, syllabus_text: str = "") -> str:
    return f"""You are the DeepLearnX Cognitive Assessment & Diagnostic Engine.
Your goal is to synthesize a complete, rigorous, pedagogically sound cognitive diagnostic assessment bank for the following topic:

Topic Title: {topic_title}
Syllabus / Notes: {syllabus_text or "No specific notes provided; infer the standard academic curriculum for this topic."}

CRITICAL RULES:
1. AUTHENTIC DISCIPLINARY CONTENT:
   - If the topic is History (e.g. French Revolution), discuss historical events, social classes, treaties, and primary causes. NEVER use computer science or software terms!
   - If the topic is Science, Economics, Math, or Literature, strictly use that discipline's real terminology and concepts.
2. EQUALIZED OPTION LENGTHS:
   - For every question, all four options (option_a, option_b, option_c, option_d) MUST have approximately equal word count (within 2-3 words of each other).
   - NEVER make the correct option significantly longer or more detailed than the distractors, to eliminate test-taking length bias!
3. TWO-TIER REASONING PROBES:
   - For every 'application' question, provide a 'reasoning_probe' object with:
     {{
       "prompt": "Why does this principle or cause explain the observed outcome?",
       "options": {{
         "A": "Reason A (equal length)",
         "B": "Reason B (equal length)",
         "C": "Reason C (equal length)",
         "D": "Reason D (equal length)"
       }},
       "correct_probe": "A"
     }}
   - This probe tests whether the student understands the underlying mechanism or just guessed.
4. DIRECTED ACYCLIC GRAPH (DAG) PREREQUISITES:
   - Break the topic into 3 or 4 sequential concepts where later concepts depend on earlier ones.

You MUST respond ONLY with a valid JSON object matching this schema:
{{
  "icon": "Emoji icon matching topic (e.g. 🏛️ for French Revolution)",
  "category": "Subject category name",
  "description": "2-3 sentence overview of what this assessment tests",
  "concepts": [
    {{
      "id_suffix": "c1",
      "name": "Concept 1 Name (e.g. The Three Estates and Feudal Inequities)",
      "description": "Clear academic explanation of this concept",
      "prerequisites": [],
      "core_idea": "Core principle in simple, conversational English",
      "example": "Relatable everyday or historical real-world example",
      "common_mistake": "Frequent misconception or trap students fall into",
      "key_takeaway": "One-sentence golden rule summary"
    }},
    {{
      "id_suffix": "c2",
      "name": "Concept 2 Name (e.g. Fiscal Crisis and Estates-General of 1789)",
      "description": "Clear academic explanation of this concept",
      "prerequisites": ["c1"],
      "core_idea": "Core principle in simple English",
      "example": "Relatable example",
      "common_mistake": "Frequent misconception",
      "key_takeaway": "One-sentence takeaway"
    }},
    {{
      "id_suffix": "c3",
      "name": "Concept 3 Name (e.g. Storming of the Bastille and Rights of Man)",
      "description": "Clear academic explanation of this concept",
      "prerequisites": ["c2"],
      "core_idea": "Core principle in simple English",
      "example": "Relatable example",
      "common_mistake": "Frequent misconception",
      "key_takeaway": "One-sentence takeaway"
    }},
    {{
      "id_suffix": "c4",
      "name": "Concept 4 Name (e.g. The Radical Republic and Reign of Terror)",
      "description": "Clear academic explanation of this concept",
      "prerequisites": ["c3"],
      "core_idea": "Core principle in simple English",
      "example": "Relatable example",
      "common_mistake": "Frequent misconception",
      "key_takeaway": "One-sentence takeaway"
    }}
  ],
  "misconceptions": [
    {{
      "concept_suffix": "c1",
      "code": "M-CUST-01",
      "name": "Specific student misconception name",
      "description": "Why students form this incorrect mental model",
      "remediation": "How a teacher corrects this misconception clearly"
    }},
    {{
      "concept_suffix": "c2",
      "code": "M-CUST-02",
      "name": "Specific misconception name",
      "description": "Why students form this incorrect mental model",
      "remediation": "How a teacher corrects this misconception clearly"
    }},
    {{
      "concept_suffix": "c3",
      "code": "M-CUST-03",
      "name": "Specific misconception name",
      "description": "Why students form this incorrect mental model",
      "remediation": "How a teacher corrects this misconception clearly"
    }},
    {{
      "concept_suffix": "c4",
      "code": "M-CUST-04",
      "name": "Specific misconception name",
      "description": "Why students form this incorrect mental model",
      "remediation": "How a teacher corrects this misconception clearly"
    }}
  ],
  "questions": [
    {{
      "concept_suffix": "c1",
      "question_type": "basic",
      "difficulty": "easy",
      "question_text": "Question testing foundational recall",
      "option_a": "Correct answer text",
      "option_b": "Plausible distractor text of equal length",
      "option_c": "Plausible distractor text of equal length",
      "option_d": "Plausible distractor text of equal length",
      "correct_option": "A",
      "explanation": "Clear explanation of why option A is correct",
      "reasoning_probe": null
    }}
    // Provide a total of 10 to 12 questions: 4 'basic', 4 'conceptual', and 3-4 'application' with reasoning_probe.
  ]
}}
"""

# Load .env file if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

def clean_and_parse_llm_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Robustly cleans and parses JSON from LLM responses."""
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    # Strip markdown block delimiters
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    # Extract outermost JSON object if surrounded by any preamble/postamble
    match = re.search(r'(\{[\s\S]*\})', cleaned)
    if match:
        cleaned = match.group(1)

    # First attempt: direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Second attempt: strip trailing commas before closing braces/brackets
    try:
        sanitized = re.sub(r',\s*([}\]])', r'\1', cleaned)
        return json.loads(sanitized)
    except Exception as e:
        print(f"[JSON Parse Error] Failed to parse LLM response: {e}")
        return None

def generate_via_gemini_api(topic_title: str, syllabus_text: str, api_key: str, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Calls Google Gemini REST API to generate structured cognitive assessment with model fallbacks and backoff."""
    # Official Google Gemini API model identifiers for v1beta
    default_candidates = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest"
    ]
    if model_name:
        candidate_models = [model_name] + [m for m in default_candidates if m != model_name]
    else:
        candidate_models = default_candidates

    # Guard prompt size to stay within token quotas
    trimmed_syllabus = (syllabus_text or "").strip()
    if len(trimmed_syllabus) > 3000:
        trimmed_syllabus = trimmed_syllabus[:3000]

    prompt = build_llm_system_prompt(topic_title, trimmed_syllabus)
    
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    
    last_error = None
    with httpx.Client(timeout=30.0) as client:
        for m in candidate_models:
            if not m:
                continue
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            try:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                        raw_text = candidates[0]["content"]["parts"][0].get("text", "")
                        parsed = clean_and_parse_llm_json(raw_text)
                        if parsed and "concepts" in parsed and "questions" in parsed:
                            print(f"[Gemini API] Successfully generated assessment using {m}!")
                            parsed["_model_used"] = m
                            return parsed
                        else:
                            print(f"[Gemini API Attempt] Model {m} returned JSON missing concepts/questions")
                elif response.status_code in (429, 503):
                    print(f"[Gemini API Attempt] Model {m} returned HTTP {response.status_code}. Trying next candidate...")
                    last_error = f"HTTP {response.status_code}: Model overloaded or rate limit reached"
                    continue
                else:
                    err_text = ""
                    try:
                        err_json = response.json()
                        err_text = err_json.get("error", {}).get("message", response.text[:200])
                    except Exception:
                        err_text = response.text[:200]
                    last_error = f"HTTP {response.status_code}: {err_text}"
                    print(f"[Gemini API Error] Model {m}: {last_error}")
                    # If invalid key (400/403), stop immediately instead of retrying across all candidates
                    if response.status_code in (400, 403):
                        break
            except Exception as e:
                last_error = str(e)
                print(f"[Gemini API Exception] Model {m}: {e}")
                continue
                
    if last_error:
        raise RuntimeError(f"Gemini API generation failed: {last_error}")
    return None

def generate_via_openai_api(topic_title: str, syllabus_text: str, api_key: str, model_name: str = "gpt-4o-mini") -> Optional[Dict[str, Any]]:
    """Calls OpenAI REST API to generate structured cognitive assessment."""
    url = "https://api.openai.com/v1/chat/completions"
    prompt = build_llm_system_prompt(topic_title, syllabus_text)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are an expert cognitive educational psychometrician who produces valid JSON assessments."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    
    with httpx.Client(timeout=45.0) as client:
        try:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                err_text = response.text[:200]
                try:
                    err_json = response.json()
                    err_text = err_json.get("error", {}).get("message", err_text)
                except Exception:
                    pass
                raise RuntimeError(f"OpenAI API HTTP {response.status_code}: {err_text}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = clean_and_parse_llm_json(content)
            if parsed:
                parsed["_model_used"] = model_name
            return parsed
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

def check_provider_status() -> Dict[str, Any]:
    """Reports live provider status, configuration, reachability, and active generation mode."""
    gemini_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    openai_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    
    def mask_key(k: str) -> str:
        if not k:
            return "Not Configured"
        if len(k) <= 8:
            return "***"
        return f"{k[:6]}...{k[-4:]}"
        
    gemini_reachable = False
    openai_reachable = False
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get("https://generativelanguage.googleapis.com")
            gemini_reachable = resp.status_code in (200, 400, 404)
    except Exception:
        gemini_reachable = False
        
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get("https://api.openai.com/v1/models")
            openai_reachable = resp.status_code in (200, 401)
    except Exception:
        openai_reachable = False
        
    active_mode = "live_llm" if (gemini_key or openai_key) else "offline_knowledge_synthesis"
    
    return {
        "status": "ready" if active_mode == "live_llm" else "offline_ready",
        "active_mode": active_mode,
        "providers": {
            "gemini": {
                "configured": bool(gemini_key),
                "key_masked": mask_key(gemini_key),
                "network_reachable": gemini_reachable,
                "supported_models": ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]
            },
            "openai": {
                "configured": bool(openai_key),
                "key_masked": mask_key(openai_key),
                "network_reachable": openai_reachable,
                "supported_models": ["gpt-4o-mini", "gpt-4o"]
            }
        },
        "notice": (
            "Live cloud LLM generation is active."
            if active_mode == "live_llm"
            else "No API key detected in environment (.env). Custom topics will generate via authentic offline factual knowledge synthesis. Enter a Gemini or OpenAI API key in the UI or Website/.env to activate live LLM generation."
        )
    }

# =============================================================================
# 2. DOMAIN-AWARE OFFLINE CURRICULA (HISTORICAL, SCIENTIFIC, ECONOMIC)
# =============================================================================

NETWORKS_CURRICULUM = {
    "icon": "🌐",
    "category": "Computer Science & Networking",
    "description": "Comprehensive diagnostic assessment of computer networking: OSI/TCP-IP layered architectures, transport layer mechanics (TCP vs. UDP), IP subnetting and routing, and application protocols.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Layered Architectures & The OSI / TCP-IP Models",
            "description": "Layered protocol abstraction, header encapsulation and decapsulation, and service boundaries between network stack layers.",
            "prerequisites": [],
            "core_idea": "Layered network stacks enable modularity: application data is sequentially encapsulated into transport segments, network packets, and link frames.",
            "example": "A web browser wrapping an HTTP GET request into a TCP segment with port 80, which is then enclosed in an IP packet with destination routing addresses.",
            "common_mistake": "Confusing the theoretical 7-layer OSI model with the operational 4-layer TCP/IP Internet model.",
            "key_takeaway": "Protocol encapsulation appends headers at each layer to manage addressing and delivery across heterogeneous networks."
        },
        {
            "id_suffix": "c2",
            "name": "Transport Layer Protocols: TCP vs. UDP Dynamics",
            "description": "Connection-oriented vs connectionless transmission, three-way handshakes, sequence numbers, sliding window flow control, and congestion avoidance.",
            "prerequisites": ["c1"],
            "core_idea": "TCP guarantees reliable, ordered byte-stream delivery using sequence acknowledgments, while UDP provides lightweight, connectionless low-latency transport.",
            "example": "Web page loading uses TCP to guarantee no text or code is missing, while real-time voice calls use UDP where dropping a 20ms packet is better than delaying audio.",
            "common_mistake": "Assuming UDP is flawed because it lacks retransmission; UDP is intentionally designed for real-time applications where delayed packets are useless.",
            "key_takeaway": "TCP trades overhead for guaranteed delivery, whereas UDP prioritizes minimal latency and simplicity."
        },
        {
            "id_suffix": "c3",
            "name": "Network Layer Addressing, Subnetting & Routing",
            "description": "IPv4/IPv6 logical addressing, CIDR subnet masking, ARP resolution, default gateways, and shortest-path packet forwarding.",
            "prerequisites": ["c2"],
            "core_idea": "IP addresses identify host interfaces logically across global subnets; routers inspect destination IP headers to forward packets hop-by-hop toward their destination.",
            "example": "A router comparing a packet's destination IP against a /24 subnet mask to determine whether to deliver it locally via ARP or forward to the default gateway.",
            "common_mistake": "Believing switches route packets using IP addresses; standard Layer 2 switches forward Ethernet frames based strictly on MAC tables, while routers use IP tables.",
            "key_takeaway": "Routers interconnect different subnets via logical IP routing, whereas switches deliver frames inside local broadcast domains using MAC addresses."
        },
        {
            "id_suffix": "c4",
            "name": "Application Protocols, DNS & Network Security",
            "description": "Hierarchical DNS namespace resolution, HTTP/HTTPS stateless request-response lifecycles, TLS cryptographic handshakes, and firewall filtering.",
            "prerequisites": ["c3"],
            "core_idea": "Application protocols facilitate user services; DNS resolves symbolic domain names to routable IP addresses, and TLS encrypts traffic across untrusted networks.",
            "example": "Entering a URL into a browser initiates recursive DNS lookups from root servers to authoritative nameservers before establishing an encrypted TLS connection.",
            "common_mistake": "Assuming standard DNS queries are encrypted; traditional DNS transmits queries in plaintext over UDP port 53 unless DNS-over-HTTPS (DoH) is active.",
            "key_takeaway": "DNS translates human-readable domain names into numerical IP addresses, acting as the global directory for the Internet."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-NET-01",
            "name": "Layer Encapsulation Confusion",
            "description": "Believing lower physical and link layers can directly read or modify application layer payloads without decapsulation.",
            "remediation": "Review the encapsulation pipeline showing how each layer only inspects and processes its own corresponding protocol header."
        },
        {
            "concept_suffix": "c2",
            "code": "M-NET-02",
            "name": "UDP Inadequacy Fallacy",
            "description": "Thinking UDP is an obsolete or defective protocol simply because it lacks acknowledgment and retransmission mechanisms.",
            "remediation": "Demonstrate that for VoIP, video streaming, and online gaming, retransmitting late packets causes jitter that destroys the real-time experience."
        },
        {
            "concept_suffix": "c3",
            "code": "M-NET-03",
            "name": "Switch vs Router Addressing Confusion",
            "description": "Conflating Layer 2 MAC address frame switching with Layer 3 IP address packet routing.",
            "remediation": "Differentiate local broadcast domain forwarding via MAC tables from inter-network hop-by-hop forwarding via IP routing tables."
        },
        {
            "concept_suffix": "c4",
            "code": "M-NET-04",
            "name": "Default DNS Encryption Fallacy",
            "description": "Assuming that all standard DNS traffic is encrypted and private from internet service providers by default.",
            "remediation": "Inspect plaintext DNS UDP query packets in Wireshark to show that domain requests are visible unless using encrypted DNS protocols like DoH or DoT."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What fundamental networking process occurs when a sender's protocol stack wraps higher-layer data with new header control information?",
            "option_a": "Protocol encapsulation down the communication stack",
            "option_b": "Data compression to minimize physical bandwidth usage",
            "option_c": "Signal modulation across analogue wireless antennas",
            "option_d": "Packet fragmentation into equalized bitstream blocks",
            "correct_option": "A",
            "explanation": "Encapsulation is the sequential process where each layer wraps payload data with its own protocol header before passing it down.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "At which layer of the OSI model does an Ethernet switch operate when making frame forwarding decisions?",
            "option_a": "Data Link layer inspecting destination MAC addresses",
            "option_b": "Network layer examining destination IP addresses",
            "option_c": "Transport layer tracking TCP port connection numbers",
            "option_d": "Physical layer converting digital bits into voltages",
            "correct_option": "A",
            "explanation": "Standard Layer 2 Ethernet switches operate at the Data Link layer, forwarding frames based on their MAC address table.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which transport protocol guarantees reliable, ordered packet delivery through sequence numbers and acknowledgments?",
            "option_a": "Transmission Control Protocol establishing byte streams",
            "option_b": "User Datagram Protocol transmitting raw datagrams",
            "option_c": "Internet Control Message Protocol reporting errors",
            "option_d": "Address Resolution Protocol resolving local hardware",
            "correct_option": "A",
            "explanation": "TCP provides reliable, ordered, and error-checked delivery of a stream of octets between applications running on hosts.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why is User Datagram Protocol (UDP) preferred over TCP for live multiplayer video games and voice calls?",
            "option_a": "It eliminates handshake and retransmission delays for real-time speed",
            "option_b": "It provides stronger end-to-end data encryption across public routers",
            "option_c": "It automatically corrects corrupt bit errors without retransmitting",
            "option_d": "It guarantees that packets arrive in the exact order they were sent",
            "correct_option": "A",
            "explanation": "UDP has minimal overhead and zero retransmission delays, making it ideal for real-time applications where timely delivery matters more than lost packets.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A network client initiates a TCP connection to a remote web server. What sequence of packets constitutes the standard connection handshake?",
            "option_a": "SYN sent by client, SYN-ACK returned by server, ACK sent by client",
            "option_b": "ACK sent by client, SYN returned by server, FIN sent by client",
            "option_c": "HELLO sent by client, READY returned by server, CONNECT by client",
            "option_d": "DATA sent by client, ACK returned by server, CLOSE sent by client",
            "correct_option": "A",
            "explanation": "The TCP three-way handshake consists of SYN (synchronize), SYN-ACK (synchronize-acknowledge), and ACK (acknowledge).",
            "reasoning_probe": {
                "prompt": "Why must the client send a final ACK packet before data transmission begins?",
                "options": {
                    "A": "To confirm to the server that the client received the server's initial sequence number.",
                    "B": "To negotiate the physical cable voltage before sending binary bits.",
                    "C": "To inform the operating system kernel to shut down background network interfaces.",
                    "D": "To verify that the client has paid for its internet service subscription."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What is the primary function of a subnet mask in an IPv4 network configuration?",
            "option_a": "Separating the host address bits from the network address bits",
            "option_b": "Encrypting outgoing data packets before transmission over the web",
            "option_c": "Assigning unique physical hardware MAC addresses to NIC cards",
            "option_d": "Compressing packet header sizes to increase throughput speeds",
            "correct_option": "A",
            "explanation": "A subnet mask determines which portion of an IP address corresponds to the network identifier and which portion identifies the specific host.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "How does Address Resolution Protocol (ARP) facilitate communication on a local Ethernet local area network?",
            "option_a": "By discovering the physical MAC address associated with a known IP address",
            "option_b": "By translating human-readable website domain names into numeric IP addresses",
            "option_c": "By dynamically assigning temporary IP addresses to newly connected devices",
            "option_d": "By encrypting wireless radio signals between client laptops and access points",
            "correct_option": "A",
            "explanation": "ARP maps a known network-layer IP address to a physical data-link layer MAC address on the local network segment.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A network host with IP 192.168.10.50/24 needs to send a packet to 10.0.0.1. What does the host do first after examining its routing table?",
            "option_a": "Forwards the packet to its local default gateway router interface",
            "option_b": "Sends an ARP broadcast directly across the local switch for 10.0.0.1",
            "option_c": "Discards the packet immediately because the destination IP is remote",
            "option_d": "Changes its own local IP address to 10.0.0.50 to match the remote subnet",
            "correct_option": "A",
            "explanation": "Because 10.0.0.1 is on a different subnet, the host forwards the packet to its configured default gateway router for routing.",
            "reasoning_probe": {
                "prompt": "How does the sending host determine that 10.0.0.1 is not on its local network?",
                "options": {
                    "A": "Applying the /24 subnet mask to 10.0.0.1 yields a different network ID than 192.168.10.0.",
                    "B": "The destination address has fewer total numbers than the local host address.",
                    "C": "The host checks its local browser cache history to see if it visited 10.0.0.1.",
                    "D": "The physical network card refuses to transmit packets to addresses starting with 10."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which internet protocol is responsible for translating human-friendly domain names like 'deeplearnx.org' into numeric IP addresses?",
            "option_a": "Domain Name System resolving hierarchical naming records",
            "option_b": "Dynamic Host Configuration Protocol allocating IP leases",
            "option_c": "Simple Network Management Protocol monitoring server uptime",
            "option_d": "Network Time Protocol synchronizing system clock timestamps",
            "correct_option": "A",
            "explanation": "DNS acts as the phonebook of the Internet, resolving alphanumeric domain names into machine-routable IP addresses.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What primary security enhancement distinguishes HTTPS communication from standard unencrypted HTTP?",
            "option_a": "Transport Layer Security encrypting data payloads and authenticating servers",
            "option_b": "Faster packet delivery by eliminating the TCP transport handshake layer",
            "option_c": "Permanent caching of all user passwords on public intermediary proxy routers",
            "option_d": "Replacing IP addresses with proprietary 128-bit hardware identifier keys",
            "correct_option": "A",
            "explanation": "HTTPS encrypts the HTTP communication channel using TLS/SSL, providing confidentiality, data integrity, and server authentication.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A network security engineer configures a stateful firewall. How does a stateful firewall differ from a basic stateless packet filter?",
            "option_a": "It tracks the state of active connections, permitting return traffic for open sessions",
            "option_b": "It only filters traffic based strictly on individual packet source and destination ports",
            "option_c": "It shuts down the physical network interface whenever incoming traffic exceeds 10 Mbps",
            "option_d": "It requires every individual data packet to be manually approved by an administrator",
            "correct_option": "A",
            "explanation": "Stateful firewalls maintain a state table tracking ongoing connections (e.g. TCP handshakes), automatically allowing legitimate return response packets.",
            "reasoning_probe": {
                "prompt": "Why does connection state tracking provide superior protection against unauthorized inbound packets?",
                "options": {
                    "A": "Inbound packets claiming to be response traffic are blocked unless an outbound connection was initiated.",
                    "B": "Stateful filters convert all TCP packets into unrouteable UDP datagrams automatically.",
                    "C": "Tracking state eliminates the need for any IP addressing in network packets.",
                    "D": "Firewalls can only inspect packet headers if the client computer is completely turned off."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What is the primary operational benefit of protocol layering in modern computer network architectures?",
            "option_a": "Enabling modular development where layer implementations can change independently",
            "option_b": "Decreasing total packet transmission size by removing all protocol headers",
            "option_c": "Ensuring that only one single computer hardware manufacturer can build devices",
            "option_d": "Preventing any application from using more than one hundred bytes of memory",
            "correct_option": "A",
            "explanation": "Layering decouples network functionality so individual layers can evolve (e.g. switching from IPv4 to IPv6) without rewriting higher-layer applications.",
            "reasoning_probe": None
        }
    ]
}

PESTICIDE_CURRICULUM = {
    "icon": "🌾",
    "category": "Agricultural Science & Ecology",
    "description": "Comprehensive diagnostic assessment of agricultural pests and chemical pesticides: target classifications, biochemical modes of action, ecotoxicological bioaccumulation, and Integrated Pest Management (IPM).",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Chemical Classification & Target Organisms",
            "description": "Classification of chemical pest controls by target taxon including insecticides, herbicides, fungicides, rodenticides, and nematicides.",
            "prerequisites": [],
            "core_idea": "Pesticides are categorized primarily by the specific type of organism they are formulated to eliminate (insects, competing weeds, fungal blights, or rodent vectors).",
            "example": "Applying glyphosate herbicide to eliminate invasive weeds in an orchard versus spraying malathion insecticide to control aphid outbreaks.",
            "common_mistake": "Assuming all pesticides are insecticides; insecticides are only one specialized subclass of pesticides alongside herbicides and fungicides.",
            "key_takeaway": "The '-cide' suffix specifies the target pest taxon, ensuring selective agricultural intervention."
        },
        {
            "id_suffix": "c2",
            "name": "Biochemical Modes of Action & Target Sites",
            "description": "Physiological mechanisms of toxicity including contact vs. systemic uptake, acetylcholinesterase inhibition, sodium channel gating, and photosynthesis disruption.",
            "prerequisites": ["c1"],
            "core_idea": "Different chemical classes attack distinct physiological processes (e.g. organophosphates bind acetylcholinesterase, locking synapses into perpetual firing).",
            "example": "Systemic neonicotinoids are absorbed through roots and translocated throughout the plant sap, poisoning sap-feeding aphids upon ingestion.",
            "common_mistake": "Believing all pesticides must be ingested by the pest; contact poisons penetrate directly through the insect's outer chitinous cuticle.",
            "key_takeaway": "Rotating chemical classes with distinct biochemical target sites prevents physiological resistance from emerging."
        },
        {
            "id_suffix": "c3",
            "name": "Environmental Persistence, Bioaccumulation & Ecotoxicity",
            "description": "Chemical stability in soil and water, lipophilic storage in fatty tissues, trophic biomagnification in food webs, and non-target risks to pollinators.",
            "prerequisites": ["c2"],
            "core_idea": "Persistent lipophilic pesticides resist biological degradation and concentrate in fatty tissues, multiplying in toxicity at higher trophic levels.",
            "example": "DDT runoff absorbed by aquatic plankton magnifies up the food chain, causing reproductive collapse and eggshell thinning in predatory bald eagles.",
            "common_mistake": "Confusing bioaccumulation (accumulation in an individual organism over its lifetime) with biomagnification (increasing concentration up trophic tiers).",
            "key_takeaway": "Persistent organic pollutants magnify up trophic pyramids, necessitating biodegradable, narrow-spectrum chemistries."
        },
        {
            "id_suffix": "c4",
            "name": "Pesticide Resistance & Integrated Pest Management (IPM)",
            "description": "The pesticide treadmill, selection pressure for resistant alleles, economic thresholds, biological control agents, and sustainable crop rotation.",
            "prerequisites": ["c3"],
            "core_idea": "Continuous single-chemical spraying eliminates susceptible individuals and selects for resistant mutants; IPM combines biological, cultural, and targeted chemical tactics.",
            "example": "Releasing predatory ladybugs to suppress aphid populations below the Economic Injury Level rather than spraying broad-spectrum neurotoxins.",
            "common_mistake": "Assuming that increasing the pesticide application rate permanently overcomes genetic resistance in pest populations.",
            "key_takeaway": "IPM aims to suppress pest populations below the Economic Injury Level using multi-faceted ecological controls rather than total eradication."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-PEST-01",
            "name": "Pesticide-Insecticide Equivalence Fallacy",
            "description": "Believing the term 'pesticide' exclusively refers to chemicals that kill insects, ignoring herbicides, fungicides, and rodenticides.",
            "remediation": "Review the taxonomic classification of pesticides where insecticides represent only one specific category among diverse chemical controls."
        },
        {
            "concept_suffix": "c2",
            "code": "M-PEST-02",
            "name": "Ingestion-Only Action Fallacy",
            "description": "Assuming that chemical pesticides can only poison an insect if the insect consumes treated foliage or plant tissues.",
            "remediation": "Clarify the distinction between stomach poisons, systemic vascular translocators, and contact poisons that penetrate cuticular membranes."
        },
        {
            "concept_suffix": "c3",
            "code": "M-PEST-03",
            "name": "Bioaccumulation vs. Biomagnification Confusion",
            "description": "Conflating chemical buildup in an individual organism with exponential concentration amplification across successive trophic predator levels.",
            "remediation": "Trace persistent organochlorines mathematically through aquatic food webs from plankton to small fish, apex fish, and predatory birds."
        },
        {
            "concept_suffix": "c4",
            "code": "M-PEST-04",
            "name": "Total Eradication Fallacy",
            "description": "Assuming that agricultural sustainability requires 100% elimination of all pest organisms from crop fields.",
            "remediation": "Explain Economic Injury Levels (EIL) and Economic Thresholds (ET) showing why maintaining low sub-economic pest populations sustains beneficial predators."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which chemical pesticide classification is formulated specifically to control and eliminate unwanted weed species competing with agricultural crops?",
            "option_a": "Herbicides targeting vegetative plant metabolic processes",
            "option_b": "Fungicides halting fungal spore germination on crops",
            "option_c": "Nematicides paralyzing microscopic soil-dwelling worms",
            "option_d": "Rodenticides causing internal mammal hemorrhage in fields",
            "correct_option": "A",
            "explanation": "Herbicides are specialized chemical compounds formulated to selectively or non-selectively eradicate competing weed vegetation.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "How do systemic pesticides fundamentally differ in their protective action from contact pesticides?",
            "option_a": "They are absorbed and translocated throughout plant vascular tissues",
            "option_b": "They remain strictly on the outer leaf surface without entering tissues",
            "option_c": "They only kill pests when volatilized into atmospheric gaseous vapors",
            "option_d": "They require direct physical spray contact with the pest cuticle to function",
            "correct_option": "A",
            "explanation": "Systemic pesticides enter the plant's xylem and phloem, protecting all tissues including new growth from feeding pests.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which classification of chemical pesticide is deployed specifically to prevent mildew, blights, and rust infections in fruit orchards?",
            "option_a": "Fungicides inhibiting fungal cellular respiration",
            "option_b": "Miticides eradicating spider mites on orchard leaves",
            "option_c": "Larvicides destroying aquatic mosquito wrigglers",
            "option_d": "Defoliants removing foliage prior to mechanized harvest",
            "correct_option": "A",
            "explanation": "Fungicides protect crops against pathogenic fungi by preventing spore germination and fungal mycelium proliferation.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What is the primary biochemical mechanism through which organophosphate insecticides inflict fatal neurotoxicity on insect pests?",
            "option_a": "Inhibiting acetylcholinesterase, causing continuous synaptic nerve firing",
            "option_b": "Blocking photosynthetic electron transport in gut chloroplasts",
            "option_c": "Dissolving the structural lipid waxes of the external exoskeleton",
            "option_d": "Preventing the transcription of messenger RNA inside cell nuclei",
            "correct_option": "A",
            "explanation": "Organophosphates irreversibly inhibit the acetylcholinesterase enzyme, preventing acetylcholine breakdown and causing fatal neuroexcitation.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "An agricultural scout notes an insecticide keeps voltage-gated sodium channels open in insect axons, causing tremors and paralysis. Which chemical class is this?",
            "option_a": "Pyrethroid insecticides altering axon channel gates",
            "option_b": "Carbamate insecticides reversibly binding enzymes",
            "option_c": "Triazine herbicides disabling electron carriers",
            "option_d": "Anticoagulant rodenticides blocking blood clotting",
            "correct_option": "A",
            "explanation": "Synthetic pyrethroids delay the inactivation of voltage-gated sodium channels in nerve axons, producing repetitive nerve impulses and paralysis.",
            "reasoning_probe": {
                "prompt": "Why does preventing sodium channel deactivation lead to rapid paralysis in insects?",
                "options": {
                    "A": "Sustained inward sodium flux maintains perpetual depolarization, exhausting muscle and nerve cells.",
                    "B": "Sodium depletion inside the blood prevents hemoglobin molecules from binding oxygen.",
                    "C": "Excess extracellular sodium crystallizes inside joints, physically immobilizing the pest.",
                    "D": "Sodium ions convert directly into toxic chlorine gas inside digestive intestines."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why do systemic neonicotinoid pesticides pose severe chronic risks to honeybees and other beneficial pollinators?",
            "option_a": "They translocate into pollen and nectar, causing systemic neurocognitive disorientation",
            "option_b": "They strip the wax coating off wings, preventing flight during foraging trips",
            "option_c": "They acidify surrounding soil, destroying subterranean bee nesting burrows",
            "option_d": "They generate loud ultrasonic vibrations that disrupt honeybee dance communication",
            "correct_option": "A",
            "explanation": "Neonicotinoids translocate systemically into floral pollen and nectar, where foraging pollinators ingest sublethal neurotoxic doses that impair navigation.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What ecological phenomenon describes the increasing concentration of persistent, fat-soluble pesticides at higher trophic tiers of a food pyramid?",
            "option_a": "Biomagnification across successive predator tiers",
            "option_b": "Bioaccumulation within an individual animal tissue",
            "option_c": "Eutrophication from nutrient enrichment in water",
            "option_d": "Bioremediation by microbes degrading soil pollutants",
            "correct_option": "A",
            "explanation": "Biomagnification is the progressive increase in chemical concentration across successive consumer trophic levels within an ecosystem food web.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "An apex raptor population experiences severe reproductive failure from cracked, thinned eggshells. Analysis reveals high DDE levels. Which property caused this outcome?",
            "option_a": "High lipid solubility and extreme chemical resistance to metabolic degradation",
            "option_b": "High water solubility allowing rapid absorption through respiratory lungs",
            "option_c": "Low molecular weight enabling swift excretion in bird urinary tracts",
            "option_d": "Instant photolysis breakdown under ultraviolet sunlight exposure",
            "correct_option": "A",
            "explanation": "Organochlorines like DDT and its metabolite DDE are highly lipophilic and chemically stable, allowing them to accumulate in adipose tissue and biomagnify.",
            "reasoning_probe": {
                "prompt": "Why do lipophilic organochlorines accumulate preferentially in apex predators rather than primary herbivores?",
                "options": {
                    "A": "Fatty tissues store unmetabolized toxins, multiplying the predator's intake across hundreds of prey items.",
                    "B": "Apex predators lack liver enzymes capable of processing any synthetic organic compounds.",
                    "C": "Primary herbivores possess active immune mechanisms that destroy all chlorinated molecules instantly.",
                    "D": "Herbivores excrete fat molecules continuously, preventing any cellular chemical retention."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which physical-chemical pesticide property creates the greatest danger of agricultural chemical leaching into drinking water aquifers?",
            "option_a": "High water solubility combined with low soil organic matter adsorption",
            "option_b": "Strong binding affinity to clay minerals and rapid photolysis breakdown",
            "option_c": "Extreme volatility causing rapid transformation into atmospheric gas",
            "option_d": "High lipophilicity causing immediate adhesion to surface vegetation wax",
            "correct_option": "A",
            "explanation": "Pesticides that dissolve readily in water and fail to bind tightly to soil organic particles migrate rapidly through the soil profile into groundwater.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why does repeated, exclusive application of a single broad-spectrum chemical insecticide frequently trigger a secondary pest outbreak?",
            "option_a": "It wipes out natural predators, allowing resistant secondary pests to multiply unchecked",
            "option_b": "It directly mutates non-pest insect species into aggressive predatory carnivores",
            "option_c": "It enriches soil nitrogen content, providing extra nutrients for pest reproduction",
            "option_d": "It causes agricultural crops to stop producing their natural chemical defense phytoalexins",
            "correct_option": "A",
            "explanation": "Broad-spectrum insecticides eliminate beneficial predators and parasitoids that naturally regulate non-target pests, unleashing severe secondary pest infestations.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "Under an Integrated Pest Management (IPM) protocol, at what specific juncture should an agricultural grower execute a chemical pesticide spray?",
            "option_a": "Only when pest population density exceeds the established Economic Threshold",
            "option_b": "As soon as a single pest organism is visibly detected in the crop field",
            "option_c": "On a fixed calendar schedule regardless of actual pest population levels",
            "option_d": "After all natural biological predators have been completely exterminated",
            "correct_option": "A",
            "explanation": "In IPM, chemical interventions are strictly triggered when pest populations cross the Economic Threshold (ET), before reaching the Economic Injury Level (EIL).",
            "reasoning_probe": {
                "prompt": "Why is the Economic Threshold (ET) established at a population level below the Economic Injury Level (EIL)?",
                "options": {
                    "A": "To provide an action buffer so control measures take effect before damage exceeds control costs.",
                    "B": "To ensure that zero pests survive in the field by harvesting time.",
                    "C": "Because chemical pesticides require three months to activate once sprayed on crops.",
                    "D": "To force growers to purchase synthetic chemicals before prices increase seasonally."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Which agricultural tactic constitutes an authentic 'biological control' strategy within an Integrated Pest Management system?",
            "option_a": "Releasing commercially reared parasitic wasps to lay eggs inside pest caterpillars",
            "option_b": "Tilling the soil before planting to expose pest larvae to freezing winter air",
            "option_c": "Spraying a synthetic organophosphate formulation across the entire crop acreage",
            "option_d": "Installing synthetic plastic tarps to prevent weed seeds from receiving sunlight",
            "correct_option": "A",
            "explanation": "Biological control utilizes living natural enemies, such as predators, parasitoids, or pathogens (e.g. Bacillus thuringiensis), to suppress pest populations.",
            "reasoning_probe": None
        }
    ]
}

BIOLOGICAL_PEST_CURRICULUM = {
    "icon": "🐛",
    "category": "Agricultural Biology & Applied Entomology",
    "description": "Comprehensive diagnostic curriculum on biological pest taxonomy: arthropod and nematode classification, feeding morphology & crop damage pathology, primary vs. secondary grain storage borers, and vector epidemiology.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Taxonomic Classification of Agricultural Pests",
            "description": "Distinguishing biological pests across major phyla: Arthropoda (insects, mites), Nematoda (root-knot, cyst nematodes), Mollusca (slugs, snails), and vertebrate rodents.",
            "prerequisites": [],
            "core_idea": "Agricultural pests span distinct taxonomic phyla; effective identification requires recognizing anatomical morphology and phylogenetic traits.",
            "example": "Distinguishing root-knot nematodes (phylum Nematoda) which induce root galls from beetle grubs (phylum Arthropoda) which chew woody root crowns.",
            "common_mistake": "Assuming that all agricultural pests are insects; nematodes, mites, slugs, and rodents represent distinct non-insect animal phyla.",
            "key_takeaway": "Pest organisms are classified by phylum and order to determine species-specific biological vulnerability."
        },
        {
            "id_suffix": "c2",
            "name": "Feeding Morphology & Crop Damage Pathology",
            "description": "Chewing vs. piercing-sucking mouthparts, leaf mining, stem boring, vascular wilting, and secondary fungal mold colonization.",
            "prerequisites": ["c1"],
            "core_idea": "The functional morphology of insect mouthparts dictates the pathological damage symptoms displayed by the host plant.",
            "example": "Aphids use piercing-sucking stylets to extract phloem sap causing leaf curl and honeydew mold, whereas armyworm caterpillars chew whole leaf laminae.",
            "common_mistake": "Believing all insect damage consists of chewed holes in leaves; piercing-sucking pests cause curling, stunting, and viral infection without tissue tearing.",
            "key_takeaway": "Mouthpart morphology (mandibulate vs. haustellate) governs crop injury symptoms and pesticide absorption routes."
        },
        {
            "id_suffix": "c3",
            "name": "Storage, Post-Harvest & Structural Pests",
            "description": "Primary internal grain borers (weevils, grain borers), secondary external feeders (flour beetles, grain mites), and structural wood borers.",
            "prerequisites": ["c2"],
            "core_idea": "Primary storage pests penetrate intact, sound cereal kernels, generating grain debris and entry pathways for secondary pests that feed solely on broken grain.",
            "example": "The rice weevil (Sitophilus oryzae) bores directly into sound wheat seeds, whereas the red flour beetle (Tribolium castaneum) only colonizes broken grain and milled flour.",
            "common_mistake": "Assuming all grain-feeding beetles can bore into whole, undamaged grain; secondary pests starve without pre-damaged grain or primary borer frass.",
            "key_takeaway": "Primary grain borers attack intact seeds; secondary pests colonize post-milling debris and pre-damaged grain."
        },
        {
            "id_suffix": "c4",
            "name": "Biological Vectors & Epidemiological Thresholds",
            "description": "Arthropods transmitting viral and phytoplasma pathogens, non-persistent vs. persistent transmission, and near-zero economic thresholds.",
            "prerequisites": ["c3"],
            "core_idea": "Many devastating pests act as biological vectors transmitting microscopic plant viruses directly into vascular bundles during feeding probes.",
            "example": "Whiteflies (Bemisia tabaci) transmitting Tomato Yellow Leaf Curl Virus into plant phloem, where a single insect vector inoculates systemic plant ruin.",
            "common_mistake": "Assuming pest damage is strictly proportional to biomass consumed; vector insects cause catastrophic loss through disease inoculation even at negligible densities.",
            "key_takeaway": "For vector pests, the economic threshold is near zero because pathogen inoculation occurs within seconds of stylet probing."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-BIOPEST-01",
            "name": "Insect-Exclusive Pest Equivalence Fallacy",
            "description": "Assuming that every agricultural and garden pest is an insect, failing to identify plant-parasitic nematodes, mites, and mollusks.",
            "remediation": "Clarify that nematodes (roundworms) and acari (mites) have distinct body plans and nervous systems requiring non-insecticidal controls."
        },
        {
            "concept_suffix": "c2",
            "code": "M-BIOPEST-02",
            "name": "Mandibular Chewing Damage Presumption",
            "description": "Assuming that harmful crop pests always create visible chew holes, ragged leaf margins, or physical defoliation.",
            "remediation": "Demonstrate that piercing-sucking stylets pierce individual phloem tubes, causing chlorosis, stunting, sooty mold, and viral wilt without tearing leaf tissue."
        },
        {
            "concept_suffix": "c3",
            "code": "M-BIOPEST-03",
            "name": "Primary vs. Secondary Storage Pest Conflation",
            "description": "Believing that all post-harvest storage beetles can bore through undamaged, whole grain seeds.",
            "remediation": "Highlight the functional distinction between primary internal feeders (weevils with rostral snouts) and secondary external feeders (flour beetles lacking boring jaws)."
        },
        {
            "concept_suffix": "c4",
            "code": "M-BIOPEST-04",
            "name": "Direct-Consumption Vector Fallacy",
            "description": "Assuming that the danger of a vector pest is measured only by the volume of plant tissue it physically consumes.",
            "remediation": "Teach that vector insects inject micro-pathogens (viruses, mycoplasmas, bacteria) during salivary exchange, where one bite inoculates a systemic lethal infection."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which agricultural pest organism belongs to the phylum Nematoda rather than the phylum Arthropoda?",
            "option_a": "Meloidogyne incognita (Root-Knot Nematode)",
            "option_b": "Myzus persicae (Green Peach Aphid)",
            "option_c": "Leptinotarsa decemlineata (Colorado Potato Beetle)",
            "option_d": "Plutella xylostella (Diamondback Moth)",
            "correct_option": "A",
            "explanation": "Root-knot nematodes are unsegmented microscopic roundworms belonging to the phylum Nematoda, whereas aphids, beetles, and moths are arthropods.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What anatomical feature reliably distinguishes adult insect pests from adult spider mite (acari) pests?",
            "option_a": "Adult insects possess three pairs of walking legs, while adult mites possess four pairs",
            "option_b": "Insects possess soft non-chitinous bodies whereas mites possess calcified armor shells",
            "option_c": "Mites possess functional wings for long-distance flight whereas insect pests never develop wings",
            "option_d": "Insects are unicellular protozoans whereas mites are multicellular invertebrates",
            "correct_option": "A",
            "explanation": "Insects are hexapods with three pairs of legs and three body regions, while arachnid mites have four pairs of walking legs in the adult stage.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why is classifying a biological pest's taxonomic phylum critical for formulating an agricultural control program?",
            "option_a": "Physiological systems differ fundamentally across phyla, rendering insect neurotoxins ineffective against plant-parasitic nematodes",
            "option_b": "All animal phyla share identical reproductive rates and identical developmental temperature thresholds",
            "option_c": "A pest's phylum determines exclusively whether it feeds on aerial foliage or in soil root systems",
            "option_d": "All invertebrate phyla are governed by identical ecdysone molting hormone regulatory pathways",
            "correct_option": "A",
            "explanation": "Nematodes, mollusks, and arthropods possess fundamentally divergent physiology, neuromuscular junctions, and cuticle chemistry, requiring distinct control mechanisms.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which insect pest feeds by piercing plant tissue and sucking phloem sap rather than chewing leaf laminae?",
            "option_a": "Green peach aphid (Myzus persicae)",
            "option_b": "Desert locust (Schistocerca gregaria)",
            "option_c": "Japanese beetle (Popillia japonica)",
            "option_d": "Fall armyworm (Spodoptera frugiperda)",
            "correct_option": "A",
            "explanation": "Aphids belong to the order Hemiptera and possess specialized piercing-sucking stylets designed to tap into plant vascular bundles.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "How does feeding damage caused by piercing-sucking insect pests fundamentally differ from that caused by chewing defoliators?",
            "option_a": "Piercing-sucking pests extract vascular fluids causing leaf curling and chlorosis without creating bite holes",
            "option_b": "Piercing-sucking pests physically sever leaf petioles, leading to immediate whole-canopy defoliation",
            "option_c": "Chewing defoliators leave leaf laminae intact and exclusively consume subterranean nitrogen nodules",
            "option_d": "Piercing-sucking pests consume only the outer waxy cuticle while leaving leaf veins exposed",
            "correct_option": "A",
            "explanation": "Piercing-sucking insects insert slender stylets into vascular phloem to extract sap, resulting in chlorosis, stunting, leaf distortion, and honeydew without ragged chew marks.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A grower observes severe leaf yellowing, stunting, and sticky liquid covered in black sooty mold across a citrus orchard, but finds zero chewed holes in the foliage. Which pest diagnosis is correct?",
            "option_a": "Infestation by phloem-feeding hemipteran pests (such as psyllids or whiteflies) with piercing-sucking stylets",
            "option_b": "Infestation by subterranean scarab beetle grubs chewing the fibrous root crowns",
            "option_c": "Infestation by grasshoppers consuming interveinal leaf tissue between major veins",
            "option_d": "Infestation by late-instar lepidopteran caterpillars during nocturnal feeding cycles",
            "correct_option": "A",
            "explanation": "Phloem feeders excrete sugar-rich honeydew that serves as a growth substrate for black sooty mold fungi, causing chlorosis without defoliation.",
            "reasoning_probe": {
                "probe_question": "Why does black sooty mold specifically develop alongside phloem-feeding pest outbreaks?",
                "probe_options": {
                    "A": "Phloem sap contains excess carbohydrates; excreted honeydew provides the nutrient substrate for saprophytic fungi",
                    "B": "Chewing defoliators spray antifungal pheromones that completely sterilize foliage against fungal spores",
                    "C": "Piercing insect stylets carry systemic black mold spores directly into root xylem vessels",
                    "D": "Chewed leaf margins prevent fungal hyphae from establishing physical attachment to host cells"
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which pest is classified as a 'primary' grain storage pest capable of boring into completely sound, undamaged cereal kernels?",
            "option_a": "Rice weevil (Sitophilus oryzae)",
            "option_b": "Red flour beetle (Tribolium castaneum)",
            "option_c": "Sawtoothed grain beetle (Oryzaephilus surinamensis)",
            "option_d": "Confused flour beetle (Tribolium confusum)",
            "correct_option": "A",
            "explanation": "Weevils of the genus Sitophilus possess strong rostral snouts with chewing mouthparts that drill directly into intact whole grain kernels.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why are secondary storage pests (such as flour beetles) unable to establish heavy infestations in clean, undamaged whole grain kernels?",
            "option_a": "Secondary pests lack powerful boring mouthparts and can only consume broken grain debris, dust, and frass",
            "option_b": "Secondary storage pests require ultraviolet sunlight which cannot penetrate intact grain husks",
            "option_c": "Primary storage pests synthesize vitamin complexes that secondary pests must ingest to survive",
            "option_d": "Undamaged grain kernels emit lethal hydrogen cyanide vapors until punctured by primary larvae",
            "correct_option": "A",
            "explanation": "Secondary pests feed externally on damaged kernels, milled flour, and dust produced by primary borers or mechanical handling.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A grain silo inspector discovers fine powdery dust, hollowed wheat seeds containing pupae, and localized heating hotspots inside stored wheat. What is the diagnosis?",
            "option_a": "Active infestation by primary internal feeders (such as Sitophilus or Rhyzopertha) whose metabolic respiration produces heat and moisture",
            "option_b": "Superficial infestation by predatory mites that do not penetrate internal grain starch",
            "option_c": "Normal physical grain settling compaction that generates mechanical friction heat",
            "option_d": "Invasion by beneficial ladybird beetles seeking overwintering shelter in the grain bulk",
            "correct_option": "A",
            "explanation": "Primary internal feeders hollow out whole kernels; insect metabolic respiration releases heat and moisture, producing 'hot spots' that degrade stored grain.",
            "reasoning_probe": {
                "probe_question": "Why does insect metabolic respiration in stored grain trigger accelerated secondary spoilage?",
                "probe_options": {
                    "A": "Released metabolic moisture elevates grain humidity, inducing secondary mould growth and grain heating",
                    "B": "Insects consume all ambient oxygen, creating a vacuum that physically crushes surrounding kernels",
                    "C": "Primary pest larvae synthesize solid wax that blocks all ventilation airflow in the silo bin",
                    "D": "Pest pupae release ethylene gas that forces harvested dormant seeds to begin immediate flowering"
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "Which pest insect serves as the primary biological vector transmitting Tomato Yellow Leaf Curl Virus (TYLCV) and Cassava Mosaic Virus?",
            "option_a": "Silverleaf whitefly (Bemisia tabaci)",
            "option_b": "Western honeybee worker (Apis mellifera)",
            "option_c": "Garden earthworm (Lumbricus terrestris)",
            "option_d": "Common green lacewing (Chrysoperla carnea)",
            "correct_option": "A",
            "explanation": "Bemisia tabaci whiteflies are notorious agricultural vectors transmitting dozens of begomoviruses across tropical and subtropical crops.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why is the Economic Injury Level (EIL) set dramatically lower for insect pests that act as plant virus vectors compared to non-vector defoliators?",
            "option_a": "Vector insects transmit systemic, incurable phytopathogens during initial probe feeding, causing total plant loss from minimal insect numbers",
            "option_b": "Non-vector defoliators consume their body weight every minute, making small populations completely harmless",
            "option_c": "Chewing defoliators inject chemical mutagens that make crops permanently toxic to livestock",
            "option_d": "Host plants can completely eradicate viral infections once the vector insect population is controlled",
            "correct_option": "A",
            "explanation": "Because a single vector insect can transmit a fatal systemic virus in seconds, crop loss occurs even at near-zero insect population densities.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "In a papaya orchard, Papaya Ringspot Virus (PRSV) spreads rapidly despite yellow sticky traps capturing only 2 winged aphids per tree each week. Why does this low insect count cause severe disease spread?",
            "option_a": "Winged aphids transmit non-persistent stylet-borne viruses within seconds of probing before flying to adjacent trees without colonizing",
            "option_b": "Two aphids consume more than 90% of total canopy photosynthetic area within forty-eight hours",
            "option_c": "Aphids bore through woody trunks, severing tap roots through rapid mechanical excavating",
            "option_d": "PRSV virus replicates only when vector aphid populations exceed tens of thousands of nymphs per leaf",
            "correct_option": "A",
            "explanation": "Non-persistent viruses attach to aphid mouthparts and transfer during rapid brief probes, allowing transient aphids to spread disease without colonizing the crop.",
            "reasoning_probe": {
                "probe_question": "Why do non-persistent plant viruses spread so effectively despite absence of established pest colonies?",
                "probe_options": {
                    "A": "Transient winged aphids probe-test plants for host suitability, transmitting virus particles within seconds before dispersing",
                    "B": "Non-persistent viruses travel through wind gusts independently of physical insect vectors",
                    "C": "Aphids lay viral spores inside flower stamens which fertilize internal seed embryos",
                    "D": "Chewing caterpillars carry the aphid saliva on their mandibles from plant to plant"
                },
                "correct_probe": "A"
            }
        }
    ]
}

UNSUPERVISED_DL_CURRICULUM = {
    "icon": "🤖",
    "category": "Deep Learning & AI",
    "description": "Comprehensive diagnostic assessment of unsupervised representation learning, autoencoder bottlenecks, manifold learning, and contrastive self-supervised representations.",
    "concepts": [
        {
            "id_suffix": "c1",
            "name": "Dimensionality Reduction & Manifold Learning",
            "description": "Geometric projection techniques including PCA, t-SNE, and UMAP to discover intrinsic low-dimensional data structures.",
            "prerequisites": [],
            "core_idea": "High-dimensional data typically lies near a much lower-dimensional non-linear manifold; dimensionality reduction uncovers these principal axes of variance.",
            "example": "Projecting 784-pixel MNIST handwritten digits onto a 2D plane where different digit clusters naturally separate.",
            "common_mistake": "Assuming linear Principal Component Analysis (PCA) can unfold complex non-linear curved manifolds like the Swiss Roll.",
            "key_takeaway": "Dimensionality reduction eliminates noise and collinearity while preserving intrinsic structural topology."
        },
        {
            "id_suffix": "c2",
            "name": "Autoencoder Bottlenecks & Reconstruction",
            "description": "Neural encoder-decoder architectures with information bottlenecks trained by minimizing input reconstruction error.",
            "prerequisites": ["c1"],
            "core_idea": "By compressing high-dimensional input through a low-dimensional bottleneck layer, the autoencoder is forced to learn efficient, non-trivial latent representations.",
            "example": "Compressing a 1000-feature audio spectrogram into a 32-dimensional code vector that accurately reconstructs the clean original audio.",
            "common_mistake": "Using an unconstrained overcomplete latent dimension without regularization, which allows the network to learn a trivial identity mapping.",
            "key_takeaway": "An information bottleneck or sparsity constraint forces autoencoders to discard noise and isolate governing generative features."
        },
        {
            "id_suffix": "c3",
            "name": "Variational Autoencoders & Probabilistic Latent Spaces",
            "description": "Generative modeling via variational inference, KL divergence prior regularization, and the reparameterization trick.",
            "prerequisites": ["c2"],
            "core_idea": "VAEs enforce a standard Gaussian prior on the latent distribution using KL divergence, enabling continuous interpolation and generative sampling.",
            "example": "Sampling a random vector from N(0, I) and decoding it into a realistic synthetic human face image that never existed in the training set.",
            "common_mistake": "Attempting backpropagation directly through a stochastic random sampling node without utilizing the reparameterization trick.",
            "key_takeaway": "The reparameterization trick isolates stochasticity into an external noise tensor, enabling gradient backpropagation through latent sampling."
        },
        {
            "id_suffix": "c4",
            "name": "Self-Supervised & Contrastive Representation Learning",
            "description": "Learning invariant representations without labels by pulling augmented views together and pushing negative views apart via InfoNCE loss.",
            "prerequisites": ["c3"],
            "core_idea": "Contrastive frameworks (like SimCLR and MoCo) train encoders to recognize that two different augmentations of the same image represent the same concept.",
            "example": "Cropping and color-jittering a dog photo, training the network to produce matching embeddings for both crops while repelling embeddings of cat photos.",
            "common_mistake": "Believing contrastive learning requires ground truth human classification labels; it generates supervision purely from data augmentations.",
            "key_takeaway": "Contrastive self-supervision learns semantic invariances from augmentations without requiring costly human manual annotations."
        }
    ],
    "misconceptions": [
        {
            "concept_suffix": "c1",
            "code": "M-UNSUP-01",
            "name": "Linear PCA Non-Linearity Fallacy",
            "description": "Believing linear PCA can capture non-linear manifold geometry as effectively as t-SNE, UMAP, or deep autoencoders.",
            "remediation": "Demonstrate the Swiss Roll dataset where linear PCA projects distinct manifold layers onto the same overlapping coordinates."
        },
        {
            "concept_suffix": "c2",
            "code": "M-UNSUP-02",
            "name": "Identity Mapping Trap in Overcomplete Autoencoders",
            "description": "Assuming wider latent layers automatically learn better semantic abstractions without regularization.",
            "remediation": "Show that without bottlenecks or L1 sparsity penalties, overcomplete autoencoders memorize the trivial identity function."
        },
        {
            "concept_suffix": "c3",
            "code": "M-UNSUP-03",
            "name": "Stochastic Sampling Gradient Fallacy",
            "description": "Failing to recognize why backpropagation cannot pass through standard random sampling distributions.",
            "remediation": "Review the derivation of the reparameterization trick: z = mu + sigma * epsilon, which keeps the sampling branch differentiable."
        },
        {
            "concept_suffix": "c4",
            "code": "M-UNSUP-04",
            "name": "Self-Supervised Ground-Truth Requirement Fallacy",
            "description": "Thinking contrastive representations require labeled target classes to construct positive and negative pairs.",
            "remediation": "Clarify that contrastive learning treats differently transformed views of the same sample as positives and other batch samples as negatives."
        }
    ],
    "questions": [
        {
            "concept_suffix": "c1",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What fundamental mathematical objective does Principal Component Analysis (PCA) optimize during linear dimensionality reduction?",
            "option_a": "Maximizing variance along orthogonal projection axes",
            "option_b": "Minimizing cross-entropy loss against class labels",
            "option_c": "Preserving geodesic distances along curved manifolds",
            "option_d": "Separating clusters using non-linear kernel boundaries",
            "correct_option": "A",
            "explanation": "PCA computes the eigenvectors of the data covariance matrix to identify orthogonal axes that maximize data variance.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "Why is standard linear PCA insufficient for unrolling non-linear structures such as the classic Swiss Roll dataset?",
            "option_a": "It can only project data onto linear hyperplanes, collapsing non-linear curves",
            "option_b": "It requires class labels that are absent in unsupervised datasets",
            "option_c": "It cannot handle input dimensions that exceed two hundred variables",
            "option_d": "Its computational complexity increases exponentially with sample count",
            "correct_option": "A",
            "explanation": "Linear PCA projects data onto straight hyperplanes, conflating distant points along the curved manifold.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "What is the primary role of the low-dimensional bottleneck layer in an undercomplete autoencoder?",
            "option_a": "Forcing the network to learn compressed latent representations",
            "option_b": "Eliminating the need for backpropagation during model training",
            "option_c": "Converting continuous real features into discrete binary tokens",
            "option_d": "Preventing the decoder from calculating reconstruction gradients",
            "correct_option": "A",
            "explanation": "The bottleneck prevents trivial identity memorization, compelling the encoder to isolate the most salient generative features.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "If an autoencoder has a latent layer wider than its input dimension (overcomplete), what prevents it from learning a trivial identity mapping?",
            "option_a": "Introducing sparsity penalties or denoising corruptions on inputs",
            "option_b": "Removing all non-linear activation functions from the hidden layers",
            "option_c": "Decreasing the total number of training epochs to under five iterations",
            "option_d": "Using softmax activation on both the encoder and decoder outputs",
            "correct_option": "A",
            "explanation": "Overcomplete autoencoders require regularizers like L1 sparsity penalties or denoising noise to prevent simple copy operations.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c3",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "During training of a Variational Autoencoder (VAE), which formulation allows gradient computation through the stochastic latent sampling operation?",
            "option_a": "Reparameterization expressing z as mu plus sigma times epsilon",
            "option_b": "Monte Carlo dropout applied to decoder weight matrices",
            "option_c": "Direct argmax discretization applied over continuous logits",
            "option_d": "Batch normalization applied directly across latent dimensions",
            "correct_option": "A",
            "explanation": "The reparameterization trick formulates z = mu + sigma * epsilon, allowing gradients to flow back through mu and sigma.",
            "reasoning_probe": {
                "prompt": "Why does moving random sampling to an external epsilon tensor resolve the non-differentiability bottleneck?",
                "options": {
                    "A": "The random node has no trainable parameters, allowing deterministic gradients to pass to mu and sigma.",
                    "B": "Epsilon converts negative gradients into positive values, accelerating Adam convergence.",
                    "C": "The epsilon tensor forces all latent distributions to collapse into a single discrete scalar.",
                    "D": "Sampling outside the computation graph eliminates the need for calculating reconstruction loss."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What is the function of the Kullback-Leibler (KL) divergence term in the VAE loss function?",
            "option_a": "Regularizing the latent distribution to match a standard normal prior",
            "option_b": "Measuring pixel-wise mean squared error between input and output",
            "option_c": "Maximizing the mutual information between input pixels and labels",
            "option_d": "Penalizing large weight magnitudes to prevent overfitting in layers",
            "correct_option": "A",
            "explanation": "The KL divergence regularizes the encoder's output distribution toward a standard Gaussian N(0, I), preventing gaps in the latent space.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "basic",
            "difficulty": "easy",
            "question_text": "In self-supervised contrastive learning frameworks like SimCLR, how are positive sample pairs constructed?",
            "option_a": "Applying distinct stochastic data augmentations to the same sample",
            "option_b": "Pairing samples that share identical ground truth class labels",
            "option_c": "Selecting the two most distant data points in the training batch",
            "option_d": "Inverting the color channels of images belonging to different classes",
            "correct_option": "A",
            "explanation": "Positive pairs are generated by applying two different random transformations (crops, color jitters) to the same source image.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "What failure mode occurs in contrastive learning if a model maps all inputs to a constant representation vector, and how is it prevented?",
            "option_a": "Representation collapse, prevented by pushing negative pairs apart in InfoNCE",
            "option_b": "Vanishing gradients, prevented by adding residual skip connections",
            "option_c": "Posterior collapse, prevented by setting KL divergence weights to zero",
            "option_d": "Catastrophic forgetting, prevented by freezing all convolutional weights",
            "correct_option": "A",
            "explanation": "Representation collapse is avoided by contrasting against negative pairs in the denominator of the InfoNCE loss.",
            "reasoning_probe": {
                "prompt": "Why does the negative pair contrast in InfoNCE prevent representation collapse?",
                "options": {
                    "A": "It imposes an information-theoretic repulsion force that disperses embeddings uniformly on the hypersphere.",
                    "B": "It forces the network to memorize all raw pixel values without dimensionality reduction.",
                    "C": "It removes all non-linear activation layers, ensuring strictly convex optimization.",
                    "D": "It replaces unsupervised gradient steps with manual cross-entropy supervision."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c1",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "How does t-SNE differ from PCA in its preservation of high-dimensional geometric relationships?",
            "option_a": "t-SNE preserves local neighborhood probabilities rather than global variance",
            "option_b": "t-SNE optimizes linear projections that preserve global Euclidean distances",
            "option_c": "t-SNE can only project data into one-dimensional scalar coordinates",
            "option_d": "t-SNE guarantees that new out-of-sample points can be projected instantaneously",
            "correct_option": "A",
            "explanation": "t-SNE converts Euclidean distances into conditional probabilities and focuses on preserving local neighborhood structures.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c2",
            "question_type": "application",
            "difficulty": "hard",
            "question_text": "A computer vision engineer notices a denoising autoencoder performs exceptionally well on downstream classification. Why does denoising improve representations?",
            "option_a": "It forces the network to learn the data manifold's score vector field",
            "option_b": "It doubles the effective spatial resolution of the input images",
            "option_c": "It eliminates the need for calculating any loss gradients during training",
            "option_d": "It replaces all continuous weights with discrete ternary quantized values",
            "correct_option": "A",
            "explanation": "Denoising autoencoders learn to project corrupted points back onto the data manifold, effectively learning the score vector field.",
            "reasoning_probe": {
                "prompt": "What geometric property makes manifold projection effective against input noise?",
                "options": {
                    "A": "True data points concentrate along lower-dimensional manifolds, while noise pushes samples orthogonal to it.",
                    "B": "Noise increases the intrinsic rank of the covariance matrix to infinity.",
                    "C": "Corrupted images contain zero high-frequency spatial gradients.",
                    "D": "Convolutional layers can only process images with zero Gaussian variance."
                },
                "correct_probe": "A"
            }
        },
        {
            "concept_suffix": "c3",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "What undesirable artifact occurs in a VAE's latent space if the KL divergence regularization weight is set to zero during training?",
            "option_a": "The latent space develops isolated islands, preventing smooth generative interpolation",
            "option_b": "The reconstruction quality deteriorates into uniform random noise pixels",
            "option_c": "The encoder parameters grow infinitely large causing numerical overflow",
            "option_d": "The decoder becomes incapable of producing any colored pixel outputs",
            "correct_option": "A",
            "explanation": "Without KL regularization, the encoder places distinct classes in isolated clusters with empty space in between, destroying generative interpolation.",
            "reasoning_probe": None
        },
        {
            "concept_suffix": "c4",
            "question_type": "conceptual",
            "difficulty": "medium",
            "question_text": "In contrastive self-supervised learning, what role does the temperature hyperparameter tau play in the InfoNCE loss?",
            "option_a": "It regulates the penalty scale on hard negative examples on the hypersphere",
            "option_b": "It controls the physical temperature of GPU hardware during matrix multiplication",
            "option_c": "It sets the percentage of neurons that undergo dropout in hidden layers",
            "option_d": "It determines the learning rate decay schedule across training epochs",
            "correct_option": "A",
            "explanation": "A smaller temperature parameter tau amplifies the gradients of hard negative samples, promoting uniform embedding dispersion.",
            "reasoning_probe": None
        }
    ]
}

CURATED_OFFLINE_DOMAINS = {
    "computer network": NETWORKS_CURRICULUM,
    "computer network system": NETWORKS_CURRICULUM,
    "computer network systems": NETWORKS_CURRICULUM,
    "computer networks": NETWORKS_CURRICULUM,
    "network": NETWORKS_CURRICULUM,
    "networking": NETWORKS_CURRICULUM,
    "tcp": NETWORKS_CURRICULUM,
    "tcp/ip": NETWORKS_CURRICULUM,
    "osi": NETWORKS_CURRICULUM,
    "pesticide": PESTICIDE_CURRICULUM,
    "pesticides": PESTICIDE_CURRICULUM,
    "chemical pesticide": PESTICIDE_CURRICULUM,
    "chemical pesticides": PESTICIDE_CURRICULUM,
    "type of pesticide": PESTICIDE_CURRICULUM,
    "type of pesticides": PESTICIDE_CURRICULUM,
    "types of pesticides": PESTICIDE_CURRICULUM,
    "insecticide": PESTICIDE_CURRICULUM,
    "herbicide": PESTICIDE_CURRICULUM,
    "fungicide": PESTICIDE_CURRICULUM,
    "pest": BIOLOGICAL_PEST_CURRICULUM,
    "pests": BIOLOGICAL_PEST_CURRICULUM,
    "type of pest": BIOLOGICAL_PEST_CURRICULUM,
    "types of pests": BIOLOGICAL_PEST_CURRICULUM,
    "agricultural pest": BIOLOGICAL_PEST_CURRICULUM,
    "agricultural pests": BIOLOGICAL_PEST_CURRICULUM,
    "biological pest": BIOLOGICAL_PEST_CURRICULUM,
    "biological pests": BIOLOGICAL_PEST_CURRICULUM,
    "crop pest": BIOLOGICAL_PEST_CURRICULUM,
    "crop pests": BIOLOGICAL_PEST_CURRICULUM,
    "insect pest": BIOLOGICAL_PEST_CURRICULUM,
    "insect pests": BIOLOGICAL_PEST_CURRICULUM,
    "storage pest": BIOLOGICAL_PEST_CURRICULUM,
    "storage pests": BIOLOGICAL_PEST_CURRICULUM,
    "unsupervised": UNSUPERVISED_DL_CURRICULUM,
    "representation": UNSUPERVISED_DL_CURRICULUM,
    "autoencoder": UNSUPERVISED_DL_CURRICULUM,
    "representation unsupervised": UNSUPERVISED_DL_CURRICULUM,
    
    # Horticulture and Plant Sciences
    "horticulture": HORTICULTURE_CURRICULUM,
    "horticultural": HORTICULTURE_CURRICULUM,
    "horticulturee": HORTICULTURE_CURRICULUM,
    "horticulture science": HORTICULTURE_CURRICULUM,
    "pomology": HORTICULTURE_CURRICULUM,
    "olericulture": HORTICULTURE_CURRICULUM,
    "floriculture": HORTICULTURE_CURRICULUM,
    "plant propagation": HORTICULTURE_CURRICULUM,
    "gardening": HORTICULTURE_CURRICULUM,

    # Full Stack Web Development & Systems Architecture
    "full stack": FULL_STACK_CURRICULUM,
    "full stack development": FULL_STACK_CURRICULUM,
    "full stack web development": FULL_STACK_CURRICULUM,
    "fsd": FULL_STACK_CURRICULUM,
    "24csi013": FULL_STACK_CURRICULUM,
    "24csi013 fsd": FULL_STACK_CURRICULUM,
    "web development": FULL_STACK_CURRICULUM,
    "mern": FULL_STACK_CURRICULUM
}


# =============================================================================
# 3. CORE SYLLABUS GENERATOR ENGINE
# =============================================================================

class SyllabusGeneratorEngine:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def generate_custom_domain(
        self,
        topic_title: str,
        syllabus_text: str = "",
        user_id: Optional[int] = None,
        num_questions: int = 12,
        api_key: Optional[str] = None,
        api_provider: Optional[str] = "gemini",
        model_name: Optional[str] = None,
        require_live_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Generates full domain assessment:
        1. Checks if an AI API key is supplied (or in env) -> calls Gemini or OpenAI for ANY custom topic.
        2. If no key, checks curated offline domain taxonomy (e.g. French Revolution).
        3. If no match, uses dynamic domain-aware synthesis.
        Persists into SQLite and registers concept learning guides.
        """
        # Clean and normalize topic title
        topic_title = normalize_topic_title(topic_title)
        if not topic_title:
            raise ValueError("Topic title cannot be empty.")

        clean_slug = slugify(topic_title)
        random_suffix = uuid.uuid4().hex[:6]
        domain_id = f"custom_{clean_slug}_{random_suffix}"

        # 1. Check for AI API key (from parameter or environment)
        explicit_key_provided = bool(api_key and api_key.strip())
        resolved_key = (api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()
        provider = (api_provider or "gemini").lower()
        
        parsed_llm_data = None
        llm_used = False
        model_used = None
        provider_error = None

        if resolved_key:
            valid_format = False
            if provider == "openai" and (resolved_key.startswith("sk-") or "openai" in resolved_key.lower()):
                valid_format = True
            elif provider == "gemini" and resolved_key.startswith("AIzaSy"):
                valid_format = True
            
            if not valid_format:
                warning_msg = f"Key for {provider} does not match official format prefix ('AIzaSy...' for Gemini, 'sk-...' for OpenAI)."
                print(f"[AI Key Warning] {warning_msg}")
                if require_live_llm or explicit_key_provided:
                    raise ValueError(warning_msg)
            else:
                print(f"[AI Generator] Calling {provider} API for topic '{topic_title}'...")
                try:
                    if provider == "openai":
                        m = model_name or "gpt-4o-mini"
                        parsed_llm_data = generate_via_openai_api(topic_title, syllabus_text, resolved_key, m)
                    else:
                        m = model_name or "gemini-1.5-flash"
                        parsed_llm_data = generate_via_gemini_api(topic_title, syllabus_text, resolved_key, m)
                    if parsed_llm_data:
                        llm_used = True
                        model_used = parsed_llm_data.get("_model_used", m)
                except Exception as e:
                    provider_error = str(e)
                    print(f"[AI Generator Failure] {provider_error}")
                    if require_live_llm or explicit_key_provided:
                        raise RuntimeError(f"Live LLM generation failed ({provider}): {provider_error}")

        # 2. Check curated domain taxonomy if LLM not used or failed
        if not parsed_llm_data:
            clean_lower = re.sub(r'[^a-z0-9\s]', '', topic_title.lower()).strip()
            for cur_key, cur_data in CURATED_OFFLINE_DOMAINS.items():
                clean_key = re.sub(r'[^a-z0-9\s]', '', cur_key.lower()).strip()
                if clean_key in clean_lower or clean_lower in clean_key:
                    print(f"[Taxonomy Match] Using curated curriculum for '{cur_key}'.")
                    parsed_llm_data = cur_data
                    break
            
            # Fuzzy match for Horticulture or FSD if specific key was missed
            if not parsed_llm_data:
                if any(k in clean_lower for k in ["horticult", "pomolog", "olericult", "floricult"]):
                    print("[Taxonomy Match] Fuzzy match for Horticulture Science.")
                    parsed_llm_data = HORTICULTURE_CURRICULUM
                elif any(k in clean_lower for k in ["full stack", "fullstack", "fsd", "web dev", "24csi013", "mern"]):
                    print("[Taxonomy Match] Fuzzy match for Full Stack Web Development.")
                    parsed_llm_data = FULL_STACK_CURRICULUM

        # 3. Assemble domain from parsed data or generalized domain-aware builder
        if parsed_llm_data and "concepts" in parsed_llm_data and "questions" in parsed_llm_data:
            res = self._build_from_structured_spec(
                domain_id=domain_id,
                topic_title=topic_title,
                spec=parsed_llm_data
            )
            res["generation_source"] = "live_llm" if llm_used else "curated_preloaded_course_catalog"
            res["llm_used"] = llm_used
            res["llm_provider"] = provider if llm_used else None
            res["model_name"] = model_used
            res["generation_notice"] = f"Generated live via {provider.upper()} ({model_used})." if llm_used else "Preloaded curated course catalog assessment."
            return res
        else:
            res = self._build_domain_aware_fallback(
                domain_id=domain_id,
                topic_title=topic_title,
                syllabus_text=syllabus_text,
                num_questions=num_questions
            )
            res["generation_source"] = "offline_knowledge_synthesis"
            res["llm_used"] = False
            res["llm_provider"] = None
            res["model_name"] = None
            if provider_error:
                res["llm_error"] = provider_error
                res["generation_notice"] = f"API call failed ({provider_error}); generated via authentic offline domain knowledge synthesis."
            else:
                res["generation_notice"] = "Generated via authentic offline domain knowledge synthesis because no live LLM API key was provided or configured."
            return res

    def _build_from_structured_spec(self, domain_id: str, topic_title: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Converts structured spec (from LLM or curated taxonomy) into SQLite records."""
        icon = spec.get("icon") or pick_icon_and_category(topic_title)[0]
        category = spec.get("category") or pick_icon_and_category(topic_title)[1]
        description = spec.get("description", f"Diagnostic assessment covering {topic_title}.")

        # 1. Process Concepts
        concepts = []
        concept_guides = []
        suffix_to_full_id = {}

        for i, c in enumerate(spec["concepts"]):
            cid = f"{domain_id}_{c.get('id_suffix', f'c{i+1}')}"
            suffix_to_full_id[c.get('id_suffix', f'c{i+1}')] = cid
            
            raw_prereqs = c.get("prerequisites", [])
            resolved_prereqs = [suffix_to_full_id.get(p, p) for p in raw_prereqs if p in suffix_to_full_id]

            concepts.append({
                "id": cid,
                "domain_id": domain_id,
                "name": c["name"],
                "slug": slugify(c["name"]),
                "category": category,
                "description": c["description"],
                "prerequisites": resolved_prereqs,
                "order_index": i + 1
            })

            concept_guides.append({
                "concept_id": cid,
                "domain_id": domain_id,
                "name": c["name"],
                "core_idea": c.get("core_idea", f"Core understanding of {c['name']}."),
                "example": c.get("example", f"Real-world context of {c['name']}."),
                "common_mistake": c.get("common_mistake", "Common conceptual traps to avoid."),
                "key_takeaway": c.get("key_takeaway", "Key summary rule.")
            })

        # 2. Process Misconceptions
        misconceptions = []
        for i, m in enumerate(spec.get("misconceptions", [])):
            mid = f"MISC_{domain_id.upper()}_{i+1}"
            target_cid = suffix_to_full_id.get(m.get("concept_suffix"), concepts[min(i, len(concepts)-1)]["id"])
            misconceptions.append({
                "id": mid,
                "domain_id": domain_id,
                "code": m.get("code", f"M-CUST-{i+1:02d}"),
                "concept_id": target_cid,
                "name": m.get("name", "Misconception"),
                "description": m.get("description", "Student misunderstanding description."),
                "remediation": m.get("remediation", "Remediation guidance.")
            })

        # 3. Process Questions
        import random
        questions = []
        for i, q in enumerate(spec.get("questions", [])):
            qid = f"{domain_id}_q{i+1}"
            target_cid = suffix_to_full_id.get(q.get("concept_suffix"), concepts[i % len(concepts)]["id"])
            misc_id = misconceptions[i % len(misconceptions)]["id"] if misconceptions else None
            
            # Application questions get reasoning probes
            rp_data = q.get("reasoning_probe")

            # Dynamically shuffle options so correct answers are evenly spread across A, B, C, D
            orig_correct = q.get("correct_option", "A").upper().strip()
            orig_options = {
                "A": q["option_a"],
                "B": q["option_b"],
                "C": q["option_c"],
                "D": q["option_d"]
            }
            correct_text = orig_options.get(orig_correct, q["option_a"])
            
            # Permute options
            shuffled_texts = list(orig_options.values())
            random.shuffle(shuffled_texts)
            new_opt_a = shuffled_texts[0]
            new_opt_b = shuffled_texts[1]
            new_opt_c = shuffled_texts[2]
            new_opt_d = shuffled_texts[3]
            
            new_correct = "A"
            for ltr, txt in [("A", new_opt_a), ("B", new_opt_b), ("C", new_opt_c), ("D", new_opt_d)]:
                if txt == correct_text:
                    new_correct = ltr
                    break

            # If reasoning probe is present, also shuffle its options
            if rp_data and "options" in rp_data and "correct_probe" in rp_data:
                orig_probe_opts = rp_data["options"]
                orig_probe_correct = rp_data.get("correct_probe", "A").upper().strip()
                correct_probe_text = orig_probe_opts.get(orig_probe_correct, orig_probe_opts.get("A", ""))

                probe_texts = list(orig_probe_opts.values())
                random.shuffle(probe_texts)
                new_probe_opts = {
                    "A": probe_texts[0] if len(probe_texts) > 0 else "",
                    "B": probe_texts[1] if len(probe_texts) > 1 else "",
                    "C": probe_texts[2] if len(probe_texts) > 2 else "",
                    "D": probe_texts[3] if len(probe_texts) > 3 else ""
                }
                new_probe_correct = "A"
                for ltr, txt in new_probe_opts.items():
                    if txt == correct_probe_text:
                        new_probe_correct = ltr
                        break
                rp_data["options"] = new_probe_opts
                rp_data["correct_probe"] = new_probe_correct

            questions.append({
                "id": qid,
                "domain_id": domain_id,
                "concept_id": target_cid,
                "question_type": q.get("question_type", "basic"),
                "difficulty": q.get("difficulty", "medium"),
                "question_text": q["question_text"],
                "option_a": new_opt_a,
                "option_b": new_opt_b,
                "option_c": new_opt_c,
                "option_d": new_opt_d,
                "correct_option": new_correct,
                "explanation": q.get("explanation", "Correct answer explanation."),
                "misconception_id": misc_id,
                "prerequisite_id": None,
                "reasoning_probe": rp_data
            })

        # Validate before persisting
        from backend.app.quiz_validator import validate_curriculum_package
        is_valid, validation_errors = validate_curriculum_package(concepts, misconceptions, questions, category)
        if not is_valid:
            print(f"[Validation Warning] Structured spec had issues: {validation_errors[:3]}")

        # Persist everything
        self.persist_to_db(
            domain_id=domain_id,
            domain_name=topic_title,
            icon=icon,
            category=category,
            description=description,
            concepts=concepts,
            misconceptions=misconceptions,
            questions=questions,
            concept_guides=concept_guides
        )

        for g in concept_guides:
            register_concept_guide(g)

        return {
            "status": "success",
            "domain_id": domain_id,
            "name": topic_title,
            "icon": icon,
            "category": category,
            "description": description,
            "concepts_count": len(concepts),
            "questions_count": len(questions),
            "concepts": concepts,
            "sample_questions": [q["question_text"] for q in questions[:3]]
        }

    def _build_domain_aware_fallback(
        self,
        domain_id: str,
        topic_title: str,
        syllabus_text: str = "",
        num_questions: int = 12
    ) -> Dict[str, Any]:
        """Dynamic domain-aware generator when neither LLM API nor curated topic matched.
        Uses universal cognitive multi-disciplinary question engine for authentic, non-repeating curricula.
        """
        from backend.app.topic_researcher import fetch_wikipedia_knowledge, synthesize_authentic_curriculum
        
        # 1. Fetch live encyclopedic knowledge for the topic
        print(f"[Topic Researcher] Researching factual knowledge for '{topic_title}'...")
        articles = fetch_wikipedia_knowledge(topic_title)
        
        # 2. Synthesize authentic concepts, misconceptions, questions, and guides
        concepts, misconceptions, questions, concept_guides, icon, category = synthesize_authentic_curriculum(
            domain_id=domain_id,
            topic_title=topic_title,
            articles=articles
        )

        self.persist_to_db(
            domain_id=domain_id,
            domain_name=topic_title,
            icon=icon,
            category=category,
            description=f"Diagnostic assessment covering {topic_title}.",
            concepts=concepts,
            misconceptions=misconceptions,
            questions=questions,
            concept_guides=concept_guides
        )

        for g in concept_guides:
            register_concept_guide(g)

        return {
            "status": "success",
            "domain_id": domain_id,
            "name": topic_title,
            "icon": icon,
            "category": category,
            "description": f"Diagnostic assessment covering {topic_title}.",
            "concepts_count": len(concepts),
            "questions_count": len(questions),
            "concepts": concepts,
            "sample_questions": [q["question_text"] for q in questions[:3]]
        }

    def persist_to_db(
        self,
        domain_id: str,
        domain_name: str,
        icon: str,
        category: str,
        description: str,
        concepts: List[Dict[str, Any]],
        misconceptions: List[Dict[str, Any]],
        questions: List[Dict[str, Any]],
        concept_guides: List[Dict[str, Any]]
    ):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 1. Insert domain
        cursor.execute("""
            INSERT OR REPLACE INTO domains (id, name, icon, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (domain_id, domain_name, icon, category, description))

        # 2. Insert concepts
        for c in concepts:
            cursor.execute("""
                INSERT OR REPLACE INTO concepts (id, domain_id, name, slug, category, description, prerequisites, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], c["domain_id"], c["name"], c["slug"], c["category"],
                c["description"], json.dumps(c["prerequisites"]), c["order_index"]
            ))

        # 3. Insert misconceptions
        for m in misconceptions:
            cursor.execute("""
                INSERT OR REPLACE INTO misconceptions (id, domain_id, code, concept_id, name, description, remediation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                m["id"], m["domain_id"], m["code"], m["concept_id"], m["name"],
                m["description"], m["remediation"]
            ))

        # 4. Insert questions
        for q in questions:
            rp_json = json.dumps(q.get("reasoning_probe")) if q.get("reasoning_probe") else None
            cursor.execute("""
                INSERT OR REPLACE INTO questions (
                    id, domain_id, concept_id, question_type, difficulty, question_text,
                    option_a, option_b, option_c, option_d, correct_option,
                    explanation, misconception_id, prerequisite_id, reasoning_probe
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"], q["domain_id"], q["concept_id"], q["question_type"], q["difficulty"],
                q["question_text"], q["option_a"], q["option_b"], q["option_c"], q["option_d"],
                q["correct_option"], q["explanation"], q.get("misconception_id"), q.get("prerequisite_id"),
                rp_json
            ))

        # 5. Insert custom concept guides
        for g in concept_guides:
            cursor.execute("""
                INSERT OR REPLACE INTO custom_concept_guides (concept_id, domain_id, name, core_idea, example, common_mistake, key_takeaway)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                g["concept_id"], g["domain_id"], g["name"], g["core_idea"],
                g["example"], g["common_mistake"], g["key_takeaway"]
            ))

        conn.commit()
        conn.close()
        print(f"Successfully saved custom domain '{domain_name}' ({domain_id}) with {len(questions)} questions.")

# Global engine instance
syllabus_engine = SyllabusGeneratorEngine()
