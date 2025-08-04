"""OpenAPI integration for Artanis framework.

This module provides comprehensive OpenAPI (Swagger) support including automatic
specification generation, interactive documentation, and request/response validation.
"""

from __future__ import annotations

from .decorators import (
    deprecated,
    example,
    openapi_route,
    operation_id,
    request_model,
    response_model,
    security,
    tag,
)
from .docs import OpenAPIDocsManager, ReDocUI, SwaggerUI
from .schema import RequestSchema, ResponseSchema, SchemaGenerator

# Core OpenAPI exports
from .spec import OpenAPIGenerator, OpenAPISpec
from .validation import ValidationMiddleware

__all__ = [
    "OpenAPIDocsManager",
    "OpenAPIGenerator",
    # Core specification
    "OpenAPISpec",
    "ReDocUI",
    "RequestSchema",
    "ResponseSchema",
    # Schema generation
    "SchemaGenerator",
    # Documentation UIs
    "SwaggerUI",
    # Validation
    "ValidationMiddleware",
    # Decorators
    "deprecated",
    "example",
    "openapi_route",
    "operation_id",
    "request_model",
    "response_model",
    "security",
    "tag",
]
