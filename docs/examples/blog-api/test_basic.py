#!/usr/bin/env python3
"""
Basic test for blog-api example without external dependencies.
"""

from __future__ import annotations

import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))  # noqa: PTH118, PTH120

# Setup test logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
test_logger = logging.getLogger("test")


def test_imports() -> bool:
    """Test that all modules can be imported."""
    test_logger.info("Testing imports...")

    try:
        from artanis import App, Router

        test_logger.info("✅ Artanis framework imports successful")
    except ImportError as e:
        test_logger.error(f"❌ Artanis import failed: {e}")
        return False

    try:
        from utils.database import init_database
        from utils.security import hash_password, sanitize_html
        from utils.validation import (
            validate_email,
            validate_password,
            validate_username,
        )

        test_logger.info("✅ Utils imports successful")
    except ImportError as e:
        test_logger.error(f"❌ Utils import failed: {e}")
        return False

    return True


def test_validation() -> None:
    """Test validation functions."""
    test_logger.info("\nTesting validation functions...")

    from utils.validation import validate_email, validate_password, validate_username

    # Test email validation
    assert validate_email("test@example.com")
    assert not validate_email("invalid-email")
    test_logger.info("✅ Email validation works")

    # Test username validation
    assert validate_username("testuser123")
    assert not validate_username("ab")  # too short
    assert not validate_username("test@user")  # invalid chars
    test_logger.info("✅ Username validation works")

    # Test password validation
    assert validate_password("SecurePass123!")
    assert not validate_password("weak")
    test_logger.info("✅ Password validation works")


def test_security() -> None:
    """Test security functions."""
    test_logger.info("\nTesting security functions...")

    from utils.security import hash_password, sanitize_html

    # Test password hashing
    test_password = "testpassword123"  # noqa: S105
    password = test_password
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    test_logger.info("✅ Password hashing works")

    # Test HTML sanitization
    html = "<p>Safe content</p><script>alert('xss')</script>"
    sanitized = sanitize_html(html)
    assert "<script>" not in sanitized
    test_logger.info("✅ HTML sanitization works")


def test_app_creation() -> None:
    """Test basic app creation without external deps."""
    test_logger.info("\nTesting app creation...")

    from artanis import App, Router

    # Create app
    app = App()
    test_logger.info("✅ App creation successful")

    # Create router
    router = Router()
    test_logger.info("✅ Router creation successful")

    # Test basic route registration
    async def test_handler() -> dict[str, str]:
        return {"message": "test"}

    app.get("/test", test_handler)
    router.get("/router-test", test_handler)
    test_logger.info("✅ Route registration successful")


if __name__ == "__main__":
    test_logger.info("🧪 Running Blog API Basic Tests")
    test_logger.info("=" * 50)

    success = True

    if not test_imports():
        success = False

    try:
        test_validation()
        test_security()
        test_app_creation()
    except Exception as e:
        test_logger.error(f"❌ Test failed: {e}")
        success = False

    test_logger.info("\n%s", "=" * 50)
    if success:
        test_logger.info("🎉 All basic tests passed!")
        test_logger.info("\n📝 Next steps:")
        test_logger.info("1. Install dependencies: pip install -r requirements.txt")
        test_logger.info("2. Install artanis: pip install -e ../../../")
        test_logger.info("3. Run server: python app.py")
    else:
        test_logger.error("❌ Some tests failed!")

    sys.exit(0 if success else 1)
