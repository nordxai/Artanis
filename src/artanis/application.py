"""Main application class for Artanis framework.

This module contains the core App class that handles route registration,
middleware management, and ASGI request processing.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from .asgi import send_error_response, send_response
from .events import EventManager
from .exceptions import HandlerError, MethodNotAllowed, RouteNotFound
from .handlers import call_handler
from .logging import RequestLoggingMiddleware, logger
from .middleware import MiddlewareExecutor, MiddlewareManager, Response
from .request import Request
from .routing import Router


class App:
    """Main Artanis application class.

    The core application class that handles route registration, middleware
    management, and ASGI request processing. Provides an Express.js-inspired
    API for building web applications.

    Args:
        enable_request_logging: Whether to enable automatic request logging

    Attributes:
        router: Router instance for handling routes
        middleware_manager: Manages global and path-based middleware
        middleware_executor: Executes middleware chains
        event_manager: Manages application events and handlers
        logger: Application logger instance

    Example:
        ```python
        from artanis import App

        app = App()

        async def hello(name: str):
            return {'message': f'Hello, {name}!'}

        app.get('/hello/{name}', hello)
        ```
    """

    def __init__(self, enable_request_logging: bool = True) -> None:
        self.router = Router()
        self.middleware_manager = MiddlewareManager()
        self.middleware_executor = MiddlewareExecutor(self.middleware_manager)
        self.event_manager = EventManager()
        self.logger = logger

        # OpenAPI integration
        self._openapi_spec: Any | None = None
        self._openapi_docs_manager: Any | None = None

        # Add request logging middleware by default
        if enable_request_logging:
            self.use(RequestLoggingMiddleware())

    @property
    def routes(self) -> list[dict[str, Any]]:
        """Get all registered routes.

        Returns:
            List of all registered route dictionaries
        """
        return self.router.get_all_routes()

    def _register_route(
        self, method: str, path: str, handler: Callable[..., Any]
    ) -> None:
        """Register a route with the application.

        Internal method to register a route handler for a specific HTTP method
        and path pattern.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: URL path pattern with optional parameters (e.g., '/users/{id}')
            handler: Route handler function or coroutine
        """
        self.router.register_route(method, path, handler)

    def get(self, path: str, handler: Callable[..., Any]) -> None:
        """Register a GET route.

        Args:
            path: URL path pattern
            handler: Route handler function
        """
        self._register_route("GET", path, handler)

    def post(self, path: str, handler: Callable[..., Any]) -> None:
        """Register a POST route.

        Args:
            path: URL path pattern
            handler: Route handler function
        """
        self._register_route("POST", path, handler)

    def put(self, path: str, handler: Callable[..., Any]) -> None:
        """Register a PUT route.

        Args:
            path: URL path pattern
            handler: Route handler function
        """
        self._register_route("PUT", path, handler)

    def delete(self, path: str, handler: Callable[..., Any]) -> None:
        """Register a DELETE route.

        Args:
            path: URL path pattern
            handler: Route handler function
        """
        self._register_route("DELETE", path, handler)

    def all(self, path: str, handler: Callable[..., Any]) -> None:
        """Register a route that responds to all HTTP methods.

        This registers the handler for all standard HTTP methods
        (GET, POST, PUT, DELETE, PATCH, OPTIONS).

        Args:
            path: URL path pattern
            handler: Route handler function

        Example:
            ```python
            # Authentication middleware for all methods
            def authenticate(request, user_id):
                # Check authentication for any HTTP method
                return {"user_id": user_id, "authenticated": True}

            app.all("/admin/{user_id}", authenticate)
            ```
        """
        self.router.all(path, handler)

    def use(
        self,
        path_or_middleware: str | Callable[..., Any],
        middleware: Callable[..., Any] | None = None,
    ) -> None:
        """Register middleware - Express style app.use() API.

        Register middleware either globally or for specific paths.

        Args:
            path_or_middleware: Either a path pattern (str) or middleware function
            middleware: Middleware function (when first arg is a path)

        Examples:
            ```python
            # Global middleware
            app.use(cors_middleware)

            # Path-specific middleware
            app.use('/api', auth_middleware)
            ```
        """
        if middleware is None:
            # app.use(middleware_func) - Global middleware
            if callable(path_or_middleware):
                self.middleware_manager.add_global(path_or_middleware)
        # app.use("/path", middleware_func) - Path-based middleware
        elif isinstance(path_or_middleware, str):
            self.middleware_manager.add_path(path_or_middleware, middleware)

    def mount(self, path: str, router: Router) -> None:
        """Mount a subrouter at the specified path.

        Args:
            path: Path prefix where the subrouter should be mounted
            router: Router instance to mount

        Example:
            ```python
            api_router = Router()
            api_router.get('/users', get_users)
            app.mount('/api', api_router)
            ```
        """
        self.router.mount(path, router)

    # Event handling methods
    def add_event_handler(
        self,
        event_name: str,
        handler: Callable[..., Any],
        priority: int = 0,
        condition: Callable[..., bool] | None = None,
    ) -> None:
        """Register an event handler.

        Args:
            event_name: Name of the event to handle (e.g., 'startup', 'shutdown', or custom)
            handler: Function to call when event is triggered
            priority: Execution priority (higher numbers run first)
            condition: Optional condition function to determine if handler should run

        Examples:
            ```python
            # Built-in lifecycle events
            app.add_event_handler("startup", setup_database)
            app.add_event_handler("shutdown", cleanup_database)

            # Custom events
            app.add_event_handler("user_registered", send_welcome_email)
            app.add_event_handler("payment_processed", update_inventory, priority=10)

            # Conditional handlers
            app.add_event_handler("order_placed",
                                send_notification,
                                condition=lambda data: data.get("urgent", False))
            ```
        """
        self.event_manager.add_handler(event_name, handler, priority, condition)

    async def emit_event(
        self,
        event_name: str,
        data: Any = None,
        source: str | None = None,
        **metadata: Any,
    ) -> None:
        """Trigger all handlers for an event.

        Args:
            event_name: Name of the event to trigger
            data: Data to pass to event handlers
            source: Optional source identifier for the event
            **metadata: Additional metadata to include in event context

        Examples:
            ```python
            # Trigger custom events
            await app.emit_event("user_registered", user_data)
            await app.emit_event("payment_processed", payment_data, source="stripe")
            await app.emit_event("order_completed", order_data, urgent=True)
            ```
        """
        await self.event_manager.emit_event(event_name, data, source, **metadata)

    def remove_event_handler(
        self, event_name: str, handler: Callable[..., Any]
    ) -> bool:
        """Remove a specific event handler.

        Args:
            event_name: Name of the event
            handler: Handler function to remove

        Returns:
            True if handler was found and removed, False otherwise

        Example:
            ```python
            app.remove_event_handler("startup", old_setup_function)
            ```
        """
        return self.event_manager.remove_handler(event_name, handler)

    def add_event_middleware(self, middleware: Callable[..., Any]) -> None:
        """Add middleware that runs for all events.

        Args:
            middleware: Function that will be called for every event

        Example:
            ```python
            async def event_logger(event_context):
                print(f"Event: {event_context.name} at {event_context.timestamp}")

            app.add_event_middleware(event_logger)
            ```
        """
        self.event_manager.add_event_middleware(middleware)

    def list_events(self) -> list[str]:
        """Get list of all registered event names.

        Returns:
            List of event names that have handlers

        Example:
            ```python
            events = app.list_events()
            print(f"Registered events: {events}")
            ```
        """
        return self.event_manager.list_events()

    # Properties for backward compatibility with tests
    @property
    def global_middleware(self) -> list[Callable[..., Any]]:
        """Get global middleware list.

        Returns:
            List of global middleware functions
        """
        return self.middleware_manager.global_middleware

    @property
    def path_middleware(self) -> dict[str, list[Callable[..., Any]]]:
        """Get path-based middleware dictionary.

        Returns:
            Dictionary mapping paths to middleware lists
        """
        return self.middleware_manager.path_middleware

    def _find_route(
        self, method: str, path: str
    ) -> tuple[dict[str, Any] | None, dict[str, str]]:
        """Find a route handler and extract path parameters.

        Args:
            method: HTTP method
            path: Request path

        Returns:
            Tuple of (route_info, path_parameters) or (None, {}) if not found

        Raises:
            RouteNotFound: If no route matches the path
            MethodNotAllowed: If path exists but method not allowed
        """
        route, params, source_router = self.router.find_route(method, path)
        if route is not None:
            return route.to_dict(), params
        return None, {}

    def _path_exists_with_different_method(self, path: str) -> tuple[bool, list[str]]:
        """Check if path exists with a different HTTP method.

        Used to determine whether to return 405 Method Not Allowed
        instead of 404 Not Found.

        Args:
            path: Request path to check

        Returns:
            Tuple of (path_exists, allowed_methods)
        """
        allowed_methods = self.router.get_allowed_methods(path)
        return len(allowed_methods) > 0, allowed_methods

    async def _handle_lifespan(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        """Handle ASGI lifespan protocol for startup and shutdown events.

        Args:
            scope: ASGI scope dictionary
            receive: ASGI receive callable
            send: ASGI send callable
        """
        message = await receive()

        if message["type"] == "lifespan.startup":
            try:
                await self.event_manager.execute_startup_handlers()
                await send({"type": "lifespan.startup.complete"})
            except Exception as e:
                self.logger.error(f"Startup failed: {e}")
                await send({"type": "lifespan.startup.failed", "message": str(e)})

        elif message["type"] == "lifespan.shutdown":
            try:
                await self.event_manager.execute_shutdown_handlers()
                await send({"type": "lifespan.shutdown.complete"})
            except Exception as e:
                self.logger.error(f"Shutdown failed: {e}")
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})

    async def __call__(  # noqa: PLR0915
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        """ASGI application entry point.

        Handles incoming HTTP requests and ASGI lifespan events.

        Args:
            scope: ASGI scope dictionary
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)
            return
        if scope["type"] != "http":
            return

        method = scope["method"]
        path = scope["path"]

        # Create request and response objects
        request = Request(scope, receive)
        response = Response()

        # Find route and extract path params BEFORE middleware execution
        route, path_params = self._find_route(method, path)

        # Add path params to request for middleware access
        request.path_params = path_params

        # Define the final handler (route handler)
        async def final_handler(req: Any) -> Any:
            if route:
                try:
                    response_data = await call_handler(
                        route["handler"], path_params, req, route
                    )
                    if not response.is_finished():
                        # Check if handler has content type hint
                        handler = route["handler"]
                        if hasattr(handler, "_artanis_content_type"):
                            content_type = handler._artanis_content_type  # noqa: SLF001
                            if content_type == "text/html":
                                response.body = response_data
                                response.set_header("Content-Type", "text/html")
                            elif content_type == "application/json":
                                response.body = response_data
                                response.set_header("Content-Type", "application/json")
                            else:
                                response.json(response_data)
                        else:
                            response.json(response_data)
                    return response
                except HandlerError as e:
                    self.logger.exception(
                        f"Handler error in {route['method']} {route['path']}: {e!s}"
                    )
                    if not response.is_finished():
                        response.set_status(e.status_code)
                        response.json(e.to_dict())
                    return response
                except Exception as e:
                    self.logger.exception(
                        f"Unexpected error in {route['method']} {route['path']}: {e!s}"
                    )
                    if not response.is_finished():
                        response.set_status(500)
                        response.json({"error": "Internal Server Error"})
                    return response
            else:
                path_exists, allowed_methods = self._path_exists_with_different_method(
                    path
                )
                if path_exists:
                    method_error = MethodNotAllowed(path, method, allowed_methods)
                    response.set_status(method_error.status_code)
                    response.json(method_error.to_dict())
                else:
                    route_error = RouteNotFound(path, method)
                    response.set_status(route_error.status_code)
                    response.json(route_error.to_dict())
                return response

        try:
            # Execute middleware chain
            await self.middleware_executor.execute_with_error_handling(
                request, response, path, final_handler
            )

            # Send response
            await send_response(send, response)

        except Exception as e:
            self.logger.exception(f"Unhandled error: {e!s}")
            await send_error_response(send, 500, "Internal Server Error")

    # OpenAPI Integration Methods

    def generate_openapi_spec(
        self,
        title: str = "Artanis API",
        version: str = "1.0.0",
        description: str = "API built with Artanis framework",
    ) -> dict[str, Any]:
        """Generate OpenAPI specification from registered routes.

        Args:
            title: API title
            version: API version
            description: API description

        Returns:
            OpenAPI specification dictionary

        Example:
            ```python
            spec = app.generate_openapi_spec(
                title="My API",
                version="2.0.0",
                description="A comprehensive REST API"
            )
            ```
        """
        try:
            from artanis.openapi import OpenAPIGenerator

            generator = OpenAPIGenerator()
            self._openapi_spec = generator.generate_spec(
                self, title, version, description
            )
            return self._openapi_spec.to_dict()
        except ImportError:
            msg = (
                "OpenAPI functionality requires the openapi package. "
                "Install with: pip install 'artanis[openapi]'"
            )
            raise ImportError(msg)

    def serve_docs(
        self,
        docs_path: str = "/docs",
        redoc_path: str = "/redoc",
        openapi_path: str = "/openapi.json",
        auto_generate: bool = True,
    ) -> None:
        """Enable interactive API documentation endpoints.

        Args:
            docs_path: Path for Swagger UI documentation
            redoc_path: Path for ReDoc documentation
            openapi_path: Path for OpenAPI JSON specification
            auto_generate: Whether to auto-generate OpenAPI spec if not exists

        Example:
            ```python
            app.serve_docs()  # Enables /docs, /redoc, /openapi.json

            # Custom paths
            app.serve_docs(
                docs_path="/api-docs",
                redoc_path="/api-redoc",
                openapi_path="/api/openapi.json"
            )
            ```
        """
        try:
            from artanis.openapi import OpenAPIDocsManager, OpenAPIGenerator

            # Auto-generate spec if needed
            if auto_generate and self._openapi_spec is None:
                generator = OpenAPIGenerator()
                self._openapi_spec = generator.generate_spec(self)

            if self._openapi_spec is None:
                msg = "No OpenAPI specification available. Call generate_openapi_spec() first."
                raise ValueError(msg)

            # Setup documentation manager
            self._openapi_docs_manager = OpenAPIDocsManager(
                self._openapi_spec,
                docs_path=docs_path,
                redoc_path=redoc_path,
                openapi_path=openapi_path,
            )

            # Register documentation routes
            self._openapi_docs_manager.setup_docs_routes(self)

            self.logger.info("OpenAPI documentation enabled:")
            self.logger.info(f"  Swagger UI: {docs_path}")
            self.logger.info(f"  ReDoc UI: {redoc_path}")
            self.logger.info(f"  OpenAPI JSON: {openapi_path}")

        except ImportError:
            msg = (
                "OpenAPI functionality requires the openapi package. "
                "Install with: pip install 'artanis[openapi]'"
            )
            raise ImportError(msg)

    def export_openapi(
        self,
        file_path: str,
        format_type: str = "json",
        auto_generate: bool = True,
    ) -> None:
        """Export OpenAPI specification to a file.

        Args:
            file_path: Path where to save the specification
            format_type: Export format ("json" or "yaml")
            auto_generate: Whether to auto-generate spec if not exists

        Example:
            ```python
            app.export_openapi("api.json")
            app.export_openapi("api.yaml", format_type="yaml")
            ```
        """
        try:
            from artanis.openapi import OpenAPIGenerator

            # Auto-generate spec if needed
            if auto_generate and self._openapi_spec is None:
                generator = OpenAPIGenerator()
                self._openapi_spec = generator.generate_spec(self)

            if self._openapi_spec is None:
                msg = "No OpenAPI specification available. Call generate_openapi_spec() first."
                raise ValueError(msg)

            # Export to file
            from pathlib import Path

            with Path(file_path).open("w", encoding="utf-8") as f:
                if format_type.lower() == "yaml":
                    try:
                        import yaml

                        yaml.dump(
                            self._openapi_spec.to_dict(), f, default_flow_style=False
                        )
                    except ImportError:
                        msg = "YAML export requires PyYAML: pip install PyYAML"
                        raise ImportError(msg)
                else:
                    f.write(self._openapi_spec.to_json())

            self.logger.info(f"OpenAPI specification exported to: {file_path}")

        except ImportError:
            msg = (
                "OpenAPI functionality requires the openapi package. "
                "Install with: pip install 'artanis[openapi]'"
            )
            raise ImportError(msg)

    def add_openapi_metadata(
        self,
        title: str | None = None,
        version: str | None = None,
        description: str | None = None,
        servers: list[dict[str, str]] | None = None,
        tags: list[dict[str, str]] | None = None,
        security_schemes: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Add metadata to OpenAPI specification.

        Args:
            title: API title
            version: API version
            description: API description
            servers: List of server objects
            tags: List of tag objects
            security_schemes: Security scheme definitions

        Example:
            ```python
            app.add_openapi_metadata(
                title="My API",
                version="2.0.0",
                description="A comprehensive REST API",
                servers=[
                    {"url": "https://api.example.com", "description": "Production"},
                    {"url": "https://staging-api.example.com", "description": "Staging"}
                ],
                tags=[
                    {"name": "users", "description": "User operations"},
                    {"name": "auth", "description": "Authentication"}
                ],
                security_schemes={
                    "bearer": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            )
            ```
        """
        try:
            from artanis.openapi import OpenAPISpec

            # Create or update spec
            if self._openapi_spec is None:
                self._openapi_spec = OpenAPISpec(
                    title=title or "Artanis API",
                    version=version or "1.0.0",
                    description=description or "API built with Artanis framework",
                )
            else:
                if title:
                    self._openapi_spec.title = title
                if version:
                    self._openapi_spec.version = version
                if description:
                    self._openapi_spec.description = description

            # Add servers
            if servers:
                for server in servers:
                    self._openapi_spec.add_server(
                        server["url"], server.get("description", "")
                    )

            # Add tags
            if tags:
                for tag in tags:
                    self._openapi_spec.add_tag(tag["name"], tag.get("description", ""))

            # Add security schemes
            if security_schemes:
                for name, scheme in security_schemes.items():
                    self._openapi_spec.add_security_scheme(
                        name,
                        scheme["type"],
                        **{k: v for k, v in scheme.items() if k != "type"},
                    )

        except ImportError:
            msg = (
                "OpenAPI functionality requires the openapi package. "
                "Install with: pip install 'artanis[openapi]'"
            )
            raise ImportError(msg)

    def add_openapi_validation(
        self,
        validate_requests: bool = True,
        validate_responses: bool = False,
        strict_mode: bool = False,
    ) -> None:
        """Add OpenAPI request/response validation middleware.

        Args:
            validate_requests: Whether to validate incoming requests
            validate_responses: Whether to validate outgoing responses
            strict_mode: Whether to enforce strict validation

        Example:
            ```python
            # Basic request validation
            app.add_openapi_validation()

            # Strict validation for both requests and responses
            app.add_openapi_validation(
                validate_requests=True,
                validate_responses=True,
                strict_mode=True
            )
            ```
        """
        try:
            from artanis.openapi import OpenAPIGenerator, ValidationMiddleware

            # Generate spec if not exists
            if self._openapi_spec is None:
                generator = OpenAPIGenerator()
                self._openapi_spec = generator.generate_spec(self)

            # Add validation middleware
            validation_middleware = ValidationMiddleware(
                self._openapi_spec,
                validate_requests=validate_requests,
                validate_responses=validate_responses,
                strict_mode=strict_mode,
            )

            self.use(validation_middleware)

            self.logger.info("OpenAPI validation middleware enabled")
            if validate_requests:
                self.logger.info("  Request validation: enabled")
            if validate_responses:
                self.logger.info("  Response validation: enabled")
            if strict_mode:
                self.logger.info("  Strict mode: enabled")

        except ImportError:
            msg = (
                "OpenAPI functionality requires the openapi package. "
                "Install with: pip install 'artanis[openapi]'"
            )
            raise ImportError(msg)
