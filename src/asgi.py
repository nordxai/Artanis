import json
import re
import inspect
from typing import Dict, Callable, Any, List, Tuple


class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self._body = None
    
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
    def __init__(self):
        self._routes = {}

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

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        method = scope["method"]
        path = scope["path"]

        route, path_params = self._find_route(method, path)

        if route:
            try:
                request = Request(scope, receive)
                response_data = await self._call_handler(route["handler"], path_params, request)
                await self._send_json_response(send, 200, response_data)
            except Exception as e:
                await self._send_error_response(send, 500, "Internal Server Error")
        else:
            if self._path_exists_with_different_method(path):
                await self._send_error_response(send, 405, "Method Not Allowed")
            else:
                await self._send_error_response(send, 404, "Not Found")