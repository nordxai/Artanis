"""
Validation utilities for the blog API.
"""

from __future__ import annotations

import re
from typing import Any


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format."""
    if not username or len(username) < 3 or len(username) > 30:
        return False
    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, username))


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special


def validate_post_data(data: dict[str, Any]) -> dict[str, Any]:
    """Validate post data."""
    from artanis.exceptions import ValidationError

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    summary = data.get("summary", "").strip()
    category = data.get("category", "General")
    tags = data.get("tags", [])
    status = data.get("status", "draft")

    if not title:
        msg = "Title is required"
        raise ValidationError(msg, field="title")

    if len(title) > 200:
        msg = "Title must be less than 200 characters"
        raise ValidationError(msg, field="title")

    if not content:
        msg = "Content is required"
        raise ValidationError(msg, field="content")

    if len(content) > 50000:
        msg = "Content must be less than 50,000 characters"
        raise ValidationError(msg, field="content")

    if summary and len(summary) > 500:
        msg = "Summary must be less than 500 characters"
        raise ValidationError(msg, field="summary")

    categories = [
        "Technology",
        "Lifestyle",
        "Travel",
        "Food",
        "Health",
        "Business",
        "Announcements",
        "General",
    ]
    if category not in categories:
        categories_str = ", ".join(categories)
        msg = f"Category must be one of: {categories_str}"
        raise ValidationError(msg, field="category")

    if not isinstance(tags, list):
        msg = "Tags must be an array"
        raise ValidationError(msg, field="tags")

    if len(tags) > 10:
        msg = "Maximum 10 tags allowed"
        raise ValidationError(msg, field="tags")

    for tag in tags:
        if not isinstance(tag, str) or len(tag.strip()) == 0:
            msg = "Tags must be non-empty strings"
            raise ValidationError(msg, field="tags")
        if len(tag) > 30:
            msg = "Each tag must be less than 30 characters"
            raise ValidationError(msg, field="tags")

    if status not in ["draft", "published"]:
        msg = "Status must be 'draft' or 'published'"
        raise ValidationError(msg, field="status")

    return {
        "title": title,
        "content": content,
        "summary": summary,
        "category": category,
        "tags": [tag.strip() for tag in tags if tag.strip()],
        "status": status,
    }


def validate_file_upload(
    file: Any,
    allowed_extensions: list[str] | None = None,
    max_size: int = 5 * 1024 * 1024,
) -> None:
    """Validate file upload."""
    from artanis.exceptions import ValidationError

    if not file:
        msg = "No file provided"
        raise ValidationError(msg)

    # Check file size
    if hasattr(file, "size") and file.size > max_size:
        size_mb = max_size // (1024 * 1024)
        msg = f"File size must be less than {size_mb}MB"
        raise ValidationError(msg)

    # Check file extension
    if allowed_extensions:
        filename = getattr(file, "filename", "")
        if not filename:
            msg = "Invalid filename"
            raise ValidationError(msg)

        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in allowed_extensions:
            extensions_str = ", ".join(allowed_extensions)
            msg = f"File type must be one of: {extensions_str}"
            raise ValidationError(msg)

    # Validation passed - no return needed for None function
