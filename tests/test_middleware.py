import pytest
import asyncio
from unittest.mock import AsyncMock


class TestMiddleware:
    """Test cases for Middleware with app.use() API"""
    
    # A. Basic Middleware Registration Tests
    
    def test_use_global_middleware(self):
        """Test app.use(middleware_func) registration for global middleware"""
        from artanis import App
        app = App()
        
        async def global_middleware(request, response, next):
            await next()
        
        app.use(global_middleware)
        
        assert hasattr(app, 'global_middleware')
        assert len(app.global_middleware) == 1
        assert app.global_middleware[0] == global_middleware
    
    def test_use_path_middleware(self):
        """Test app.use('/path', middleware_func) registration for path-based middleware"""
        from artanis import App
        app = App()
        
        async def api_middleware(request, response, next):
            await next()
        
        app.use("/api", api_middleware)
        
        assert hasattr(app, 'path_middleware')
        assert "/api" in app.path_middleware
        assert len(app.path_middleware["/api"]) == 1
        assert app.path_middleware["/api"][0] == api_middleware
    
    def test_middleware_storage_separation(self):
        """Test that global and path middleware are stored separately"""
        from artanis import App
        app = App()
        
        async def global_middleware(request, response, next):
            await next()
        
        async def path_middleware(request, response, next):
            await next()
        
        app.use(global_middleware)
        app.use("/admin", path_middleware)
        
        assert len(app.global_middleware) == 1
        assert len(app.path_middleware) == 1
        assert "/admin" in app.path_middleware
        assert global_middleware in app.global_middleware
        assert path_middleware in app.path_middleware["/admin"]
    
    def test_multiple_middleware_same_path(self):
        """Test multiple middleware registered for the same path"""
        from artanis import App
        app = App()
        
        async def middleware1(request, response, next):
            await next()
        
        async def middleware2(request, response, next):
            await next()
        
        app.use("/api", middleware1)
        app.use("/api", middleware2)
        
        assert len(app.path_middleware["/api"]) == 2
        assert app.path_middleware["/api"][0] == middleware1
        assert app.path_middleware["/api"][1] == middleware2
    
    # B. Global Middleware Execution Tests
    
    @pytest.mark.asyncio
    async def test_global_middleware_execution(self):
        """Test that global middleware runs on all routes"""
        from artanis import App
        app = App()
        
        middleware_called = False
        
        async def global_middleware(request, response, next):
            nonlocal middleware_called
            middleware_called = True
            await next()
        
        async def handler():
            return {"message": "Hello"}
        
        app.use(global_middleware)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert middleware_called == True
    
    @pytest.mark.asyncio
    async def test_multiple_global_middleware_order(self):
        """Test execution order for multiple global middleware"""
        from artanis import App
        app = App()
        
        execution_order = []
        
        async def middleware1(request, response, next):
            execution_order.append("middleware1_start")
            await next()
            execution_order.append("middleware1_end")
        
        async def middleware2(request, response, next):
            execution_order.append("middleware2_start")
            await next()
            execution_order.append("middleware2_end")
        
        async def handler():
            execution_order.append("handler")
            return {"message": "Hello"}
        
        app.use(middleware1)
        app.use(middleware2)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Should execute in order: middleware1 -> middleware2 -> handler -> middleware2 -> middleware1
        expected_order = [
            "middleware1_start",
            "middleware2_start", 
            "handler",
            "middleware2_end",
            "middleware1_end"
        ]
        assert execution_order == expected_order
    
    @pytest.mark.asyncio
    async def test_global_middleware_request_modification(self):
        """Test that global middleware can modify request"""
        from artanis import App
        app = App()
        
        async def request_modifier(request, response, next):
            request.custom_header = "added_by_middleware"
            await next()
        
        handler_request = None
        
        async def handler(request):
            nonlocal handler_request
            handler_request = request
            return {"message": "Hello"}
        
        app.use(request_modifier)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert hasattr(handler_request, 'custom_header')
        assert handler_request.custom_header == "added_by_middleware"
    
    @pytest.mark.asyncio
    async def test_global_middleware_response_modification(self):
        """Test that global middleware can modify response"""
        from artanis import App
        app = App()
        
        async def response_modifier(request, response, next):
            await next()
            response.headers["X-Custom-Header"] = "added_by_middleware"
        
        async def handler():
            return {"message": "Hello"}
        
        app.use(response_modifier)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check that custom header was added to response
        header_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert len(header_calls) > 0
        headers = dict(header_calls[0][0][0]["headers"])
        assert b"X-Custom-Header" in headers
        assert headers[b"X-Custom-Header"] == b"added_by_middleware"
    
    # C. Path-Based Middleware Execution Tests
    
    @pytest.mark.asyncio
    async def test_path_middleware_matching(self):
        """Test that path middleware only runs on matching paths"""
        from artanis import App
        app = App()
        
        api_middleware_called = False
        admin_middleware_called = False
        
        async def api_middleware(request, response, next):
            nonlocal api_middleware_called
            api_middleware_called = True
            await next()
        
        async def admin_middleware(request, response, next):
            nonlocal admin_middleware_called
            admin_middleware_called = True
            await next()
        
        async def api_handler():
            return {"api": "response"}
        
        async def other_handler():
            return {"other": "response"}
        
        app.use("/api", api_middleware)
        app.use("/admin", admin_middleware)
        app.get("/api/users", api_handler)
        app.get("/other", other_handler)
        
        # Test API route
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/users",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert api_middleware_called == True
        assert admin_middleware_called == False
        
        # Reset and test other route
        api_middleware_called = False
        admin_middleware_called = False
        
        scope["path"] = "/other"
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert api_middleware_called == False
        assert admin_middleware_called == False
    
    @pytest.mark.asyncio
    async def test_path_middleware_with_parameters(self):
        """Test path middleware works with route parameters like /users/{id}"""
        from artanis import App
        app = App()
        
        user_middleware_called = False
        extracted_user_id = None
        
        async def user_middleware(request, response, next):
            nonlocal user_middleware_called, extracted_user_id
            user_middleware_called = True
            # Should be able to access path parameters
            if hasattr(request, 'path_params'):
                extracted_user_id = request.path_params.get('user_id')
            await next()
        
        async def handler(user_id):
            return {"user_id": user_id}
        
        app.use("/users/{user_id}", user_middleware)
        app.get("/users/{user_id}", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/users/123",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert user_middleware_called == True
        assert extracted_user_id == "123"
    
    @pytest.mark.asyncio
    async def test_nested_path_middleware(self):
        """Test middleware interaction with nested paths like /api and /api/users"""
        from artanis import App
        app = App()
        
        api_middleware_called = False
        users_middleware_called = False
        
        async def api_middleware(request, response, next):
            nonlocal api_middleware_called
            api_middleware_called = True
            await next()
        
        async def users_middleware(request, response, next):
            nonlocal users_middleware_called
            users_middleware_called = True
            await next()
        
        async def handler():
            return {"users": []}
        
        app.use("/api", api_middleware)
        app.use("/api/users", users_middleware)
        app.get("/api/users", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/users",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Both middleware should be called for /api/users
        assert api_middleware_called == True
        assert users_middleware_called == True
    
    @pytest.mark.asyncio
    async def test_path_middleware_execution_order(self):
        """Test execution order within path-specific middleware"""
        from artanis import App
        app = App()
        
        execution_order = []
        
        async def middleware1(request, response, next):
            execution_order.append("path_middleware1")
            await next()
        
        async def middleware2(request, response, next):
            execution_order.append("path_middleware2")
            await next()
        
        async def handler():
            execution_order.append("handler")
            return {"message": "Hello"}
        
        app.use("/api", middleware1)
        app.use("/api", middleware2)
        app.get("/api/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Path middleware should execute in registration order
        assert execution_order == ["path_middleware1", "path_middleware2", "handler"]
    
    # D. Combined Global + Path Middleware Tests
    
    @pytest.mark.asyncio
    async def test_global_and_path_middleware_order(self):
        """Test execution order: Global → Path → Handler → Path → Global"""
        from artanis import App
        app = App()
        
        execution_order = []
        
        async def global_middleware(request, response, next):
            execution_order.append("global_start")
            await next()
            execution_order.append("global_end")
        
        async def path_middleware(request, response, next):
            execution_order.append("path_start")
            await next()
            execution_order.append("path_end")
        
        async def handler():
            execution_order.append("handler")
            return {"message": "Hello"}
        
        app.use(global_middleware)
        app.use("/api", path_middleware)
        app.get("/api/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        expected_order = [
            "global_start",
            "path_start", 
            "handler",
            "path_end",
            "global_end"
        ]
        assert execution_order == expected_order
    
    @pytest.mark.asyncio 
    async def test_middleware_chain_with_route_params(self):
        """Test full middleware chain with path parameters"""
        from artanis import App
        app = App()
        
        middleware_user_id = None
        handler_user_id = None
        
        async def user_middleware(request, response, next):
            nonlocal middleware_user_id
            if hasattr(request, 'path_params'):
                middleware_user_id = request.path_params.get('user_id')
            await next()
        
        async def handler(user_id):
            nonlocal handler_user_id
            handler_user_id = user_id
            return {"user_id": user_id}
        
        app.use("/users/{user_id}", user_middleware)
        app.get("/users/{user_id}", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/users/123",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert middleware_user_id == "123"
        assert handler_user_id == "123"
    
    @pytest.mark.asyncio
    async def test_middleware_early_response(self):
        """Test middleware returning response without calling next()"""
        from artanis import App
        app = App()
        
        handler_called = False
        
        async def auth_middleware(request, response, next):
            # Simulate authentication failure
            if not request.headers.get("Authorization"):
                response.status = 401
                response.body = {"error": "Unauthorized"}
                return  # Don't call next()
            await next()
        
        async def handler():
            nonlocal handler_called
            handler_called = True
            return {"message": "Protected resource"}
        
        app.use("/protected", auth_middleware)
        app.get("/protected", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/protected",
            "headers": []  # No Authorization header
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Handler should not be called
        assert handler_called == False
        
        # Should return 401 status
        status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 401

    # E. Middleware Next() Function Tests

    @pytest.mark.asyncio
    async def test_next_function_continues_chain(self):
        """Test that await next() continues execution chain"""
        from artanis import App
        app = App()
        
        next_called = False
        handler_called = False
        
        async def middleware(request, response, next):
            nonlocal next_called
            next_called = True
            await next()
        
        async def handler():
            nonlocal handler_called
            handler_called = True
            return {"message": "Hello"}
        
        app.use(middleware)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert next_called == True
        assert handler_called == True
    
    @pytest.mark.asyncio
    async def test_middleware_without_next_call(self):
        """Test middleware that doesn't call next()"""
        from artanis import App
        app = App()
        
        handler_called = False
        
        async def blocking_middleware(request, response, next):
            response.status = 200
            response.body = {"blocked": True}
            # Intentionally don't call next()
        
        async def handler():
            nonlocal handler_called
            handler_called = True
            return {"message": "Should not reach"}
        
        app.use(blocking_middleware)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Handler should not be called
        assert handler_called == False
        
        # Should return response from middleware
        response_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.body"]
        assert len(response_calls) > 0
    
    @pytest.mark.asyncio
    async def test_next_with_error_handling(self):
        """Test error handling in middleware chain"""
        from artanis import App
        app = App()
        
        error_caught = False
        
        async def error_handling_middleware(request, response, next):
            nonlocal error_caught
            try:
                await next()
            except Exception as e:
                error_caught = True
                response.status = 500
                response.body = {"error": "Internal server error"}
        
        async def error_middleware(request, response, next):
            raise Exception("Something went wrong")
        
        async def handler():
            return {"message": "Should not reach"}
        
        app.use(error_handling_middleware)
        app.use(error_middleware)
        app.get("/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        assert error_caught == True
        
        # Should return 500 status
        status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert len(status_calls) > 0
        assert status_calls[0][0][0]["status"] == 500
    
    # F. Real-World Middleware Scenarios
    
    @pytest.mark.asyncio
    async def test_cors_middleware_global(self):
        """Test CORS middleware example"""
        from artanis import App
        app = App()
        
        async def cors_middleware(request, response, next):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
            await next()
        
        async def handler():
            return {"message": "Hello"}
        
        app.use(cors_middleware)
        app.get("/api/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check CORS headers were added
        header_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert len(header_calls) > 0
        headers = dict(header_calls[0][0][0]["headers"])
        assert b"Access-Control-Allow-Origin" in headers
        assert headers[b"Access-Control-Allow-Origin"] == b"*"
    
    @pytest.mark.asyncio
    async def test_auth_middleware_on_admin_routes(self):
        """Test authentication middleware only on /admin/* routes"""
        from artanis import App
        app = App()
        
        async def auth_middleware(request, response, next):
            auth_header = None
            for name, value in request.scope.get("headers", []):
                if name == b"authorization":
                    auth_header = value.decode()
                    break
            
            if not auth_header or auth_header != "Bearer valid-token":
                response.status = 401
                response.body = {"error": "Unauthorized"}
                return
            await next()
        
        async def admin_handler():
            return {"admin": "dashboard"}
        
        async def public_handler():
            return {"public": "content"}
        
        app.use("/admin", auth_middleware)
        app.get("/admin/dashboard", admin_handler)
        app.get("/public", public_handler)
        
        # Test admin route without auth - should fail
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/admin/dashboard",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert status_calls[0][0][0]["status"] == 401
        
        # Test admin route with auth - should succeed
        scope["headers"] = [(b"authorization", b"Bearer valid-token")]
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert status_calls[0][0][0]["status"] == 200
        
        # Test public route - should work without auth
        scope["path"] = "/public"
        scope["headers"] = []
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        assert status_calls[0][0][0]["status"] == 200
    
    @pytest.mark.asyncio
    async def test_logging_and_timing_middleware(self):
        """Test request logging and timing middleware"""
        from artanis import App
        import time
        app = App()
        
        logged_requests = []
        
        async def logging_middleware(request, response, next):
            start_time = time.time()
            logged_requests.append({
                "method": request.scope["method"],
                "path": request.scope["path"],
                "start_time": start_time
            })
            
            await next()
            
            end_time = time.time()
            duration = end_time - start_time
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        async def handler():
            # Simulate some processing time
            await asyncio.sleep(0.01)
            return {"message": "Hello"}
        
        app.use("/api", logging_middleware)
        app.get("/api/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": []
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        # Check request was logged
        assert len(logged_requests) == 1
        assert logged_requests[0]["method"] == "GET"
        assert logged_requests[0]["path"] == "/api/test"
        
        # Check timing header was added
        header_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
        headers = dict(header_calls[0][0][0]["headers"])
        assert b"X-Response-Time" in headers
        
        # Should contain a timing value
        timing_value = headers[b"X-Response-Time"].decode()
        assert timing_value.endswith("s")
        assert float(timing_value[:-1]) >= 0.01  # Should be at least 10ms
    
    @pytest.mark.asyncio
    async def test_rate_limiting_middleware(self):
        """Test rate limiting middleware on specific paths"""
        from artanis import App
        app = App()
        
        request_counts = {}
        
        async def rate_limit_middleware(request, response, next):
            client_ip = "127.0.0.1"  # Simplified for testing
            
            if client_ip not in request_counts:
                request_counts[client_ip] = 0
            
            request_counts[client_ip] += 1
            
            if request_counts[client_ip] > 5:  # Rate limit: 5 requests
                response.status = 429
                response.body = {"error": "Rate limit exceeded"}
                return
            
            await next()
        
        async def handler():
            return {"message": "API response"}
        
        app.use("/api", rate_limit_middleware)
        app.get("/api/test", handler)
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": []
        }
        
        # Make 6 requests to trigger rate limit
        for i in range(6):
            receive = AsyncMock()
            send = AsyncMock()
            
            await app(scope, receive, send)
            
            status_calls = [call for call in send.call_args_list if call[0][0].get("type") == "http.response.start"]
            
            if i < 5:
                # First 5 requests should succeed
                assert status_calls[0][0][0]["status"] == 200
            else:
                # 6th request should be rate limited
                assert status_calls[0][0][0]["status"] == 429