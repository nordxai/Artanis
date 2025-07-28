"""
Security utilities for the blog API.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

import jwt

# Secret key for JWT (in production, use environment variable)
DEFAULT_DEV_SECRET = "dev-secret-change-in-production"  # noqa: S105
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_DEV_SECRET)
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt (simplified for demo)."""
    # In production, use bcrypt or similar
    salt = "artanis_blog_salt"  # Use random salt per user in production
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def generate_jwt_token(payload: dict[str, Any]) -> str:
    """Generate JWT token."""
    return str(jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM))


def decode_jwt_token(token: str) -> dict[str, Any]:
    """Decode JWT token."""
    result = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return dict(result) if result else {}


def sanitize_html(content: str) -> str:
    """Basic HTML sanitization (simplified for demo)."""
    # In production, use a proper HTML sanitizer like bleach

    # Remove script tags
    content = re.sub(
        r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove dangerous attributes
    # In production, implement proper HTML sanitization with allowlist:
    # allowed_tags = ["p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li",
    #                 "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "code", "pre", "a", "img"]

    # Simple tag filtering (in production, use a proper HTML sanitizer)
    return re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', "", content, flags=re.IGNORECASE)


def generate_secure_filename(filename: str) -> str:
    """Generate secure filename."""
    # Remove path components
    file_path = Path(filename)
    filename = file_path.name

    # Replace unsafe characters
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Limit length
    file_path = Path(filename)
    name = file_path.stem
    ext = file_path.suffix
    if len(name) > 50:
        name = name[:50]

    return name + ext
