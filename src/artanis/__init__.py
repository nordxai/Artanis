"""Artanis ASGI Web Framework.

A lightweight, Express.js-inspired ASGI web framework for Python with
middleware support, path parameters, and comprehensive logging.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Awaitable, Callable

from ._version import (
    VERSION as VERSION,
)
from ._version import (
    __version__ as __version__,
)
from ._version import (
    get_version as get_version,
)
from ._version import (
    get_version_info as get_version_info,
)
from ._version import (
    version_info as version_info,
)
from .exceptions import (
    ArtanisException as ArtanisException,
)
from .exceptions import (
    AuthenticationError as AuthenticationError,
)
from .exceptions import (
    AuthorizationError as AuthorizationError,
)
from .exceptions import (
    ConfigurationError as ConfigurationError,
)
from .exceptions import (
    HandlerError as HandlerError,
)
from .exceptions import (
    MethodNotAllowed as MethodNotAllowed,
)
from .exceptions import (
    MiddlewareError as MiddlewareError,
)
from .exceptions import (
    RateLimitError as RateLimitError,
)
from .exceptions import (
    RouteNotFound as RouteNotFound,
)
from .exceptions import (
    ValidationError as ValidationError,
)
from .logging import (
    ArtanisLogger as ArtanisLogger,
)
from .logging import (
    RequestLoggingMiddleware as RequestLoggingMiddleware,
)
from .logging import (
    logger,
)
from .middleware import (
    ExceptionHandlerMiddleware as ExceptionHandlerMiddleware,
)
from .middleware import (
    MiddlewareExecutor,
    MiddlewareManager,
    Response,
)
from .middleware import (
    ValidationMiddleware as ValidationMiddleware,
)
from .routing import (
    Route as Route,
)
from .routing import (
    Router as Router,
)


class Request:
    """HTTP request object providing access to request data.

    This class encapsulates the ASGI scope and receive callable to provide
    a convenient interface for accessing request data including headers,
    body content, and path parameters.

    Args:
        scope: ASGI scope dictionary containing request metadata
        receive: ASGI receive callable for getting request body

    Attributes:
        scope: The ASGI scope dictionary
        receive: The ASGI receive callable
        path_params: Dictionary of extracted path parameters
        headers: Dictionary of request headers
    """

    def __init__(
        self, scope: dict[str, Any], receive: Callable[[], Awaitable[dict[str, Any]]]
    ) -> None:
        self.scope = scope
        self.receive = receive
        self._body: bytes | None = None
        self.path_params: dict[
            str, str
        ] = {}  # For middleware access to path parameters
        self.headers: dict[str, str] = dict(scope.get("headers", []))

    async def body(self) -> bytes:
        """Get the request body as bytes.

        Reads and caches the complete request body from the ASGI receive callable.
        The body is cached after the first call to avoid multiple reads.

        Returns:
            The complete request body as bytes
        """
        if self._body is None:
            body_parts = []
            while True:
                message = await self.receive()
                if message["type"] == "http.request":
                    body_parts.append(message.get("body", b""))
                    if not message.get("more_body", False):
                        break
            self._body = b"".join(body_parts)
        return self._body

    async def json(self) -> Any:
        """Parse request body as JSON.

        Reads the request body and parses it as JSON data.

        Returns:
            Parsed JSON data (dict, list, or other JSON-serializable types)

        Raises:
            ValidationError: If the body is not valid JSON
        """
        try:
            body = await self.body()
            return json.loads(body.decode())
        except json.JSONDecodeError as e:
            raise ValidationError(
                message="Invalid JSON in request body",
                field="body",
                value=body.decode() if len(body) < 200 else body.decode()[:200] + "...",
                validation_errors={"json_error": str(e)},
            )


class App:
    """Main Artanis application class.

    The core application class that handles route registration, middleware
    management, and ASGI request processing. Provides an Express.js-inspired
    API for building web applications.

    Args:
        enable_request_logging: Whether to enable automatic request logging

    Attributes:
        middleware_manager: Manages global and path-based middleware
        middleware_executor: Executes middleware chains
        logger: Application logger instance

    Example:
        ```python
        from artanis import App

        app = App()

        @app.get('/hello/{name}')
        async def hello(name: str):
            return {'message': f'Hello, {name}!'}
        ```
    """

    def __init__(self, enable_request_logging: bool = True) -> None:
        self.router = Router()
        self.middleware_manager = MiddlewareManager()
        self.middleware_executor = MiddlewareExecutor(self.middleware_manager)
        self.logger = logger

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

    async def _call_handler(
        self,
        handler: Callable[..., Any],
        path_params: dict[str, str],
        request: Request | None = None,
        route_info: dict[str, Any] | None = None,
    ) -> Any:
        """Call a route handler with appropriate parameters.

        Inspects the handler signature and provides path parameters and
        request object as needed.

        Args:
            handler: Route handler function
            path_params: Extracted path parameters
            request: Request object (optional)
            route_info: Route information for error context (optional)

        Returns:
            Handler response data

        Raises:
            HandlerError: If handler execution fails
        """
        try:
            sig = inspect.signature(handler)
            params = list(sig.parameters.keys())

            args: list[Any] = []
            for param in params:
                if param in path_params:
                    args.append(path_params[param])
                elif param == "request" and request:
                    args.append(request)

            if inspect.iscoroutinefunction(handler):
                return await handler(*args)
            return handler(*args)
        except Exception as e:
            route_path = route_info.get("path") if route_info else None
            method = route_info.get("method") if route_info else None
            raise HandlerError(
                message=f"Handler execution failed: {e!s}",
                route_path=route_path,
                method=method,
                original_error=e,
            )

    async def _send_json_response(
        self, send: Callable[..., Any], status: int, data: Any
    ) -> None:
        """Send a JSON response.

        Args:
            send: ASGI send callable
            status: HTTP status code
            data: Data to serialize as JSON
        """
        response_body = json.dumps(data).encode()

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(response_body)).encode()],
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": response_body,
            }
        )

    async def _send_error_response(
        self, send: Callable[..., Any], status: int, message: str
    ) -> None:
        """Send an error response.

        Args:
            send: ASGI send callable
            status: HTTP status code
            message: Error message
        """
        await self._send_json_response(send, status, {"error": message})

    async def _send_response(
        self, send: Callable[..., Any], response: Response
    ) -> None:
        """Send response using middleware Response object.

        Args:
            send: ASGI send callable
            response: Response object with headers, status, and body
        """
        response_body = response.to_bytes()

        # Build headers list, ensuring content-length is set
        headers = response.get_headers_list()

        # Add content-length if not already set
        content_length_set = any(
            name.lower() == b"content-length" for name, _ in headers
        )
        if not content_length_set:
            headers.append((b"content-length", str(len(response_body)).encode()))

        # Add content-type if not already set and body is JSON
        content_type_set = any(name.lower() == b"content-type" for name, _ in headers)
        if not content_type_set and response.body is not None:
            if isinstance(response.body, (dict, list)):
                headers.append((b"content-type", b"application/json"))

        await send(
            {
                "type": "http.response.start",
                "status": response.status,
                "headers": headers,
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": response_body,
            }
        )

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        """ASGI application entry point.

        Handles incoming HTTP requests by routing them through the middleware
        chain to the appropriate route handler.

        Args:
            scope: ASGI scope dictionary
            receive: ASGI receive callable
            send: ASGI send callable
        """
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
                    response_data = await self._call_handler(
                        route["handler"], path_params, req, route
                    )
                    if not response.is_finished():
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
            await self._send_response(send, response)

        except Exception as e:
            self.logger.exception(f"Unhandled error: {e!s}")
            await self._send_error_response(send, 500, "Internal Server Error")
