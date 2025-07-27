"""Tests for Artanis routing module.

This module contains comprehensive tests for the routing functionality
including route registration, path matching, parameter extraction,
and subrouting capabilities.
"""

import pytest

from artanis import App, Router
from artanis.routing import Route


class TestRoute:
    """Test Route class functionality."""

    def test_route_creation(self):
        """Test Route object creation."""

        def handler():
            return {"message": "test"}

        route = Route("GET", "/test", handler)

        assert route.method == "GET"
        assert route.path == "/test"
        assert route.handler == handler
        assert route.middleware == []

    def test_route_creation_with_middleware(self):
        """Test Route object creation with middleware."""

        def handler():
            return {"message": "test"}

        def middleware(request, response, next_func):
            return next_func(request)

        route = Route("POST", "/api/test", handler, [middleware])

        assert route.method == "POST"
        assert route.path == "/api/test"
        assert route.handler == handler
        assert route.middleware == [middleware]

    def test_route_path_matching_simple(self):
        """Test simple path matching without parameters."""

        def handler():
            return {"message": "test"}

        route = Route("GET", "/test", handler)

        # Should match exact path
        params = route.match("/test")
        assert params == {}

        # Should not match different path
        params = route.match("/different")
        assert params is None

    def test_route_path_matching_with_parameters(self):
        """Test path matching with parameters."""

        def handler():
            return {"message": "test"}

        route = Route("GET", "/users/{user_id}", handler)

        # Should match and extract parameters
        params = route.match("/users/123")
        assert params == {"user_id": "123"}

        # Should not match different structure
        params = route.match("/users")
        assert params is None

        params = route.match("/users/123/posts")
        assert params is None

    def test_route_path_matching_multiple_parameters(self):
        """Test path matching with multiple parameters."""

        def handler():
            return {"message": "test"}

        route = Route("GET", "/users/{user_id}/posts/{post_id}", handler)

        # Should match and extract all parameters
        params = route.match("/users/123/posts/456")
        assert params == {"user_id": "123", "post_id": "456"}

        # Should not match partial paths
        params = route.match("/users/123")
        assert params is None

    def test_route_to_dict(self):
        """Test Route to_dict method for compatibility."""

        def handler():
            return {"message": "test"}

        route = Route("GET", "/test", handler)
        route_dict = route.to_dict()

        assert route_dict["method"] == "GET"
        assert route_dict["path"] == "/test"
        assert route_dict["handler"] == handler
        assert "pattern" in route_dict


class TestRouter:
    """Test Router class functionality."""

    def test_router_creation(self):
        """Test Router object creation."""
        router = Router()

        assert router.prefix == ""
        assert router.routes == {}
        assert router.subrouters == {}

    def test_router_creation_with_prefix(self):
        """Test Router object creation with prefix."""
        router = Router("/api")

        assert router.prefix == "/api"

    def test_router_get_route_registration(self):
        """Test GET route registration."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.get("/test", handler)

        assert "/test" in router.routes
        assert "GET" in router.routes["/test"]
        assert router.routes["/test"]["GET"].handler == handler

    def test_router_multiple_http_methods(self):
        """Test registration of multiple HTTP methods."""
        router = Router()

        def get_handler():
            return {"method": "GET"}

        def post_handler():
            return {"method": "POST"}

        def put_handler():
            return {"method": "PUT"}

        def delete_handler():
            return {"method": "DELETE"}

        def patch_handler():
            return {"method": "PATCH"}

        def options_handler():
            return {"method": "OPTIONS"}

        router.get("/test", get_handler)
        router.post("/test", post_handler)
        router.put("/test", put_handler)
        router.delete("/test", delete_handler)
        router.patch("/test", patch_handler)
        router.options("/test", options_handler)

        assert len(router.routes["/test"]) == 6
        assert router.routes["/test"]["GET"].handler == get_handler
        assert router.routes["/test"]["POST"].handler == post_handler
        assert router.routes["/test"]["PUT"].handler == put_handler
        assert router.routes["/test"]["DELETE"].handler == delete_handler
        assert router.routes["/test"]["PATCH"].handler == patch_handler
        assert router.routes["/test"]["OPTIONS"].handler == options_handler

    def test_router_path_normalization(self):
        """Test path normalization with prefixes."""
        router = Router("/api/v1")

        def handler():
            return {"message": "test"}

        router.get("/users", handler)
        router.get("posts", handler)  # Without leading slash

        assert "/api/v1/users" in router.routes
        assert "/api/v1/posts" in router.routes

    def test_router_find_route_simple(self):
        """Test finding simple routes."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.get("/test", handler)

        route, params, source_router = router.find_route("GET", "/test")
        assert route is not None
        assert route.handler == handler
        assert params == {}
        assert source_router == router

    def test_router_find_route_with_parameters(self):
        """Test finding routes with parameters."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.get("/users/{user_id}", handler)

        route, params, source_router = router.find_route("GET", "/users/123")
        assert route is not None
        assert route.handler == handler
        assert params == {"user_id": "123"}

    def test_router_find_route_not_found(self):
        """Test route not found scenario."""
        router = Router()

        route, params, source_router = router.find_route("GET", "/nonexistent")
        assert route is None
        assert params == {}
        assert source_router is None

    def test_router_get_allowed_methods(self):
        """Test getting allowed methods for a path."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.get("/test", handler)
        router.post("/test", handler)
        router.put("/test", handler)

        allowed_methods = router.get_allowed_methods("/test")
        assert set(allowed_methods) == {"GET", "POST", "PUT"}

    def test_router_get_all_routes(self):
        """Test getting all routes."""
        router = Router()

        def handler1():
            return {"message": "test1"}

        def handler2():
            return {"message": "test2"}

        router.get("/test1", handler1)
        router.post("/test2", handler2)

        all_routes = router.get_all_routes()
        assert len(all_routes) == 2

        paths = [route["path"] for route in all_routes]
        assert "/test1" in paths
        assert "/test2" in paths


class TestSubrouting:
    """Test subrouting functionality."""

    def test_router_mounting(self):
        """Test mounting a subrouter."""
        main_router = Router()
        sub_router = Router()

        def handler():
            return {"message": "sub"}

        sub_router.get("/test", handler)
        main_router.mount("/api", sub_router)

        assert "/api" in main_router.subrouters
        assert main_router.subrouters["/api"] == sub_router
        assert sub_router.prefix == "/api"

    def test_subrouter_route_resolution(self):
        """Test resolving routes through subrouters."""
        main_router = Router()
        sub_router = Router()

        def sub_handler():
            return {"message": "sub"}

        def main_handler():
            return {"message": "main"}

        # Add route to main router
        main_router.get("/main", main_handler)

        # Add route to subrouter and mount it
        sub_router.get("/test", sub_handler)
        main_router.mount("/api", sub_router)

        # Test main route
        route, params, source_router = main_router.find_route("GET", "/main")
        assert route is not None
        assert route.handler == main_handler

        # Test subroute
        route, params, source_router = main_router.find_route("GET", "/api/test")
        assert route is not None
        assert route.handler == sub_handler
        assert source_router == sub_router

    def test_nested_subrouting(self):
        """Test nested subrouting."""
        main_router = Router()
        api_router = Router()
        v1_router = Router()

        def handler():
            return {"message": "nested"}

        # Create nested structure: main -> /api -> /v1
        v1_router.get("/users", handler)
        api_router.mount("/v1", v1_router)
        main_router.mount("/api", api_router)

        # Should find route at /api/v1/users
        route, params, source_router = main_router.find_route("GET", "/api/v1/users")
        assert route is not None
        assert route.handler == handler

    def test_subrouter_with_parameters(self):
        """Test subrouter with parameterized paths."""
        main_router = Router()
        user_router = Router()

        def get_profile():
            return {"action": "get_profile"}

        def update_profile():
            return {"action": "update_profile"}

        user_router.get("/", get_profile)
        user_router.put("/", update_profile)
        main_router.mount("/users/{user_id}", user_router)

        # Test GET /users/123/ (note: without trailing slash first)
        route, params, source_router = main_router.find_route("GET", "/users/123")
        if route is None:
            # Try with trailing slash if first attempt fails
            route, params, source_router = main_router.find_route("GET", "/users/123/")
        assert route is not None
        assert route.handler == get_profile
        assert params == {"user_id": "123"}

        # Test PUT /users/456/
        route, params, source_router = main_router.find_route("PUT", "/users/456")
        if route is None:
            route, params, source_router = main_router.find_route("PUT", "/users/456/")
        assert route is not None
        assert route.handler == update_profile
        assert params == {"user_id": "456"}

    def test_subrouter_get_all_routes(self):
        """Test getting all routes including subrouter routes."""
        main_router = Router()
        sub_router = Router()

        def main_handler():
            return {"message": "main"}

        def sub_handler():
            return {"message": "sub"}

        main_router.get("/main", main_handler)
        sub_router.get("/sub", sub_handler)
        main_router.mount("/api", sub_router)

        all_routes = main_router.get_all_routes()
        assert len(all_routes) == 2

        paths = [route["path"] for route in all_routes]
        assert "/main" in paths
        assert "/api/sub" in paths


class TestAppIntegration:
    """Test integration of Router with App class."""

    def test_app_api_compatibility(self):
        """Test that existing App API still works."""
        app = App()

        def handler():
            return {"message": "test"}

        # App API should still work
        app.get("/test", handler)
        app.post("/test", handler)

        # Routes should be accessible via routes property
        routes = app.routes
        assert any(route["path"] == "/test" for route in routes)

    def test_app_router_property(self):
        """Test App.router property for new functionality."""
        app = App()

        def handler():
            return {"message": "test"}

        # New Router API should work
        app.router.get("/api/test", handler)

        # Route should be findable
        route, params, source_router = app.router.find_route("GET", "/api/test")
        assert route is not None
        assert route.handler == handler

    def test_app_mount_functionality(self):
        """Test App.mount method."""
        app = App()
        api_router = Router()

        def handler():
            return {"message": "api"}

        api_router.get("/users", handler)
        app.mount("/api", api_router)

        # Should be able to find mounted route
        route, params, source_router = app.router.find_route("GET", "/api/users")
        assert route is not None
        assert route.handler == handler

    def test_app_mixed_routing_styles(self):
        """Test mixing old and new routing styles."""
        app = App()
        api_router = Router()

        def old_handler():
            return {"message": "old"}

        def new_handler():
            return {"message": "new"}

        def api_handler():
            return {"message": "api"}

        # Old style
        app.get("/old", old_handler)

        # New style via app.router
        app.router.get("/new", new_handler)

        # Subrouter style
        api_router.get("/test", api_handler)
        app.mount("/api", api_router)

        # All should work
        old_route, _ = app._find_route("GET", "/old")
        assert old_route is not None

        new_route, _ = app._find_route("GET", "/new")
        assert new_route is not None

        api_route, _ = app._find_route("GET", "/api/test")
        assert api_route is not None

    def test_app_route_property_compatibility(self):
        """Test that app.routes property works with new Router."""
        app = App()

        def handler1():
            return {"message": "1"}

        def handler2():
            return {"message": "2"}

        # Mix of old and new styles
        app.get("/old", handler1)
        app.router.register_route("GET", "/new", handler2)

        routes = app.routes

        # Should include both routes
        assert len(routes) >= 2
        paths = [route["path"] for route in routes]
        assert "/old" in paths
        assert "/new" in paths


class TestAllMethod:
    """Test .all() method functionality."""

    def test_router_all_method_registration(self):
        """Test router.all() registers all HTTP methods."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.all("/test", handler)

        # Should have all standard HTTP methods registered
        assert "/test" in router.routes
        methods = router.routes["/test"]
        expected_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        for method in expected_methods:
            assert method in methods
            assert methods[method].handler == handler

    def test_router_all_method_with_middleware(self):
        """Test router.all() with middleware."""
        router = Router()

        def handler():
            return {"message": "test"}

        def middleware(request, response, next_func):
            return next_func(request)

        router.all("/test", handler, [middleware])

        # All methods should have the middleware
        methods = router.routes["/test"]
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]:
            assert methods[method].middleware == [middleware]

    def test_router_all_method_with_parameters(self):
        """Test router.all() with path parameters."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.all("/users/{user_id}", handler)

        # Test each method can match and extract parameters
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        for method in methods:
            route, params, source_router = router.find_route(method, "/users/123")
            assert route is not None
            assert params == {"user_id": "123"}
            assert route.handler == handler

    def test_app_all_method_registration(self):
        """Test app.all() registers all HTTP methods."""
        from artanis import App

        app = App()

        def handler():
            return {"message": "test"}

        app.all("/test", handler)

        # Should have all methods in routes
        routes = app.routes
        test_routes = [r for r in routes if r["path"] == "/test"]
        assert len(test_routes) == 6  # 6 HTTP methods

        methods = [r["method"] for r in test_routes]
        expected_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        for method in expected_methods:
            assert method in methods

    def test_app_all_method_integration(self):
        """Test app.all() integration with route finding."""
        from artanis import App

        app = App()

        def handler():
            return {"message": "test"}

        app.all("/api/{resource_id}", handler)

        # Test that all methods can be found
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        for method in methods:
            route, params = app._find_route(method, "/api/123")
            assert route is not None
            assert params == {"resource_id": "123"}
            assert route["handler"] == handler

    def test_all_method_mixed_with_specific_methods(self):
        """Test .all() method mixed with specific method registrations."""
        router = Router()

        def all_handler():
            return {"type": "all"}

        def get_handler():
            return {"type": "get"}

        # Register all methods first
        router.all("/test", all_handler)

        # Override GET with specific handler
        router.get("/test", get_handler)

        # GET should use the specific handler
        route, params, source_router = router.find_route("GET", "/test")
        assert route.handler == get_handler

        # Other methods should use the all handler
        for method in ["POST", "PUT", "DELETE", "PATCH", "OPTIONS"]:
            route, params, source_router = router.find_route(method, "/test")
            assert route.handler == all_handler

    def test_all_method_get_allowed_methods(self):
        """Test get_allowed_methods works with .all() routes."""
        router = Router()

        def handler():
            return {"message": "test"}

        router.all("/test", handler)

        allowed_methods = router.get_allowed_methods("/test")
        expected_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        assert set(allowed_methods) == set(expected_methods)

    def test_all_method_subrouter(self):
        """Test .all() method in subrouters."""
        main_router = Router()
        sub_router = Router()

        def handler():
            return {"message": "sub"}

        sub_router.all("/resource", handler)
        main_router.mount("/api", sub_router)

        # Test all methods work through subrouter
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        for method in methods:
            route, params, source_router = main_router.find_route(
                method, "/api/resource"
            )
            assert route is not None
            assert route.handler == handler
            assert source_router == sub_router
