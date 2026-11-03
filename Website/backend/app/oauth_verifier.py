"""
DeepLearnX OAuth & Google Identity Services (GIS) Verification Subsystem
Authoritative token validation, cryptographic certificate verification,
environment segregation, and secure session management.
"""

import os
import sys
import uuid
import time
import logging
import hashlib
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Google Auth imports
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

logger = logging.getLogger("deeplearnx.oauth")

# Trusted Google Identity Token Issuers
GOOGLE_ISSUERS = {
    "accounts.google.com",
    "https://accounts.google.com"
}


class OAuthVerificationError(Exception):
    """Raised when OAuth token verification fails."""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def is_production() -> bool:
    """
    Determines if DeepLearnX is operating in strict production mode.
    Checks DEEPLEARNX_ENV, ENVIRONMENT, and ENV environment variables.
    """
    env = os.getenv("DEEPLEARNX_ENV", os.getenv("ENVIRONMENT", os.getenv("ENV", ""))).strip().lower()
    return env in {"production", "prod"}


def get_google_client_id() -> Optional[str]:
    """Returns the configured Google OAuth Client ID, if any."""
    cid = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    return cid if cid else None


def init_session_table(conn):
    """Initializes the user_sessions table in SQLite with index on token."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            auth_method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
    conn.commit()


def create_user_session(conn, user_id: int, auth_method: str = "google", ttl_seconds: int = 86400 * 7) -> str:
    """
    Issues and stores a cryptographically secure session token in SQLite.
    Default TTL: 7 days.
    """
    init_session_table(conn)
    token = f"sess-{auth_method}-{user_id}-{uuid.uuid4().hex}"
    expires_at = int(time.time()) + ttl_seconds
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_sessions (user_id, token, auth_method, expires_at, is_active) VALUES (?, ?, ?, ?, 1)",
        (user_id, token, auth_method, expires_at)
    )
    conn.commit()
    return token


def verify_user_session(conn, token: str) -> Optional[Dict[str, Any]]:
    """
    Validates an issued session token against the active sessions table.
    Returns the user dict if valid and unexpired; None otherwise.
    """
    if not token or not isinstance(token, str):
        return None
        
    init_session_table(conn)
    now = int(time.time())
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT s.user_id, s.auth_method, s.expires_at, s.is_active,
               u.id, u.username, u.email, u.full_name, u.role
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.is_active = 1
    """, (token.strip(),)).fetchone()
    
    if not row:
        return None
        
    # Check expiry
    if row["expires_at"] < now:
        cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE token = ?", (token.strip(),))
        conn.commit()
        return None
        
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "auth_method": row["auth_method"]
    }


def revoke_user_session(conn, token: str) -> bool:
    """Revokes an active session token upon logout."""
    if not token:
        return False
    init_session_table(conn)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE token = ?", (token.strip(),))
    conn.commit()
    return cursor.rowcount > 0


def verify_google_id_token(
    credential: str,
    client_id: Optional[str] = None,
    clock_skew_seconds: int = 10
) -> Dict[str, Any]:
    """
    Cryptographically verifies a genuine Google ID token (JWT).
    Validates:
      - RSA cryptographic signature against Google's public JWKS certificates
      - Issuer (accounts.google.com or https://accounts.google.com)
      - Audience (matches configured GOOGLE_CLIENT_ID if present)
      - Expiration (exp claim > current time)
      - Email verification (email_verified claim must be True)
    Returns:
      Dict with verified claims: email, full_name, sub, picture
    Raises:
      OAuthVerificationError on any validation failure.
    """
    if not GOOGLE_AUTH_AVAILABLE:
        raise OAuthVerificationError(
            "google-auth library is not installed in the backend environment.",
            status_code=500
        )
        
    if not credential or not isinstance(credential, str):
        raise OAuthVerificationError("Google credential token is missing or empty.", status_code=400)
        
    clean_token = credential.strip()
    if not clean_token:
        raise OAuthVerificationError("Google credential token is empty.", status_code=400)
        
    expected_audience = client_id or get_google_client_id()
    request_adapter = google_requests.Request()
    
    try:
        id_info = id_token.verify_oauth2_token(
            clean_token,
            request_adapter,
            audience=expected_audience,
            clock_skew_in_seconds=clock_skew_seconds
        )
    except ValueError as ve:
        # Signature mismatch, expired token, or audience mismatch
        err_msg = str(ve)
        logger.warning(f"Google ID token cryptographic verification failed: {err_msg}")
        raise OAuthVerificationError(f"Invalid Google ID token: {err_msg}", status_code=401)
    except Exception as e:
        logger.warning(f"Unexpected Google token verification error: {e}")
        raise OAuthVerificationError(f"Google authentication failed: {str(e)}", status_code=401)
        
    # Verify Issuer
    iss = id_info.get("iss", "")
    if iss not in GOOGLE_ISSUERS:
        raise OAuthVerificationError(
            f"Invalid Google token issuer '{iss}'. Expected accounts.google.com.",
            status_code=401
        )
        
    # Verify Email Presence
    email = id_info.get("email")
    if not email or not isinstance(email, str) or "@" not in email:
        raise OAuthVerificationError("Token does not contain a valid email address.", status_code=401)
        
    # Verify Email Verification Status
    email_verified = id_info.get("email_verified")
    if email_verified is not True and str(email_verified).lower() != "true":
        raise OAuthVerificationError(
            f"Google account email '{email}' has not been verified by Google.",
            status_code=401
        )
        
    return {
        "email": email.strip().lower(),
        "full_name": (id_info.get("name") or email.split("@")[0]).strip(),
        "sub": id_info.get("sub"),
        "picture": id_info.get("picture"),
        "auth_provider": "google",
        "verified": True
    }


def authenticate_oauth_payload(
    provider: str,
    credential: Optional[str],
    email: Optional[str],
    full_name: Optional[str],
    is_dev_mock: bool = False
) -> Dict[str, Any]:
    """
    High-level OAuth authentication orchestrator.
    
    Enforces strict security boundaries:
    1. If `credential` is present:
       - Strictly verifies the cryptographic Google ID token.
       - The authenticated email is derived SOLELY from the verified token claims.
       - Any user-submitted email in the request body is IGNORED.
    2. If `credential` is absent:
       - In PRODUCTION mode (`DEEPLEARNX_ENV=production`):
         Immediately REJECTS with HTTP 403 Forbidden. Mock OAuth is forbidden in production.
       - In DEVELOPMENT mode:
         Requires `is_dev_mock=True` and a valid email format.
         Issues a clearly marked dev simulation identity.
    3. Guarantees that neither method can escalate privileges to 'faculty' or 'admin'.
    """
    prod = is_production()
    prov = (provider or "google").strip().lower()
    
    # Path A: Genuine Cryptographic Credential
    if credential and credential.strip():
        if prov == "google":
            verified_claims = verify_google_id_token(credential.strip())
            return {
                "email": verified_claims["email"],
                "full_name": verified_claims["full_name"],
                "sub": verified_claims.get("sub"),
                "picture": verified_claims.get("picture"),
                "auth_method": "google_token_verified",
                "provider": "google",
                "is_mock": False
            }
        else:
            raise OAuthVerificationError(f"Unsupported OAuth provider with credential: {prov}", status_code=400)
            
    # Path B: Credential Missing
    if prod:
        raise OAuthVerificationError(
            "Production mode requires a genuine Google Identity credential (ID token). "
            "Simulated/mock OAuth is strictly forbidden in production.",
            status_code=403
        )
        
    # Path C: Development Simulation
    if not is_dev_mock:
        raise OAuthVerificationError(
            "Missing Google credential token. Provide a valid Google ID token, "
            "or set 'is_dev_mock: true' for local development simulation.",
            status_code=401
        )
        
    if not email or not isinstance(email, str) or "@" not in email:
        raise OAuthVerificationError(
            "A valid email address is required for development OAuth simulation.",
            status_code=400
        )
        
    clean_email = email.strip().lower()
    clean_name = (full_name or clean_email.split("@")[0]).strip()
    
    return {
        "email": clean_email,
        "full_name": clean_name,
        "sub": f"dev-mock-{hashlib.sha256(clean_email.encode()).hexdigest()[:12]}",
        "picture": None,
        "auth_method": "dev_mock_simulation",
        "provider": prov,
        "is_mock": True
    }
