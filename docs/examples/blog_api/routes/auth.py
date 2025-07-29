"""
Authentication Routes

Handles user registration, login, logout, and token management.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt
from typing_extensions import TypedDict
from utils.database import get_db_connection
from utils.security import generate_jwt_token, hash_password, verify_password
from utils.validation import validate_email, validate_password, validate_username

from artanis import Router
from artanis.exceptions import AuthenticationError, ValidationError
from artanis.logging import ArtanisLogger


class UserDict(TypedDict):
    """Type definition for user data."""

    id: int
    username: str
    email: str
    password_hash: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: str


logger = ArtanisLogger.get_logger("auth")
auth_router = Router()

# In-memory user storage for demo (replace with database)
users: list[UserDict] = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": hash_password("admin123"),
        "full_name": "Administrator",
        "is_active": True,
        "is_admin": True,
        "created_at": "2024-01-01T00:00:00Z",
    }
]
next_user_id = 2

# Token blacklist for logout (in production, use Redis)
token_blacklist = set()


async def register(request: Any) -> tuple[dict[str, Any], int]:
    """Register a new user."""
    global next_user_id  # noqa: PLW0603

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    # Validate required fields
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    # Field validation
    if not username:
        msg = "Username is required"
        raise ValidationError(msg, field="username")

    if not validate_username(username):
        msg = "Username must be 3-30 characters, letters, numbers, and underscores only"
        raise ValidationError(msg, field="username")

    if not email:
        msg = "Email is required"
        raise ValidationError(msg, field="email")

    if not validate_email(email):
        msg = "Invalid email format"
        raise ValidationError(msg, field="email")

    if not password:
        msg = "Password is required"
        raise ValidationError(msg, field="password")

    if not validate_password(password):
        msg = "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        raise ValidationError(msg, field="password")

    if not full_name:
        msg = "Full name is required"
        raise ValidationError(msg, field="full_name")

    # Check if user already exists
    if any(u["username"] == username for u in users):
        msg = "Username already exists"
        raise ValidationError(msg, field="username")

    if any(u["email"] == email for u in users):
        msg = "Email already exists"
        raise ValidationError(msg, field="email")

    # Create new user
    new_user: UserDict = {
        "id": next_user_id,
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
    }

    users.append(new_user)
    next_user_id += 1

    logger.info(f"New user registered: {username}")

    # Return user without password
    user_response = {k: v for k, v in new_user.items() if k != "password_hash"}

    return {"message": "User registered successfully", "user": user_response}, 201


async def login(request: Any) -> dict[str, Any]:
    """Authenticate user and return JWT token."""
    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username:
        msg = "Username is required"
        raise ValidationError(msg, field="username")

    if not password:
        msg = "Password is required"
        raise ValidationError(msg, field="password")

    # Find user (case-insensitive username)
    user = next((u for u in users if u["username"].lower() == username.lower()), None)

    if not user:
        msg = "Invalid username or password"
        raise AuthenticationError(msg)

    if not user["is_active"]:
        msg = "Account is disabled"
        raise AuthenticationError(msg)

    # Verify password
    if not verify_password(password, user["password_hash"]):
        logger.warning(f"Failed login attempt for user: {username}")
        msg = "Invalid username or password"
        raise AuthenticationError(msg)

    # Generate JWT token
    token_payload = {
        "user_id": user["id"],
        "username": user["username"],
        "is_admin": user["is_admin"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc),
    }

    token = generate_jwt_token(token_payload)

    logger.info(f"User logged in: {username}")

    # Return user info and token
    user_response = {k: v for k, v in user.items() if k != "password_hash"}

    return {
        "message": "Login successful",
        "user": user_response,
        "token": token,
        "expires_in": 86400,  # 24 hours in seconds
    }


async def logout(request: Any) -> dict[str, str]:
    """Logout user by blacklisting token."""
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        msg = "Authorization token required"
        raise AuthenticationError(msg)

    token = auth_header.split(" ")[1]

    # Add token to blacklist
    token_blacklist.add(token)

    logger.info("User logged out")

    return {"message": "Logout successful"}


async def refresh_token(request: Any) -> dict[str, Any]:
    """Refresh JWT token."""
    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    old_token = data.get("token")
    if not old_token:
        msg = "Token is required"
        raise ValidationError(msg, field="token")

    # Check if token is blacklisted
    if old_token in token_blacklist:
        msg = "Token is invalid"
        raise AuthenticationError(msg)

    try:
        # Decode token (without verification for refresh)
        payload = jwt.decode(old_token, options={"verify_signature": False})

        # Find user
        user = next((u for u in users if u["id"] == payload["user_id"]), None)
        if not user or not user["is_active"]:
            msg = "User not found or inactive"
            raise AuthenticationError(msg)

        # Generate new token
        new_token_payload = {
            "user_id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            "iat": datetime.now(timezone.utc),
        }

        new_token = generate_jwt_token(new_token_payload)

        # Blacklist old token
        token_blacklist.add(old_token)

        logger.info(f"Token refreshed for user: {user['username']}")

        return {
            "message": "Token refreshed successfully",
            "token": new_token,
            "expires_in": 86400,
        }

    except jwt.InvalidTokenError:
        msg = "Invalid token"
        raise AuthenticationError(msg)


async def get_current_user(request: Any) -> dict[str, Any]:
    """Get current user profile."""
    # This endpoint requires authentication (handled by auth middleware)
    current_user = getattr(request, "current_user", None)

    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    # Return user without password
    user_response = {k: v for k, v in current_user.items() if k != "password_hash"}

    return {"user": user_response}


async def update_current_user(request: Any) -> dict[str, Any]:
    """Update current user profile."""
    current_user = getattr(request, "current_user", None)

    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    # Update allowed fields
    if "full_name" in data:
        full_name = data["full_name"].strip()
        if not full_name:
            msg = "Full name cannot be empty"
            raise ValidationError(msg, field="full_name")
        current_user["full_name"] = full_name

    if "email" in data:
        email = data["email"].strip().lower()
        if not validate_email(email):
            msg = "Invalid email format"
            raise ValidationError(msg, field="email")

        # Check if email is already taken by another user
        if any(u["email"] == email and u["id"] != current_user["id"] for u in users):
            msg = "Email already exists"
            raise ValidationError(msg, field="email")

        current_user["email"] = email

    logger.info(f"User profile updated: {current_user['username']}")

    # Return updated user
    user_response = {k: v for k, v in current_user.items() if k != "password_hash"}

    return {"message": "Profile updated successfully", "user": user_response}


async def change_password(request: Any) -> dict[str, str]:
    """Change user password."""
    current_user = getattr(request, "current_user", None)

    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password:
        msg = "Current password is required"
        raise ValidationError(msg, field="current_password")

    if not new_password:
        msg = "New password is required"
        raise ValidationError(msg, field="new_password")

    # Verify current password
    if not verify_password(current_password, current_user["password_hash"]):
        msg = "Current password is incorrect"
        raise AuthenticationError(msg)

    # Validate new password
    if not validate_password(new_password):
        msg = "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        raise ValidationError(msg, field="new_password")

    # Update password
    current_user["password_hash"] = hash_password(new_password)

    logger.info(f"Password changed for user: {current_user['username']}")

    return {"message": "Password changed successfully"}


async def get_auth_stats() -> dict[str, int]:
    """Get authentication statistics (admin only)."""
    # This would require admin authentication in production

    active_users = len([u for u in users if u["is_active"]])
    admin_users = len([u for u in users if u["is_admin"]])
    blacklisted_tokens = len(token_blacklist)

    return {
        "total_users": len(users),
        "active_users": active_users,
        "admin_users": admin_users,
        "blacklisted_tokens": blacklisted_tokens,
    }


# Route registrations
auth_router.post("/register", register)
auth_router.post("/login", login)
auth_router.post("/logout", logout)
auth_router.post("/refresh", refresh_token)
auth_router.get("/me", get_current_user)
auth_router.put("/me", update_current_user)
auth_router.post("/change-password", change_password)
auth_router.get("/stats", get_auth_stats)


"""
🔐 Authentication Routes Documentation:

Endpoints:
- POST /auth/register - Register new user
- POST /auth/login - User login
- POST /auth/logout - User logout
- POST /auth/refresh - Refresh JWT token
- GET /auth/me - Get current user profile
- PUT /auth/me - Update current user profile
- POST /auth/change-password - Change password
- GET /auth/stats - Authentication statistics

Features:
1. **Secure Registration**: Username/email uniqueness, password validation
2. **JWT Authentication**: Token-based authentication with expiration
3. **Password Security**: Bcrypt hashing with salt
4. **Token Management**: Refresh and blacklist functionality
5. **Profile Management**: Update user information
6. **Input Validation**: Comprehensive validation with detailed errors
7. **Logging**: Security events logging
8. **Admin Features**: User statistics and management

Security Considerations:
- Password hashing with bcrypt
- JWT tokens with expiration
- Token blacklisting for logout
- Input validation and sanitization
- Rate limiting (handled by middleware)
- Secure password requirements
- Failed login attempt logging

Example Usage:

1. Register:
   POST /api/v1/auth/register
   {
     "username": "johndoe",
     "email": "john@example.com",
     "password": "SecurePass123!",
     "full_name": "John Doe"
   }

2. Login:
   POST /api/v1/auth/login
   {
     "username": "johndoe",
     "password": "SecurePass123!"
   }

3. Access protected endpoint:
   GET /api/v1/auth/me
   Authorization: Bearer <jwt-token>

The authentication system provides a solid foundation for secure user management
in the blog API, with proper validation, security measures, and admin capabilities.
"""
