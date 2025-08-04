"""Request and response validation middleware for OpenAPI.

This module provides middleware for validating HTTP requests and responses
against OpenAPI schemas with detailed error reporting.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from src.artanis.exceptions import ValidationError

from .schema import SchemaGenerator

if TYPE_CHECKING:
    from src.artanis.middleware.response import Response
    from src.artanis.request import Request

    from .spec import OpenAPISpec


class ValidationMiddleware:
    """Middleware for validating requests and responses against OpenAPI schemas.

    Provides automatic validation of incoming requests and outgoing responses
    based on OpenAPI specifications with detailed error reporting.

    Example:
        ```python
        validator = ValidationMiddleware(openapi_spec)
        app.use(validator)
        ```
    """

    def __init__(
        self,
        openapi_spec: OpenAPISpec,
        validate_requests: bool = True,
        validate_responses: bool = False,
        strict_mode: bool = False,
    ) -> None:
        """Initialize validation middleware.

        Args:
            openapi_spec: OpenAPI specification for validation
            validate_requests: Whether to validate incoming requests
            validate_responses: Whether to validate outgoing responses
            strict_mode: Whether to enforce strict validation
        """
        self.openapi_spec = openapi_spec
        self.validate_requests = validate_requests
        self.validate_responses = validate_responses
        self.strict_mode = strict_mode
        self.schema_generator = SchemaGenerator()

    async def __call__(
        self,
        request: Request,
        response: Response,
        next_middleware: Callable[[], Any],
    ) -> Response:
        """Process request through validation middleware.

        Args:
            request: HTTP request object
            response: HTTP response object
            next_middleware: Next middleware in the chain

        Returns:
            HTTP response object

        Raises:
            ValidationError: If validation fails
        """
        # Validate request if enabled
        if self.validate_requests:
            await self._validate_request(request)

        # Process request through next middleware
        final_response = await next_middleware()

        # Validate response if enabled
        if self.validate_responses:
            await self._validate_response(request, final_response)

        return final_response  # type: ignore[no-any-return]

    async def _validate_request(self, request: Request) -> None:
        """Validate incoming request against OpenAPI schema.

        Args:
            request: HTTP request to validate

        Raises:
            ValidationError: If request validation fails
        """
        spec = self.openapi_spec.to_dict()
        path = request.scope["path"]
        method = request.scope["method"].lower()

        # Find matching path in OpenAPI spec
        openapi_path = self._find_matching_path(path, spec)
        if not openapi_path:
            if self.strict_mode:
                msg = f"Path not found in OpenAPI spec: {path}"
                raise ValidationError(msg)
            return

        # Get operation definition
        paths = spec.get("paths", {})
        operation = paths.get(openapi_path, {}).get(method)
        if not operation:
            if self.strict_mode:
                msg = f"Method {method.upper()} not allowed for path {path}"
                raise ValidationError(msg)
            return

        # Validate path parameters
        await self._validate_path_parameters(request, operation)

        # Validate query parameters
        await self._validate_query_parameters(request, operation)

        # Validate request body for applicable methods
        if method in ["post", "put", "patch"]:
            await self._validate_request_body(request, operation)

    async def _validate_response(self, request: Request, response: Response) -> None:
        """Validate outgoing response against OpenAPI schema.

        Args:
            request: HTTP request object
            response: HTTP response to validate

        Raises:
            ValidationError: If response validation fails
        """
        spec = self.openapi_spec.to_dict()
        path = request.scope["path"]
        method = request.scope["method"].lower()

        # Find matching operation
        openapi_path = self._find_matching_path(path, spec)
        if not openapi_path:
            return

        paths = spec.get("paths", {})
        operation = paths.get(openapi_path, {}).get(method)
        if not operation:
            return

        # Get response definition
        responses = operation.get("responses", {})
        status_code = str(response.status)
        response_def = responses.get(status_code) or responses.get("default")

        if not response_def:
            if self.strict_mode:
                msg = f"Response {status_code} not defined for {method.upper()} {path}"
                raise ValidationError(msg)
            return

        # Validate response content
        await self._validate_response_content(response, response_def)

    def _find_matching_path(
        self, request_path: str, spec: dict[str, Any]
    ) -> str | None:
        """Find matching OpenAPI path for a request path.

        Args:
            request_path: Actual request path
            spec: OpenAPI specification

        Returns:
            Matching OpenAPI path pattern or None
        """
        paths = spec.get("paths", {})

        # Try exact match first
        if request_path in paths:
            return request_path

        # Try pattern matching for parameterized paths
        for openapi_path in paths:
            if self._path_matches(request_path, openapi_path):
                return str(openapi_path)

        return None

    def _path_matches(self, request_path: str, openapi_path: str) -> bool:
        """Check if request path matches OpenAPI path pattern.

        Args:
            request_path: Actual request path
            openapi_path: OpenAPI path with parameters

        Returns:
            True if paths match
        """
        import re

        # Convert OpenAPI path to regex pattern
        pattern = re.sub(r"\{[^}]+\}", r"[^/]+", openapi_path)
        pattern = f"^{pattern}$"

        return bool(re.match(pattern, request_path))

    async def _validate_path_parameters(
        self, request: Request, operation: dict[str, Any]
    ) -> None:
        """Validate path parameters against operation schema.

        Args:
            request: HTTP request
            operation: OpenAPI operation definition

        Raises:
            ValidationError: If path parameter validation fails
        """
        parameters = operation.get("parameters", [])
        path_params = [p for p in parameters if p.get("in") == "path"]

        for param in path_params:
            param_name = param.get("name")
            required = param.get("required", False)
            schema = param.get("schema", {})

            # Extract parameter value from request
            param_value = getattr(request, "path_params", {}).get(param_name)

            if required and param_value is None:
                msg = f"Required path parameter missing: {param_name}"
                raise ValidationError(msg)

            if param_value is not None:
                # Validate parameter type
                await self._validate_value_against_schema(
                    param_value, schema, f"path parameter {param_name}"
                )

    async def _validate_query_parameters(
        self, request: Request, operation: dict[str, Any]
    ) -> None:
        """Validate query parameters against operation schema.

        Args:
            request: HTTP request
            operation: OpenAPI operation definition

        Raises:
            ValidationError: If query parameter validation fails
        """
        parameters = operation.get("parameters", [])
        query_params = [p for p in parameters if p.get("in") == "query"]

        # Parse query string from ASGI scope
        query_string = request.scope.get("query_string", b"").decode("utf-8")
        parsed_query = {}
        if query_string:
            from urllib.parse import parse_qs

            parsed_query = {
                k: v[0] if len(v) == 1 else v for k, v in parse_qs(query_string).items()
            }

        for param in query_params:
            param_name = param.get("name")
            required = param.get("required", False)
            schema = param.get("schema", {})

            # Extract parameter value from parsed query parameters
            param_value = parsed_query.get(param_name)

            if required and param_value is None:
                msg = f"Required query parameter missing: {param_name}"
                raise ValidationError(msg)

            if param_value is not None:
                # Validate parameter type
                await self._validate_value_against_schema(
                    param_value, schema, f"query parameter {param_name}"
                )

    async def _validate_request_body(
        self, request: Request, operation: dict[str, Any]
    ) -> None:
        """Validate request body against operation schema.

        Args:
            request: HTTP request
            operation: OpenAPI operation definition

        Raises:
            ValidationError: If request body validation fails
        """
        request_body_def = operation.get("requestBody")
        if not request_body_def:
            return

        required = request_body_def.get("required", False)
        content = request_body_def.get("content", {})

        # Get request body
        body = await request.body()

        if required and not body:
            msg = "Request body is required"
            raise ValidationError(msg)

        if body:
            # Check content type
            content_type = request.headers.get("content-type", "").split(";")[0]

            if content_type in content:
                schema = content[content_type].get("schema", {})

                # Parse JSON body
                if content_type == "application/json":
                    try:
                        json_data = json.loads(body)
                        await self._validate_value_against_schema(
                            json_data, schema, "request body"
                        )
                    except json.JSONDecodeError as e:
                        msg = f"Invalid JSON in request body: {e}"
                        raise ValidationError(msg)

    async def _validate_response_content(
        self, response: Response, response_def: dict[str, Any]
    ) -> None:
        """Validate response content against schema.

        Args:
            response: HTTP response
            response_def: OpenAPI response definition

        Raises:
            ValidationError: If response validation fails
        """
        content = response_def.get("content", {})

        if not content:
            return

        # Check if response has content type
        response_content_type = (
            getattr(response, "content_type", None) or "application/json"
        )

        if response_content_type in content:
            schema = content[response_content_type].get("schema", {})

            # Validate response body
            if hasattr(response, "content") and response.content:
                if response_content_type == "application/json":
                    try:
                        json_data = json.loads(response.content)
                        await self._validate_value_against_schema(
                            json_data, schema, "response body"
                        )
                    except json.JSONDecodeError:
                        # Response content is not valid JSON
                        if self.strict_mode:
                            msg = "Response content is not valid JSON"
                            raise ValidationError(msg)

    async def _validate_value_against_schema(  # noqa: PLR0915
        self,
        value: Any,
        schema: dict[str, Any],
        field_name: str,
    ) -> None:
        """Validate a value against a JSON schema.

        Args:
            value: Value to validate
            schema: JSON schema to validate against
            field_name: Name of the field being validated

        Raises:
            ValidationError: If validation fails
        """
        schema_type = schema.get("type")

        if schema_type == "string" and not isinstance(value, str):
            msg = f"{field_name} must be a string"
            raise ValidationError(msg)
        if schema_type == "integer" and not isinstance(value, int):
            try:
                int(value)
            except (ValueError, TypeError):
                msg = f"{field_name} must be an integer"
                raise ValidationError(msg)
        elif schema_type == "number" and not isinstance(value, (int, float)):
            try:
                float(value)
            except (ValueError, TypeError):
                msg = f"{field_name} must be a number"
                raise ValidationError(msg)
        elif schema_type == "boolean" and not isinstance(value, bool):
            msg = f"{field_name} must be a boolean"
            raise ValidationError(msg)
        elif schema_type == "array" and not isinstance(value, list):
            msg = f"{field_name} must be an array"
            raise ValidationError(msg)
        elif schema_type == "object" and not isinstance(value, dict):
            msg = f"{field_name} must be an object"
            raise ValidationError(msg)

        # Validate enum values
        if "enum" in schema and value not in schema["enum"]:
            msg = f"{field_name} must be one of: {schema['enum']}"
            raise ValidationError(msg)

        # Validate string patterns
        if schema_type == "string" and "pattern" in schema:
            import re

            if not re.match(schema["pattern"], value):
                msg = f"{field_name} does not match required pattern"
                raise ValidationError(msg)

        # Validate numeric ranges
        if schema_type in ["integer", "number"]:
            if "minimum" in schema and value < schema["minimum"]:
                msg = f"{field_name} must be >= {schema['minimum']}"
                raise ValidationError(msg)
            if "maximum" in schema and value > schema["maximum"]:
                msg = f"{field_name} must be <= {schema['maximum']}"
                raise ValidationError(msg)

        # Validate array items
        if schema_type == "array" and "items" in schema and isinstance(value, list):
            items_schema = schema["items"]
            for i, item in enumerate(value):
                await self._validate_value_against_schema(
                    item, items_schema, f"{field_name}[{i}]"
                )

        # Validate object properties
        if schema_type == "object" and isinstance(value, dict):
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            # Check required properties
            for req_prop in required:
                if req_prop not in value:
                    msg = f"Required property missing in {field_name}: {req_prop}"
                    raise ValidationError(msg)

            # Validate properties
            for prop_name, prop_value in value.items():
                if prop_name in properties:
                    prop_schema = properties[prop_name]
                    await self._validate_value_against_schema(
                        prop_value, prop_schema, f"{field_name}.{prop_name}"
                    )
