"""
DeepLearnX FastAPI Application
Main backend server connecting:
- Deep Learning Cognitive Model (DeepCognitiveNet)
- Knowledge Dependency Graph Engine
- SQLite Database
- Student Assessment & Remedial Quiz
- Faculty Analytics Dashboard
- Modern Web Frontend
"""

import os
import sys
import json
import uuid
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Query, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Ensure local imports work cleanly
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "model"))
sys.path.insert(0, str(CURRENT_DIR))

from database import get_db_connection, init_db
from graph_engine import KnowledgeGraphEngine
from predictor import DeepLearnXPredictor
from concept_guide import get_concept_guide, CONCEPT_GUIDE
from syllabus_generator import syllabus_engine

# Initialize core services
init_db()
graph_engine = KnowledgeGraphEngine()
predictor = DeepLearnXPredictor()

app = FastAPI(
    title="DeepLearnX API",
    description="Deep Learning-Based Student Concept Understanding & Knowledge Gap Detection System",
    version="2.0.0"
)

# Enable CORS for local development and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper for password hashing
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ----------------- PYDANTIC SCHEMAS -----------------

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "student"

class OAuthLoginRequest(BaseModel):
    provider: str  # "google", "microsoft"
    email: str
    full_name: str
    avatar_url: Optional[str] = None

class QuestionAnswer(BaseModel):
    question_id: str
    selected_option: Optional[str] = None # 'A', 'B', 'C', 'D' or None if unanswered
    response_time: float = 30.0 # seconds
    confidence: int = 3 # 1 to 5
    reasoning_selected: Optional[str] = None

class AssessmentSubmission(BaseModel):
    user_id: int
    domain_id: str = "deep_learning"
    answers: List[QuestionAnswer]

class RemedialSubmission(BaseModel):
    user_id: int
    domain_id: str = "deep_learning"
    original_session_id: str
    target_concept_id: str
    answers: List[QuestionAnswer]

class CustomGenerateRequest(BaseModel):
    topic_title: str
    syllabus_text: Optional[str] = ""
    user_id: Optional[int] = None
    num_questions: int = 12
    api_key: Optional[str] = None
    api_provider: Optional[str] = "gemini"
    model_name: Optional[str] = None
    require_live_llm: Optional[bool] = False

# ----------------- AUTH ENDPOINTS -----------------

@app.post("/api/auth/login")
def login(req: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    pw_hash = hash_pw(req.password)
    identifier = req.username.strip().lower()
    user = cursor.execute(
        "SELECT id, username, email, full_name, role FROM users WHERE (LOWER(username) = ? OR LOWER(email) = ?) AND password_hash = ?",
        (identifier, identifier, pw_hash)
    ).fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
        
    return {
        "status": "success",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        },
        "token": f"token-{user['id']}-{uuid.uuid4().hex[:8]}"
    }

@app.post("/api/auth/oauth-login")
def oauth_login(req: OAuthLoginRequest):
    """
    Seamless OAuth handler for Google and Microsoft SSO authentication.
    Automatically finds or provisions user profile and logs them in.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = req.email.strip().lower()
    
    user = cursor.execute(
        "SELECT id, username, email, full_name, role FROM users WHERE LOWER(email) = ?",
        (clean_email,)
    ).fetchone()
    
    if not user:
        # Auto-provision new account for Google / Microsoft user
        base_username = clean_email.split("@")[0]
        cleaned_username = "".join(c for c in base_username if c.isalnum() or c == "_") or "student"
        # Check collision
        existing = cursor.execute("SELECT id FROM users WHERE username = ?", (cleaned_username,)).fetchone()
        if existing:
            cleaned_username = f"{cleaned_username}_{uuid.uuid4().hex[:4]}"
            
        dummy_hash = hash_pw(f"oauth_{req.provider}_{uuid.uuid4().hex}")
        cursor.execute(
            "INSERT INTO users (username, email, full_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (cleaned_username, clean_email, req.full_name.strip(), dummy_hash, "student")
        )
        conn.commit()
        user_id = cursor.lastrowid
        user_data = {
            "id": user_id,
            "username": cleaned_username,
            "email": clean_email,
            "full_name": req.full_name.strip(),
            "role": "student"
        }
    else:
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
        
    conn.close()
    return {
        "status": "success",
        "provider": req.provider,
        "user": user_data,
        "token": f"oauth-{req.provider}-{user_data['id']}-{uuid.uuid4().hex[:8]}"
    }

@app.get("/api/user/profile/{user_id}")
def get_user_profile(user_id: int):
    """
    Returns the user's isolated profile metadata and multi-subject telemetry statistics.
    """
    conn = get_db_connection()
    user = conn.execute("SELECT id, username, email, full_name, role, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User profile not found")
        
    sessions = conn.execute("""
        SELECT s.id, s.domain_id, d.name as domain_name, d.icon as domain_icon,
               s.score, s.total_questions, s.accuracy, s.predicted_state, s.created_at
        FROM assessment_sessions s
        LEFT JOIN domains d ON s.domain_id = d.id
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    
    total_tests = len(sessions)
    avg_accuracy = round(sum(s["accuracy"] for s in sessions) / total_tests, 3) if total_tests > 0 else 0.0
    latest_state = sessions[0]["predicted_state"] if total_tests > 0 else "Ready for Assessment"
    
    # Distinct subjects attempted
    subjects = []
    seen = set()
    for s in sessions:
        did = s["domain_id"]
        if did not in seen:
            seen.add(did)
            subjects.append({
                "id": did,
                "name": s["domain_name"] or did,
                "icon": s["domain_icon"] or "📚"
            })
            
    names = (user["full_name"] or user["username"]).strip().split()
    initials = "".join(n[0].upper() for n in names[:2]) if names else "U"
    
    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "created_at": user["created_at"],
            "avatar_initials": initials
        },
        "stats": {
            "total_assessments": total_tests,
            "average_accuracy": avg_accuracy,
            "latest_state": latest_state,
            "subjects_tested": subjects
        }
    }

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    pw_hash = hash_pw(req.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, full_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (req.username, req.email, req.full_name, pw_hash, req.role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "username": req.username,
                "email": req.email,
                "full_name": req.full_name,
                "role": req.role
            }
        }
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")

@app.get("/api/auth/demo-users")
def get_demo_users():
    """Returns preset demo user personas for 1-click viva/hackathon presentations."""
    return [
        {
            "id": 2,
            "username": "student_a",
            "full_name": "Ananya Sharma",
            "role": "student",
            "archetype": "Genuine Mastery",
            "description": "Consistent high accuracy across basic, conceptual, and application questions."
        },
        {
            "id": 3,
            "username": "student_b",
            "full_name": "Rahul Verma",
            "role": "student",
            "archetype": "False Mastery",
            "description": "Scored 100% on basic definitions and recall, but failed on application questions (Memorization bias)."
        },
        {
            "id": 4,
            "username": "student_c",
            "full_name": "Sneha Patel",
            "role": "student",
            "archetype": "Prerequisite Knowledge Gap",
            "description": "Struggles with Backpropagation due to missing prerequisite knowledge in Calculus Chain Rule."
        },
        {
            "id": 5,
            "username": "student_d",
            "full_name": "Karan Singh",
            "role": "student",
            "archetype": "Conceptual Misconception",
            "description": "Actively confuses Activation Functions with Loss Functions."
        },
        {
            "id": 1,
            "username": "admin",
            "full_name": "Prof. Dr. R. K. Murthy",
            "role": "faculty",
            "archetype": "Faculty Administrator",
            "description": "Full access to Class Analytics, Misconception Heatmaps, and Prerequisite Bottlenecks."
        }
    ]

# ----------------- DOMAINS, CONCEPTS & GRAPH ENDPOINTS -----------------

@app.get("/api/domains")
def get_domains():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM domains").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/concepts")
def get_concepts(domain: str = "deep_learning"):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM concepts WHERE domain_id = ? ORDER BY order_index ASC", (domain,)).fetchall()
    conn.close()
    
    concepts = []
    for r in rows:
        concepts.append({
            "id": r["id"],
            "domain_id": r["domain_id"],
            "name": r["name"],
            "slug": r["slug"],
            "category": r["category"],
            "description": r["description"],
            "prerequisites": json.loads(r["prerequisites"] or "[]"),
            "order_index": r["order_index"]
        })
    return concepts

@app.get("/api/concepts/guide")
def get_concept_learning_guide(concept_id: Optional[str] = None, domain: str = "deep_learning"):
    """Returns detailed concept learning guide with simple-English explanations and real-world examples."""
    if concept_id and concept_id != "all":
        return get_concept_guide(concept_id, domain)
    
    # Return all concept guides for this domain
    domain_guides = {k: v for k, v in CONCEPT_GUIDE.items() if v.get("domain_id") == domain}
    return domain_guides

@app.get("/api/graph/base")
def get_base_graph(domain: str = "deep_learning"):
    return graph_engine.get_full_graph_structure(domain_id=domain)

@app.get("/api/graph/student/{user_id}")
def get_student_knowledge_map(user_id: int, domain: str = "deep_learning", session_id: Optional[str] = None):
    """
    Returns the student's personalized concept dependency graph
    with nodes color-coded:
    GREEN = Strong Understanding (Mastered)
    YELLOW = Partial Understanding
    ORANGE = Conceptual Misconception / False Mastery
    RED = Prerequisite Knowledge Gap
    Can load either the most recent session for this domain, or a specific past session_id.
    """
    conn = get_db_connection()
    if session_id:
        session = conn.execute(
            "SELECT * FROM assessment_sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        if session:
            domain = session["domain_id"]
    else:
        # Fetch most recent assessment session for this student and domain
        session = conn.execute(
            "SELECT * FROM assessment_sessions WHERE user_id = ? AND domain_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id, domain)
        ).fetchone()
    
    if not session:
        conn.close()
        # Return default graph if student has not taken any test yet
        base_graph = graph_engine.get_full_graph_structure(domain_id=domain)
        return {
            "has_assessment": False,
            "domain_id": domain,
            "graph_nodes": base_graph["nodes"],
            "graph_edges": base_graph["edges"],
            "primary_gap_name": "No assessment taken yet",
            "root_prerequisite_gaps": []
        }
        
    session_id = session["id"]
    # Fetch student question responses
    resp_rows = conn.execute("""
        SELECT sr.question_id, sr.selected_option, sr.is_correct, q.concept_id, q.misconception_id
        FROM student_responses sr
        JOIN questions q ON sr.question_id = q.id
        WHERE sr.session_id = ?
    """, (session_id,)).fetchall()
    
    conn.close()
    
    # Calculate concept-level scores
    concept_scores = {}
    for r in resp_rows:
        cid = r["concept_id"]
        if cid not in concept_scores:
            concept_scores[cid] = {"correct": 0, "total": 0, "acc": 0.0}
        concept_scores[cid]["total"] += 1
        if r["is_correct"]:
            concept_scores[cid]["correct"] += 1
            
    for cid, st in concept_scores.items():
        st["acc"] = st["correct"] / st["total"] if st["total"] > 0 else 0.0
        
    detected_miscs = json.loads(session["detected_misconceptions"] or "[]")
    
    eval_result = graph_engine.evaluate_student_graph(
        concept_scores=concept_scores,
        detected_misconceptions=detected_miscs,
        primary_state=session["predicted_state"],
        domain_id=domain
    )
    
    eval_result["has_assessment"] = True
    eval_result["session_id"] = session_id
    eval_result["predicted_state"] = session["predicted_state"]
    eval_result["overall_accuracy"] = session["accuracy"]
    eval_result["created_at"] = session["created_at"]
    return eval_result

# ----------------- ASSESSMENT ENDPOINTS -----------------

@app.get("/api/assessment/questions")
def get_assessment_questions(
    limit: int = 10,
    domain: str = "deep_learning",
    user_id: Optional[int] = None
):
    """
    Returns balanced diagnostic assessment questions for the chosen domain.
    If user_id is provided, guarantees non-repeating questions across consecutive test attempts
    by prioritizing questions the user has NOT previously answered in this domain.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    selected_rows = []
    
    if user_id:
        # Prioritize questions unseen by this user in this domain
        unseen_rows = cursor.execute("""
            SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                   q.option_a, q.option_b, q.option_c, q.option_d, q.reasoning_probe, c.name as concept_name
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            WHERE q.domain_id = ?
              AND q.id NOT IN (
                  SELECT sr.question_id
                  FROM student_responses sr
                  JOIN assessment_sessions s ON sr.session_id = s.id
                  WHERE s.user_id = ? AND s.domain_id = ?
              )
            ORDER BY RANDOM()
            LIMIT ?
        """, (domain, user_id, domain, limit)).fetchall()
        
        for r in unseen_rows:
            selected_rows.append(r)

    # If user_id wasn't provided or unseen questions are fewer than the requested limit,
    # fill the remaining slots from the full domain pool (excluding questions already in this batch)
    remaining_needed = limit - len(selected_rows)
    if remaining_needed > 0:
        already_picked = [r["id"] for r in selected_rows]
        if already_picked:
            placeholders = ",".join("?" for _ in already_picked)
            fallback_query = f"""
                SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                       q.option_a, q.option_b, q.option_c, q.option_d, q.reasoning_probe, c.name as concept_name
                FROM questions q
                JOIN concepts c ON q.concept_id = c.id
                WHERE q.domain_id = ?
                  AND q.id NOT IN ({placeholders})
                ORDER BY RANDOM()
                LIMIT ?
            """
            extra_rows = cursor.execute(fallback_query, [domain] + already_picked + [remaining_needed]).fetchall()
        else:
            fallback_query = """
                SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                       q.option_a, q.option_b, q.option_c, q.option_d, q.reasoning_probe, c.name as concept_name
                FROM questions q
                JOIN concepts c ON q.concept_id = c.id
                WHERE q.domain_id = ?
                ORDER BY RANDOM()
                LIMIT ?
            """
            extra_rows = cursor.execute(fallback_query, (domain, remaining_needed)).fetchall()

        for r in extra_rows:
            selected_rows.append(r)

    conn.close()
    
    questions = []
    for r in selected_rows:
        rp_data = None
        if r["reasoning_probe"]:
            try:
                rp_data = json.loads(r["reasoning_probe"])
            except Exception:
                rp_data = None

        questions.append({
            "id": r["id"],
            "domain_id": r["domain_id"],
            "concept_id": r["concept_id"],
            "concept_name": r["concept_name"],
            "question_type": r["question_type"], # basic, conceptual, application
            "difficulty": r["difficulty"],
            "question_text": r["question_text"],
            "options": {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            },
            "reasoning_probe": rp_data
        })
    return questions

@app.get("/api/assessment/provider-status")
def get_provider_status():
    """Endpoint for UI and testing to inspect configured LLM providers and active generation mode."""
    from backend.app.syllabus_generator import check_provider_status
    return check_provider_status()

@app.post("/api/assessment/custom-generate")
def custom_generate_assessment(req: CustomGenerateRequest):
    """
    Generates a custom syllabus assessment:
    - Synthesizes 3-4 hierarchical sub-concepts with prerequisite DAG links
    - Generates misconceptions with remediation guidance
    - Creates 12 tiered diagnostic questions with equalized option lengths and reasoning probes
    - Registers concept refresher guides for personalized learning
    - Returns new domain details ready for instant assessment launch
    """
    if not req.topic_title or not req.topic_title.strip():
        raise HTTPException(status_code=400, detail="Topic title is required")
        
    try:
        result = syllabus_engine.generate_custom_domain(
            topic_title=req.topic_title.strip(),
            syllabus_text=req.syllabus_text or "",
            user_id=req.user_id,
            num_questions=req.num_questions,
            api_key=req.api_key,
            api_provider=req.api_provider,
            model_name=req.model_name,
            require_live_llm=bool(req.require_live_llm)
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re_err:
        raise HTTPException(status_code=502, detail=str(re_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate custom assessment: {str(e)}")

@app.post("/api/assessment/upload-syllabus-file")
def upload_syllabus_file(
    topic_title: str = Query(...),
    api_key: Optional[str] = Query(None),
    api_provider: Optional[str] = Query("gemini"),
    file: UploadFile = File(...)
):
    """
    Uploads a syllabus document (.pdf, .txt, .md, .json, .csv) and automatically
    prepares a customized question bank and prerequisite DAG.
    Runs in a worker threadpool so long-running LLM generation does not block the main event loop.
    """
    try:
        content_bytes = file.file.read()
        filename = (file.filename or "").lower()
        syllabus_text = ""

        # 1. Handle PDF uploads cleanly
        if filename.endswith(".pdf"):
            try:
                import io, pypdf
                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                extracted_pages = []
                for p in reader.pages[:10]:
                    txt = p.extract_text()
                    if txt:
                        extracted_pages.append(txt.strip())
                syllabus_text = "\n\n".join(extracted_pages)
                print(f"[PDF Extract] Extracted {len(syllabus_text)} characters from {file.filename}")
            except Exception as pdf_err:
                print(f"[PDF Extract Warning] {pdf_err}")

        # 2. Text / generic decodes
        if not syllabus_text:
            try:
                syllabus_text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    syllabus_text = content_bytes.decode("latin-1")
                except Exception:
                    syllabus_text = ""

        # 3. Limit size to prevent token rate limits (429)
        if len(syllabus_text) > 3500:
            syllabus_text = syllabus_text[:3500]

        result = syllabus_engine.generate_custom_domain(
            topic_title=topic_title.strip(),
            syllabus_text=syllabus_text,
            num_questions=12,
            api_key=api_key,
            api_provider=api_provider
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process syllabus file: {str(e)}")

@app.post("/api/assessment/submit")
def submit_assessment(sub: AssessmentSubmission):
    """
    Core Deep Learning Pipeline execution:
    1. Runs PyTorch DeepCognitiveNet inference on student response sequence + structured features.
    2. Detects False Mastery (Basic vs Application divergence).
    3. Detects Misconceptions via distractor category mapping and neural multi-task head.
    4. Traces Root Prerequisite Gap using the Knowledge Dependency DAG.
    5. Generates personalized learning recommendations.
    6. Stores results in SQLite and returns comprehensive report.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Format answers for predictor
    ans_dicts = [a.model_dump() for a in sub.answers]
    
    # Execute Deep Learning model inference
    dl_result = predictor.analyze_session(ans_dicts)
    
    # Calculate question correctness and concept stats
    total_q = len(sub.answers)
    score = 0
    concept_scores = {}
    
    for a in sub.answers:
        q_row = cursor.execute("SELECT * FROM questions WHERE id = ?", (a.question_id,)).fetchone()
        if not q_row:
            continue
        cid = q_row["concept_id"]
        is_corr = bool(a.selected_option and q_row["correct_option"] and str(a.selected_option).strip().upper() == str(q_row["correct_option"]).strip().upper())
        if is_corr:
            score += 1
            
        if cid not in concept_scores:
            concept_scores[cid] = {"correct": 0, "total": 0, "acc": 0.0}
        concept_scores[cid]["total"] += 1
        if is_corr:
            concept_scores[cid]["correct"] += 1
            
    for cid, st in concept_scores.items():
        st["acc"] = st["correct"] / st["total"] if st["total"] > 0 else 0.0
        
    accuracy = round((score / total_q) * 100, 1) if total_q > 0 else 0.0
    
    # Evaluate Knowledge Graph
    graph_eval = graph_engine.evaluate_student_graph(
        concept_scores=concept_scores,
        detected_misconceptions=dl_result["detected_misconceptions"],
        primary_state=dl_result["predicted_state"],
        domain_id=sub.domain_id
    )
    
    primary_gap_id = graph_eval.get("primary_prerequisite_gap")
    primary_gap_name = graph_eval.get("primary_gap_name", "None Detected")
    
    troubled_concepts = [
        cid for cid, s in graph_eval["node_status_map"].items()
        if s["status"] in ["gap", "misconception", "partial"]
    ]
    
    recommendations = graph_engine.generate_recommendations(
        predicted_state=dl_result["predicted_state"],
        primary_gap_id=primary_gap_id,
        detected_misconceptions=dl_result["detected_misconceptions"],
        troubled_concepts=troubled_concepts,
        domain_id=sub.domain_id
    )
    
    # Save assessment session to SQLite
    session_id = f"sess-{uuid.uuid4().hex[:12]}"
    
    cursor.execute("""
        INSERT INTO assessment_sessions (
            id, user_id, domain_id, score, total_questions, accuracy, predicted_state, confidence,
            state_probabilities, primary_gap_id, primary_gap_name, detected_misconceptions,
            false_mastery_data, recommendations, concept_mastery_map
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, sub.user_id, sub.domain_id, score, total_q, accuracy,
        dl_result["predicted_state"], dl_result["confidence"],
        json.dumps(dl_result["state_probabilities"]),
        primary_gap_id, primary_gap_name,
        json.dumps(dl_result["detected_misconceptions"]),
        json.dumps(dl_result["false_mastery_breakdown"]),
        json.dumps(recommendations),
        json.dumps({k: v["status"] for k, v in graph_eval["node_status_map"].items()})
    ))
    
    # Build detailed question reviews with conceptual mistake analysis and teaching remediations
    question_reviews = []
    for a in sub.answers:
        q_row = cursor.execute("""
            SELECT q.*, c.name as concept_name, m.name as misc_name, m.description as misc_desc, m.remediation as misc_remediation
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            LEFT JOIN misconceptions m ON q.misconception_id = m.id
            WHERE q.id = ?
        """, (a.question_id,)).fetchone()
        if not q_row:
            continue
            
        is_corr = (a.selected_option.upper() == q_row["correct_option"].upper())
        opts = {
            "A": q_row["option_a"],
            "B": q_row["option_b"],
            "C": q_row["option_c"],
            "D": q_row["option_d"]
        }
        
        misc_info = None
        detected_misc_ids = {m["id"] for m in dl_result.get("detected_misconceptions", []) if isinstance(m, dict)}
        if not is_corr and q_row["misconception_id"] and q_row["misc_name"]:
            if (q_row["misconception_id"] in detected_misc_ids) or q_row["question_type"] in ["conceptual", "application"]:
                misc_info = {
                    "id": q_row["misconception_id"],
                    "name": q_row["misc_name"],
                    "description": q_row["misc_desc"],
                    "remediation": q_row["misc_remediation"]
                }
            
        probe_info = None
        if q_row["reasoning_probe"]:
            try:
                rp = json.loads(q_row["reasoning_probe"])
                p_sel = a.reasoning_selected.upper() if a.reasoning_selected else None
                c_prb = rp.get("correct_probe", "A").upper()
                probe_info = {
                    "prompt": rp.get("prompt"),
                    "selected": p_sel,
                    "selected_text": rp.get("options", {}).get(p_sel, "Not Answered"),
                    "correct": c_prb,
                    "correct_text": rp.get("options", {}).get(c_prb, ""),
                    "is_correct": (p_sel == c_prb) if p_sel else False
                }
            except Exception:
                pass
                
        question_reviews.append({
            "question_id": a.question_id,
            "question_text": q_row["question_text"],
            "question_type": q_row["question_type"],
            "concept_id": q_row["concept_id"],
            "concept_name": q_row["concept_name"],
            "selected_option": a.selected_option.upper(),
            "selected_text": opts.get(a.selected_option.upper(), ""),
            "correct_option": q_row["correct_option"].upper(),
            "correct_text": opts.get(q_row["correct_option"].upper(), ""),
            "is_correct": is_corr,
            "explanation": q_row["explanation"],
            "misconception": misc_info,
            "reasoning_probe": probe_info
        })

    # Save individual responses
    for a in sub.answers:
        q_row = cursor.execute("SELECT correct_option FROM questions WHERE id = ?", (a.question_id,)).fetchone()
        is_corr = 1 if (q_row and a.selected_option.upper() == q_row["correct_option"].upper()) else 0
        cursor.execute("""
            INSERT INTO student_responses (session_id, question_id, selected_option, is_correct, response_time, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, a.question_id, a.selected_option, is_corr, a.response_time, a.confidence))
        
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "session_id": session_id,
        "score": score,
        "total_questions": total_q,
        "accuracy": accuracy,
        "deep_learning_analysis": {
            "predicted_state": dl_result["predicted_state"],
            "confidence": dl_result["confidence"],
            "state_probabilities": dl_result["state_probabilities"],
            "prerequisite_risk": dl_result["prerequisite_risk"],
            "false_mastery_breakdown": dl_result["false_mastery_breakdown"],
            "detected_misconceptions": dl_result["detected_misconceptions"],
            "metrics_summary": dl_result["metrics_summary"],
            "attention_weights": dl_result["attention_weights"]
        },
        "knowledge_gap_detection": {
            "primary_prerequisite_gap": primary_gap_id,
            "primary_gap_name": primary_gap_name,
            "root_prerequisite_gaps": graph_eval["root_prerequisite_gaps"],
            "node_status_map": graph_eval["node_status_map"],
            "graph_nodes": graph_eval["graph_nodes"],
            "graph_edges": graph_eval["graph_edges"]
        },
        "recommendations": recommendations,
        "question_reviews": question_reviews
    }

@app.get("/api/assessment/history/{user_id}")
def get_student_history(user_id: int, domain: Optional[str] = None):
    conn = get_db_connection()
    if domain:
        sessions = conn.execute("""
            SELECT s.id, s.domain_id, d.name as domain_name, d.icon as domain_icon, d.category as domain_category,
                   s.score, s.total_questions, s.accuracy, s.predicted_state, s.confidence,
                   s.primary_gap_name, s.created_at
            FROM assessment_sessions s
            LEFT JOIN domains d ON s.domain_id = d.id
            WHERE s.user_id = ? AND s.domain_id = ?
            ORDER BY s.created_at DESC
        """, (user_id, domain)).fetchall()
    else:
        sessions = conn.execute("""
            SELECT s.id, s.domain_id, d.name as domain_name, d.icon as domain_icon, d.category as domain_category,
                   s.score, s.total_questions, s.accuracy, s.predicted_state, s.confidence,
                   s.primary_gap_name, s.created_at
            FROM assessment_sessions s
            LEFT JOIN domains d ON s.domain_id = d.id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
        """, (user_id,)).fetchall()
    conn.close()
    
    return [dict(s) for s in sessions]

@app.get("/api/assessment/session/{session_id}")
def get_session_details(session_id: str):
    conn = get_db_connection()
    session = conn.execute("""
        SELECT s.*, d.name as domain_name, d.icon as domain_icon, d.category as domain_category
        FROM assessment_sessions s
        LEFT JOIN domains d ON s.domain_id = d.id
        WHERE s.id = ?
    """, (session_id,)).fetchone()
    if not session:
        conn.close()
        raise HTTPException(status_code=404, detail="Assessment session not found")
        
    responses = conn.execute("""
        SELECT sr.*, q.concept_id, q.question_text, q.question_type, q.difficulty, q.correct_option,
               q.option_a, q.option_b, q.option_c, q.option_d, q.reasoning_probe,
               q.explanation, c.name as concept_name,
               m.id as misc_id, m.name as misc_name, m.description as misc_desc, m.remediation as misc_remediation
        FROM student_responses sr
        JOIN questions q ON sr.question_id = q.id
        JOIN concepts c ON q.concept_id = c.id
        LEFT JOIN misconceptions m ON q.misconception_id = m.id
        WHERE sr.session_id = ?
    """, (session_id,)).fetchall()
    
    conn.close()
    
    question_reviews = []
    for r in responses:
        is_corr = bool(r["is_correct"])
        opts = {
            "A": r["option_a"],
            "B": r["option_b"],
            "C": r["option_c"],
            "D": r["option_d"]
        }
        misc_info = None
        if not is_corr and r["misc_id"] and r["misc_name"]:
            misc_info = {
                "id": r["misc_id"],
                "name": r["misc_name"],
                "description": r["misc_desc"],
                "remediation": r["misc_remediation"]
            }
        probe_info = None
        if r["reasoning_probe"]:
            try:
                rp = json.loads(r["reasoning_probe"])
                c_prb = rp.get("correct_probe", "A").upper()
                probe_info = {
                    "prompt": rp.get("prompt"),
                    "correct": c_prb,
                    "correct_text": rp.get("options", {}).get(c_prb, "")
                }
            except Exception:
                pass
        question_reviews.append({
            "question_id": r["question_id"],
            "question_text": r["question_text"],
            "question_type": r["question_type"],
            "concept_id": r["concept_id"],
            "concept_name": r["concept_name"],
            "selected_option": r["selected_option"].upper(),
            "selected_text": opts.get(r["selected_option"].upper(), ""),
            "correct_option": r["correct_option"].upper(),
            "correct_text": opts.get(r["correct_option"].upper(), ""),
            "is_correct": is_corr,
            "explanation": r["explanation"],
            "misconception": misc_info,
            "reasoning_probe": probe_info
        })

    sess_dict = dict(session)
    sess_dict["state_probabilities"] = json.loads(sess_dict["state_probabilities"] or "{}")
    sess_dict["detected_misconceptions"] = json.loads(sess_dict["detected_misconceptions"] or "[]")
    sess_dict["false_mastery_data"] = json.loads(sess_dict["false_mastery_data"] or "{}")
    sess_dict["recommendations"] = json.loads(sess_dict["recommendations"] or "[]")
    sess_dict["concept_mastery_map"] = json.loads(sess_dict["concept_mastery_map"] or "{}")
    sess_dict["responses"] = [dict(r) for r in responses]
    sess_dict["question_reviews"] = question_reviews
    return sess_dict

# ----------------- REMEDIAL ASSESSMENT ENDPOINTS -----------------

@app.get("/api/remedial/questions")
def get_remedial_questions(concept_id: str = "", count: int = 3, domain: str = ""):
    """Returns questions specifically targeting the identified weak concept or prerequisite gap within the domain."""
    conn = get_db_connection()
    target_domain = domain.strip() if domain else ""
    
    rows = []
    if concept_id:
        rows = conn.execute("""
            SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                   q.option_a, q.option_b, q.option_c, q.option_d, c.name as concept_name
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            WHERE q.concept_id = ?
            ORDER BY q.question_type ASC
            LIMIT ?
        """, (concept_id, count)).fetchall()

    if not target_domain and rows:
        target_domain = rows[0]["domain_id"]

    if len(rows) < count and target_domain:
        needed = count - len(rows)
        existing_ids = [r["id"] for r in rows]
        if existing_ids:
            placeholders = ",".join("?" for _ in existing_ids)
            extra = conn.execute(f"""
                SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                       q.option_a, q.option_b, q.option_c, q.option_d, c.name as concept_name
                FROM questions q
                JOIN concepts c ON q.concept_id = c.id
                WHERE q.domain_id = ? AND q.id NOT IN ({placeholders})
                ORDER BY RANDOM()
                LIMIT ?
            """, (target_domain, *existing_ids, needed)).fetchall()
        else:
            extra = conn.execute("""
                SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                       q.option_a, q.option_b, q.option_c, q.option_d, c.name as concept_name
                FROM questions q
                JOIN concepts c ON q.concept_id = c.id
                WHERE q.domain_id = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (target_domain, needed)).fetchall()
        rows = list(rows) + list(extra)

    if not rows:
        rows = conn.execute("""
            SELECT q.id, q.domain_id, q.concept_id, q.question_type, q.difficulty, q.question_text,
                   q.option_a, q.option_b, q.option_c, q.option_d, c.name as concept_name
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,)).fetchall()
        
    conn.close()
    
    return [
        {
            "id": r["id"],
            "domain_id": r["domain_id"],
            "concept_id": r["concept_id"],
            "concept_name": r["concept_name"],
            "question_type": r["question_type"],
            "difficulty": r["difficulty"],
            "question_text": r["question_text"],
            "options": {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            }
        }
        for r in rows
    ]

@app.post("/api/remedial/submit")
def submit_remedial(sub: RemedialSubmission):
    """
    Submits remedial drill:
    If student passes remedial drill (>=66%), their status for the target concept
    is upgraded to 'mastered' in the concept mastery map!
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    score = 0
    total = len(sub.answers)
    
    for a in sub.answers:
        q = cursor.execute("SELECT correct_option FROM questions WHERE id = ?", (a.question_id,)).fetchone()
        if q and a.selected_option.upper() == q["correct_option"].upper():
            score += 1
            
    pct = (score / total) * 100 if total > 0 else 0
    passed = (pct >= 66.0)
    updated_status = "Mastered (Remediated)" if passed else "Needs Continued Revision"
    
    remedial_id = f"rem-{uuid.uuid4().hex[:10]}"
    cursor.execute("""
        INSERT INTO remedial_sessions (
            id, user_id, domain_id, original_session_id, target_concept_id, score, total_questions, updated_mastery_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (remedial_id, sub.user_id, sub.domain_id, sub.original_session_id, sub.target_concept_id, score, total, updated_status))
    
    # If passed, update the original session's concept_mastery_map so the graph map turns GREEN!
    if passed:
        orig = cursor.execute("SELECT concept_mastery_map FROM assessment_sessions WHERE id = ?", (sub.original_session_id,)).fetchone()
        if orig:
            c_map = json.loads(orig["concept_mastery_map"] or "{}")
            c_map[sub.target_concept_id] = "mastered"
            cursor.execute(
                "UPDATE assessment_sessions SET concept_mastery_map = ? WHERE id = ?",
                (json.dumps(c_map), sub.original_session_id)
            )
            
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "score": score,
        "total_questions": total,
        "accuracy": round(pct, 1),
        "passed": passed,
        "updated_mastery_status": updated_status,
        "message": "Concept successfully remediated! Your knowledge gap map has been updated." if passed else "Please review the foundation notes and try again."
    }

# ----------------- FACULTY & ADMIN DASHBOARD ENDPOINTS -----------------

@app.get("/api/faculty/dashboard")
def get_faculty_dashboard():
    """
    Comprehensive Faculty & Admin Analytics:
    - Total students
    - Average mastery score
    - State distribution (Genuine, False, Misconception, Gap)
    - Most difficult concepts ranking
    - Most prevalent misconceptions
    - Common prerequisite bottlenecks
    - Student roster with individual reports
    """
    conn = get_db_connection()
    
    # Student counts
    students = conn.execute("SELECT id, username, full_name, email FROM users WHERE role = 'student'").fetchall()
    total_students = len(students)
    
    # All assessment sessions
    sessions = conn.execute("SELECT * FROM assessment_sessions ORDER BY created_at DESC").fetchall()
    
    avg_score = 0.0
    state_counts = {
        "Genuine Mastery": 0,
        "False Mastery": 0,
        "Conceptual Misconception": 0,
        "Knowledge Gap": 0
    }
    
    gap_counts = {}
    misconception_counts = {}
    
    for s in sessions:
        avg_score += s["accuracy"]
        st = s["predicted_state"]
        if st in state_counts:
            state_counts[st] += 1
            
        gap = s["primary_gap_name"]
        if gap and gap != "None Detected":
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
            
        try:
            m_list = json.loads(s["detected_misconceptions"] or "[]")
            for m in m_list:
                m_name = m.get("name", "Unknown Misconception")
                misconception_counts[m_name] = misconception_counts.get(m_name, 0) + 1
        except Exception:
            pass
            
    if sessions:
        avg_score = round(avg_score / len(sessions), 1)
        
    # Question level difficulty analysis
    q_stats = conn.execute("""
        SELECT q.concept_id, c.name as concept_name,
               COUNT(sr.id) as total_attempts,
               SUM(sr.is_correct) as correct_attempts
        FROM student_responses sr
        JOIN questions q ON sr.question_id = q.id
        JOIN concepts c ON q.concept_id = c.id
        GROUP BY q.concept_id
    """).fetchall()
    
    difficult_concepts = []
    for qs in q_stats:
        tot = qs["total_attempts"]
        corr = qs["correct_attempts"] or 0
        rate = round((corr / tot) * 100, 1) if tot > 0 else 0.0
        difficult_concepts.append({
            "concept_id": qs["concept_id"],
            "concept_name": qs["concept_name"],
            "success_rate": rate,
            "failure_rate": round(100.0 - rate, 1),
            "attempts": tot
        })
    difficult_concepts.sort(key=lambda x: x["success_rate"]) # lowest success rate first
    
    # Student Roster
    roster = []
    for st in students:
        s_id = st["id"]
        latest = conn.execute(
            "SELECT * FROM assessment_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (s_id,)
        ).fetchone()
        
        roster.append({
            "user_id": s_id,
            "username": st["username"],
            "full_name": st["full_name"],
            "email": st["email"],
            "has_assessment": (latest is not None),
            "accuracy": latest["accuracy"] if latest else None,
            "predicted_state": latest["predicted_state"] if latest else "No Assessment",
            "primary_gap": latest["primary_gap_name"] if latest else "-",
            "latest_session_id": latest["id"] if latest else None,
            "created_at": latest["created_at"] if latest else "-"
        })
        
    conn.close()
    
    # Sort bottlenecks
    sorted_gaps = sorted([{"gap": k, "count": v} for k, v in gap_counts.items()], key=lambda x: x["count"], reverse=True)
    sorted_miscs = sorted([{"misconception": k, "count": v} for k, v in misconception_counts.items()], key=lambda x: x["count"], reverse=True)
    
    return {
        "total_students": total_students,
        "total_assessments": len(sessions),
        "average_accuracy": avg_score,
        "state_distribution": state_counts,
        "most_difficult_concepts": difficult_concepts[:5],
        "common_prerequisite_bottlenecks": sorted_gaps[:5],
        "most_prevalent_misconceptions": sorted_miscs[:5],
        "student_roster": roster
    }

# ----------------- MODEL METRICS & TRANSPARENCY -----------------

@app.get("/api/model/metrics")
def get_model_metrics():
    """Returns actual trained PyTorch model evaluation metrics and training history."""
    metrics_path = PROJECT_ROOT / "model" / "metrics.json"
    history_path = PROJECT_ROOT / "model" / "training_history.json"
    
    metrics_data = {}
    history_data = {}
    
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)
            
    if history_path.exists():
        with open(history_path, "r") as f:
            history_data = json.load(f)
            
    return {
        "model_architecture": "DeepLearnX Multi-Branch Cognitive Neural Network (Bi-GRU + Cognitive ANN + Multi-Task Heads)",
        "framework": "PyTorch 2.9.0",
        "evaluation_metrics": metrics_data,
        "training_history": history_data
    }

@app.get("/api/model/confusion-matrix-img")
def get_confusion_matrix_image():
    img_path = PROJECT_ROOT / "model" / "confusion_matrix.png"
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Confusion matrix image not found")
    return FileResponse(img_path, media_type="image/png")

@app.get("/api/health")
def healthcheck():
    """Production health check verifying database and neural engine readiness."""
    status = {"status": "healthy", "service": "DeepLearnX", "version": "4.2.0"}
    
    # Check SQLite database
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
        
    # Check PyTorch model checkpoint
    model_path = PROJECT_ROOT / "model" / "deeplearnx_cognitive_model.pt"
    status["model_checkpoint"] = "ready" if model_path.exists() else "not_trained"
    
    return status

# ----------------- SERVE FRONTEND STATIC FILES -----------------

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", NoCacheStaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(
            str(index_file),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "DeepLearnX Backend Running. Frontend is being loaded."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8055, reload=True)
