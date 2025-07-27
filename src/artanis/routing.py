"""Routing module for Artanis framework.

This module provides comprehensive routing functionality including route registration,
path matching, parameter extraction, and subrouting capabilities for better API
organization and modularity.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Pattern

from .exceptions import MethodNotAllowed, RouteNotFound
from .logging import logger


class Route:
    """Represents a single route with its handler and metadata.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: URL path pattern with optional parameters
        handler: Route handler function or coroutine
        middleware: Optional route-specific middleware

    Attributes:
        method: HTTP method
        path: URL path pattern
        handler: Route handler function
        pattern: Compiled regex pattern for path matching
        middleware: Route-specific middleware
    """

    def __init__(
        self,
        method: str,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        self.method = method.upper()
        self.path = path
        self.handler = handler
        self.pattern = self._compile_path_pattern(path)
        self.middleware = middleware or []

    def _compile_path_pattern(self, path: str) -> Pattern[str]:
        """Compile a path pattern into a regular expression.

        Converts path patterns with parameters (e.g., '/users/{id}') into
        regular expressions that can extract parameter values.

        Args:
            path: Path pattern with optional parameters

        Returns:
            Compiled regular expression pattern
        """
        pattern = re.escape(path)
        pattern = pattern.replace(r"\{", "(?P<").replace(r"\}", r">[^/]+)")
        pattern = f"^{pattern}$"
        return re.compile(pattern)

    def match(self, path: str) -> dict[str, str] | None:
        """Check if this route matches the given path.

        Args:
            path: URL path to match against

        Returns:
            Dictionary of extracted path parameters if match, None otherwise
        """
        match = self.pattern.match(path)
        return match.groupdict() if match else None

    def to_dict(self) -> dict[str, Any]:
        """Convert route to dictionary for compatibility.

        Returns:
            Dictionary representation of the route
        """
        return {
            "handler": self.handler,
            "method": self.method,
            "path": self.path,
            "pattern": self.pattern,
        }


class Router:
    """Router class for handling route registration and resolution.

    Provides methods for registering routes with different HTTP methods,
    mounting subrouters, and resolving incoming requests to appropriate handlers.

    Args:
        prefix: Optional path prefix for all routes in this router

    Attributes:
        prefix: Path prefix for this router
        routes: Dictionary of registered routes
        subrouters: Dictionary of mounted subrouters
    """

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self.routes: dict[str, dict[str, Route]] = {}
        self.subrouters: dict[str, Router] = {}
        self.logger = logger

    def register_route(
        self,
        method: str,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a route with the router.

        Args:
            method: HTTP method
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        # Normalize path
        full_path = self._normalize_path(path)

        if full_path not in self.routes:
            self.routes[full_path] = {}

        route = Route(method, full_path, handler, middleware)
        self.routes[full_path][method.upper()] = route

        self.logger.debug(f"Registered {method.upper()} route: {full_path}")

    def _normalize_path(self, path: str) -> str:
        """Normalize path by combining with prefix.

        Args:
            path: Original path pattern

        Returns:
            Normalized path with prefix
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path

        # Combine with prefix
        full_path = self.prefix + path if self.prefix else path

        # Normalize double slashes
        while "//" in full_path:
            full_path = full_path.replace("//", "/")

        return full_path if full_path != "" else "/"

    def get(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a GET route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("GET", path, handler, middleware)

    def post(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a POST route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("POST", path, handler, middleware)

    def put(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a PUT route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("PUT", path, handler, middleware)

    def delete(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a DELETE route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("DELETE", path, handler, middleware)

    def patch(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a PATCH route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("PATCH", path, handler, middleware)

    def options(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register an OPTIONS route.

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware
        """
        self.register_route("OPTIONS", path, handler, middleware)

    def all(
        self,
        path: str,
        handler: Callable[..., Any],
        middleware: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Register a route that responds to all HTTP methods.

        This registers the handler for all standard HTTP methods
        (GET, POST, PUT, DELETE, PATCH, OPTIONS).

        Args:
            path: URL path pattern
            handler: Route handler function
            middleware: Optional route-specific middleware

        Example:
            ```python
            # Middleware that runs for all methods
            def auth_middleware(request, user_id):
                # Authenticate user for any HTTP method
                return {"user_id": user_id, "authenticated": True}

            router.all("/users/{user_id}", auth_middleware)
            ```
        """
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        for method in methods:
            self.register_route(method, path, handler, middleware)

    def mount(self, path: str, router: Router) -> None:
        """Mount a subrouter at the specified path.

        Args:
            path: Path prefix where the subrouter should be mounted
            router: Router instance to mount
        """
        normalized_path = self._normalize_path(path)

        # Update subrouter's prefix
        router.prefix = normalized_path

        # Store subrouter
        self.subrouters[normalized_path] = router

        self.logger.debug(f"Mounted subrouter at: {normalized_path}")

    def find_route(
        self, method: str, path: str
    ) -> tuple[Route | None, dict[str, str], Router | None]:
        """Find a route handler and extract path parameters.

        Args:
            method: HTTP method
            path: Request path

        Returns:
            Tuple of (route, path_parameters, source_router) or (None, {}, None) if not found
        """
        method = method.upper()

        # First, try direct routes in this router
        for methods in self.routes.values():
            if method in methods:
                route = methods[method]
                params = route.match(path)
                if params is not None:
                    return route, params, self

        # Then, try subrouters
        for mount_path, subrouter in self.subrouters.items():
            if "{" in mount_path:
                # Handle parameterized mount paths
                mount_route = Route("GET", mount_path, lambda: None)

                # Try to match the mount pattern against the beginning of the path
                # We need to check if the path can be split into mount + sub parts
                mount_pattern = mount_route.pattern.pattern
                # Remove only the start ^ and end $ anchors, not ^ inside character classes
                if mount_pattern.startswith("^"):
                    partial_pattern = mount_pattern[1:]
                else:
                    partial_pattern = mount_pattern
                if partial_pattern.endswith("$"):
                    partial_pattern = partial_pattern[:-1]

                import re

                # Try to match from start of path
                match = re.match(partial_pattern, path)
                if match:
                    mount_params = match.groupdict()
                    matched_length = match.end()

                    # Extract remaining path for subrouter
                    sub_path = path[matched_length:]
                    if not sub_path:
                        sub_path = "/"
                    elif not sub_path.startswith("/"):
                        sub_path = "/" + sub_path

                    # Recursively search in subrouter
                    sub_route, sub_params, source_router = subrouter.find_route(
                        method, sub_path
                    )
                    if sub_route is not None:
                        # Merge mount parameters with subroute parameters
                        all_params = {**mount_params, **sub_params}
                        return sub_route, all_params, source_router
            # Simple mount path (no parameters)
            elif path.startswith(mount_path):
                if mount_path == "/":
                    sub_path = path
                else:
                    sub_path = path[len(mount_path) :]
                    if not sub_path:
                        sub_path = "/"
                    elif not sub_path.startswith("/"):
                        sub_path = "/" + sub_path

                # Recursively search in subrouter
                sub_route, sub_params, source_router = subrouter.find_route(
                    method, sub_path
                )
                if sub_route is not None:
                    return sub_route, sub_params, source_router

        return None, {}, None

    def get_allowed_methods(self, path: str) -> list[str]:
        """Get allowed HTTP methods for a given path.

        Args:
            path: Request path

        Returns:
            List of allowed HTTP methods
        """
        allowed_methods = []

        # Check direct routes
        for methods in self.routes.values():
            for route in methods.values():
                if route.match(path) is not None:
                    allowed_methods.append(route.method)

        # Check subrouters
        for mount_path, subrouter in self.subrouters.items():
            if path.startswith(mount_path):
                if mount_path == "/":
                    sub_path = path
                else:
                    sub_path = path[len(mount_path) :]
                    if not sub_path.startswith("/"):
                        sub_path = "/" + sub_path

                allowed_methods.extend(subrouter.get_allowed_methods(sub_path))

        return list(set(allowed_methods))  # Remove duplicates

    def get_all_routes(self) -> list[dict[str, Any]]:
        """Get all routes from this router and subrouters.

        Returns:
            List of all route dictionaries
        """
        all_routes = []

        # Add direct routes
        for methods in self.routes.values():
            for route in methods.values():
                all_routes.append(route.to_dict())

        # Add subrouter routes with proper path prefixes
        for mount_path, subrouter in self.subrouters.items():
            subrouter_routes = subrouter.get_all_routes()
            for route_dict in subrouter_routes:
                # Update the path to include the mount prefix
                original_path = route_dict["path"]
                if mount_path == "/":
                    full_path = original_path
                elif original_path == "/":
                    full_path = mount_path
                else:
                    full_path = mount_path + original_path

                # Create a new route dict with updated path
                updated_route = route_dict.copy()
                updated_route["path"] = full_path
                all_routes.append(updated_route)

        return all_routes
