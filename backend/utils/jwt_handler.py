"""
JWT Token Handler
Handles JWT token generation, verification, and user extraction.
"""

import os
import base64
import json
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key").encode("utf-8")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign_jwt(header: dict, payload: dict) -> str:
    header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    signing_input = f"{_base64url_encode(header_bytes)}.{_base64url_encode(payload_bytes)}".encode("utf-8")
    signature = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
    return _base64url_encode(signature)


def _verify_jwt(token: str) -> Optional[dict]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = _base64url_encode(hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest())

    if not hmac.compare_digest(expected_sig, signature_b64):
        return None

    try:
        payload_json = _base64url_decode(payload_b64)
        payload = json.loads(payload_json)
    except (ValueError, json.JSONDecodeError):
        return None

    exp = payload.get("exp")
    if exp is None or datetime.now(timezone.utc).timestamp() > exp:
        return None

    return payload


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(to_encode, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = _base64url_encode(hmac.new(SECRET_KEY, f"{header_b64}.{payload_b64}".encode("utf-8"), hashlib.sha256).digest())

    return f"{header_b64}.{payload_b64}.{signature}"


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data or None if invalid
    """
    return _verify_jwt(token)


def get_current_user(token: str) -> Optional[dict]:
    """
    Extract user information from JWT token.

    Args:
        token: JWT token

    Returns:
        User data or None if token invalid
    """
    payload = verify_token(token)
    if payload:
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "company": payload.get("company")
        }
    return None


def create_user_token(user_data: dict) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_data: User information dictionary

    Returns:
        JWT token string
    """
    token_data = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "company": user_data.get("company_name", "")
    }

    return create_access_token(token_data)