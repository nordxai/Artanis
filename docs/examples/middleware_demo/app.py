"""
Middleware Demo - Artanis Example

Demonstrates various middleware patterns with Artanis:
- Custom middleware creation
- Middleware execution order
- Error handling middleware
- Authentication middleware
- Request/response modification
- Conditional middleware

Run with: python app.py
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Awaitable, Callable, TypedDict, cast

import uvicorn

from artanis import App, Request
from artanis.exceptions import AuthenticationError, ValidationError
from artanis.middleware import ExceptionHandlerMiddleware, Response


# Type definitions for request extensions
class UserData(TypedDict):
    """Type definition for user authentication data."""

    id: int
    username: str
    api_key: str


# Helper functions for type-safe request extensions
def add_request_id(request: Request, request_id: str) -> None:
    """Add request ID to request object in a type-safe way."""
    object.__setattr__(request, "request_id", request_id)


def get_request_id(request: Request) -> str:
    """Get request ID from request object with fallback."""
    return getattr(request, "request_id", "unknown")


def add_current_user(request: Request, user_data: UserData) -> None:
    """Add current user data to request object in a type-safe way."""
    object.__setattr__(request, "current_user", user_data)


def get_current_user(request: Request) -> UserData | None:
    """Get current user data from request object with proper typing."""
    user = getattr(request, "current_user", None)
    # Type guard to ensure we return properly typed UserData or None
    if (
        user
        and isinstance(user, dict)
        and all(k in user for k in ["id", "username", "api_key"])
    ):
        return cast("UserData", user)
    return None


# Create the application
app = App()

# ================================
# CUSTOM MIDDLEWARE EXAMPLES
# ================================


# 1. Request ID Middleware
async def request_id_middleware(
    request: Request, response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Add unique request ID to each request."""
    request_id = str(uuid.uuid4())[:8]

    # Add to request for use in handlers
    add_request_id(request, request_id)

    # Add to response headers
    response.set_header("X-Request-ID", request_id)

    print(f"🔍 Request ID: {request_id}")
    await call_next()


# 2. Timing Middleware
async def timing_middleware(
    request: Request, response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Measure request processing time."""
    start_time = time.time()

    await call_next()

    duration = time.time() - start_time
    response.set_header("X-Response-Time", f"{duration:.3f}s")

    method = request.scope.get("method", "UNKNOWN")
    path = request.scope.get("path", "/")
    print(f"⏱️  {method} {path} - {duration:.3f}s")


# 3. Authentication Middleware
async def auth_middleware(
    request: Request, _response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Simple authentication check."""
    path = request.scope.get("path", "")

    # Skip auth for public routes
    public_routes = ["/", "/health", "/public"]
    if path in public_routes:
        await call_next()
        return

    # Check for API key in headers
    api_key = request.headers.get("x-api-key")
    if not api_key:
        msg = "API key required. Add X-API-Key header."
        raise AuthenticationError(msg)

    if api_key != "demo-key-12345":
        msg = "Invalid API key."
        raise AuthenticationError(msg)

    # Add user info to request
    user_data: UserData = {"id": 1, "username": "demo_user", "api_key": api_key}
    add_current_user(request, user_data)

    print(f"🔐 Authenticated user: {user_data['username']}")
    await call_next()


# 4. Request Validation Middleware
async def validation_middleware(
    request: Request, _response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Validate request format."""
    method = request.scope.get("method", "")
    content_type = request.headers.get("content-type", "")

    # Validate POST/PUT requests have proper content type
    if method in ["POST", "PUT"] and not content_type.startswith("application/json"):
        msg = "Content-Type must be application/json for POST/PUT requests"
        raise ValidationError(msg)

    await call_next()


# 5. Response Headers Middleware
async def security_headers_middleware(
    _request: Request, response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Add security headers."""
    await call_next()

    # Add security headers
    response.set_header("X-Content-Type-Options", "nosniff")
    response.set_header("X-Frame-Options", "DENY")
    response.set_header("X-XSS-Protection", "1; mode=block")


# 6. Error Logging Middleware
async def error_logging_middleware(
    request: Request, _response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Log errors with context."""
    try:
        await call_next()
    except Exception as e:
        method = request.scope.get("method", "UNKNOWN")
        path = request.scope.get("path", "/")
        request_id = get_request_id(request)

        print(f"❌ Error in {method} {path} (ID: {request_id}): {e!s}")

        # Re-raise to let Artanis handle the error response
        raise


# ================================
# MIDDLEWARE REGISTRATION
# ================================

# Order matters! Register middleware in execution order:

# 1. Exception handling (should be first to catch all errors)
app.use(ExceptionHandlerMiddleware(debug=True))

# 2. Error logging (early to catch all errors)
app.use(error_logging_middleware)

# 3. Request ID (early for tracking)
app.use(request_id_middleware)

# 4. Security headers
app.use(security_headers_middleware)


# 5. Simple CORS Middleware (function-based for demo)
async def cors_middleware(
    _request: Request, response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Simple CORS middleware."""
    await call_next()

    # Add CORS headers
    response.set_header("Access-Control-Allow-Origin", "http://localhost:3000")
    response.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
    response.set_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
    response.set_header("Access-Control-Allow-Credentials", "true")


app.use(cors_middleware)

# 6. Simple Rate Limiting (function-based for demo)
request_counts: dict[str, list[int]] = {}


async def simple_rate_limit_middleware(
    request: Request, response: Response, call_next: Callable[[], Awaitable[Any]]
) -> None:
    """Simple rate limiting middleware."""
    import time

    # Get client IP (simplified)
    client_ip = request.headers.get("x-forwarded-for", "127.0.0.1")
    current_time = int(time.time())

    # Clean old entries (older than 60 seconds)
    request_counts[client_ip] = [
        timestamp
        for timestamp in request_counts.get(client_ip, [])
        if current_time - timestamp < 60
    ]

    # Check rate limit (20 requests per minute)
    if len(request_counts.get(client_ip, [])) >= 20:
        response.set_status(429)
        response.json(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Try again later.",
            }
        )
        return

    # Record this request
    request_counts.setdefault(client_ip, []).append(current_time)

    await call_next()


app.use(simple_rate_limit_middleware)

# 7. Timing (to measure full request time)
app.use(timing_middleware)

# 8. Request validation
app.use(validation_middleware)

# 9. Authentication (after validation, before business logic)
app.use(auth_middleware)

# ================================
# ROUTE HANDLERS
# ================================


async def root() -> dict[str, Any]:
    """API root - public route."""
    return {
        "message": "Middleware Demo API",
        "endpoints": {
            "GET /": "This endpoint (public)",
            "GET /health": "Health check (public)",
            "GET /public": "Public endpoint (no auth)",
            "GET /protected": "Protected endpoint (requires API key)",
            "POST /data": "Create data (requires API key + JSON)",
            "GET /error": "Test error handling",
        },
        "authentication": {"header": "X-API-Key", "demo_key": "demo-key-12345"},
    }


async def health() -> dict[str, Any]:
    """Health check - public route."""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "middleware": "active",
    }


async def public_endpoint() -> dict[str, Any]:
    """Public endpoint - no authentication required."""
    return {
        "message": "This is a public endpoint",
        "note": "No authentication required",
    }


async def protected_endpoint(request: Request) -> dict[str, Any]:
    """Protected endpoint - requires authentication."""
    user = get_current_user(request)
    request_id = get_request_id(request)

    return {
        "message": "Welcome to the protected area!",
        "user": user,
        "request_id": request_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


async def create_data(request: Request) -> tuple[dict[str, Any], int]:
    """Create data - requires auth and JSON."""
    user = get_current_user(request)

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    name = data.get("name")
    if not name:
        msg = "Name is required"
        raise ValidationError(msg, field="name")

    # Safe access to user data with proper typing
    username = user["username"] if user else "unknown"

    return {
        "message": "Data created successfully",
        "data": {
            "id": int(time.time()),
            "name": name,
            "created_by": username,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }, 201


class DemoError(Exception):
    """Custom exception for demo purposes."""


async def test_error() -> None:
    """Test error handling."""
    msg = "This is a test error to demonstrate error handling middleware"
    raise DemoError(msg)


# ================================
# ROUTE REGISTRATION
# ================================

app.get("/", root)
app.get("/health", health)
app.get("/public", public_endpoint)
app.get("/protected", protected_endpoint)
app.post("/data", create_data)
app.get("/error", test_error)

# ================================
# MAIN APPLICATION
# ================================

if __name__ == "__main__":
    print("🚀 Starting Middleware Demo with Artanis")
    print()
    print("📍 Available endpoints:")
    print("   GET    /                - API root (public)")
    print("   GET    /health          - Health check (public)")
    print("   GET    /public          - Public endpoint")
    print("   GET    /protected       - Protected endpoint (auth required)")
    print("   POST   /data            - Create data (auth + JSON required)")
    print("   GET    /error           - Test error handling")
    print()
    print("🔧 Middleware enabled (in order):")
    print("   1. Exception Handler")
    print("   2. Error Logging")
    print("   3. Request ID")
    print("   4. Security Headers")
    print("   5. CORS (Simple)")
    print("   6. Rate Limiting (Simple)")
    print("   7. Timing")
    print("   8. Request Validation")
    print("   9. Authentication")
    print()
    print("🔑 Authentication: X-API-Key: demo-key-12345")
    print("🌐 Server starting at: http://127.0.0.1:8000")
    print("⏹️  Press Ctrl+C to stop")
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, log_level="info")


"""
🧪 Testing Middleware:

1. Public endpoints (no auth needed):
   curl http://127.0.0.1:8000/
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8000/public

2. Protected endpoint (auth required):
   curl http://127.0.0.1:8000/protected
   # Should fail with 401

   curl -H "X-API-Key: demo-key-12345" http://127.0.0.1:8000/protected
   # Should succeed

3. Create data (auth + JSON required):
   curl -X POST http://127.0.0.1:8000/data \
     -H "X-API-Key: demo-key-12345" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Item"}'

4. Test validation errors:
   curl -X POST http://127.0.0.1:8000/data \
     -H "X-API-Key: demo-key-12345" \
     -H "Content-Type: text/plain" \
     -d 'not json'

5. Test error handling:
   curl -H "X-API-Key: demo-key-12345" http://127.0.0.1:8000/error

6. Test rate limiting:
   # Make many requests quickly to trigger rate limit
   for i in {1..25}; do curl http://127.0.0.1:8000/health; done

🔍 Watch the Console:

Notice how middleware executes in order and provides useful information:
- Request IDs for tracking
- Timing information
- Authentication logs
- Error details with context

💡 Key Middleware Concepts:

1. **Execution Order**: Middleware runs in registration order
2. **Next Function**: Must call await next() to continue the chain
3. **Request Modification**: Add properties to request object
4. **Response Modification**: Set headers and modify response
5. **Error Handling**: Use try/catch to handle errors
6. **Conditional Logic**: Skip middleware for certain routes
7. **Cross-Cutting Concerns**: Authentication, logging, timing, etc.

This demo shows how to build a comprehensive middleware stack
that provides security, monitoring, and functionality across
your entire API.
"""
