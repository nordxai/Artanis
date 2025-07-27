"""Security middleware for Artanis framework.

This module provides comprehensive security middleware components including
CORS, CSP, HSTS, rate limiting, and other security headers to enhance
application security and follow web security best practices.
"""

from __future__ import annotations

import time
from typing import Any, Callable
from urllib.parse import urlparse

from ..exceptions import RateLimitError  # noqa: TID252


class SecurityConfig:
    """Configuration container for security middleware settings.

    Provides centralized configuration management for all security middleware
    components with sensible defaults and validation.
    """

    def __init__(
        self,
        cors_enabled: bool = True,
        cors_allow_origins: list[str] | str = "*",
        cors_allow_methods: list[str] | None = None,
        cors_allow_headers: list[str] | None = None,
        cors_allow_credentials: bool = False,
        cors_max_age: int = 86400,
        csp_enabled: bool = True,
        csp_directives: dict[str, str] | None = None,
        hsts_enabled: bool = True,
        hsts_max_age: int = 31536000,
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        security_headers_enabled: bool = True,
        rate_limit_enabled: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,
        rate_limit_storage: str = "memory",
    ) -> None:
        """Initialize security configuration.

        Args:
            cors_enabled: Enable CORS middleware
            cors_allow_origins: Allowed origins for CORS
            cors_allow_methods: Allowed HTTP methods for CORS
            cors_allow_headers: Allowed headers for CORS
            cors_allow_credentials: Allow credentials in CORS requests
            cors_max_age: Max age for CORS preflight cache
            csp_enabled: Enable Content Security Policy
            csp_directives: CSP directive mappings
            hsts_enabled: Enable HTTP Strict Transport Security
            hsts_max_age: HSTS max age in seconds
            hsts_include_subdomains: Include subdomains in HSTS
            hsts_preload: Enable HSTS preload
            security_headers_enabled: Enable general security headers
            rate_limit_enabled: Enable rate limiting
            rate_limit_requests: Number of requests per window
            rate_limit_window: Time window in seconds
            rate_limit_storage: Storage backend for rate limiting
        """
        # CORS configuration
        self.cors_enabled = cors_enabled
        self.cors_allow_origins = cors_allow_origins
        self.cors_allow_methods = cors_allow_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]
        self.cors_allow_headers = cors_allow_headers or [
            "Content-Type",
            "Authorization",
        ]
        self.cors_allow_credentials = cors_allow_credentials
        self.cors_max_age = cors_max_age

        # CSP configuration
        self.csp_enabled = csp_enabled
        self.csp_directives = csp_directives or {
            "default-src": "'self'",
            "script-src": "'self'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data:",
            "connect-src": "'self'",
            "font-src": "'self'",
            "object-src": "'none'",
            "media-src": "'self'",
            "frame-src": "'none'",
        }

        # HSTS configuration
        self.hsts_enabled = hsts_enabled
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload

        # Security headers configuration
        self.security_headers_enabled = security_headers_enabled

        # Rate limiting configuration
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.rate_limit_storage = rate_limit_storage


class CORSMiddleware:
    """Cross-Origin Resource Sharing (CORS) middleware.

    Handles CORS preflight requests and adds appropriate CORS headers
    to responses to enable cross-origin requests from web browsers.
    """

    def __init__(
        self,
        allow_origins: list[str] | str = "*",
        allow_methods: list[str] | None = None,
        allow_headers: list[str] | None = None,
        allow_credentials: bool = False,
        max_age: int = 86400,
    ) -> None:
        """Initialize CORS middleware.

        Args:
            allow_origins: Allowed origins (* for all, or list of origins)
            allow_methods: Allowed HTTP methods
            allow_headers: Allowed request headers
            allow_credentials: Whether to allow credentials
            max_age: Max age for preflight cache in seconds
        """
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]
        self.allow_headers = allow_headers or ["Content-Type", "Authorization"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def __call__(self, request: Any, next_func: Callable[[Any], Any]) -> Any:
        """Process CORS middleware.

        Args:
            request: The request object
            next_func: Next middleware function

        Returns:
            Response with CORS headers
        """
        from .response import Response

        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._handle_preflight(request)

        # Process regular request
        response = next_func(request)

        # Ensure we have a Response object
        if not isinstance(response, Response):
            response_obj = Response()
            response_obj.body = response
            response = response_obj

        # Add CORS headers
        self._add_cors_headers(response, request)

        return response

    def _handle_preflight(self, request: Any) -> Any:
        """Handle CORS preflight OPTIONS request.

        Args:
            request: The preflight request

        Returns:
            Preflight response with CORS headers
        """
        from .response import Response

        response = Response()
        response.status = 204
        self._add_cors_headers(response, request)

        # Add preflight-specific headers
        if self.max_age > 0:
            response.headers["Access-Control-Max-Age"] = str(self.max_age)

        # Handle requested method
        requested_method = request.headers.get("Access-Control-Request-Method")
        if requested_method and requested_method in self.allow_methods:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                self.allow_methods
            )

        # Handle requested headers
        requested_headers = request.headers.get("Access-Control-Request-Headers")
        if requested_headers:
            # Validate requested headers against allowed headers
            requested_list = [h.strip() for h in requested_headers.split(",")]
            allowed_list = [h.lower() for h in self.allow_headers]

            if all(h.lower() in allowed_list for h in requested_list):
                response.headers["Access-Control-Allow-Headers"] = ", ".join(
                    self.allow_headers
                )

        return response

    def _add_cors_headers(self, response: Any, request: Any) -> None:
        """Add CORS headers to response.

        Args:
            response: Response object to modify
            request: Original request object
        """
        origin = request.headers.get("Origin")

        # Handle origin validation
        if self._is_origin_allowed(origin):
            if self.allow_origins == "*" and not self.allow_credentials:
                response.headers["Access-Control-Allow-Origin"] = "*"
            else:
                response.headers["Access-Control-Allow-Origin"] = origin or "*"

        # Add credentials header if enabled
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        # Add exposed headers
        response.headers["Access-Control-Expose-Headers"] = (
            "Content-Length, Content-Type"
        )

    def _is_origin_allowed(self, origin: str | None) -> bool:
        """Check if origin is allowed.

        Args:
            origin: Origin header value

        Returns:
            True if origin is allowed
        """
        if not origin:
            return True

        if self.allow_origins == "*":
            return True

        if isinstance(self.allow_origins, list):
            return origin in self.allow_origins

        return origin == self.allow_origins


class CSPMiddleware:
    """Content Security Policy (CSP) middleware.

    Adds Content Security Policy headers to responses to prevent
    cross-site scripting (XSS) and data injection attacks.
    """

    def __init__(
        self,
        directives: dict[str, str] | None = None,
        report_only: bool = False,
        report_uri: str | None = None,
    ) -> None:
        """Initialize CSP middleware.

        Args:
            directives: CSP directive mappings
            report_only: Use report-only mode
            report_uri: URI for violation reports
        """
        self.directives = directives or {
            "default-src": "'self'",
            "script-src": "'self'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data:",
            "connect-src": "'self'",
            "font-src": "'self'",
            "object-src": "'none'",
            "media-src": "'self'",
            "frame-src": "'none'",
        }
        self.report_only = report_only
        self.report_uri = report_uri

    def __call__(self, request: Any, next_func: Callable[[Any], Any]) -> Any:
        """Process CSP middleware.

        Args:
            request: The request object
            next_func: Next middleware function

        Returns:
            Response with CSP headers
        """
        from .response import Response

        response = next_func(request)

        # Ensure we have a Response object
        if not isinstance(response, Response):
            response_obj = Response()
            response_obj.body = response
            response = response_obj

        # Build CSP policy string
        policy_parts = []
        for directive, value in self.directives.items():
            policy_parts.append(f"{directive} {value}")

        if self.report_uri:
            policy_parts.append(f"report-uri {self.report_uri}")

        policy = "; ".join(policy_parts)

        # Set appropriate CSP header
        header_name = (
            "Content-Security-Policy-Report-Only"
            if self.report_only
            else "Content-Security-Policy"
        )
        response.headers[header_name] = policy

        return response


class HSTSMiddleware:
    """HTTP Strict Transport Security (HSTS) middleware.

    Adds HSTS headers to responses to enforce HTTPS connections
    and prevent protocol downgrade attacks.
    """

    def __init__(
        self,
        max_age: int = 31536000,
        include_subdomains: bool = True,
        preload: bool = False,
    ) -> None:
        """Initialize HSTS middleware.

        Args:
            max_age: Max age in seconds (default: 1 year)
            include_subdomains: Include subdomains in HSTS
            preload: Enable HSTS preload
        """
        self.max_age = max_age
        self.include_subdomains = include_subdomains
        self.preload = preload

    def __call__(self, request: Any, next_func: Callable[[Any], Any]) -> Any:
        """Process HSTS middleware.

        Args:
            request: The request object
            next_func: Next middleware function

        Returns:
            Response with HSTS headers
        """
        from .response import Response

        response = next_func(request)

        # Ensure we have a Response object
        if not isinstance(response, Response):
            response_obj = Response()
            response_obj.body = response
            response = response_obj

        # Only add HSTS header for HTTPS requests
        if self._is_https_request(request):
            hsts_value = f"max-age={self.max_age}"

            if self.include_subdomains:
                hsts_value += "; includeSubDomains"

            if self.preload:
                hsts_value += "; preload"

            response.headers["Strict-Transport-Security"] = hsts_value

        return response

    def _is_https_request(self, request: Any) -> bool:
        """Check if request is HTTPS.

        Args:
            request: Request object

        Returns:
            True if HTTPS request
        """
        # Check scheme from request
        if hasattr(request, "scheme") and request.scheme == "https":
            return True

        # Check forwarded headers for proxy scenarios
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        if forwarded_proto == "https":
            return True

        # Check for other proxy headers
        return bool(request.headers.get("X-Forwarded-SSL") == "on")


class SecurityHeadersMiddleware:
    """General security headers middleware.

    Adds various security headers to responses to enhance application
    security and prevent common web vulnerabilities.
    """

    def __init__(
        self,
        x_frame_options: str = "DENY",
        x_content_type_options: str = "nosniff",
        x_xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str | None = None,
    ) -> None:
        """Initialize security headers middleware.

        Args:
            x_frame_options: X-Frame-Options header value
            x_content_type_options: X-Content-Type-Options header value
            x_xss_protection: X-XSS-Protection header value
            referrer_policy: Referrer-Policy header value
            permissions_policy: Permissions-Policy header value
        """
        self.x_frame_options = x_frame_options
        self.x_content_type_options = x_content_type_options
        self.x_xss_protection = x_xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy

    def __call__(self, request: Any, next_func: Callable[[Any], Any]) -> Any:
        """Process security headers middleware.

        Args:
            request: The request object
            next_func: Next middleware function

        Returns:
            Response with security headers
        """
        from .response import Response

        response = next_func(request)

        # Ensure we have a Response object
        if not isinstance(response, Response):
            response_obj = Response()
            response_obj.body = response
            response = response_obj

        # Add security headers
        if self.x_frame_options:
            response.headers["X-Frame-Options"] = self.x_frame_options

        if self.x_content_type_options:
            response.headers["X-Content-Type-Options"] = self.x_content_type_options

        if self.x_xss_protection:
            response.headers["X-XSS-Protection"] = self.x_xss_protection

        if self.referrer_policy:
            response.headers["Referrer-Policy"] = self.referrer_policy

        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy

        return response


class RateLimitMiddleware:
    """Rate limiting middleware.

    Implements rate limiting to prevent abuse and ensure fair usage
    of API endpoints. Supports multiple storage backends and strategies.
    """

    def __init__(
        self,
        requests_per_window: int = 100,
        window_seconds: int = 3600,
        storage: str = "memory",
        key_function: Callable[[Any], str] | None = None,
        skip_successful_requests: bool = False,
    ) -> None:
        """Initialize rate limit middleware.

        Args:
            requests_per_window: Number of requests allowed per window
            window_seconds: Time window in seconds
            storage: Storage backend ("memory" or "redis")
            key_function: Function to generate rate limit key
            skip_successful_requests: Only count failed requests
        """
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.storage = storage
        self.key_function = key_function or self._default_key_function
        self.skip_successful_requests = skip_successful_requests

        # Initialize storage backend
        self._storage: dict[str, dict[str, int | float]] = {}

    def __call__(self, request: Any, next_func: Callable[[Any], Any]) -> Any:
        """Process rate limit middleware.

        Args:
            request: The request object
            next_func: Next middleware function

        Returns:
            Response or rate limit error
        """
        from .response import Response

        # Generate rate limit key
        key = self.key_function(request)

        # Check rate limit
        if not self._is_allowed(key):
            # Rate limit exceeded
            retry_after = self._get_retry_after(key)
            raise RateLimitError(
                message="Rate limit exceeded",
                limit=self.requests_per_window,
                window=self.window_seconds,
                retry_after=retry_after,
            )

        # Process request
        response = next_func(request)

        # Ensure we have a Response object
        if not isinstance(response, Response):
            response_obj = Response()
            response_obj.body = response
            response = response_obj

        # Count request if configured to do so
        should_count = True
        if self.skip_successful_requests:
            should_count = response.status >= 400

        if should_count:
            self._increment_counter(key)

        # Add rate limit headers
        remaining = self._get_remaining_requests(key)
        reset_time = self._get_reset_time(key)

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response

    def _default_key_function(self, request: Any) -> str:
        """Default key function using client IP.

        Args:
            request: Request object

        Returns:
            Rate limit key
        """
        # Try to get real IP from forwarded headers
        ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not ip:
            ip = request.headers.get("X-Real-IP", "")
        if not ip:
            ip = getattr(request, "client", {}).get("host", "unknown")

        return f"rate_limit:{ip}"

    def _is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit.

        Args:
            key: Rate limit key

        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._clean_expired_entries(key, window_start)

        # Check current count
        if key not in self._storage:
            return True

        current_count = int(self._storage[key].get("count", 0))
        return current_count < self.requests_per_window

    def _increment_counter(self, key: str) -> None:
        """Increment request counter for key.

        Args:
            key: Rate limit key
        """
        now = time.time()

        if key not in self._storage:
            self._storage[key] = {"count": 0, "window_start": now}

        self._storage[key]["count"] += 1

    def _get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for key.

        Args:
            key: Rate limit key

        Returns:
            Number of remaining requests
        """
        if key not in self._storage:
            return self.requests_per_window

        current_count = int(self._storage[key].get("count", 0))
        return max(0, self.requests_per_window - current_count)

    def _get_reset_time(self, key: str) -> float:
        """Get reset time for rate limit window.

        Args:
            key: Rate limit key

        Returns:
            Unix timestamp of window reset
        """
        if key not in self._storage:
            return time.time() + self.window_seconds

        window_start = self._storage[key].get("window_start", time.time())
        return window_start + self.window_seconds

    def _get_retry_after(self, key: str) -> int:
        """Get retry after seconds.

        Args:
            key: Rate limit key

        Returns:
            Seconds until next request allowed
        """
        reset_time = self._get_reset_time(key)
        return max(1, int(reset_time - time.time()))

    def _clean_expired_entries(self, key: str, window_start: float) -> None:
        """Clean expired entries from storage.

        Args:
            key: Rate limit key
            window_start: Start of current window
        """
        if key in self._storage:
            entry_window_start = self._storage[key].get("window_start", 0)
            if entry_window_start < window_start:
                # Reset counter for new window
                self._storage[key] = {"count": 0, "window_start": time.time()}
