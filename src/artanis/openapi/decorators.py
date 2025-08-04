"""OpenAPI decorators for enhancing route metadata.

This module provides decorators for adding OpenAPI-specific metadata to routes,
including summaries, descriptions, request/response models, and tags.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from .schema import RequestSchema, ResponseSchema

F = TypeVar("F", bound=Callable[..., Any])


def openapi_route(
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    responses: dict[int, type[Any]] | None = None,
    deprecated: bool = False,
    operation_id: str | None = None,
) -> Callable[[F], F]:
    """Decorator to add OpenAPI metadata to a route handler.

    Args:
        summary: Short summary of the operation
        description: Detailed description of the operation
        tags: List of tags for grouping operations
        responses: Dictionary mapping status codes to response models
        deprecated: Whether the operation is deprecated
        operation_id: Unique identifier for the operation

    Returns:
        Decorated function with OpenAPI metadata

    Example:
        ```python
        @openapi_route(
            summary="Get user by ID",
            description="Retrieve a specific user by their unique identifier",
            tags=["users"],
            responses={200: UserResponse, 404: ErrorResponse}
        )
        async def get_user(user_id: int) -> UserResponse:
            pass

        app.get('/users/{user_id}', get_user)
        ```
    """

    def decorator(func: F) -> F:
        # Add OpenAPI metadata as function attributes
        if summary is not None:
            func.openapi_summary = summary  # type: ignore[attr-defined]
        if description is not None:
            func.openapi_description = description  # type: ignore[attr-defined]
        if tags is not None:
            func.openapi_tags = tags  # type: ignore[attr-defined]
        if responses is not None:
            func.openapi_responses = responses  # type: ignore[attr-defined]
        if deprecated:
            func.openapi_deprecated = deprecated  # type: ignore[attr-defined]
        if operation_id is not None:
            func.openapi_operation_id = operation_id  # type: ignore[attr-defined]

        return func

    return decorator


def response_model(
    model: type[Any],
    status_code: int = 200,
    description: str | None = None,
) -> Callable[[F], F]:
    """Decorator to specify response model for a route.

    Args:
        model: Response model class
        status_code: HTTP status code for this response
        description: Description of the response

    Returns:
        Decorated function with response model metadata

    Example:
        ```python
        @response_model(UserResponse, status_code=200)
        async def get_user(id: int) -> UserResponse:
            pass

        app.get('/users/{id}', get_user)
        ```
    """

    def decorator(func: F) -> F:
        if not hasattr(func, "openapi_responses"):
            func.openapi_responses = {}  # type: ignore[attr-defined]

        func.openapi_responses[status_code] = model  # type: ignore[attr-defined]

        if description:
            if not hasattr(func, "openapi_response_descriptions"):
                func.openapi_response_descriptions = {}  # type: ignore[attr-defined]
            func.openapi_response_descriptions[status_code] = description  # type: ignore[attr-defined]

        return func

    return decorator


def request_model(
    model: type[Any],
    description: str | None = None,
) -> Callable[[F], F]:
    """Decorator to specify request body model for a route.

    Args:
        model: Request body model class
        description: Description of the request body

    Returns:
        Decorated function with request model metadata

    Example:
        ```python
        @request_model(CreateUserRequest)
        async def create_user(user: CreateUserRequest):
            pass

        app.post('/users', create_user)
        ```
    """

    def decorator(func: F) -> F:
        func.openapi_request_model = model  # type: ignore[attr-defined]

        if description:
            func.openapi_request_description = description  # type: ignore[attr-defined]

        return func

    return decorator


def deprecated(reason: str | None = None) -> Callable[[F], F]:
    """Mark a route as deprecated in OpenAPI documentation.

    Args:
        reason: Optional reason for deprecation

    Returns:
        Decorated function marked as deprecated

    Example:
        ```python
        @deprecated("Use /api/v2/users instead")
        async def get_users_v1():
            pass

        app.get('/api/v1/users', get_users_v1)
        ```
    """

    def decorator(func: F) -> F:
        func.openapi_deprecated = True  # type: ignore[attr-defined]

        if reason:
            func.openapi_deprecation_reason = reason  # type: ignore[attr-defined]

        return func

    return decorator


def tag(*tags: str) -> Callable[[F], F]:
    """Add tags to a route for OpenAPI grouping.

    Args:
        *tags: Tag names to add to the route

    Returns:
        Decorated function with tags

    Example:
        ```python
        @tag("users", "admin")
        async def get_admin_users():
            pass

        app.get('/admin/users', get_admin_users)
        ```
    """

    def decorator(func: F) -> F:
        func.openapi_tags = list(tags)  # type: ignore[attr-defined]
        return func

    return decorator


def operation_id(op_id: str) -> Callable[[F], F]:
    """Set operation ID for a route.

    Args:
        op_id: Unique operation identifier

    Returns:
        Decorated function with operation ID

    Example:
        ```python
        @operation_id("getUserById")
        async def get_user(id: int):
            pass

        app.get('/users/{id}', get_user)
        ```
    """

    def decorator(func: F) -> F:
        func.openapi_operation_id = op_id  # type: ignore[attr-defined]
        return func

    return decorator


def security(
    schemes: str | list[str] | dict[str, list[str]],
) -> Callable[[F], F]:
    """Add security requirements to a route.

    Args:
        schemes: Security scheme name(s) or mapping of schemes to scopes

    Returns:
        Decorated function with security requirements

    Example:
        ```python
        @security("api_key")
        async def protected_endpoint():
            pass

        app.get('/protected', protected_endpoint)

        @security({"oauth2": ["read", "write"]})
        async def admin_endpoint():
            pass

        app.post('/admin', admin_endpoint)
        ```
    """

    def decorator(func: F) -> F:
        if isinstance(schemes, str):
            # Single scheme name
            func.openapi_security = [{schemes: []}]  # type: ignore[attr-defined]
        elif isinstance(schemes, list):
            # List of scheme names
            func.openapi_security = [{scheme: []} for scheme in schemes]  # type: ignore[attr-defined]
        elif isinstance(schemes, dict):
            # Mapping of schemes to scopes
            func.openapi_security = [schemes]  # type: ignore[attr-defined]
        else:
            func.openapi_security = []  # type: ignore[unreachable]

        return func

    return decorator


def example(
    request_example: dict[str, Any] | None = None,
    response_examples: dict[int, dict[str, Any]] | None = None,
) -> Callable[[F], F]:
    """Add examples to route documentation.

    Args:
        request_example: Example request body
        response_examples: Examples for different response status codes

    Returns:
        Decorated function with examples

    Example:
        ```python
        @example(
            request_example={"name": "John", "email": "john@example.com"},
            response_examples={
                200: {"id": 1, "name": "John", "email": "john@example.com"}
            }
        )
        async def create_user(user: dict):
            pass

        app.post('/users', create_user)
        ```
    """

    def decorator(func: F) -> F:
        if request_example is not None:
            func.openapi_request_example = request_example  # type: ignore[attr-defined]

        if response_examples is not None:
            func.openapi_response_examples = response_examples  # type: ignore[attr-defined]

        return func

    return decorator
