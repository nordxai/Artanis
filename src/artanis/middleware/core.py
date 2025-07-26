"""Core middleware management for the Artanis framework.

Provides the MiddlewareManager class for registering and organizing
global and path-based middleware with pattern matching capabilities.
"""

from __future__ import annotations

import re
from typing import Callable, Pattern


class MiddlewareManager:
    """Manages global and path-based middleware registration and retrieval.

    Provides functionality to register middleware that runs globally on all
    routes or only on specific path patterns. Supports Express.js-style
    path matching with parameter extraction capabilities.

    Attributes:
        global_middleware: List of middleware functions that run on all routes
        path_middleware: Dictionary mapping path patterns to middleware lists

    Example:
        ```python
        manager = MiddlewareManager()

        # Add global middleware
        manager.add_global(cors_middleware)

        # Add path-specific middleware
        manager.add_path('/api', auth_middleware)
        manager.add_path('/admin/{id}', admin_middleware)
        ```
    """

    def __init__(self) -> None:
        self.global_middleware: list[Callable] = []
        self.path_middleware: dict[str, list[Callable]] = {}

    def add_global(self, middleware_func: Callable) -> None:
        """Add global middleware that runs on all routes.

        Global middleware is executed for every request regardless of the
        request path. It's added to the beginning of the middleware chain.

        Args:
            middleware_func: Middleware function to add globally
        """
        self.global_middleware.append(middleware_func)

    def add_path(self, path: str, middleware_func: Callable) -> None:
        """Add path-based middleware that runs on specific routes.

        Path-based middleware only executes when the request path matches
        the specified pattern. Supports parameter patterns like '/users/{id}'.

        Args:
            path: Path pattern to match (supports parameter syntax)
            middleware_func: Middleware function to add for this path
        """
        if path not in self.path_middleware:
            self.path_middleware[path] = []
        self.path_middleware[path].append(middleware_func)

    def find_matching_middleware(self, request_path: str) -> list[Callable]:
        """Find all path middleware that match the request path.

        Iterates through all registered path patterns and returns middleware
        functions for patterns that match the given request path.

        Args:
            request_path: The request path to match against patterns

        Returns:
            List of middleware functions that match the path
        """
        matching_middleware = []

        for pattern, middleware_list in self.path_middleware.items():
            if self._path_matches(pattern, request_path):
                matching_middleware.extend(middleware_list)

        return matching_middleware

    def _path_matches(self, pattern: str, request_path: str) -> bool:
        """Check if a path pattern matches the request path.

        Args:
            pattern: Path pattern with optional parameters
            request_path: Actual request path to check

        Returns:
            True if the pattern matches the request path, False otherwise
        """
        # Convert path pattern to regex
        regex_pattern = self._compile_path_pattern(pattern)
        return bool(regex_pattern.match(request_path))

    def _compile_path_pattern(self, path: str) -> Pattern[str]:
        """Compile path pattern to regex, handling parameters like {id}.

        Converts path patterns with parameters into regular expressions
        that can match request paths. Supports nested path matching.

        Args:
            path: Path pattern with optional parameters (e.g., '/users/{id}')

        Returns:
            Compiled regular expression pattern

        Example:
            '/users/{id}' becomes regex that matches '/users/123', '/users/abc', etc.
        """
        # Escape special regex characters except for our parameter syntax
        pattern = re.escape(path)

        # Replace escaped parameter syntax with regex groups
        # \{param\} becomes (?P<param>[^/]+)
        pattern = pattern.replace(r"\{", "(?P<").replace(r"\}", r">[^/]+)")

        # Handle nested paths - /api should match /api/users
        pattern = f"^{pattern}(?:/.*)?$" if not pattern.endswith("$") else f"^{pattern}"

        return re.compile(pattern)

    def get_all_middleware_for_path(self, request_path: str) -> list[Callable]:
        """Get combined global and path middleware for a specific path.

        Returns middleware in execution order: global middleware first,
        then path-specific middleware.

        Args:
            request_path: The request path to get middleware for

        Returns:
            Combined list of all applicable middleware functions
        """
        path_middleware = self.find_matching_middleware(request_path)
        return self.global_middleware + path_middleware

    def clear(self) -> None:
        """Clear all middleware (useful for testing).

        Removes all registered global and path-based middleware.
        Primarily used in test environments to ensure clean state.
        """
        self.global_middleware.clear()
        self.path_middleware.clear()

    def middleware_count(self) -> dict[str, int]:
        """Get count of middleware for debugging.

        Provides statistics about registered middleware for debugging
        and monitoring purposes.

        Returns:
            Dictionary with counts for 'global', 'path', and 'total' middleware
        """
        path_count = sum(
            len(middleware_list) for middleware_list in self.path_middleware.values()
        )
        return {
            "global": len(self.global_middleware),
            "path": path_count,
            "total": len(self.global_middleware) + path_count,
        }
