"""Tests for Artanis custom exceptions and exception handling."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from artanis import App
from artanis.exceptions import (
    ArtanisException, RouteNotFound, MethodNotAllowed, ValidationError,
    ConfigurationError, MiddlewareError, HandlerError, AuthenticationError,
    AuthorizationError, RateLimitError
)
from artanis.middleware.exception import ExceptionHandlerMiddleware, ValidationMiddleware
from artanis.middleware.response import Response


class TestArtanisExceptions:
    """Test the base exception class and inheritance hierarchy."""
    
    def test_base_exception_creation(self):
        """Test creating a base ArtanisException."""
        exc = ArtanisException("Test error")
        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.error_code == "ArtanisException"
        assert exc.details == {}
    
    def test_base_exception_with_all_params(self):
        """Test creating ArtanisException with all parameters."""
        details = {"key": "value", "count": 42}
        exc = ArtanisException(
            message="Custom error",
            status_code=400,
            error_code="CUSTOM_ERROR",
            details=details
        )
        assert exc.message == "Custom error"
        assert exc.status_code == 400
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.details == details
    
    def test_exception_to_dict(self):
        """Test converting exception to dictionary."""
        details = {"field": "username", "value": "invalid"}
        exc = ArtanisException(
            message="Validation failed",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )
        
        result = exc.to_dict()
        expected = {
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "status_code": 400,
            "details": details
        }
        assert result == expected
    
    def test_exception_to_dict_no_details(self):
        """Test converting exception to dictionary without details."""
        exc = ArtanisException("Simple error")
        result = exc.to_dict()
        expected = {
            "error": "Simple error",
            "error_code": "ArtanisException",
            "status_code": 500
        }
        assert result == expected


class TestRouteNotFound:
    """Test RouteNotFound exception."""
    
    def test_route_not_found_path_only(self):
        """Test RouteNotFound with path only."""
        exc = RouteNotFound("/api/users")
        assert exc.message == "Route not found: /api/users"
        assert exc.status_code == 404
        assert exc.error_code == "ROUTE_NOT_FOUND"
        assert exc.details == {"path": "/api/users"}
    
    def test_route_not_found_with_method(self):
        """Test RouteNotFound with path and method."""
        exc = RouteNotFound("/api/users", "POST")
        assert exc.message == "Route not found: POST /api/users"
        assert exc.status_code == 404
        assert exc.error_code == "ROUTE_NOT_FOUND"
        assert exc.details == {"path": "/api/users", "method": "POST"}


class TestMethodNotAllowed:
    """Test MethodNotAllowed exception."""
    
    def test_method_not_allowed_basic(self):
        """Test MethodNotAllowed with basic parameters."""
        exc = MethodNotAllowed("/api/users", "DELETE")
        assert exc.message == "Method DELETE not allowed for /api/users"
        assert exc.status_code == 405
        assert exc.error_code == "METHOD_NOT_ALLOWED"
        assert exc.details == {"path": "/api/users", "method": "DELETE"}
    
    def test_method_not_allowed_with_allowed_methods(self):
        """Test MethodNotAllowed with allowed methods list."""
        allowed = ["GET", "POST"]
        exc = MethodNotAllowed("/api/users", "DELETE", allowed)
        assert exc.message == "Method DELETE not allowed for /api/users. Allowed: GET, POST"
        assert exc.status_code == 405
        assert exc.error_code == "METHOD_NOT_ALLOWED"
        assert exc.details == {
            "path": "/api/users", 
            "method": "DELETE",
            "allowed_methods": allowed
        }


class TestValidationError:
    """Test ValidationError exception."""
    
    def test_validation_error_basic(self):
        """Test ValidationError with basic message."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.status_code == 400
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details == {}
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        exc = ValidationError("Invalid email format", field="email", value="invalid-email")
        assert exc.message == "Invalid email format"
        assert exc.status_code == 400
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details == {"field": "email", "value": "invalid-email"}
    
    def test_validation_error_with_validation_errors(self):
        """Test ValidationError with detailed validation errors."""
        validation_errors = {"email": "Invalid format", "age": "Must be positive"}
        exc = ValidationError(
            "Multiple validation errors",
            validation_errors=validation_errors
        )
        assert exc.details["validation_errors"] == validation_errors


class TestOtherExceptions:
    """Test other exception classes."""
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        exc = ConfigurationError("Invalid config", config_key="database_url")
        assert exc.message == "Invalid config"
        assert exc.status_code == 500
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.details["config_key"] == "database_url"
    
    def test_middleware_error(self):
        """Test MiddlewareError."""
        original = ValueError("Original error")
        exc = MiddlewareError("Middleware failed", middleware_name="auth", original_error=original)
        assert exc.message == "Middleware failed"
        assert exc.status_code == 500
        assert exc.error_code == "MIDDLEWARE_ERROR"
        assert exc.details["middleware"] == "auth"
        assert exc.details["original_error"] == "Original error"
        assert exc.details["original_error_type"] == "ValueError"
    
    def test_handler_error(self):
        """Test HandlerError."""
        original = RuntimeError("Handler failed")
        exc = HandlerError(
            "Route handler error",
            route_path="/api/users",
            method="POST",
            original_error=original
        )
        assert exc.message == "Route handler error"
        assert exc.status_code == 500
        assert exc.error_code == "HANDLER_ERROR"
        assert exc.details["route_path"] == "/api/users"
        assert exc.details["method"] == "POST"
        assert exc.details["original_error"] == "Handler failed"
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError(auth_type="bearer")
        assert exc.message == "Authentication required"
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.details["auth_type"] == "bearer"
    
    def test_authorization_error(self):
        """Test AuthorizationError."""
        exc = AuthorizationError(
            "Insufficient permissions",
            resource="/admin",
            required_permission="admin:read"
        )
        assert exc.message == "Insufficient permissions"
        assert exc.status_code == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.details["resource"] == "/admin"
        assert exc.details["required_permission"] == "admin:read"
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        exc = RateLimitError(
            "Too many requests",
            limit=100,
            window=3600,
            retry_after=300
        )
        assert exc.message == "Too many requests"
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.details["limit"] == 100
        assert exc.details["window"] == 3600
        assert exc.details["retry_after"] == 300


class TestFrameworkExceptionIntegration:
    """Test exception integration with the framework."""
    
    @pytest.mark.asyncio
    async def test_route_not_found_integration(self):
        """Test RouteNotFound integration with framework."""
        app = App(enable_request_logging=False)
        
        # Mock ASGI components
        scope = {"type": "http", "method": "GET", "path": "/nonexistent", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check that 404 response was sent
        response_start_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.start":
                response_start_call = call[0][0]
                break
        
        assert response_start_call is not None
        assert response_start_call["status"] == 404
        
        # Get the response body
        body_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.body":
                body_call = call[0][0]
                break
        
        assert body_call is not None
        response_data = json.loads(body_call["body"].decode())
        assert response_data["error_code"] == "ROUTE_NOT_FOUND"
        assert response_data["status_code"] == 404
        assert "/nonexistent" in response_data["error"]
    
    @pytest.mark.asyncio
    async def test_method_not_allowed_integration(self):
        """Test MethodNotAllowed integration with framework."""
        app = App(enable_request_logging=False)
        
        # Register a GET route
        async def get_users():
            return {"users": []}
        
        app.get("/users", get_users)
        
        # Try to POST to the same route
        scope = {"type": "http", "method": "POST", "path": "/users", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check that 405 response was sent
        response_start_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.start":
                response_start_call = call[0][0]
                break
        
        assert response_start_call is not None
        assert response_start_call["status"] == 405
        
        # Get the response body
        body_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.body":
                body_call = call[0][0]
                break
        
        assert body_call is not None
        response_data = json.loads(body_call["body"].decode())
        assert response_data["error_code"] == "METHOD_NOT_ALLOWED"
        assert response_data["status_code"] == 405
        assert "GET" in response_data["details"]["allowed_methods"]
    
    @pytest.mark.asyncio
    async def test_handler_error_integration(self):
        """Test HandlerError integration with framework."""
        app = App(enable_request_logging=False)
        
        async def error_handler():
            raise ValueError("Something went wrong")
        
        app.get("/error", error_handler)
        
        scope = {"type": "http", "method": "GET", "path": "/error", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check that 500 response was sent
        response_start_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.start":
                response_start_call = call[0][0]
                break
        
        assert response_start_call is not None
        assert response_start_call["status"] == 500
        
        # Get the response body
        body_call = None
        for call in send.call_args_list:
            if call[0][0]["type"] == "http.response.body":
                body_call = call[0][0]
                break
        
        assert body_call is not None
        response_data = json.loads(body_call["body"].decode())
        assert response_data["error_code"] == "HANDLER_ERROR"
        assert response_data["status_code"] == 500
        assert "Something went wrong" in response_data["error"]


class TestExceptionHandlerMiddleware:
    """Test the ExceptionHandlerMiddleware."""
    
    def test_middleware_creation(self):
        """Test creating exception handler middleware."""
        middleware = ExceptionHandlerMiddleware(debug=True, include_traceback=True)
        assert middleware.debug is True
        assert middleware.include_traceback is True
        assert middleware.custom_handlers == {}
    
    def test_add_custom_handler(self):
        """Test adding custom exception handler."""
        middleware = ExceptionHandlerMiddleware()
        
        def custom_handler(exc, req, resp):
            return resp
        
        middleware.add_handler(ValueError, custom_handler)
        assert ValueError in middleware.custom_handlers
        assert middleware.custom_handlers[ValueError] == custom_handler
    
    @pytest.mark.asyncio
    async def test_middleware_handles_artanis_exception(self):
        """Test middleware handling ArtanisException."""
        middleware = ExceptionHandlerMiddleware()
        request = MagicMock()
        request.scope = {"method": "GET", "path": "/test"}
        response = Response()
        
        async def failing_middleware(req):
            raise ValidationError("Invalid data", field="email")
        
        result = await middleware(request, response, failing_middleware)
        
        assert result.status == 400
        response_data = json.loads(result.to_bytes().decode())
        assert response_data["error_code"] == "VALIDATION_ERROR"
        assert response_data["error"] == "Invalid data"
    
    @pytest.mark.asyncio
    async def test_middleware_handles_unexpected_exception(self):
        """Test middleware handling unexpected exceptions."""
        middleware = ExceptionHandlerMiddleware()
        request = MagicMock()
        request.scope = {"method": "GET", "path": "/test"}
        response = Response()
        
        async def failing_middleware(req):
            raise ValueError("Unexpected error")
        
        result = await middleware(request, response, failing_middleware)
        
        assert result.status == 500
        response_data = json.loads(result.to_bytes().decode())
        assert response_data["error_code"] == "INTERNAL_ERROR"
        assert response_data["error"] == "Internal Server Error"
    
    @pytest.mark.asyncio
    async def test_middleware_debug_mode(self):
        """Test middleware in debug mode."""
        middleware = ExceptionHandlerMiddleware(debug=True, include_traceback=True)
        request = MagicMock()
        request.scope = {"method": "GET", "path": "/test"}
        response = Response()
        
        async def failing_middleware(req):
            raise ValueError("Debug error")
        
        result = await middleware(request, response, failing_middleware)
        
        assert result.status == 500
        response_data = json.loads(result.to_bytes().decode())
        assert response_data["error_code"] == "INTERNAL_ERROR"
        assert response_data["error"] == "Debug error"
        assert "exception_type" in response_data
        assert response_data["exception_type"] == "ValueError"
        assert "traceback" in response_data


class TestValidationMiddleware:
    """Test the ValidationMiddleware."""
    
    def test_validation_middleware_creation(self):
        """Test creating validation middleware."""
        middleware = ValidationMiddleware(
            validate_json=True,
            required_fields=["name", "email"],
            custom_validators={"email": lambda x: "@" in x}
        )
        assert middleware.validate_json is True
        assert middleware.required_fields == ["name", "email"]
        assert "email" in middleware.custom_validators
    
    @pytest.mark.asyncio
    async def test_validation_passes_with_valid_data(self):
        """Test validation middleware with valid data."""
        middleware = ValidationMiddleware(required_fields=["name"])
        request = MagicMock()
        request.scope = {
            "method": "POST",
            "headers": [(b"content-type", b"application/json")]
        }
        request.json = AsyncMock(return_value={"name": "John", "email": "john@example.com"})
        response = Response()
        
        async def next_middleware(req):
            return response
        
        result = await middleware(request, response, next_middleware)
        assert result == response
    
    @pytest.mark.asyncio
    async def test_validation_fails_missing_required_field(self):
        """Test validation middleware with missing required field."""
        middleware = ValidationMiddleware(required_fields=["name", "email"])
        request = MagicMock()
        request.scope = {
            "method": "POST",
            "headers": [(b"content-type", b"application/json")]
        }
        request.json = AsyncMock(return_value={"name": "John"})  # Missing email
        response = Response()
        
        async def next_middleware(req):
            return response
        
        with pytest.raises(ValidationError) as exc_info:
            await middleware(request, response, next_middleware)
        
        assert "Missing required fields: email" in str(exc_info.value)
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validation_custom_validator_fails(self):
        """Test validation middleware with failing custom validator."""
        def email_validator(value):
            return "@" in value and "." in value
        
        middleware = ValidationMiddleware(
            custom_validators={"email": email_validator}
        )
        request = MagicMock()
        request.scope = {
            "method": "POST",
            "headers": [(b"content-type", b"application/json")]
        }
        request.json = AsyncMock(return_value={"email": "invalid-email"})
        response = Response()
        
        async def next_middleware(req):
            return response
        
        with pytest.raises(ValidationError) as exc_info:
            await middleware(request, response, next_middleware)
        
        assert "Validation failed for field: email" in str(exc_info.value)
        assert exc_info.value.details["field"] == "email"