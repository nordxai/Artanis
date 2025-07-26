"""Artanis Framework Exception Classes.

Custom exception hierarchy for the Artanis ASGI web framework providing
specific error types for common web application scenarios with proper
status codes and error messages.
"""

from __future__ import annotations

from typing import Any


class ArtanisException(Exception):
    """Base exception class for all Artanis framework errors.

    This is the root exception that all other Artanis exceptions inherit from.
    It provides a common interface for error handling with HTTP status codes
    and structured error data.

    Args:
        message: Human-readable error message
        status_code: HTTP status code associated with this error (default: 500)
        error_code: Framework-specific error code for categorization
        details: Additional error details as key-value pairs

    Attributes:
        message: The error message
        status_code: HTTP status code for the error
        error_code: Framework error code
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON responses.

        Returns:
            Dictionary representation of the exception
        """
        result = {
            "error": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code,
        }

        if self.details:
            result["details"] = self.details

        return result


class RouteNotFound(ArtanisException):
    """Exception raised when a requested route is not found.

    This exception is raised when the application receives a request
    for a path that has no registered route handlers.

    Args:
        path: The requested path that was not found
        method: The HTTP method used (optional)
    """

    def __init__(self, path: str, method: str | None = None) -> None:
        details = {"path": path}
        if method:
            details["method"] = method

        message = (
            f"Route not found: {method} {path}"
            if method
            else f"Route not found: {path}"
        )

        super().__init__(
            message=message,
            status_code=404,
            error_code="ROUTE_NOT_FOUND",
            details=details,
        )


class MethodNotAllowed(ArtanisException):
    """Exception raised when a route exists but method is not allowed.

    This exception is raised when a client requests a path that exists
    but using an HTTP method that is not supported for that path.

    Args:
        path: The requested path
        method: The HTTP method that was attempted
        allowed_methods: List of allowed methods for this path
    """

    def __init__(
        self, path: str, method: str, allowed_methods: list[str] | None = None
    ) -> None:
        details: dict[str, Any] = {"path": path, "method": method}

        if allowed_methods:
            details["allowed_methods"] = allowed_methods

        message = f"Method {method} not allowed for {path}"
        if allowed_methods:
            message += f". Allowed: {', '.join(allowed_methods)}"

        super().__init__(
            message=message,
            status_code=405,
            error_code="METHOD_NOT_ALLOWED",
            details=details,
        )


class ValidationError(ArtanisException):
    """Exception raised for request validation failures.

    This exception is raised when request data fails validation,
    such as invalid JSON, missing required fields, or invalid formats.

    Args:
        message: Description of the validation error
        field: The field that failed validation (optional)
        value: The invalid value (optional)
        validation_errors: Detailed validation error information
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        validation_errors: dict[str, Any] | None = None,
    ) -> None:
        details: dict[str, Any] = {}

        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ConfigurationError(ArtanisException):
    """Exception raised for framework configuration errors.

    This exception is raised when there are issues with framework
    configuration, such as invalid settings, missing required
    configuration values, or conflicting options.

    Args:
        message: Description of the configuration error
        config_key: The configuration key that caused the error (optional)
        config_value: The invalid configuration value (optional)
    """

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: Any | None = None,
    ) -> None:
        details = {}

        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = str(config_value)

        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


class MiddlewareError(ArtanisException):
    """Exception raised for middleware execution errors.

    This exception is raised when middleware encounters an error
    during execution, such as middleware chain failures or
    middleware-specific errors.

    Args:
        message: Description of the middleware error
        middleware_name: Name of the middleware that failed (optional)
        original_error: The original exception that caused this error (optional)
    """

    def __init__(
        self,
        message: str,
        middleware_name: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        details = {}

        if middleware_name:
            details["middleware"] = middleware_name
        if original_error:
            details["original_error"] = str(original_error)
            details["original_error_type"] = type(original_error).__name__

        super().__init__(
            message=message,
            status_code=500,
            error_code="MIDDLEWARE_ERROR",
            details=details,
        )


class HandlerError(ArtanisException):
    """Exception raised for route handler execution errors.

    This exception is raised when a route handler encounters an error
    during execution, providing context about which route failed.

    Args:
        message: Description of the handler error
        route_path: The route path where the error occurred (optional)
        method: The HTTP method of the failing route (optional)
        original_error: The original exception that caused this error (optional)
    """

    def __init__(
        self,
        message: str,
        route_path: str | None = None,
        method: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        details = {}

        if route_path:
            details["route_path"] = route_path
        if method:
            details["method"] = method
        if original_error:
            details["original_error"] = str(original_error)
            details["original_error_type"] = type(original_error).__name__

        super().__init__(
            message=message,
            status_code=500,
            error_code="HANDLER_ERROR",
            details=details,
        )


class AuthenticationError(ArtanisException):
    """Exception raised for authentication failures.

    This exception is raised when authentication is required
    but not provided, or when provided credentials are invalid.

    Args:
        message: Description of the authentication error
        auth_type: Type of authentication that failed (optional)
    """

    def __init__(
        self, message: str = "Authentication required", auth_type: str | None = None
    ) -> None:
        details = {}

        if auth_type:
            details["auth_type"] = auth_type

        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(ArtanisException):
    """Exception raised for authorization failures.

    This exception is raised when a user is authenticated but
    does not have permission to access the requested resource.

    Args:
        message: Description of the authorization error
        resource: The resource that was attempted to be accessed (optional)
        required_permission: The permission that was required (optional)
    """

    def __init__(
        self,
        message: str = "Access denied",
        resource: str | None = None,
        required_permission: str | None = None,
    ) -> None:
        details = {}

        if resource:
            details["resource"] = resource
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class RateLimitError(ArtanisException):
    """Exception raised when rate limits are exceeded.

    This exception is raised when a client exceeds the configured
    rate limits for API requests.

    Args:
        message: Description of the rate limit error
        limit: The rate limit that was exceeded (optional)
        window: The time window for the rate limit (optional)
        retry_after: Seconds until the client can retry (optional)
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int | None = None,
        window: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        details = {}

        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )
