from unittest.mock import AsyncMock

import pytest


class TestASGIFramework:
    """Test cases for ASGI framework with named routes"""

    def test_create_app_instance(self):
        """Test that we can create an app instance"""
        from artanis import App

        app = App()
        assert app is not None

    def test_register_get_route(self):
        """Test registering a GET route using app.get(path, handler)"""
        from artanis import App

        app = App()

        async def hello_handler():
            return {"message": "Hello World"}

        app.get("/hello", hello_handler)

        assert "/hello" in app.routes
        assert app.routes["/hello"]["method"] == "GET"
        assert app.routes["/hello"]["handler"] == hello_handler

    def test_register_post_route(self):
        """Test registering a POST route using app.post(path, handler)"""
        from artanis import App

        app = App()

        async def create_user_handler():
            return {"message": "User created"}

        app.post("/users", create_user_handler)

        assert "/users" in app.routes
        assert app.routes["/users"]["method"] == "POST"
        assert app.routes["/users"]["handler"] == create_user_handler

    def test_multiple_routes_same_path_different_methods(self):
        """Test registering multiple routes with same path but different methods"""
        from artanis import App

        app = App()

        async def get_users_handler():
            return {"users": []}

        async def create_user_handler():
            return {"message": "User created"}

        app.get("/users", get_users_handler)
        app.post("/users", create_user_handler)

        # Should have separate route entries for GET and POST
        routes_for_users = [r for r in app.routes.values() if r["path"] == "/users"]
        assert len(routes_for_users) == 2
        methods = [r["method"] for r in routes_for_users]
        assert "GET" in methods
        assert "POST" in methods

    @pytest.mark.asyncio
    async def test_asgi_application_callable(self):
        """Test that app can be called as ASGI application"""
        from artanis import App

        app = App()

        async def test_handler():
            return {"test": True}

        app.get("/test", test_handler)

        scope = {"type": "http", "method": "GET", "path": "/test", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Should have called send at least once
        assert send.called

    @pytest.mark.asyncio
    async def test_route_handler_execution(self):
        """Test that route handlers are executed correctly"""
        from artanis import App

        app = App()

        async def hello_handler():
            return {"message": "Hello World"}

        app.get("/hello", hello_handler)

        scope = {"type": "http", "method": "GET", "path": "/hello", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Check that response was sent
        send.assert_called()
        # Verify the response contains our expected data
        response_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.body"
        ]
        assert len(response_calls) > 0

    @pytest.mark.asyncio
    async def test_404_for_unregistered_route(self):
        """Test 404 response for unregistered routes"""
        from artanis import App

        app = App()

        scope = {"type": "http", "method": "GET", "path": "/nonexistent", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Should send 404 status
        status_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.start"
        ]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self):
        """Test 405 response for wrong HTTP method"""
        from artanis import App

        app = App()

        async def get_users_handler():
            return {"users": []}

        app.get("/users", get_users_handler)

        scope = {
            "type": "http",
            "method": "POST",  # Wrong method
            "path": "/users",
            "headers": [],
        }
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Should send 405 status
        status_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.start"
        ]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 405

    def test_route_with_path_parameters(self):
        """Test registering routes with path parameters"""
        from artanis import App

        app = App()

        async def get_user_handler(user_id):
            return {"user_id": user_id}

        app.get("/users/{user_id}", get_user_handler)

        assert "/users/{user_id}" in [route["path"] for route in app.routes.values()]

    @pytest.mark.asyncio
    async def test_path_parameter_extraction(self):
        """Test that path parameters are extracted and passed to handlers"""
        from artanis import App

        app = App()

        async def get_user_handler(user_id):
            return {"user_id": user_id}

        app.get("/users/{user_id}", get_user_handler)

        scope = {"type": "http", "method": "GET", "path": "/users/123", "headers": []}
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Should successfully handle the request
        status_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.start"
        ]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 200

    def test_put_route_method(self):
        """Test PUT route method"""
        from artanis import App

        app = App()

        async def update_user_handler(user_id):
            return {"message": f"Updated user {user_id}"}

        app.put("/users/{user_id}", update_user_handler)

        assert any(route["method"] == "PUT" for route in app.routes.values())

    def test_delete_route_method(self):
        """Test DELETE route method"""
        from artanis import App

        app = App()

        async def delete_user_handler(user_id):
            return {"message": f"Deleted user {user_id}"}

        app.delete("/users/{user_id}", delete_user_handler)

        assert any(route["method"] == "DELETE" for route in app.routes.values())

    @pytest.mark.asyncio
    async def test_request_object_passed_to_handler(self):
        """Test that request object is passed to POST handlers"""
        from artanis import App

        app = App()

        async def create_user_handler(request):
            body = await request.json()
            return {"created": body}

        app.post("/users", create_user_handler)

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/users",
            "headers": [(b"content-type", b"application/json")],
        }

        # Mock receive to return JSON body
        receive = AsyncMock()
        receive.side_effect = [
            {"type": "http.request", "body": b'{"name": "John"}', "more_body": False}
        ]
        send = AsyncMock()

        await app(scope, receive, send)

        # Should handle the request successfully
        status_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.start"
        ]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 200

    def test_multiple_path_parameters(self):
        """Test routes with multiple path parameters"""
        from artanis import App

        app = App()

        async def get_user_post_handler(user_id, post_id):
            return {"user_id": user_id, "post_id": post_id}

        app.get("/users/{user_id}/posts/{post_id}", get_user_post_handler)

        route_paths = [route["path"] for route in app.routes.values()]
        assert "/users/{user_id}/posts/{post_id}" in route_paths

    @pytest.mark.asyncio
    async def test_multiple_path_parameters_extraction(self):
        """Test extraction of multiple path parameters"""
        from artanis import App

        app = App()

        async def get_user_post_handler(user_id, post_id):
            return {"user_id": user_id, "post_id": post_id}

        app.get("/users/{user_id}/posts/{post_id}", get_user_post_handler)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/users/123/posts/456",
            "headers": [],
        }
        receive = AsyncMock()
        send = AsyncMock()

        await app(scope, receive, send)

        # Should successfully handle the request
        status_calls = [
            call
            for call in send.call_args_list
            if call[0][0].get("type") == "http.response.start"
        ]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 200

    def test_handler_with_mixed_parameters(self):
        """Test handler that receives both path params and request object"""
        from artanis import App

        app = App()

        async def update_user_handler(user_id, request):
            body = await request.json()
            return {"user_id": user_id, "updated": body}

        app.put("/users/{user_id}", update_user_handler)

        route_paths = [route["path"] for route in app.routes.values()]
        assert "/users/{user_id}" in route_paths
