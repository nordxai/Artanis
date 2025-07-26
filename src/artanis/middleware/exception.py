"""Exception handling middleware for Artanis framework.

Provides centralized exception handling with consistent error responses,
proper logging, and structured error formatting for API responses.
"""

from typing import Any, Awaitable, Callable, Dict, Optional

from ..exceptions import ArtanisException
from ..logging import logger
from .response import Response


class ExceptionHandlerMiddleware:
    """Middleware for centralized exception handling.

    This middleware catches exceptions from route handlers and other middleware,
    provides consistent error responses, and ensures proper logging of errors.
    It handles both Artanis custom exceptions and unexpected system exceptions.

    Args:
        debug: Whether to include detailed error information in responses
        include_traceback: Whether to include stack traces in debug mode
        custom_handlers: Dict mapping exception types to custom handler functions

    Attributes:
        debug: Debug mode flag
        include_traceback: Traceback inclusion flag
        custom_handlers: Custom exception handlers
        logger: Logger instance for error tracking
    """

    def __init__(
        self,
        debug: bool = False,
        include_traceback: bool = False,
        custom_handlers: Optional[Dict[type, Callable]] = None,
    ) -> None:
        self.debug = debug
        self.include_traceback = include_traceback
        self.custom_handlers = custom_handlers or {}
        self.logger = logger

    def add_handler(self, exception_type: type, handler: Callable) -> None:
        """Add a custom handler for a specific exception type.

        Args:
            exception_type: The exception class to handle
            handler: Function that takes (exception, request, response) and returns response
        """
        self.custom_handlers[exception_type] = handler

    def _format_error_response(
        self, exception: Exception, request: Any
    ) -> Dict[str, Any]:
        """Format an exception into a structured error response.

        Args:
            exception: The exception that occurred
            request: The request object

        Returns:
            Dictionary containing structured error information
        """
        if isinstance(exception, ArtanisException):
            error_data = exception.to_dict()

            if self.debug and self.include_traceback:
                import traceback

                error_data["traceback"] = traceback.format_exc()

            return error_data
        # Handle unexpected exceptions
        error_data = {
            "error": "Internal Server Error" if not self.debug else str(exception),
            "error_code": "INTERNAL_ERROR",
            "status_code": 500,
        }

        if self.debug:
            error_data["exception_type"] = type(exception).__name__
            if self.include_traceback:
                import traceback

                error_data["traceback"] = traceback.format_exc()

        return error_data

    def _log_exception(self, exception: Exception, request: Any) -> None:
        """Log an exception with appropriate level and context.

        Args:
            exception: The exception that occurred
            request: The request object for context
        """
        method = (
            getattr(request.scope, "method", "UNKNOWN")
            if hasattr(request, "scope")
            else "UNKNOWN"
        )
        path = (
            getattr(request.scope, "path", "UNKNOWN")
            if hasattr(request, "scope")
            else "UNKNOWN"
        )

        if isinstance(exception, ArtanisException):
            if exception.status_code >= 500:
                # Server errors - log as error
                self.logger.error(
                    f"{exception.error_code}: {exception.message}",
                    extra={
                        "method": method,
                        "path": path,
                        "status_code": exception.status_code,
                        "error_code": exception.error_code,
                        "details": exception.details,
                    },
                )
            elif exception.status_code >= 400:
                # Client errors - log as warning
                self.logger.warning(
                    f"{exception.error_code}: {exception.message}",
                    extra={
                        "method": method,
                        "path": path,
                        "status_code": exception.status_code,
                        "error_code": exception.error_code,
                        "details": exception.details,
                    },
                )
        else:
            # Unexpected exceptions - always log as error
            self.logger.error(
                f"Unhandled exception: {type(exception).__name__}: {exception!s}",
                extra={
                    "method": method,
                    "path": path,
                    "exception_type": type(exception).__name__,
                },
                exc_info=True,
            )

    async def __call__(
        self,
        request: Any,
        response: Response,
        next_middleware: Callable[..., Awaitable[Response]],
    ) -> Response:
        """Execute the exception handling middleware.

        Args:
            request: The request object
            response: The response object
            next_middleware: The next middleware in the chain

        Returns:
            Response object with error handling applied
        """
        try:
            return await next_middleware(request)

        except Exception as e:
            # Check for custom handlers first
            exception_type = type(e)
            if exception_type in self.custom_handlers:
                try:
                    return await self.custom_handlers[exception_type](
                        e, request, response
                    )
                except Exception as handler_error:
                    # If custom handler fails, fall back to default handling
                    self.logger.error(
                        f"Custom exception handler failed: {handler_error!s}"
                    )
                    e = handler_error

            # Log the exception
            self._log_exception(e, request)

            # Format error response
            error_data = self._format_error_response(e, request)

            # Set response status and body
            if isinstance(e, ArtanisException):
                response.set_status(e.status_code)
            else:
                response.set_status(500)

            response.json(error_data)

            return response


class ValidationMiddleware:
    """Middleware for request validation.

    Provides common validation patterns for requests including
    JSON validation, required fields, and custom validation rules.

    Args:
        validate_json: Whether to validate JSON requests
        required_fields: List of required fields for JSON requests
        custom_validators: Dict of custom validation functions
    """

    def __init__(
        self,
        validate_json: bool = True,
        required_fields: Optional[list] = None,
        custom_validators: Optional[Dict[str, Callable]] = None,
    ) -> None:
        self.validate_json = validate_json
        self.required_fields = required_fields or []
        self.custom_validators = custom_validators or {}

    async def __call__(
        self,
        request: Any,
        response: Response,
        next_middleware: Callable[..., Awaitable[Response]],
    ) -> Response:
        """Execute validation middleware.

        Args:
            request: The request object
            response: The response object
            next_middleware: The next middleware in the chain

        Returns:
            Response object with validation applied

        Raises:
            ValidationError: If validation fails
        """
        from ..exceptions import ValidationError

        # Validate JSON requests
        if (
            self.validate_json
            and hasattr(request, "scope")
            and request.scope.get("method") in ["POST", "PUT", "PATCH"]
        ):
            content_type = None
            for name, value in request.scope.get("headers", []):
                if name == b"content-type":
                    content_type = value.decode()
                    break

            if content_type and "application/json" in content_type:
                try:
                    json_data = await request.json()

                    # Check required fields
                    if isinstance(json_data, dict):
                        missing_fields = []
                        for field in self.required_fields:
                            if field not in json_data:
                                missing_fields.append(field)

                        if missing_fields:
                            raise ValidationError(
                                message=f"Missing required fields: {', '.join(missing_fields)}",
                                validation_errors={"missing_fields": missing_fields},
                            )

                        # Run custom validators
                        for field, validator in self.custom_validators.items():
                            if field in json_data:
                                try:
                                    if not validator(json_data[field]):
                                        raise ValidationError(
                                            message=f"Validation failed for field: {field}",
                                            field=field,
                                            value=json_data[field],
                                        )
                                except ValidationError:
                                    raise
                                except Exception as e:
                                    raise ValidationError(
                                        message=f"Validator error for field {field}: {e!s}",
                                        field=field,
                                        validation_errors={"validator_error": str(e)},
                                    )

                except ValidationError:
                    raise
                except Exception as e:
                    # JSON parsing already handled by request.json(), but catch any other validation errors
                    raise ValidationError(
                        message=f"Request validation failed: {e!s}",
                        validation_errors={"validation_error": str(e)},
                    )

        return await next_middleware(request)
