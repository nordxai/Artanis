"""OpenAPI specification generation for Artanis framework.

This module handles the generation of OpenAPI 3.0.1 specifications from Artanis
routes, including automatic schema inference and comprehensive API documentation.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, get_type_hints

from src.artanis.routing import Route

from .schema import SchemaGenerator

if TYPE_CHECKING:
    from src.artanis.application import App
    from src.artanis.routing import Router


class OpenAPISpec:
    """OpenAPI 3.0.1 specification builder.

    Provides a fluent interface for building OpenAPI specifications with
    comprehensive support for paths, schemas, security, and metadata.

    Example:
        ```python
        spec = OpenAPISpec(
            title="My API",
            version="1.0.0",
            description="A comprehensive API"
        )
        ```
    """

    def __init__(
        self,
        title: str = "Artanis API",
        version: str = "1.0.0",
        description: str = "API built with Artanis framework",
        openapi_version: str = "3.0.1",
    ) -> None:
        """Initialize OpenAPI specification.

        Args:
            title: API title
            version: API version
            description: API description
            openapi_version: OpenAPI specification version
        """
        self.title = title
        self.version = version
        self.description = description
        self.openapi_version = openapi_version
        self.schema_generator = SchemaGenerator()

        # Core OpenAPI structure
        self._spec: dict[str, Any] = {
            "openapi": openapi_version,
            "info": {
                "title": title,
                "version": version,
                "description": description,
            },
            "paths": {},
            "components": {
                "schemas": {},
                "parameters": {},
                "responses": {},
                "securitySchemes": {},
            },
            "tags": [],
            "servers": [],
        }

    def add_server(self, url: str, description: str = "") -> OpenAPISpec:
        """Add a server to the OpenAPI specification.

        Args:
            url: Server URL
            description: Server description

        Returns:
            Self for method chaining
        """
        self._spec["servers"].append(
            {
                "url": url,
                "description": description,
            }
        )
        return self

    def add_tag(self, name: str, description: str = "") -> OpenAPISpec:
        """Add a tag to the OpenAPI specification.

        Args:
            name: Tag name
            description: Tag description

        Returns:
            Self for method chaining
        """
        self._spec["tags"].append(
            {
                "name": name,
                "description": description,
            }
        )
        return self

    def add_security_scheme(
        self,
        name: str,
        scheme_type: str,
        **kwargs: Any,
    ) -> OpenAPISpec:
        """Add a security scheme to the specification.

        Args:
            name: Security scheme name
            scheme_type: Type of security (http, apiKey, oauth2, etc.)
            **kwargs: Additional security scheme properties

        Returns:
            Self for method chaining
        """
        self._spec["components"]["securitySchemes"][name] = {
            "type": scheme_type,
            **kwargs,
        }
        return self

    def add_path(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
    ) -> OpenAPISpec:
        """Add a path operation to the specification.

        Args:
            path: API path
            method: HTTP method
            operation: OpenAPI operation object

        Returns:
            Self for method chaining
        """
        if path not in self._spec["paths"]:
            self._spec["paths"][path] = {}

        self._spec["paths"][path][method.lower()] = operation
        return self

    def add_schema(self, name: str, schema: dict[str, Any]) -> OpenAPISpec:
        """Add a schema component to the specification.

        Args:
            name: Schema name
            schema: JSON Schema object

        Returns:
            Self for method chaining
        """
        self._spec["components"]["schemas"][name] = schema
        return self

    def to_dict(self) -> dict[str, Any]:
        """Export the specification as a dictionary.

        Returns:
            Complete OpenAPI specification dictionary
        """
        return self._spec.copy()

    def to_json(self) -> str:
        """Export the specification as JSON string.

        Returns:
            JSON representation of the OpenAPI specification
        """
        import json

        return json.dumps(self._spec, indent=2)


class OpenAPIGenerator:
    """Generator for creating OpenAPI specifications from Artanis applications.

    Automatically scans routes, extracts type hints, and generates comprehensive
    OpenAPI documentation with minimal configuration required.

    Example:
        ```python
        app = App()
        generator = OpenAPIGenerator()
        spec = generator.generate_spec(app)
        ```
    """

    def __init__(self) -> None:
        """Initialize the OpenAPI generator."""
        self.schema_generator = SchemaGenerator()

    def generate_spec(
        self,
        app: App,
        title: str = "Artanis API",
        version: str = "1.0.0",
        description: str = "API built with Artanis framework",
    ) -> OpenAPISpec:
        """Generate OpenAPI specification from an Artanis app.

        Args:
            app: Artanis application instance
            title: API title
            version: API version
            description: API description

        Returns:
            Complete OpenAPI specification
        """
        spec = OpenAPISpec(title=title, version=version, description=description)

        # Add default server
        spec.add_server("http://localhost:8000", "Development server")

        # Generate paths from routes
        self._generate_paths(app.router, spec)

        return spec

    def _generate_paths(self, router: Router, spec: OpenAPISpec) -> None:
        """Generate OpenAPI paths from router routes.

        Args:
            router: Router instance to scan
            spec: OpenAPI specification to update
        """
        for route_dict in router.get_all_routes():
            path_item = self._generate_path_item(route_dict)
            openapi_path = self._convert_path_to_openapi(route_dict["path"])
            spec.add_path(openapi_path, route_dict["method"], path_item)

    def _generate_path_item(self, route_dict: dict[str, Any]) -> dict[str, Any]:
        """Generate OpenAPI path item from a route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            OpenAPI path item dictionary
        """
        operation: dict[str, Any] = {
            "summary": self._extract_summary(route_dict),
            "description": self._extract_description(route_dict),
            "parameters": self._extract_parameters(route_dict),
            "responses": self._extract_responses(route_dict),
        }

        # Add tags if available
        tags = self._extract_tags(route_dict)
        if tags:
            operation["tags"] = tags

        # Add request body if applicable
        request_body = self._extract_request_body(route_dict)
        if request_body:
            operation["requestBody"] = request_body

        return operation

    def _extract_summary(self, route_dict: dict[str, Any]) -> str:
        """Extract operation summary from route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            Operation summary
        """
        handler = route_dict["handler"]

        # Check for OpenAPI metadata first
        if hasattr(handler, "openapi_summary") and isinstance(
            handler.openapi_summary, str
        ):
            return handler.openapi_summary

        # Generate from function name
        func_name = handler.__name__
        return func_name.replace("_", " ").title()  # type: ignore[no-any-return]

    def _extract_description(self, route_dict: dict[str, Any]) -> str:
        """Extract operation description from route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            Operation description
        """
        handler = route_dict["handler"]

        # Check for OpenAPI metadata first
        if hasattr(handler, "openapi_description") and isinstance(
            handler.openapi_description, str
        ):
            return handler.openapi_description

        # Extract from docstring
        doc = inspect.getdoc(handler)
        if doc:
            return doc.split("\n")[0]  # First line of docstring

        return f"{route_dict['method']} {route_dict['path']}"

    def _extract_tags(self, route_dict: dict[str, Any]) -> list[str]:
        """Extract tags from route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            List of tags
        """
        handler = route_dict["handler"]
        if hasattr(handler, "openapi_tags") and isinstance(handler.openapi_tags, list):
            return handler.openapi_tags
        return []

    def _extract_parameters(self, route_dict: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract parameters from route path and function signature.

        Args:
            route_dict: Route dictionary from router

        Returns:
            List of OpenAPI parameter objects
        """
        parameters = []
        handler = route_dict["handler"]

        # Extract path parameters
        import re

        path_params = re.findall(r"\{(\w+)\}", route_dict["path"])

        # Get function signature for type hints
        sig = inspect.signature(handler)
        type_hints = get_type_hints(handler)

        for param_name in path_params:
            param_info: dict[str, Any] = {
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},  # Default to string
            }

            # Try to get type from function signature
            if param_name in sig.parameters:
                sig.parameters[param_name]
                if param_name in type_hints:
                    param_type = type_hints[param_name]
                    param_info["schema"] = self.schema_generator.generate_schema(
                        param_type
                    )

            parameters.append(param_info)

        return parameters

    def _extract_request_body(
        self, route_dict: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Extract request body schema from route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            OpenAPI request body object or None
        """
        handler = route_dict["handler"]

        # Only applicable for POST, PUT, PATCH methods
        if route_dict["method"] not in ["POST", "PUT", "PATCH"]:
            return None

        # Check for OpenAPI metadata
        if hasattr(handler, "openapi_request_model"):
            schema = self.schema_generator.generate_schema(
                handler.openapi_request_model
            )
            return {
                "required": True,
                "content": {"application/json": {"schema": schema}},
            }

        return None

    def _extract_responses(self, route_dict: dict[str, Any]) -> dict[str, Any]:
        """Extract response schemas from route dictionary.

        Args:
            route_dict: Route dictionary from router

        Returns:
            OpenAPI responses object
        """
        responses: dict[str, Any] = {}
        handler = route_dict["handler"]

        # Check for OpenAPI response models
        if hasattr(handler, "openapi_responses"):
            for status_code, model in handler.openapi_responses.items():
                schema = self.schema_generator.generate_schema(model)
                responses[str(status_code)] = {
                    "description": f"Response {status_code}",
                    "content": {"application/json": {"schema": schema}},
                }
        else:
            # Default success response
            responses["200"] = {
                "description": "Successful response",
                "content": {"application/json": {"schema": {"type": "object"}}},
            }

        # Add common error responses
        responses["422"] = {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                            "errors": {"type": "array", "items": {"type": "object"}},
                        },
                    }
                }
            },
        }

        return responses

    def _convert_path_to_openapi(self, artanis_path: str) -> str:
        """Convert Artanis path format to OpenAPI format.

        Args:
            artanis_path: Path in Artanis format (/users/{id})

        Returns:
            Path in OpenAPI format (/users/{id})
        """
        # Artanis already uses OpenAPI-compatible format
        return artanis_path
