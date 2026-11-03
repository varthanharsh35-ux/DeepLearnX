"""
DeepLearnX Secure Google OAuth, GIS Verification & Session Security Test Suite
Validates:
1. Genuine Google ID token verification (signature, issuer, audience, exp, email_verified).
2. Rejection of forged, expired, malformed, and unverified credentials.
3. Strict production environment segregation (mock OAuth rejected with 403 in production).
4. Anti-impersonation (token email authoritative over body email).
5. Privilege escalation immunity (OAuth cannot grant faculty/admin roles).
6. Server-tracked session issuance, persistence verification, and revocation on logout.
7. Protected faculty route access control (students rejected with 403).
8. Regression compatibility for existing username/password and demo logins.
"""

import os
import sys
import time
import json
import base64
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db_connection
from backend.app.oauth_verifier import (
    verify_google_id_token,
    authenticate_oauth_payload,
    OAuthVerificationError,
    create_user_session,
    verify_user_session,
    revoke_user_session
)

client = TestClient(app)

# Helper to build a syntactically valid JWT
def create_dummy_jwt(payload: dict) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(b"test_cryptographic_signature_mock").decode().rstrip("=")
    return f"{header}.{body}.{sig}"


# ----------------- 1. GENUINE GOOGLE ID TOKEN VERIFICATION -----------------

def test_genuine_google_token_verification_success():
    """Valid Google ID token returns authoritative verified email and claims."""
    fake_token = create_dummy_jwt({
        "iss": "https://accounts.google.com",
        "email": "verified.student@gmail.com",
        "email_verified": True,
        "name": "Verified Student",
        "sub": "google-sub-12345",
        "exp": int(time.time()) + 3600
    })

    verified_claims = {
        "iss": "https://accounts.google.com",
        "email": "verified.student@gmail.com",
        "email_verified": True,
        "name": "Verified Student",
        "sub": "google-sub-12345",
        "picture": "https://lh3.googleusercontent.com/photo.jpg"
    }

    with patch("backend.app.oauth_verifier.id_token.verify_oauth2_token", return_value=verified_claims):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "credential": fake_token,
            # Even if attacker supplies an impersonated email in the body, it must be ignored!
            "email": "impersonated.victim@school.edu",
            "full_name": "Impersonator"
        })
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["status"] == "success"
        assert data["auth_method"] == "google_token_verified"
        assert data["is_mock"] is False
        # MUST match the cryptographically verified token email, NOT the body email!
        assert data["user"]["email"] == "verified.student@gmail.com"
        assert data["user"]["role"] == "student"
        assert "token" in data and data["token"].startswith("sess-")


def test_forged_google_token_signature_rejection():
    """Forged Google tokens with invalid signatures are rejected with HTTP 401."""
    forged_token = create_dummy_jwt({
        "iss": "https://accounts.google.com",
        "email": "hacker@evil.com",
        "email_verified": True,
        "exp": int(time.time()) + 3600
    })

    with patch("backend.app.oauth_verifier.id_token.verify_oauth2_token", side_effect=ValueError("Could not verify token signature")):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "credential": forged_token
        })
        assert res.status_code == 401
        assert "Invalid Google ID token" in res.json()["detail"]


def test_expired_google_token_rejection():
    """Expired Google tokens are rejected with HTTP 401."""
    expired_token = create_dummy_jwt({
        "iss": "https://accounts.google.com",
        "email": "student@gmail.com",
        "exp": int(time.time()) - 3600
    })

    with patch("backend.app.oauth_verifier.id_token.verify_oauth2_token", side_effect=ValueError("Token used too late")):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "credential": expired_token
        })
        assert res.status_code == 401
        assert "Invalid Google ID token" in res.json()["detail"]


def test_unverified_email_google_token_rejection():
    """Google tokens where email_verified is False are rejected with HTTP 401."""
    token = create_dummy_jwt({
        "iss": "https://accounts.google.com",
        "email": "unverified@gmail.com",
        "email_verified": False,
        "exp": int(time.time()) + 3600
    })

    unverified_claims = {
        "iss": "https://accounts.google.com",
        "email": "unverified@gmail.com",
        "email_verified": False,
        "sub": "unverified-sub"
    }

    with patch("backend.app.oauth_verifier.id_token.verify_oauth2_token", return_value=unverified_claims):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "credential": token
        })
        assert res.status_code == 401
        assert "not been verified" in res.json()["detail"]


def test_invalid_issuer_google_token_rejection():
    """Google tokens with untrusted issuer are rejected with HTTP 401."""
    token = create_dummy_jwt({
        "iss": "https://rogue-auth.attacker.com",
        "email": "user@gmail.com",
        "email_verified": True
    })

    rogue_claims = {
        "iss": "https://rogue-auth.attacker.com",
        "email": "user@gmail.com",
        "email_verified": True
    }

    with patch("backend.app.oauth_verifier.id_token.verify_oauth2_token", return_value=rogue_claims):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "credential": token
        })
        assert res.status_code == 401
        assert "Invalid Google token issuer" in res.json()["detail"]


# ----------------- 2. PRODUCTION VS DEVELOPMENT MODE SEGREGATION -----------------

def test_production_mode_rejects_mock_oauth():
    """In production mode, mock OAuth without genuine credential is strictly rejected with 403."""
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "production"}):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "dev.test@gmail.com",
            "full_name": "Dev Tester",
            "is_dev_mock": True
        })
        assert res.status_code == 403
        assert "forbidden in production" in res.json()["detail"].lower()


def test_development_mode_allows_explicit_dev_mock():
    """In development mode, explicit is_dev_mock=True is allowed for local simulation."""
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "development"}):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "local.dev.student@gmail.com",
            "full_name": "Local Dev Student",
            "is_dev_mock": True
        })
        assert res.status_code == 200
        data = res.json()
        assert data["auth_method"] == "dev_mock_simulation"
        assert data["is_mock"] is True
        assert data["user"]["email"] == "local.dev.student@gmail.com"


def test_development_mode_rejects_missing_mock_flag():
    """In development mode, omitted credential and is_dev_mock=False is rejected with 401."""
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "development"}):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "local.dev.student@gmail.com",
            "is_dev_mock": False
        })
        assert res.status_code == 401
        assert "Missing Google credential" in res.json()["detail"]


# ----------------- 3. PRIVILEGE ESCALATION IMMUNITY -----------------

def test_oauth_cannot_escalate_role_to_faculty():
    """OAuth login cannot set user role to faculty or admin."""
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "development"}):
        res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "privilege.attempt@gmail.com",
            "full_name": "Privilege Escalator",
            "is_dev_mock": True,
            # Attacker attempt to inject faculty role
            "role": "faculty"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["role"] == "student"


# ----------------- 4. SESSION TRACKING, VERIFICATION & LOGOUT -----------------

def test_session_lifecycle_persistence_and_revocation():
    """Session token is verified on /api/auth/session and invalidated on /api/auth/logout."""
    # 1. Login to obtain a session
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "development"}):
        login_res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "session.tester@gmail.com",
            "full_name": "Session Tester",
            "is_dev_mock": True
        })
        assert login_res.status_code == 200
        token = login_res.json()["token"]

    # 2. Verify session persistence
    sess_res = client.get(f"/api/auth/session?token={token}")
    assert sess_res.status_code == 200
    sess_data = sess_res.json()
    assert sess_data["status"] == "success"
    assert sess_data["user"]["email"] == "session.tester@gmail.com"

    # 3. Logout and revoke session
    logout_res = client.post("/api/auth/logout", json={"token": token})
    assert logout_res.status_code == 200

    # 4. Subsequent session check must be rejected with 401
    revoked_res = client.get(f"/api/auth/session?token={token}")
    assert revoked_res.status_code == 401
    assert "expired or invalid" in revoked_res.json()["detail"].lower()


# ----------------- 5. PROTECTED FACULTY ROUTE ACCESS CONTROL -----------------

def test_faculty_route_rejects_student_access():
    """Faculty analytics route rejects requests with student role or student session."""
    # Obtain a student session
    with patch.dict(os.environ, {"DEEPLEARNX_ENV": "development"}):
        login_res = client.post("/api/auth/oauth-login", json={
            "provider": "google",
            "email": "student.unauth@gmail.com",
            "full_name": "Student Unauth",
            "is_dev_mock": True
        })
        student_token = login_res.json()["token"]

    # Student session attempting to access faculty dashboard
    res = client.get(f"/api/faculty/dashboard?token={student_token}")
    assert res.status_code == 403
    assert "Faculty or Admin role required" in res.json()["detail"]


# ----------------- 6. REGRESSION: EXISTING USERNAME/PASSWORD LOGIN -----------------

def test_existing_password_login_functional():
    """Verify standard demo user username/password authentication remains 100% operational."""
    res = client.post("/api/auth/login", json={
        "username": "student_b",
        "password": "student123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["username"] == "student_b"
    assert "token" in data
