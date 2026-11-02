"""
DeepLearnX Server-Issued Assessment Attempt Security Manager.
Provides cryptographically signed attempt tokens, replay protection, and time-bounded validity.
"""

import os
import time
import json
import uuid
import hmac
import hashlib
import base64
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Server-side signing secret (never exposed to client)
SECRET_KEY = os.environ.get("DEEPLEARNX_SECRET_KEY") or os.environ.get("SECRET_KEY") or "deeplearnx_cognitive_assessment_secret_v2"
if isinstance(SECRET_KEY, str):
    SECRET_KEY_BYTES = SECRET_KEY.encode("utf-8")
else:
    SECRET_KEY_BYTES = bytes(SECRET_KEY)

DEFAULT_EXPIRATION_SECONDS = 7200  # 2 hours


def init_attempt_tables(conn: sqlite3.Connection) -> None:
    """Ensures assessment_attempts table exists non-destructively."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_attempts (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            domain_id TEXT NOT NULL,
            question_ids TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'issued',
            issued_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            submitted_at REAL,
            session_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user_status ON assessment_attempts(user_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_domain ON assessment_attempts(domain_id)")
    conn.commit()


def _sign_payload(payload_bytes: bytes) -> str:
    """Computes URL-safe HMAC-SHA256 signature."""
    sig = hmac.new(SECRET_KEY_BYTES, payload_bytes, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")


def create_assessment_attempt(
    conn: sqlite3.Connection,
    user_id: int,
    domain_id: str,
    question_ids: List[str],
    expires_in_seconds: int = DEFAULT_EXPIRATION_SECONDS
) -> Dict[str, Any]:
    """
    Creates a server-issued, cryptographically signed attempt token and persists attempt state.
    """
    init_attempt_tables(conn)
    attempt_id = f"att_{uuid.uuid4().hex}"
    now = time.time()
    expires_at = now + expires_in_seconds

    # Save to SQLite
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_attempts (id, user_id, domain_id, question_ids, status, issued_at, expires_at)
        VALUES (?, ?, ?, ?, 'issued', ?, ?)
    """, (attempt_id, user_id, domain_id, json.dumps(question_ids), now, expires_at))
    conn.commit()

    # Construct cryptographic token
    claims = {
        "att_id": attempt_id,
        "uid": user_id,
        "dom": domain_id,
        "q_count": len(question_ids),
        "iat": int(now),
        "exp": int(expires_at)
    }
    payload_json = json.dumps(claims, separators=(",", ":"), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("ascii").rstrip("=")
    signature = _sign_payload(payload_b64.encode("ascii"))
    token = f"{payload_b64}.{signature}"

    return {
        "attempt_id": attempt_id,
        "attempt_token": token,
        "user_id": user_id,
        "domain_id": domain_id,
        "question_count": len(question_ids),
        "issued_at": now,
        "expires_at": expires_at
    }


def verify_assessment_attempt(
    conn: sqlite3.Connection,
    token: str,
    user_id: int,
    domain_id: str,
    submitted_question_ids: Optional[List[str]] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Cryptographically verifies the attempt token and confirms its database state:
    1. Signature verification
    2. Expiration check
    3. User and domain match
    4. Replay attack check (must still be in 'issued' status)
    5. Question containment check
    """
    init_attempt_tables(conn)
    if not token or "." not in token:
        return False, "Malformed attempt token format", None

    parts = token.split(".")
    if len(parts) != 2:
        return False, "Invalid token structure", None

    payload_b64, signature = parts
    expected_sig = _sign_payload(payload_b64.encode("ascii"))
    if not hmac.compare_digest(signature, expected_sig):
        return False, "Cryptographic signature verification failed", None

    # Decode claims
    try:
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    except Exception as e:
        return False, f"Failed to decode token claims: {str(e)}", None

    now = time.time()
    if claims.get("exp", 0) < now:
        return False, f"Attempt token expired at {claims.get('exp')}, current time is {int(now)}", None

    if claims.get("uid") != user_id:
        return False, f"Token user_id ({claims.get('uid')}) does not match submission ({user_id})", None

    if claims.get("dom") != domain_id:
        return False, f"Token domain_id ({claims.get('dom')}) does not match submission ({domain_id})", None

    attempt_id = claims.get("att_id")
    if not attempt_id:
        return False, "Missing attempt ID in token claims", None

    # Check database state for replay protection
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT id, user_id, domain_id, question_ids, status, issued_at, expires_at, submitted_at, session_id
        FROM assessment_attempts
        WHERE id = ?
    """, (attempt_id,)).fetchone()

    if not row:
        return False, f"Attempt '{attempt_id}' not found in server registry", None

    if row["status"] == "submitted":
        return False, f"Assessment attempt '{attempt_id}' has already been submitted and graded (replay rejected)", None

    if row["status"] != "issued":
        return False, f"Assessment attempt '{attempt_id}' is in invalid status '{row['status']}'", None

    if submitted_question_ids is not None:
        try:
            allowed_qids = set(json.loads(row["question_ids"]))
            submitted_set = set(submitted_question_ids)
            # Ensure submitted questions belong to this issued attempt
            diff = submitted_set - allowed_qids
            if diff:
                return False, f"Submission contains questions not issued in this attempt: {list(diff)}", None
        except Exception:
            pass

    return True, "Valid attempt", {
        "attempt_id": attempt_id,
        "claims": claims,
        "row": dict(row)
    }


def mark_attempt_submitted(
    conn: sqlite3.Connection,
    attempt_id: str,
    session_id: str
) -> None:
    """Marks an attempt as submitted to prevent replay attacks."""
    now = time.time()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assessment_attempts
        SET status = 'submitted', submitted_at = ?, session_id = ?
        WHERE id = ?
    """, (now, session_id, attempt_id))
    conn.commit()
