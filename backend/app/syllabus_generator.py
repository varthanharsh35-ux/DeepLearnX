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
    from app.concept_guide import register_concept_guide

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "deeplearnx.db"

# Domain icon selection heuristics based on subject keywords
THEME_ICONS = [
    (["french revolution", "history", "revolution", "empire", "war", "civilization", "ancient", "medieval", "bastille", "monarchy"], "🏛️", "History & Humanities"),
    (["pesticide", "pest", "crop", "agriculture", "soil", "farming", "insecticide", "herbicide", "fungicide"], "🌾", "Agricultural & Environmental Sciences"),
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
        if any(kw in combined for kw in keywords):
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
    default_candidates = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash"]
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
    
    with httpx.Client(timeout=70.0) as client:
        for m in candidate_models:
            if not m:
                continue
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            for attempt in range(2):
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
                                return parsed
                            else:
                                print(f"[Gemini API Attempt] Model {m} returned JSON missing concepts/questions")
                    elif response.status_code in (429, 503):
                        print(f"[Gemini API Attempt] Model {m} returned HTTP {response.status_code} (attempt {attempt+1}/2). Waiting 2.5s before retry...")
                        time.sleep(2.5)
                        continue
                    else:
                        print(f"[Gemini API Attempt] Model {m} returned HTTP {response.status_code}")
                        break
                except Exception as e:
                    print(f"[Gemini API Exception] Model {m}: {e}")
                    break
                
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
                print(f"[OpenAI API Error] Status {response.status_code}: {response.text}")
                return None
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return clean_and_parse_llm_json(content)
        except Exception as e:
            print(f"[OpenAI Exception]: {e}")
            return None

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
    "french revolution": {
        "icon": "🏛️",
        "category": "History & Humanities",
        "description": "Comprehensive diagnostic evaluation of the French Revolution, feudal class inequities, constitutional crises, and political radicalization.",
        "concepts": [
            {
                "id_suffix": "c1",
                "name": "The Three Estates & Feudal Inequities",
                "description": "The rigid social hierarchy of the Ancien Régime and the heavy taxation borne by the Third Estate.",
                "prerequisites": [],
                "core_idea": "French society was divided into three unequal estates: the Clergy (First) and Nobility (Second) owned most land and paid virtually no taxes, while the Commoners (Third Estate, 98% of people) paid all taxes.",
                "example": "If 100 people eat a meal, the two wealthiest individuals eat the finest food for free, while forcing the remaining 98 people to pay the entire bill.",
                "common_mistake": "Thinking the Third Estate consisted only of poor peasants; it also included wealthy, educated bourgeoisie like doctors, merchants, and lawyers.",
                "key_takeaway": "The Ancien Régime collapsed because the overwhelming majority produced all wealth but held zero political rights."
            },
            {
                "id_suffix": "c2",
                "name": "Fiscal Collapse & Estates-General (1789)",
                "description": "Royal debt from the American War of Independence leading to King Louis XVI convening the Estates-General and the Tennis Court Oath.",
                "prerequisites": ["c1"],
                "core_idea": "France was bankrupt due to royal wars. When the King convened the Estates-General, voting by order gave the two privileged estates a 2-to-1 veto over the Third Estate, triggering the Tennis Court Oath.",
                "example": "In a school council, 2 teachers and 98 students vote, but teachers get 2 collective votes and all 98 students get only 1 collective vote.",
                "common_mistake": "Believing the King summoned the Estates-General out of democratic goodwill; he did so solely because French parlements refused new loans.",
                "key_takeaway": "Voting by order rather than by head prompted the Third Estate to declare itself the sovereign National Assembly."
            },
            {
                "id_suffix": "c3",
                "name": "Storming of the Bastille & Rights of Man",
                "description": "The popular Parisian insurrection on July 14, 1789, abolition of feudalism, and the Declaration of the Rights of Man and of the Citizen.",
                "prerequisites": ["c2"],
                "core_idea": "Fearing royal troops would crush the National Assembly, Parisian citizens stormed the Bastille fortress on July 14, 1789 to seize gunpowder and arms, symbolizing the fall of absolute despotism.",
                "example": "Citizens dismantling a famous prison brick by brick to signal that the ruler's absolute power to imprison critics is ended forever.",
                "common_mistake": "Thinking the Bastille was attacked primarily to release hundreds of prisoners; it held only 7 inmates and was stormed for stored gunpowder.",
                "key_takeaway": "The Bastille's fall proved popular armed resistance could defeat absolute monarchy, leading to the Declaration of the Rights of Man."
            },
            {
                "id_suffix": "c4",
                "name": "The Radical Republic & Reign of Terror",
                "description": "Foreign counter-revolutionary war, the rise of the Jacobins, Committee of Public Safety, and the execution of King Louis XVI.",
                "prerequisites": ["c3"],
                "core_idea": "Faced with foreign invasion and domestic counter-rebellion, Maximilien Robespierre and the Jacobins centralized power in the Committee of Public Safety, using the guillotine to eliminate perceived traitors.",
                "example": "A revolution becoming so paranoid of betrayal that anyone criticizing government policies is treated as an enemy of the state.",
                "common_mistake": "Assuming the Reign of Terror executed only aristocrats; the vast majority of victims were ordinary peasants and working-class citizens accused of hoarding or treason.",
                "key_takeaway": "Radical revolutionary paranoia culminated in the Terror, which ended when Robespierre himself was overthrown in the Thermidorian Reaction."
            }
        ],
        "misconceptions": [
            {
                "concept_suffix": "c1",
                "code": "M-HIST-01",
                "name": "Universal Aristocratic Taxation Myth",
                "description": "Student mistakenly believes that French nobles paid the largest portion of royal taxes prior to 1789.",
                "remediation": "Review the tax laws of the Ancien Régime: nobles and high clergy enjoyed legal exemptions from the direct land tax (taille) and church tithe."
            },
            {
                "concept_suffix": "c2",
                "code": "M-HIST-02",
                "name": "Estates-General Democratic Voting Fallacy",
                "description": "Student assumes each delegate had an individual vote in the Estates-General.",
                "remediation": "Voting occurred 'by order' (one vote per estate), guaranteeing the First and Second Estates could outvote the Third Estate 2-to-1."
            },
            {
                "concept_suffix": "c3",
                "code": "M-HIST-03",
                "name": "Bastille Mass Prisoner Liberation Myth",
                "description": "Student believes the Bastille fortress was assaulted primarily to liberate hundreds of political dissidents.",
                "remediation": "The primary objective was seizing the 250 barrels of gunpowder stored inside to defend Paris against approaching royal mercenaries."
            },
            {
                "concept_suffix": "c4",
                "code": "M-HIST-04",
                "name": "Noble-Exclusive Guillotine Target Misconception",
                "description": "Student assumes the Reign of Terror executed only wealthy aristocrats and royals.",
                "remediation": "Historical trial records confirm over 80% of victims condemned by revolutionary tribunals were Third Estate workers and peasants."
            }
        ],
        "questions": [
            {
                "concept_suffix": "c1",
                "question_type": "basic",
                "difficulty": "easy",
                "question_text": "Which social order comprised approximately 98% of the French population in 1789?",
                "option_a": "The Third Estate commoners",
                "option_b": "The First Estate clergy",
                "option_c": "The Second Estate nobles",
                "option_d": "The Royal Family court",
                "correct_option": "A",
                "explanation": "The Third Estate encompassed peasants, city workers, artisans, and the educated middle class (bourgeoisie), totaling 98% of France.",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c1",
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": "Why did the French educated bourgeoisie feel deeply alienated by the Ancien Régime despite their growing wealth?",
                "option_a": "High political offices and senior military ranks were reserved strictly for the nobility",
                "option_b": "The monarchy prohibited bourgeois merchants from owning rural agricultural land holdings",
                "option_c": "The Catholic Church declared commercial trade profits to be strictly sinful and illegal",
                "option_d": "The Third Estate was legally barred from reading philosophical Enlightenment pamphlets",
                "correct_option": "A",
                "explanation": "Despite their education and economic success, the bourgeoisie were excluded from high state offices and social prestige reserved for birth-right nobles.",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c2",
                "question_type": "basic",
                "difficulty": "easy",
                "question_text": "What dramatic action did the Third Estate delegates take on an indoor tennis court in June 1789?",
                "option_a": "Vowed not to separate until they had drafted a written constitution for France",
                "option_b": "Voted to execute King Louis XVI and establish an immediate socialist commune",
                "option_c": "Signed a military mutual defense treaty with Great Britain and Prussia",
                "option_d": "Surrendered their political representation completely to the Catholic Church",
                "correct_option": "A",
                "explanation": "In the Tennis Court Oath (June 20, 1789), deputies resolved never to separate until France had a written constitution.",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c2",
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": "Why did the Third Estate vehemently reject the traditional 'voting by order' procedure at the Estates-General?",
                "option_a": "It ensured the Clergy and Nobility could perpetually combine to defeat reform by 2-to-1",
                "option_b": "It required all Third Estate deputies to pay double voting taxes before casting ballots",
                "option_c": "It granted the monarch an unconditional veto over all proposed taxation compromises",
                "option_d": "It prevented delegates from speaking French during formal parliamentary sessions",
                "correct_option": "A",
                "explanation": "Under voting by order, each estate had one vote. The First and Second Estates voted together, rendering the Third Estate's larger population powerless.",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c3",
                "question_type": "basic",
                "difficulty": "easy",
                "question_text": "On what historic date did Parisian citizens storm the medieval Bastille fortress?",
                "option_a": "July 14, 1789",
                "option_b": "August 4, 1789",
                "option_c": "January 21, 1793",
                "option_d": "September 2, 1792",
                "correct_option": "A",
                "explanation": "July 14, 1789 marks the Storming of the Bastille, celebrated annually as France's National Day (Bastille Day).",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c3",
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": "What fundamental principle is enshrined in Article 1 of the Declaration of the Rights of Man and of the Citizen?",
                "option_a": "Men are born and remain free and equal in their civil rights",
                "option_b": "Monarchical authority is ordained directly by divine heavenly power",
                "option_c": "Private property is abolished and held collectively by the state",
                "option_d": "Nobles retain ancestral judicial privileges over rural peasant lands",
                "correct_option": "A",
                "explanation": "Article 1 asserts: 'Men are born and remain free and equal in rights. Social distinctions may be based only on common utility.'",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c3",
                "question_type": "application",
                "difficulty": "hard",
                "question_text": "In July 1789, severe bread inflation collided with rumors of royal military deployments around Paris. Which tactical objective drove the militia to storm the Bastille?",
                "option_a": "To seize the stored barrels of gunpowder needed to resist royal troops",
                "option_b": "To liberate hundreds of prominent Enlightenment political philosophers",
                "option_c": "To capture King Louis XVI and hold the royal treasury under hostage",
                "option_d": "To demolish the building because it blocked the municipal grain carts",
                "correct_option": "A",
                "explanation": "The crowd seized 30,000 muskets earlier at the Invalides, but had no gunpowder. The Bastille held 250 barrels of gunpowder, making it the primary objective.",
                "reasoning_probe": {
                    "prompt": "Why was capturing gunpowder at the Bastille more urgent to the Parisian crowd than looting royal food stores?",
                    "options": {
                        "A": "Without munitions, the armed citizens could not defend the city against encircling royal regiments.",
                        "B": "The price of gunpowder was higher than gold on the international European black market.",
                        "C": "King Louis XVI had offered an unconditional royal pardon to anyone possessing gunpowder.",
                        "D": "The National Assembly had banned civilian consumption of wheat flour during the crisis."
                    },
                    "correct_probe": "A"
                }
            },
            {
                "concept_suffix": "c4",
                "question_type": "basic",
                "difficulty": "easy",
                "question_text": "Which Jacobin leader headed the Committee of Public Safety during the Reign of Terror?",
                "option_a": "Maximilien Robespierre",
                "option_b": "Napoleon Bonaparte",
                "option_c": "Marquis de Lafayette",
                "option_d": "Georges Danton only",
                "correct_option": "A",
                "explanation": "Robespierre became the dominant political figure of the Committee of Public Safety during the Reign of Terror (1793-1794).",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c4",
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": "Why did the Revolutionary government institute the Reign of Terror in 1793?",
                "option_a": "To crush internal counter-rebellions and mobilize total war against foreign coalition invaders",
                "option_b": "To restore absolute monarchy under an English prince favored by the Girondin faction",
                "option_c": "To convince the Pope to formally bless the newly drafted Civil Constitution of the Clergy",
                "option_d": "To force peasant farmers into collective industrial factories in suburban Lyon districts",
                "correct_option": "A",
                "explanation": "Facing civil war in the Vendée, federalist revolts, and foreign invasion by Austria and Prussia, the Terror was an emergency wartime dictatorship.",
                "reasoning_probe": None
            },
            {
                "concept_suffix": "c4",
                "question_type": "application",
                "difficulty": "hard",
                "question_text": "In 1793, King Louis XVI was convicted of high treason and executed by guillotine. What major international escalation resulted directly from this event?",
                "option_a": "Britain, Spain, and the Netherlands joined Austria and Prussia in the First Coalition against France",
                "option_b": "All European monarchies immediately recognized the French Republic and signed mutual peace treaties",
                "option_c": "The United States declared war on Great Britain to assist the Jacobin Revolutionary government",
                "option_d": "The Ottoman Empire launched naval invasions against French Mediterranean ports in Marseille",
                "correct_option": "A",
                "explanation": "The regicide horrified European monarchies, precipitating Britain, the Dutch Republic, and Spain joining the First Coalition war against France.",
                "reasoning_probe": {
                    "prompt": "Why did European monarchies view the execution of Louis XVI as an existential security threat?",
                    "options": {
                        "A": "They feared popular revolutionary ideas of popular sovereignty would spread and inspire regicide at home.",
                        "B": "The French monarchy was the primary creditor bank financing all central European national budgets.",
                        "C": "Louis XVI held supreme religious authority over both Catholic and Protestant European churches.",
                        "D": "France had threatened to annex the entire continent of North America if coalition forces invaded."
                    },
                    "correct_probe": "A"
                }
            },
            {
                "concept_suffix": "c4",
                "question_type": "application",
                "difficulty": "hard",
                "question_text": "What political event in July 1794 (9 Thermidor) brought a dramatic end to the Reign of Terror?",
                "option_a": "The National Convention turned on Robespierre, ordering his arrest and execution",
                "option_b": "Napoleon Bonaparte invaded Paris with his army from the Italian military campaign",
                "option_c": "King Louis XVII reached adulthood and reclaimed the royal French throne in Paris",
                "option_d": "The Austrian army captured Paris and reinstated the traditional Three Estates system",
                "correct_option": "A",
                "explanation": "Fearing they would be Robespierre's next victims, members of the National Convention united against him on 9 Thermidor, executing him the next day.",
                "reasoning_probe": {
                    "prompt": "What drove deputies in the National Convention to unite against Robespierre after months of obedience?",
                    "options": {
                        "A": "Robespierre announced a new list of conspirators without naming them, making every deputy fear for their life.",
                        "B": "The price of Parisian bread dropped dramatically, removing all popular support for Jacobin clubs.",
                        "C": "The Pope offered financial rewards to any French politician who dismantled the Revolutionary Tribunal.",
                        "D": "Austria surrendered completely, eliminating all external wartime justification for government emergency powers."
                    },
                    "correct_probe": "A"
                }
            },
            {
                "concept_suffix": "c2",
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": "How did Enlightenment philosophers like Voltaire and Rousseau contribute to the outbreak of the French Revolution?",
                "option_a": "By popularizing ideas of reason, natural human equality, and challenging the divine right of kings",
                "option_b": "By designing advanced military artillery tactics adopted by Parisian street militia groups",
                "option_c": "By personally financing the purchase of overseas weapon shipments from the United States",
                "option_d": "By commanding royal administrative finance ministries under King Louis XVI during 1788",
                "correct_option": "A",
                "explanation": "Enlightenment thought provided the intellectual framework that undermined traditional feudal hierarchies and absolute divine-right monarchy.",
                "reasoning_probe": None
            }
        ]
    },
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
    "pest": PESTICIDE_CURRICULUM,
    "pests": PESTICIDE_CURRICULUM,
    "insecticide": PESTICIDE_CURRICULUM,
    "herbicide": PESTICIDE_CURRICULUM,
    "fungicide": PESTICIDE_CURRICULUM,
    "type of pesticides": PESTICIDE_CURRICULUM,
    "types of pests": PESTICIDE_CURRICULUM,
    "unsupervised": UNSUPERVISED_DL_CURRICULUM,
    "representation": UNSUPERVISED_DL_CURRICULUM,
    "autoencoder": UNSUPERVISED_DL_CURRICULUM,
    "representation unsupervised": UNSUPERVISED_DL_CURRICULUM
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
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates full domain assessment:
        1. Checks if an AI API key is supplied (or in env) -> calls Gemini or OpenAI for ANY custom topic.
        2. If no key, checks curated offline domain taxonomy (e.g. French Revolution).
        3. If no match, uses dynamic domain-aware synthesis.
        Persists into SQLite and registers concept learning guides.
        """
        topic_title = topic_title.strip()
        if not topic_title:
            raise ValueError("Topic title cannot be empty.")

        clean_slug = slugify(topic_title)
        random_suffix = uuid.uuid4().hex[:6]
        domain_id = f"custom_{clean_slug}_{random_suffix}"

        # 1. Check for AI API key (from parameter or environment)
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        provider = (api_provider or "gemini").lower()
        
        parsed_llm_data = None
        if resolved_key:
            print(f"[AI Generator] Calling {provider} API for topic '{topic_title}'...")
            try:
                if provider == "openai" or "sk-" in resolved_key:
                    m = model_name or "gpt-4o-mini"
                    parsed_llm_data = generate_via_openai_api(topic_title, syllabus_text, resolved_key, m)
                else:
                    m = model_name or os.environ.get("GEMINI_DEFAULT_MODEL") or "gemini-3.5-flash-lite"
                    parsed_llm_data = generate_via_gemini_api(topic_title, syllabus_text, resolved_key, m)
            except Exception as e:
                print(f"[AI Generator Exception] {e}. Falling back to domain taxonomy.")

        # 2. Check curated domain taxonomy if LLM not used or failed
        if not parsed_llm_data:
            lower_topic = topic_title.lower()
            for cur_key, cur_data in CURATED_OFFLINE_DOMAINS.items():
                if cur_key in lower_topic or lower_topic in cur_key:
                    print(f"[Taxonomy Match] Using curated offline curriculum for '{cur_key}'.")
                    parsed_llm_data = cur_data
                    break

        # 3. Assemble domain from parsed data or generalized domain-aware builder
        if parsed_llm_data and "concepts" in parsed_llm_data and "questions" in parsed_llm_data:
            return self._build_from_structured_spec(
                domain_id=domain_id,
                topic_title=topic_title,
                spec=parsed_llm_data
            )
        else:
            return self._build_domain_aware_fallback(
                domain_id=domain_id,
                topic_title=topic_title,
                syllabus_text=syllabus_text,
                num_questions=num_questions
            )

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
        questions = []
        for i, q in enumerate(spec.get("questions", [])):
            qid = f"{domain_id}_q{i+1}"
            target_cid = suffix_to_full_id.get(q.get("concept_suffix"), concepts[i % len(concepts)]["id"])
            misc_id = misconceptions[i % len(misconceptions)]["id"] if misconceptions else None
            
            # Application questions get reasoning probes
            rp_data = q.get("reasoning_probe")

            questions.append({
                "id": qid,
                "domain_id": domain_id,
                "concept_id": target_cid,
                "question_type": q.get("question_type", "basic"),
                "difficulty": q.get("difficulty", "medium"),
                "question_text": q["question_text"],
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "correct_option": q.get("correct_option", "A").upper(),
                "explanation": q.get("explanation", "Correct answer explanation."),
                "misconception_id": misc_id,
                "prerequisite_id": None,
                "reasoning_probe": rp_data
            })

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
        """Dynamic domain-aware generator when neither LLM API nor curated topic matched."""
        icon, category = pick_icon_and_category(topic_title, syllabus_text)
        is_tech = any(k in category for k in ["Computer", "Tech", "AI", "Data", "Eng", "Network", "Software", "Information"])
        is_econ = any(k in category for k in ["Econ", "Business", "Finance", "Commerce"])
        is_humanities = any(k in category for k in ["History", "Humanities", "Social", "Law", "Literature", "Philosophy"])
        is_science = (not is_tech) and (not is_econ) and (not is_humanities)

        # Build 3-4 structured disciplinary concepts
        if is_science:
            raw_concepts = [
                (f"{topic_title}: Taxonomic & Structural Foundations", f"Basic biological and chemical classification, structures, and foundational definitions of {topic_title}."),
                (f"{topic_title}: Physiological & Biochemical Mechanisms", f"Functional modes of action, biochemical pathways, and operational dynamics governing {topic_title}."),
                (f"{topic_title}: Ecological Impact & Systemic Interactions", f"Environmental trade-offs, bioaccumulation, resistance evolution, and multi-trophic interactions in {topic_title}."),
                (f"{topic_title}: Diagnostic Evaluation & Problem Solving", f"Practical application, analytical diagnostics, quantitative measurement, and optimal management strategies.")
            ]
        elif is_tech:
            raw_concepts = [
                (f"{topic_title}: Mathematical & Algorithmic Foundations", f"Core formal definitions, mathematical invariants, and architectural structures of {topic_title}."),
                (f"{topic_title}: Internal Mechanisms & Optimization", f"Objective functions, gradient optimization, representations, and computational complexity in {topic_title}."),
                (f"{topic_title}: Architectural Constraints & Generalization", f"Overfitting vs underfitting trade-offs, regularization, latency bottlenecks, and stability."),
                (f"{topic_title}: Applied Engineering & Troubleshooting", f"Practical deployment, diagnostic evaluation, empirical debugging, and performance benchmarks.")
            ]
        elif is_econ:
            raw_concepts = [
                (f"{topic_title}: Microeconomic Principles & Market Dynamics", f"Core price mechanisms, supply/demand elasticity, and consumer preferences in {topic_title}."),
                (f"{topic_title}: Cost Structures & Equilibrium Dynamics", f"Marginal revenue, cost optimization, competitive equilibrium, and market failure mechanisms."),
                (f"{topic_title}: Policy Interventions & Externalities", f"Government regulation, deadweight loss, tax incidence, and welfare economics in {topic_title}."),
                (f"{topic_title}: Strategic Decision Analysis & Diagnostics", f"Empirical econometric modeling, forecasting, game-theoretic analysis, and trade-off evaluation.")
            ]
        else:
            raw_concepts = [
                (f"{topic_title}: Historical & Structural Origins", f"Primary socio-economic causes, institutional baselines, and historical emergence of {topic_title}."),
                (f"{topic_title}: Pivotal Developments & Critical Mechanisms", f"Key turning points, internal interactions, ideological debates, and structural milestones."),
                (f"{topic_title}: Structural Consequences & Systemic Legacy", f"Long-term systemic outcomes, institutional reforms, comparative analyses, and lasting impact."),
                (f"{topic_title}: Historiographical Analysis & Interpretation", f"Critical assessment of primary evidence, competing analytical schools, and empirical diagnosis.")
            ]

        concepts = []
        concept_guides = []
        for i, (cname, cdesc) in enumerate(raw_concepts):
            cid = f"{domain_id}_c{i+1}"
            prereqs = [concepts[i-1]["id"]] if i > 0 else []
            concepts.append({
                "id": cid,
                "domain_id": domain_id,
                "name": cname,
                "slug": slugify(cname),
                "category": category,
                "description": cdesc,
                "prerequisites": prereqs,
                "order_index": i + 1
            })
            concept_guides.append({
                "concept_id": cid,
                "domain_id": domain_id,
                "name": cname,
                "core_idea": f"Core principles and governing rules of {cname}.",
                "example": f"Authentic real-world application illustrating {cname}.",
                "common_mistake": f"Common diagnostic trap: overlooking foundational prerequisites in {cname}.",
                "key_takeaway": f"Mastery of {cname} is essential for accurate problem-solving in {topic_title}."
            })

        misconceptions = []
        for i, c in enumerate(concepts):
            mid = f"MISC_{domain_id.upper()}_{i+1}"
            misconceptions.append({
                "id": mid,
                "domain_id": domain_id,
                "code": f"M-GEN-{i+1:02d}",
                "concept_id": c["id"],
                "name": f"Diagnostic Misconception in {c['name'].split(':')[1].strip() if ':' in c['name'] else c['name']}",
                "description": f"Confusing governing causal mechanisms in {c['name']}.",
                "remediation": f"Review structural prerequisites and empirical evidence for {c['name']}."
            })

        questions = []
        for c_idx, c in enumerate(concepts):
            cid = c["id"]
            misc = misconceptions[c_idx]

            # 1. Basic question
            if is_science:
                q_text = f"Which taxonomic or physiological characteristic correctly distinguishes {c['name']} from adjacent scientific phenomena?"
                opt_a = f"Specific biochemical target interactions and physiological pathways."
                opt_b = f"Spontaneous molecular creation without energetic or mass conservation."
                opt_c = f"Static equilibrium that undergoes zero biochemical transformation."
                opt_d = f"Uniform dispersion of mass without selective cellular uptake."
                expl = f"{c['name']} operates via specific physiological mechanisms and biochemical pathways."
            elif is_tech:
                q_text = f"Which foundational computational property defines {c['name']} in technical systems?"
                opt_a = f"Mathematical formalization optimizing objective loss functions."
                opt_b = f"Infinite compute capacity eliminating all algorithmic bottlenecks."
                opt_c = f"Static heuristics that completely bypass mathematical optimization."
                opt_d = f"Random execution sequences with zero deterministic invariants."
                expl = f"{c['name']} is formalized through objective mathematical principles and optimization."
            else:
                q_text = f"Which fundamental principle distinguishes {c['name']} within {topic_title}?"
                opt_a = f"Established causal relationships supported by empirical baseline evidence."
                opt_b = f"Arbitrary isolated assumptions that contradict historical facts."
                opt_c = f"Superficial rhetoric that ignores structural socioeconomic forces."
                opt_d = f"Random coincidence that accounts for zero institutional patterns."
                expl = f"{c['name']} is grounded in structural causal mechanisms and empirical evidence."

            questions.append({
                "id": f"{domain_id}_q{len(questions)+1}",
                "domain_id": domain_id,
                "concept_id": cid,
                "question_type": "basic",
                "difficulty": "easy",
                "question_text": q_text,
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_option": "A",
                "explanation": expl,
                "misconception_id": misc["id"],
                "prerequisite_id": None,
                "reasoning_probe": None
            })

            # 2. Conceptual question
            if is_science:
                q_text = f"Why is understanding the operational mechanism of {c['name']} critical when analyzing {topic_title}?"
                opt_a = f"Because downstream metabolic or ecological outcomes directly depend on it."
                opt_b = f"Because it allows scientists to ignore all surrounding environmental factors."
                opt_c = f"Because chemical compounds remain identical regardless of dosage or exposure."
                opt_d = f"Because single isolated variables dictate all complex biological systems."
                expl = f"Downstream systemic responses in {topic_title} depend directly on the mechanism of {c['name']}."
            else:
                q_text = f"Why is understanding {c['name']} essential for evaluating outcomes in {topic_title}?"
                opt_a = f"Because downstream developments depend directly on its underlying mechanisms."
                opt_b = f"Because it eliminates any nuance between competing diagnostic viewpoints."
                opt_c = f"Because isolated single factors dictate all systemic dynamics."
                opt_d = f"Because it guarantees identical results across completely differing domains."
                expl = f"{c['name']} provides the causal baseline required to understand systemic developments."

            questions.append({
                "id": f"{domain_id}_q{len(questions)+1}",
                "domain_id": domain_id,
                "concept_id": cid,
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": q_text,
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_option": "A",
                "explanation": expl,
                "misconception_id": misc["id"],
                "prerequisite_id": None,
                "reasoning_probe": None
            })

            # 3. Application with Two-Tier Reasoning Probe
            if is_science:
                q_text = f"When evaluating an adverse anomaly in {c['name']}, which diagnostic methodology yields the most reliable findings?"
                opt_a = f"Empirically measuring quantitative biomarkers and physiological dose-responses."
                opt_b = f"Relying solely on visual appearance without consulting quantitative assays."
                opt_c = f"Assuming all deviations stem purely from random environmental fluctuations."
                opt_d = f"Extrapolating outcomes without verifying prerequisite chemical kinetics."
                expl = f"Reliable diagnosis requires quantitative empirical measurement of physiological biomarkers and dose-responses."
                probe_prompt = f"Why does quantitative biomarker analysis provide superior diagnosis over visual inspection?"
                probe_opts = {
                    "A": "Biochemical biomarkers detect sub-clinical cellular toxicity prior to gross phenotypic symptoms.",
                    "B": "Visual inspections require complex laser equipment unavailable in biological field laboratories.",
                    "C": "Cellular kinetics are completely unaffected by chemical dose concentrations.",
                    "D": "Biological tissues repair all cellular damage instantaneously before symptoms can manifest."
                }
            else:
                q_text = f"When analyzing a critical constraint in {c['name']}, which methodology yields the most reliable diagnosis?"
                opt_a = f"Evaluating structural causal drivers and testing prerequisite state constraints."
                opt_b = f"Accepting surface claims without consulting corroborating empirical evidence."
                opt_c = f"Attributing systemic failures entirely to random coincidental events."
                opt_d = f"Selecting extreme interventions regardless of foundational context."
                expl = f"Systematic analysis requires assessing causal drivers and prerequisite constraints."
                probe_prompt = f"Why does evaluating causal drivers provide deeper insight than superficial narratives?"
                probe_opts = {
                    "A": "Structural causal factors explain why systemic outcomes were compelled to occur.",
                    "B": "Superficial narratives contain infallible mathematical equations that cannot be challenged.",
                    "C": "Prerequisite drivers are completely unrelated to outcomes in complex systems.",
                    "D": "Systemic outcomes are determined solely by chronological coincidence without causation."
                }

            questions.append({
                "id": f"{domain_id}_q{len(questions)+1}",
                "domain_id": domain_id,
                "concept_id": cid,
                "question_type": "application",
                "difficulty": "hard",
                "question_text": q_text,
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_option": "A",
                "explanation": expl,
                "misconception_id": misc["id"],
                "prerequisite_id": c["prerequisites"][0] if c["prerequisites"] else cid,
                "reasoning_probe": {
                    "prompt": probe_prompt,
                    "options": probe_opts,
                    "correct_probe": "A"
                }
            })

        while len(questions) < num_questions:
            c = concepts[len(questions) % len(concepts)]
            questions.append({
                "id": f"{domain_id}_q{len(questions)+1}",
                "domain_id": domain_id,
                "concept_id": c["id"],
                "question_type": "conceptual",
                "difficulty": "medium",
                "question_text": f"Which analytical criterion distinguishes genuine mastery of {c['name']} from superficial memorization?",
                "option_a": f"Explaining the causal mechanisms and prerequisite constraints governing outcomes.",
                "option_b": f"Reciting isolated definitions without understanding their systemic function.",
                "option_c": f"Assuming every complex diagnostic problem can be resolved with one formula.",
                "option_d": f"Accepting contradictory hypotheses without verifying empirical consistency.",
                "correct_option": "A",
                "explanation": f"Genuine mastery involves understanding causal mechanisms and prerequisite constraints.",
                "misconception_id": misconceptions[0]["id"],
                "prerequisite_id": None,
                "reasoning_probe": None
            })

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
