"""
Version information for Artanis framework.

This module provides the single source of truth for version information,
following PEP 396 and setuptools best practices.
"""

from __future__ import annotations

# Version information
__version__ = "0.1.3"

# Version components for programmatic access
VERSION: tuple[int, int, int] = (0, 1, 3)

# Version info tuple (similar to sys.version_info)
version_info = VERSION


def get_version() -> str:
    """
    Get the current version string.

    Returns:
        str: The version string in format 'major.minor.patch'

    Example:
        >>> from artanis._version import get_version
        >>> get_version()
        '0.1.2'
    """
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """
    Get version information as a tuple of integers.

    Returns:
        Tuple[int, int, int]: Version components as (major, minor, patch)

    Example:
        >>> from artanis._version import get_version_info
        >>> get_version_info()
        (0, 1, 2)
    """
    return VERSION
