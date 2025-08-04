"""Tests for OpenAPI functionality."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import pytest

from artanis import App
from artanis.openapi import (
    OpenAPIGenerator,
    OpenAPISpec,
    ReDocUI,
    SchemaGenerator,
    SwaggerUI,
    ValidationMiddleware,
    openapi_route,
    request_model,
    response_model,
)


# Test data models
@dataclass
class User:
    id: int
    name: str
    email: str
    age: Optional[int] = None  # noqa: UP045


@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: Optional[int] = None  # noqa: UP045


@dataclass
class ErrorResponse:
    error: str
    code: int


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class TestOpenAPISpec:
    """Test OpenAPI specification building."""

    def test_spec_creation(self):
        """Test basic OpenAPI spec creation."""
        spec = OpenAPISpec(title="Test API", version="1.0.0", description="A test API")

        assert spec.title == "Test API"
        assert spec.version == "1.0.0"
        assert spec.description == "A test API"

        spec_dict = spec.to_dict()
        assert spec_dict["openapi"] == "3.0.1"
        assert spec_dict["info"]["title"] == "Test API"
        assert spec_dict["info"]["version"] == "1.0.0"

    def test_add_server(self):
        """Test adding servers to spec."""
        spec = OpenAPISpec()
        spec.add_server("https://api.example.com", "Production server")

        spec_dict = spec.to_dict()
        servers = spec_dict["servers"]
        assert len(servers) == 1
        assert servers[0]["url"] == "https://api.example.com"
        assert servers[0]["description"] == "Production server"

    def test_add_tag(self):
        """Test adding tags to spec."""
        spec = OpenAPISpec()
        spec.add_tag("users", "User operations")

        spec_dict = spec.to_dict()
        tags = spec_dict["tags"]
        assert len(tags) == 1
        assert tags[0]["name"] == "users"
        assert tags[0]["description"] == "User operations"

    def test_add_security_scheme(self):
        """Test adding security schemes."""
        spec = OpenAPISpec()
        spec.add_security_scheme("bearer", "http", scheme="bearer", bearerFormat="JWT")

        spec_dict = spec.to_dict()
        schemes = spec_dict["components"]["securitySchemes"]
        assert "bearer" in schemes
        assert schemes["bearer"]["type"] == "http"
        assert schemes["bearer"]["scheme"] == "bearer"

    def test_add_path(self):
        """Test adding paths to spec."""
        spec = OpenAPISpec()
        operation = {
            "summary": "Get user",
            "responses": {"200": {"description": "Success"}},
        }
        spec.add_path("/users/{id}", "get", operation)

        spec_dict = spec.to_dict()
        paths = spec_dict["paths"]
        assert "/users/{id}" in paths
        assert "get" in paths["/users/{id}"]

    def test_to_json(self):
        """Test JSON export."""
        spec = OpenAPISpec(title="Test API")
        json_str = spec.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["info"]["title"] == "Test API"


class TestSchemaGenerator:
    """Test schema generation from Python types."""

    def setup_method(self):
        """Setup test fixtures."""
        self.generator = SchemaGenerator()

    def test_primitive_types(self):
        """Test primitive type conversion."""
        assert self.generator.generate_schema(str) == {"type": "string"}
        assert self.generator.generate_schema(int) == {"type": "integer"}
        assert self.generator.generate_schema(float) == {"type": "number"}
        assert self.generator.generate_schema(bool) == {"type": "boolean"}

    def test_list_type(self):
        """Test list type conversion."""
        schema = self.generator.generate_schema(List[str])
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "string"

    def test_dict_type(self):
        """Test dict type conversion."""
        schema = self.generator.generate_schema(Dict[str, int])
        assert schema["type"] == "object"
        assert schema["additionalProperties"]["type"] == "integer"

    def test_optional_type(self):
        """Test Optional type conversion."""
        schema = self.generator.generate_schema(Optional[str])
        assert schema["type"] == "string"
        assert schema["nullable"] is True

    def test_dataclass_conversion(self):
        """Test dataclass to schema conversion."""
        schema = self.generator.generate_schema(User)

        assert schema["type"] == "object"
        assert "properties" in schema

        props = schema["properties"]
        assert props["id"]["type"] == "integer"
        assert props["name"]["type"] == "string"
        assert props["email"]["type"] == "string"
        assert props["age"]["type"] == "integer"
        assert props["age"]["nullable"] is True

        # Required fields (non-optional)
        assert "required" in schema
        required = schema["required"]
        assert "id" in required
        assert "name" in required
        assert "email" in required
        assert "age" not in required

    def test_enum_conversion(self):
        """Test enum to schema conversion."""
        schema = self.generator.generate_schema(UserStatus)

        assert schema["type"] == "string"
        assert schema["enum"] == ["active", "inactive", "pending"]

    def test_get_schema_name(self):
        """Test schema name generation."""
        assert self.generator.get_schema_name(User) == "User"
        assert self.generator.get_schema_name(str) == "str"

    def test_generate_component_schema(self):
        """Test component schema generation."""
        name, schema = self.generator.generate_component_schema(User)

        assert name == "User"
        assert schema["type"] == "object"
        assert "properties" in schema


class TestOpenAPIGenerator:
    """Test OpenAPI specification generation from apps."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = App()
        self.generator = OpenAPIGenerator()

    def test_basic_generation(self):
        """Test basic spec generation from app."""

        async def get_users():
            """Get all users."""
            return [{"id": 1, "name": "John"}]

        self.app.get("/users", get_users)

        spec = self.generator.generate_spec(self.app)
        spec_dict = spec.to_dict()

        assert spec_dict["info"]["title"] == "Artanis API"
        assert "/users" in spec_dict["paths"]
        assert "get" in spec_dict["paths"]["/users"]

    def test_path_parameter_extraction(self):
        """Test path parameter extraction."""

        async def get_user(user_id: int):
            """Get user by ID."""
            return {"id": user_id}

        self.app.get("/users/{user_id}", get_user)

        spec = self.generator.generate_spec(self.app)
        spec_dict = spec.to_dict()

        operation = spec_dict["paths"]["/users/{user_id}"]["get"]
        parameters = operation["parameters"]

        assert len(parameters) == 1
        param = parameters[0]
        assert param["name"] == "user_id"
        assert param["in"] == "path"
        assert param["required"] is True
        assert param["schema"]["type"] == "integer"

    def test_summary_from_function_name(self):
        """Test summary generation from function name."""

        async def create_user_account():
            pass

        self.app.get("/test", create_user_account)

        spec = self.generator.generate_spec(self.app)
        operation = spec.to_dict()["paths"]["/test"]["get"]

        assert operation["summary"] == "Create User Account"

    def test_description_from_docstring(self):
        """Test description extraction from docstring."""

        async def test_handler():
            """This is a test handler.

            More details here.
            """

        self.app.get("/test", test_handler)

        spec = self.generator.generate_spec(self.app)
        operation = spec.to_dict()["paths"]["/test"]["get"]

        assert operation["description"] == "This is a test handler."


class TestOpenAPIDecorators:
    """Test OpenAPI decorators."""

    def test_openapi_route_decorator(self):
        """Test openapi_route decorator."""

        @openapi_route(
            summary="Get user",
            description="Get a specific user",
            tags=["users"],
            responses={200: User, 404: ErrorResponse},
        )
        async def get_user():
            pass

        assert hasattr(get_user, "openapi_summary")
        assert get_user.openapi_summary == "Get user"
        assert get_user.openapi_description == "Get a specific user"
        assert get_user.openapi_tags == ["users"]
        assert get_user.openapi_responses == {200: User, 404: ErrorResponse}

    def test_response_model_decorator(self):
        """Test response_model decorator."""

        @response_model(User, status_code=200)
        async def get_user():
            pass

        assert hasattr(get_user, "openapi_responses")
        assert get_user.openapi_responses[200] == User

    def test_request_model_decorator(self):
        """Test request_model decorator."""

        @request_model(CreateUserRequest)
        async def create_user():
            pass

        assert hasattr(create_user, "openapi_request_model")
        assert create_user.openapi_request_model == CreateUserRequest


class TestSwaggerUI:
    """Test Swagger UI integration."""

    def test_swagger_ui_creation(self):
        """Test Swagger UI instance creation."""
        spec = OpenAPISpec(title="Test API")
        swagger_ui = SwaggerUI(spec)

        assert swagger_ui.openapi_spec == spec
        assert swagger_ui.title == "API Documentation"

    def test_swagger_html_generation(self):
        """Test Swagger UI HTML generation."""
        spec = OpenAPISpec(title="Test API")
        swagger_ui = SwaggerUI(spec)

        html = swagger_ui._generate_swagger_html()

        assert "<!DOCTYPE html>" in html
        assert "swagger-ui" in html
        assert "SwaggerUIBundle" in html

    def test_docs_handler(self):
        """Test docs handler creation."""
        spec = OpenAPISpec()
        swagger_ui = SwaggerUI(spec)

        handler = swagger_ui.get_docs_handler()
        assert callable(handler)

    def test_openapi_json_handler(self):
        """Test OpenAPI JSON handler."""
        spec = OpenAPISpec(title="Test API")
        swagger_ui = SwaggerUI(spec)

        handler = swagger_ui.get_openapi_json_handler()
        assert callable(handler)


class TestReDocUI:
    """Test ReDoc UI integration."""

    def test_redoc_ui_creation(self):
        """Test ReDoc UI instance creation."""
        spec = OpenAPISpec(title="Test API")
        redoc_ui = ReDocUI(spec)

        assert redoc_ui.openapi_spec == spec
        assert redoc_ui.title == "API Documentation"

    def test_redoc_html_generation(self):
        """Test ReDoc HTML generation."""
        spec = OpenAPISpec(title="Test API")
        redoc_ui = ReDocUI(spec)

        html = redoc_ui._generate_redoc_html()

        assert "<!DOCTYPE html>" in html
        assert "redoc" in html
        assert "redoc.standalone.js" in html


class TestValidationMiddleware:
    """Test request/response validation middleware."""

    def test_middleware_creation(self):
        """Test validation middleware creation."""
        spec = OpenAPISpec()
        middleware = ValidationMiddleware(spec)

        assert middleware.openapi_spec == spec
        assert middleware.validate_requests is True
        assert middleware.validate_responses is False

    def test_custom_validation_settings(self):
        """Test custom validation settings."""
        spec = OpenAPISpec()
        middleware = ValidationMiddleware(
            spec, validate_requests=False, validate_responses=True, strict_mode=True
        )

        assert middleware.validate_requests is False
        assert middleware.validate_responses is True
        assert middleware.strict_mode is True


class TestAppIntegration:
    """Test OpenAPI integration with App class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = App()

    def test_generate_openapi_spec(self):
        """Test OpenAPI spec generation on app."""

        async def get_users():
            return []

        self.app.get("/users", get_users)

        spec_dict = self.app.generate_openapi_spec(title="My API", version="2.0.0")

        assert spec_dict["info"]["title"] == "My API"
        assert spec_dict["info"]["version"] == "2.0.0"
        assert "/users" in spec_dict["paths"]

    def test_serve_docs(self):
        """Test docs serving setup."""

        async def test():
            return {}

        self.app.get("/test", test)

        # This should not raise an error
        self.app.serve_docs()

        # Check that routes were added
        routes = [route["path"] for route in self.app.routes]
        assert "/docs" in routes
        assert "/redoc" in routes
        assert "/openapi.json" in routes

    def test_add_openapi_metadata(self):
        """Test adding OpenAPI metadata."""
        self.app.add_openapi_metadata(
            title="Custom API",
            version="3.0.0",
            servers=[{"url": "https://api.example.com", "description": "Production"}],
            tags=[{"name": "users", "description": "User operations"}],
        )

        # Should not raise an error
        assert self.app._openapi_spec is not None

    def test_export_openapi_json(self):
        """Test OpenAPI export to JSON."""

        async def test():
            return {}

        self.app.get("/test", test)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            try:
                self.app.export_openapi(f.name, format_type="json")

                # Check file was created and contains valid JSON
                with Path(f.name).open() as read_f:
                    content = read_f.read()
                    spec = json.loads(content)
                    assert "openapi" in spec
                    assert spec["info"]["title"] == "Artanis API"
            finally:
                Path(f.name).unlink()

    def test_add_openapi_validation(self):
        """Test adding OpenAPI validation middleware."""

        async def test():
            return {}

        self.app.get("/test", test)

        # Should not raise an error
        self.app.add_openapi_validation(validate_requests=True)


class TestEndToEndIntegration:
    """Test complete OpenAPI integration scenarios."""

    def test_complete_api_documentation(self):
        """Test complete API with OpenAPI documentation."""
        app = App()

        @openapi_route(
            summary="Health check",
            description="Check API health status",
            tags=["monitoring"],
        )
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy"}

        @openapi_route(
            summary="Get user by ID",
            description="Retrieve a specific user by their ID",
            tags=["users"],
            responses={200: User, 404: ErrorResponse},
        )
        async def get_user(user_id: int):
            """Get a user by ID."""
            return {"id": user_id, "name": "John", "email": "john@example.com"}

        @openapi_route(
            summary="Create user",
            description="Create a new user account",
            tags=["users"],
        )
        @request_model(CreateUserRequest)
        @response_model(User, status_code=201)
        async def create_user(user: CreateUserRequest):
            """Create a new user."""
            return {"id": 1, "name": user.name, "email": user.email}

        app.get("/health", health_check)
        app.get("/users/{user_id}", get_user)
        app.post("/users", create_user)

        # Generate complete OpenAPI spec
        spec_dict = app.generate_openapi_spec(
            title="User Management API",
            version="1.0.0",
            description="A comprehensive user management system",
        )

        # Verify spec structure
        assert spec_dict["info"]["title"] == "User Management API"
        assert spec_dict["info"]["version"] == "1.0.0"

        # Verify paths
        paths = spec_dict["paths"]
        assert "/health" in paths
        assert "/users/{user_id}" in paths
        assert "/users" in paths

        # Verify operations
        health_op = paths["/health"]["get"]
        assert health_op["summary"] == "Health check"
        assert "monitoring" in health_op["tags"]

        get_user_op = paths["/users/{user_id}"]["get"]
        assert get_user_op["summary"] == "Get user by ID"
        assert "users" in get_user_op["tags"]
        assert len(get_user_op["parameters"]) == 1
        assert get_user_op["parameters"][0]["name"] == "user_id"

        create_user_op = paths["/users"]["post"]
        assert create_user_op["summary"] == "Create user"
        assert "requestBody" in create_user_op

        # Setup documentation
        app.serve_docs()

        # Verify documentation routes were added
        routes = [route["path"] for route in app.routes]
        assert "/docs" in routes
        assert "/redoc" in routes
        assert "/openapi.json" in routes
