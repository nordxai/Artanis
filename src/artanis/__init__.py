import json
import re
import inspect
from typing import Dict, Callable, Any, List, Tuple
from .middleware import MiddlewareManager, MiddlewareExecutor, Response
from .logging import logger, ArtanisLogger, RequestLoggingMiddleware


class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self._body = None
        self.path_params = {}  # For middleware access to path parameters
        self.headers = dict(scope.get("headers", []))
    
    async def body(self):
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
    
    async def json(self):
        body = await self.body()
        return json.loads(body.decode())

class RoutesDict(dict):
    def __init__(self, all_routes):
        super().__init__()
        self._all_routes = all_routes

    def values(self):
        return self._all_routes

class App:
    def __init__(self, enable_request_logging: bool = True):
        self._routes = {}
        self.middleware_manager = MiddlewareManager()
        self.middleware_executor = MiddlewareExecutor(self.middleware_manager)
        self.logger = logger
        
        # Add request logging middleware by default
        if enable_request_logging:
            self.use(RequestLoggingMiddleware())

    @property
    def routes(self):
        # Return flattened view for test compatibility
        flattened = {}
        all_routes = []  # For multiple method test

        for path, methods in self._routes.items():
            for method, route_data in methods.items():
                # For simple tests - last method wins
                flattened[path] = route_data
                # Keep all routes for values() iteration
                all_routes.append(route_data)
        # Add a custom values() method that returns all routes
        result = RoutesDict(all_routes)
        result.update(flattened)
        return result

    def _register_route(self, method: str, path: str, handler: Callable):
        if path not in self._routes:
            self._routes[path] = {}
        self._routes[path][method] = {
            "handler": handler,
            "method": method,
            "path": path,
            "pattern": self._compile_path_pattern(path)
        }
        self.logger.debug(f"Registered {method} route: {path}")

    def _compile_path_pattern(self, path: str) -> re.Pattern:
        pattern = re.escape(path)
        pattern = pattern.replace(r'\{', '(?P<').replace(r'\}', r'>[^/]+)')
        pattern = f"^{pattern}$"
        return re.compile(pattern)

    def get(self, path: str, handler: Callable):
        self._register_route("GET", path, handler)

    def post(self, path: str, handler: Callable):
        self._register_route("POST", path, handler)

    def put(self, path: str, handler: Callable):
        self._register_route("PUT", path, handler)

    def delete(self, path: str, handler: Callable):
        self._register_route("DELETE", path, handler)
    
    def use(self, path_or_middleware, middleware=None):
        """Register middleware - Express style app.use() API"""
        if middleware is None:
            # app.use(middleware_func) - Global middleware
            self.middleware_manager.add_global(path_or_middleware)
        else:
            # app.use("/path", middleware_func) - Path-based middleware
            self.middleware_manager.add_path(path_or_middleware, middleware)
    
    # Properties for backward compatibility with tests
    @property
    def global_middleware(self):
        return self.middleware_manager.global_middleware
    
    @property
    def path_middleware(self):
        return self.middleware_manager.path_middleware

    def _find_route(self, method: str, path: str) -> Tuple[Dict, Dict]:
        for route_path, methods in self._routes.items():
            if method in methods:
                route_info = methods[method]
                match = route_info["pattern"].match(path)
                if match:
                    return route_info, match.groupdict()
        return None, {}

    def _path_exists_with_different_method(self, path: str) -> bool:
        for route_path, methods in self._routes.items():
            for method, route_info in methods.items():
                match = route_info["pattern"].match(path)
                if match:
                    return True
        return False

    async def _call_handler(self, handler: Callable, path_params: dict, request: Request = None):
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())

        args = []
        for param in params:
            if param in path_params:
                args.append(path_params[param])
            elif param == "request" and request:
                args.append(request)

        if inspect.iscoroutinefunction(handler):
            return await handler(*args)
        else:
            return handler(*args)

    async def _send_json_response(self, send, status: int, data: Any):
        response_body = json.dumps(data).encode()

        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(response_body)).encode()],
            ],
        })

        await send({
            "type": "http.response.body",
            "body": response_body,
        })

    async def _send_error_response(self, send, status: int, message: str):
        await self._send_json_response(send, status, {"error": message})
    
    async def _send_response(self, send, response: Response):
        """Send response using middleware Response object"""
        response_body = response.to_bytes()
        
        # Build headers list, ensuring content-length is set
        headers = response.get_headers_list()
        
        # Add content-length if not already set
        content_length_set = any(name.lower() == b"content-length" for name, _ in headers)
        if not content_length_set:
            headers.append((b"content-length", str(len(response_body)).encode()))
        
        # Add content-type if not already set and body is JSON
        content_type_set = any(name.lower() == b"content-type" for name, _ in headers)
        if not content_type_set and response.body is not None:
            if isinstance(response.body, (dict, list)):
                headers.append((b"content-type", b"application/json"))

        await send({
            "type": "http.response.start",
            "status": response.status,
            "headers": headers,
        })

        await send({
            "type": "http.response.body",
            "body": response_body,
        })

    async def __call__(self, scope, receive, send):
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
        async def final_handler(req):            
            if route:
                try:
                    response_data = await self._call_handler(route["handler"], path_params, req)
                    if not response.is_finished():
                        response.json(response_data)
                    return response
                except Exception as e:
                    self.logger.error(f"Handler error in {route['method']} {route['path']}: {str(e)}")
                    if not response.is_finished():
                        response.set_status(500)
                        response.json({"error": "Internal Server Error"})
                    return response
            else:
                if self._path_exists_with_different_method(path):
                    response.set_status(405)
                    response.json({"error": "Method Not Allowed"})
                else:
                    response.set_status(404)
                    response.json({"error": "Not Found"})
                return response

        try:
            # Execute middleware chain
            result = await self.middleware_executor.execute_with_error_handling(
                request, response, path, final_handler
            )
            
            # Send response
            await self._send_response(send, response)
            
        except Exception as e:
            self.logger.error(f"Unhandled error: {str(e)}")
            await self._send_error_response(send, 500, "Internal Server Error")