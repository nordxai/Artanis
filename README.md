# Artanis

[![Tests](https://github.com/nordxai/projectArtanis/actions/workflows/test.yml/badge.svg)](https://github.com/nordxai/projectArtanis/actions/workflows/test.yml)
[![Code Quality](https://github.com/nordxai/projectArtanis/actions/workflows/code-quality.yml/badge.svg)](https://github.com/nordxai/projectArtanis/actions/workflows/code-quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Open%20Source-green.svg)](LICENSE)

A lightweight, minimalist ASGI web framework for Python built with simplicity and performance in mind. Artanis provides a clean, intuitive API for building modern web applications using named routes.

## ✨ Features

- **Named Routes**: Clean `app.get(path, handler)` and `app.post(path, handler)` syntax
- **Advanced Routing**: Modular routing system with `Router` class and subrouting support
- **Path Parameters**: Support for dynamic path segments like `/users/{user_id}`
- **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE, PATCH, OPTIONS on the same path
- **Subrouting**: Mount routers at specific paths for modular application organization
- **Parameterized Mounts**: Mount subrouters at dynamic paths like `/users/{user_id}`
- **ASGI Compliant**: Works with any ASGI server (Uvicorn, Hypercorn, etc.)
- **Express-Style Middleware**: Powerful middleware system with `app.use()` API
- **Path-Based Middleware**: Apply middleware to specific routes or paths
- **Security Middleware**: Built-in CORS, CSP, HSTS, rate limiting, and security headers
- **Exception Handling**: Comprehensive custom exception system with structured error responses
- **Automatic JSON Responses**: Built-in JSON serialization for response data
- **Request Body Parsing**: Easy access to JSON request bodies
- **Proper HTTP Status Codes**: Automatic 404, 405, and 500 error handling
- **Type Hints**: Full type annotation support with mypy compatibility
- **Structured Logging**: Built-in logging system with configurable formatters and request tracking
- **Event System**: Extensible event handlers for startup, shutdown, and custom business events with priority execution

## 📦 Installation

```bash
pip install artanis
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/nordxai/artanis
cd artanis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install specific dependency groups
pip install -e ".[test]"     # Testing dependencies only
pip install -e ".[all]"      # All optional dependencies
```

### Available Dependency Groups

- **`dev`**: Development tools (ruff, mypy, pre-commit, pytest)
- **`test`**: Testing and coverage tools (pytest, pytest-asyncio, pytest-cov, coverage)
- **`all`**: All optional dependencies combined

### Code Quality Tools

Artanis uses **Ruff** as its primary code quality tool, providing ultra-fast linting and formatting:

```bash
# Run ruff linting
ruff check .

# Run ruff linting with auto-fix
ruff check --fix .

# Run ruff formatting
ruff format .

# Run type checking with mypy
mypy src/artanis --strict --ignore-missing-imports
```

#### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit (included in dev dependencies)
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

The pre-commit configuration includes:
- **Ruff linting** with auto-fix
- **Ruff formatting** for consistent code style
- **MyPy type checking** for type safety
- **Standard hooks** for trailing whitespace, file endings, YAML/TOML validation

## 📦 Package Metadata

Artanis follows modern Python packaging standards with comprehensive metadata configuration in `pyproject.toml`. The package is designed for professional deployment and development workflows.

### PyPI Classification

The package includes extensive PyPI classifiers for optimal discoverability:

- **Development Status**: Beta (stable API, production-ready)
- **Environment**: Web Environment with AsyncIO framework support
- **Audience**: Developers, IT professionals, system administrators
- **Topics**: Web frameworks, HTTP servers, ASGI/WSGI applications, logging, monitoring
- **Python Support**: 3.8+ including the latest Python 3.13
- **Typing**: Fully typed with mypy compatibility

### Project URLs

- **Homepage & Repository**: [github.com/nordxai/artanis](https://github.com/nordxai/artanis)
- **Issues & Bug Reports**: [Issues Tracker](https://github.com/nordxai/artanis/issues)
- **Discussions**: [Community Discussions](https://github.com/nordxai/artanis/discussions)
- **Changelog**: [Release Notes](https://github.com/nordxai/artanis/releases)

### Build Configuration

- **Build System**: Modern setuptools with PEP 517/518 compliance
- **Dynamic Versioning**: Single source of truth from `src/artanis/_version.py`
- **Package Discovery**: Automatic source package finding in `src/` layout
- **Dependencies**: Zero runtime dependencies for maximum compatibility

### Development Tool Configuration

The package includes pre-configured settings for professional development tools:

- **Testing**: pytest with asyncio support, coverage reporting
- **Code Quality**: ruff for ultra-fast linting and formatting
- **Type Checking**: mypy with strict settings and test overrides
- **Coverage**: Source-based coverage with intelligent exclusions
- **Pre-commit**: Automated quality checks on every commit

## 🚀 Quick Start

### Basic Application

```python
from artanis import App

app = App()

# Simple GET route
async def hello():
    return {"message": "Hello, World!"}

app.get("/", hello)

# Route with path parameter
async def get_user(user_id):
    return {"user_id": user_id, "name": f"User {user_id}"}

app.get("/users/{user_id}", get_user)

# POST route with request body
async def create_user(request):
    user_data = await request.json()
    return {"message": "User created", "data": user_data}

app.post("/users", create_user)
```

### Running the Application

```python
# main.py
import uvicorn
from artanis import App

app = App()

# Add your routes here...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# Run with uvicorn
uvicorn main:app --reload
```

## 📚 API Reference

### App Class

The main application class that handles route registration and request routing.

#### Methods

##### `app.get(path: str, handler: Callable)`

Register a GET route handler.

```python
async def handler():
    return {"data": "response"}

app.get("/api/data", handler)
```

##### `app.post(path: str, handler: Callable)`

Register a POST route handler.

```python
async def create_item(request):
    data = await request.json()
    return {"created": data}

app.post("/api/items", create_item)
```

##### `app.put(path: str, handler: Callable)`

Register a PUT route handler.

```python
async def update_item(item_id, request):
    data = await request.json()
    return {"item_id": item_id, "updated": data}

app.put("/api/items/{item_id}", update_item)
```

##### `app.delete(path: str, handler: Callable)`

Register a DELETE route handler.

```python
async def delete_item(item_id):
    return {"deleted": item_id}

app.delete("/api/items/{item_id}", delete_item)
```

##### `app.all(path: str, handler: Callable)`

Register a route handler for all HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS).

```python
async def universal_handler():
    return {"message": "Handles all HTTP methods"}

app.all("/api/universal", universal_handler)
```

##### `app.use(middleware)` or `app.use(path, middleware)`

Register middleware functions using Express-style API.

```python
# Global middleware (applies to all routes)
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    await next()

app.use(cors_middleware)

# Path-based middleware (applies to specific paths)
async def auth_middleware(request, response, next):
    if not request.headers.get("Authorization"):
        response.status = 401
        response.body = {"error": "Unauthorized"}
        return  # Don't call next()
    await next()

app.use("/admin", auth_middleware)
```

### Request Class

The request object provides access to the incoming HTTP request data.

#### Methods

##### `await request.body()`

Get the raw request body as bytes.

```python
async def handler(request):
    body = await request.body()
    return {"body_length": len(body)}
```

##### `await request.json()`

Parse the request body as JSON.

```python
async def handler(request):
    data = await request.json()
    return {"received": data}
```

## 🗂️ Advanced Routing

Artanis provides a powerful routing system with support for modular route organization through subrouting and advanced path matching.

### Router Class

The `Router` class allows you to create modular, reusable route groups that can be mounted to your main application.

```python
from artanis import App, Router

# Create a router for user-related routes
user_router = Router()

def get_users():
    return {"users": ["alice", "bob"]}

def create_user():
    return {"message": "User created"}

user_router.get("/", get_users)
user_router.post("/", create_user)

# Main application
app = App()

# Mount the user router at /users
app.mount("/users", user_router)

# Results in:
# GET /users -> get_users()
# POST /users -> create_user()
```

### Nested Subrouting

Create complex route hierarchies with nested routers for better organization.

```python
from artanis import App, Router

# API v1 router
v1_router = Router()

# User management subrouter
users_router = Router()
users_router.get("/", lambda: {"users": []})
users_router.post("/", lambda: {"message": "User created"})

# Posts subrouter
posts_router = Router()
posts_router.get("/", lambda: {"posts": []})
posts_router.post("/", lambda: {"message": "Post created"})

# Mount subrouters to v1
v1_router.mount("/users", users_router)
v1_router.mount("/posts", posts_router)

# Mount v1 to main app
app = App()
app.mount("/api/v1", v1_router)

# Results in:
# GET /api/v1/users -> get users
# POST /api/v1/users -> create user
# GET /api/v1/posts -> get posts
# POST /api/v1/posts -> create post
```

### Parameterized Subrouting

Subrouters can be mounted at parameterized paths, allowing for dynamic route organization.

```python
from artanis import App, Router

# User profile router
profile_router = Router()

def get_profile(user_id):
    return {"user_id": user_id, "profile": "data"}

def update_profile(user_id):
    return {"user_id": user_id, "message": "Profile updated"}

profile_router.get("/", get_profile)
profile_router.put("/", update_profile)

# Mount at parameterized path
app = App()
app.mount("/users/{user_id}", profile_router)

# Results in:
# GET /users/123 -> get_profile(user_id="123")
# PUT /users/123 -> update_profile(user_id="123")
```

### Mixed Routing Styles

You can mix traditional app routing with the new Router system for maximum flexibility.

```python
from artanis import App, Router

app = App()

# Traditional style - directly on app
app.get("/health", lambda: {"status": "ok"})

# Direct router access - same as traditional but more explicit
app.router.register_route("GET", "/info", lambda: {"version": "1.0"})

# Subrouter style
api_router = Router()
api_router.get("/data", lambda: {"data": "example"})
app.mount("/api", api_router)

# All styles work together:
# GET /health -> traditional app.get()
# GET /info -> direct router access
# GET /api/data -> via subrouter
```

### Router with Prefix

Create routers with predefined prefixes for easier organization.

```python
from artanis import Router

# Create router with prefix
api_router = Router("/api/v2")

api_router.get("/users", get_users)  # Becomes /api/v2/users
api_router.get("/posts", get_posts)  # Becomes /api/v2/posts

app = App()
# Mount without additional prefix since router already has one
app.mount("/", api_router)
```

### All HTTP Methods

Routers support all standard HTTP methods.

```python
router = Router()

router.get("/resource", get_handler)
router.post("/resource", create_handler)
router.put("/resource", update_handler)
router.patch("/resource", patch_handler)
router.delete("/resource", delete_handler)
router.options("/resource", options_handler)

# Register handler for all HTTP methods
router.all("/resource", universal_handler)
```

### Benefits of Router System

- **Modularity**: Organize routes into logical groups
- **Reusability**: Routers can be reused across applications
- **Scalability**: Better organization for large applications
- **Clean API**: Simple, consistent interface across the framework
- **Testing**: Easier to test individual route groups
- **Team Development**: Different teams can work on different routers

## 🔗 Path Parameters

Artanis supports dynamic path segments using curly braces `{}`. Parameters are automatically extracted and passed to your handler functions.

```python
# Single parameter
async def get_user(user_id):
    return {"user_id": user_id}

app.get("/users/{user_id}", get_user)

# Multiple parameters
async def get_user_post(user_id, post_id):
    return {"user_id": user_id, "post_id": post_id}

app.get("/users/{user_id}/posts/{post_id}", get_user_post)

# Mix parameters with request object
async def update_user(user_id, request):
    data = await request.json()
    return {"user_id": user_id, "updated": data}

app.put("/users/{user_id}", update_user)
```

## 🔧 Middleware

Artanis provides a powerful Express-style middleware system that allows you to run code before and after your route handlers. Middleware functions can modify requests, responses, handle authentication, logging, CORS, and more.

### Middleware Basics

Middleware functions have access to three parameters:
- `request`: The incoming HTTP request object
- `response`: The response object for modifying the response
- `next`: An async function to continue to the next middleware or route handler

```python
async def middleware(request, response, next):
    # Pre-processing code (before route handler)
    print(f"Request to {request.scope['path']}")

    await next()  # Continue to next middleware or route handler

    # Post-processing code (after route handler)
    print("Response sent")
```

### Global Middleware

Global middleware runs on every request to your application:

```python
from artanis import App

app = App()

# CORS middleware
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    await next()

# Request logging middleware
async def logging_middleware(request, response, next):
    import time
    start_time = time.time()

    print(f"→ {request.scope['method']} {request.scope['path']}")
    await next()

    duration = time.time() - start_time
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    print(f"← {response.status} ({duration:.3f}s)")

# Register global middleware
app.use(cors_middleware)
app.use(logging_middleware)

# Your routes here...
async def hello():
    return {"message": "Hello, World!"}

app.get("/", hello)
```

### Path-Based Middleware

Path-based middleware only runs for requests that match specific path patterns:

```python
# Authentication middleware for admin routes
async def auth_middleware(request, response, next):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        response.status = 401
        response.body = {"error": "Authentication required"}
        return  # Don't call next() to stop the chain

    # Validate token here...
    await next()

# Rate limiting for API routes
async def rate_limit_middleware(request, response, next):
    # Implementation would check rate limits
    await next()

# Apply middleware to specific paths
app.use("/admin", auth_middleware)
app.use("/api", rate_limit_middleware)

# Routes
async def admin_dashboard():
    return {"message": "Welcome to admin dashboard"}

async def api_data():
    return {"data": "API response"}

app.get("/admin/dashboard", admin_dashboard)  # Protected by auth
app.get("/api/data", api_data)  # Rate limited
app.get("/public", lambda: {"message": "Public endpoint"})  # No middleware
```

### Middleware with Path Parameters

Middleware can access path parameters just like route handlers:

```python
async def user_validation_middleware(request, response, next):
    user_id = request.path_params.get('user_id')

    if not user_id or not user_id.isdigit():
        response.status = 400
        response.body = {"error": "Invalid user ID"}
        return

    # Add validated user_id to request for handler use
    request.validated_user_id = int(user_id)
    await next()

# Apply to user routes with parameters
app.use("/users/{user_id}", user_validation_middleware)

async def get_user(user_id):
    # user_id is guaranteed to be valid here
    return {"user_id": user_id, "name": f"User {user_id}"}

app.get("/users/{user_id}", get_user)
```

### Middleware Execution Order

Middleware executes in a specific order:

1. **Global middleware** (in registration order)
2. **Path-specific middleware** (matching path patterns, in registration order)
3. **Route handler**
4. **Path-specific middleware** (in reverse order for response processing)
5. **Global middleware** (in reverse order for response processing)

```python
app = App()

async def global_middleware1(request, response, next):
    print("Global 1 - Before")
    await next()
    print("Global 1 - After")

async def global_middleware2(request, response, next):
    print("Global 2 - Before")
    await next()
    print("Global 2 - After")

async def path_middleware(request, response, next):
    print("Path - Before")
    await next()
    print("Path - After")

app.use(global_middleware1)
app.use(global_middleware2)
app.use("/api", path_middleware)

async def handler():
    print("Route Handler")
    return {"message": "Hello"}

app.get("/api/test", handler)

# Request to /api/test produces:
# Global 1 - Before
# Global 2 - Before
# Path - Before
# Route Handler
# Path - After
# Global 2 - After
# Global 1 - After
```

### Response Object

Middleware can modify the response using the response object:

```python
async def response_modifier(request, response, next):
    await next()  # Let handler run first

    # Modify response after handler
    response.headers["X-Powered-By"] = "Artanis"
    response.headers["Cache-Control"] = "no-cache"

    # You can also modify status and body
    if isinstance(response.body, dict):
        response.body["timestamp"] = time.time()

app.use(response_modifier)
```

#### Response Object Methods

- `response.set_status(status_code)`: Set HTTP status code
- `response.set_header(name, value)`: Set response header
- `response.get_header(name)`: Get response header value
- `response.json(data)`: Set response body as JSON
- `response.is_finished()`: Check if response is complete

### Early Response from Middleware

Middleware can send a response early by not calling `next()`:

```python
async def auth_middleware(request, response, next):
    token = request.headers.get("Authorization")

    if not is_valid_token(token):
        response.status = 401
        response.body = {"error": "Invalid token"}
        return  # Don't call next() - stops execution chain

    await next()  # Continue to next middleware/handler
```

### Error Handling in Middleware

Middleware can handle errors from subsequent middleware or handlers:

```python
async def error_handler_middleware(request, response, next):
    try:
        await next()
    except ValueError as e:
        response.status = 400
        response.body = {"error": f"Bad request: {str(e)}"}
    except Exception as e:
        response.status = 500
        response.body = {"error": "Internal server error"}
```

## 🔐 Security Middleware

Artanis includes a comprehensive suite of security middleware components to protect your applications against common web vulnerabilities and attacks. These middleware are production-ready and follow security best practices.

### Security Configuration

Configure all security middleware with a centralized configuration:

```python
from artanis.middleware.security import SecurityConfig

# Create security configuration
security_config = SecurityConfig(
    # CORS settings
    cors_allow_origins=["https://yourdomain.com", "https://api.yourdomain.com"],
    cors_allow_credentials=True,

    # CSP settings
    csp_directives={
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data: https:",
        "connect-src": "'self'",
        "font-src": "'self'",
        "object-src": "'none'",
        "media-src": "'self'",
        "frame-src": "'none'"
    },

    # HSTS settings
    hsts_max_age=31536000,  # 1 year
    hsts_include_subdomains=True,
    hsts_preload=True,

    # Rate limiting
    rate_limit_requests=100,
    rate_limit_window=3600  # 1 hour
)
```

### CORS Middleware

Comprehensive Cross-Origin Resource Sharing (CORS) middleware with full preflight request support:

```python
from artanis.middleware.security import CORSMiddleware

# Basic CORS (allow all origins)
app.use(CORSMiddleware())

# Production CORS with specific origins
cors = CORSMiddleware(
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    allow_credentials=True,
    max_age=86400  # 24 hours preflight cache
)
app.use(cors)

# Apply CORS to specific paths only
app.use("/api", cors)
```

### Content Security Policy (CSP) Middleware

Protect against XSS and data injection attacks with Content Security Policy:

```python
from artanis.middleware.security import CSPMiddleware

# Default secure CSP
app.use(CSPMiddleware())

# Custom CSP directives
csp = CSPMiddleware(
    directives={
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
        "img-src": "'self' data: https:",
        "connect-src": "'self' https://api.example.com",
        "font-src": "'self' https://fonts.gstatic.com",
        "object-src": "'none'",
        "media-src": "'self'",
        "frame-src": "'none'"
    },
    report_uri="/csp-report"  # Optional violation reporting
)
app.use(csp)

# CSP in report-only mode for testing
csp_report_only = CSPMiddleware(
    directives={"default-src": "'self'"},
    report_only=True,
    report_uri="/csp-report"
)
app.use(csp_report_only)
```

### HTTP Strict Transport Security (HSTS) Middleware

Enforce HTTPS connections and prevent protocol downgrade attacks:

```python
from artanis.middleware.security import HSTSMiddleware

# Default HSTS (1 year, include subdomains)
app.use(HSTSMiddleware())

# Custom HSTS configuration
hsts = HSTSMiddleware(
    max_age=31536000,      # 1 year in seconds
    include_subdomains=True,
    preload=True           # Enable HSTS preload list
)
app.use(hsts)

# Conservative HSTS for testing
hsts_test = HSTSMiddleware(
    max_age=3600,          # 1 hour for testing
    include_subdomains=False,
    preload=False
)
app.use(hsts_test)
```

### Security Headers Middleware

Add essential security headers to protect against common vulnerabilities:

```python
from artanis.middleware.security import SecurityHeadersMiddleware

# Default security headers
app.use(SecurityHeadersMiddleware())

# Custom security headers
security_headers = SecurityHeadersMiddleware(
    x_frame_options="DENY",                           # Prevent clickjacking
    x_content_type_options="nosniff",                 # Prevent MIME sniffing
    x_xss_protection="1; mode=block",                 # XSS protection
    referrer_policy="strict-origin-when-cross-origin", # Control referrer info
    permissions_policy="geolocation=(), microphone=(), camera=()"  # Feature policy
)
app.use(security_headers)
```

### Rate Limiting Middleware

Protect against abuse and ensure fair usage with sophisticated rate limiting:

```python
from artanis.middleware.security import RateLimitMiddleware

# Basic rate limiting (100 requests per hour per IP)
app.use(RateLimitMiddleware())

# Custom rate limiting
rate_limiter = RateLimitMiddleware(
    requests_per_window=50,    # 50 requests
    window_seconds=300,        # per 5 minutes
    skip_successful_requests=False  # Count all requests
)
app.use(rate_limiter)

# API-specific rate limiting
api_rate_limiter = RateLimitMiddleware(
    requests_per_window=1000,   # Higher limit for API
    window_seconds=3600,        # per hour
    key_function=lambda req: f"api:{req.headers.get('X-API-Key', 'anonymous')}"
)
app.use("/api", api_rate_limiter)

# Strict rate limiting for authentication endpoints
auth_rate_limiter = RateLimitMiddleware(
    requests_per_window=5,      # Only 5 attempts
    window_seconds=900,         # per 15 minutes
    skip_successful_requests=True  # Only count failed attempts
)
app.use("/auth/login", auth_rate_limiter)
```

### Complete Security Setup

Here's a complete example of a production-ready security setup:

```python
from artanis import App
from artanis.middleware.security import (
    CORSMiddleware,
    CSPMiddleware,
    HSTSMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware
)

app = App()

# 1. Rate limiting (apply first to reject abusive requests early)
app.use(RateLimitMiddleware(
    requests_per_window=1000,
    window_seconds=3600
))

# 2. CORS for cross-origin requests
app.use(CORSMiddleware(
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
))

# 3. Security headers
app.use(SecurityHeadersMiddleware())

# 4. HSTS for HTTPS enforcement
app.use(HSTSMiddleware(
    max_age=31536000,
    include_subdomains=True,
    preload=True
))

# 5. Content Security Policy
app.use(CSPMiddleware(
    directives={
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data: https:",
    }
))

# 6. Stricter rate limiting for sensitive endpoints
app.use("/auth", RateLimitMiddleware(
    requests_per_window=10,
    window_seconds=300,
    skip_successful_requests=True
))

@app.get("/")
async def home(request):
    return {"message": "Secure API endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Error Handling for Security Middleware

Security middleware integrates seamlessly with Artanis exception handling:

```python
from artanis.exceptions import RateLimitError
from artanis.middleware.exception import ExceptionHandlerMiddleware

# Custom handler for rate limit errors
def handle_rate_limit_error(error: RateLimitError) -> dict:
    return {
        "error": "Rate limit exceeded",
        "message": str(error),
        "retry_after": error.details.get("retry_after", 60),
        "limit": error.details.get("limit", 100)
    }

# Add exception handling middleware
exception_handler = ExceptionHandlerMiddleware()
exception_handler.add_handler(RateLimitError, handle_rate_limit_error)
app.use(exception_handler)
```

## 📡 Event Handling System

Artanis provides a powerful, extensible event system that goes beyond traditional startup/shutdown events. With method-style APIs, priority execution, and unlimited custom events, you can build sophisticated event-driven applications with ease.

### Event System Overview

The event system supports:
- **ASGI Lifecycle Events**: Automatic startup and shutdown handling
- **Custom Business Events**: Unlimited user-defined events for application logic
- **Priority Execution**: Control the order of event handler execution
- **Conditional Handlers**: Execute handlers only when specific conditions are met
- **Event Middleware**: Cross-cutting concerns that run for all events
- **Type Safety**: Full type annotation support for event handlers and data

### Basic Event Handler Registration

Register event handlers using the method-style API:

```python
from artanis import App

app = App()

# Basic event handlers
def setup_database():
    print("Database connected")

def cleanup_database():
    print("Database disconnected")

# Register lifecycle events
app.add_event_handler("startup", setup_database)
app.add_event_handler("shutdown", cleanup_database)

# Custom business events
def send_welcome_email(user_data):
    print(f"Welcome email sent to {user_data['email']}")

def update_analytics(user_data):
    print(f"Analytics updated for user {user_data['email']}")

app.add_event_handler("user_registered", send_welcome_email)
app.add_event_handler("user_registered", update_analytics)
```

### ASGI Lifecycle Integration

Artanis automatically integrates with ASGI servers for proper application lifecycle management:

```python
from artanis import App
import asyncio

app = App()

# Startup event - runs when server starts
async def initialize_services():
    print("Initializing external services...")
    # Connect to database, setup caches, etc.
    await asyncio.sleep(0.1)  # Simulate async setup
    print("Services initialized")

# Shutdown event - runs when server stops
async def cleanup_services():
    print("Cleaning up services...")
    # Close database connections, cleanup caches, etc.
    await asyncio.sleep(0.1)  # Simulate async cleanup
    print("Services cleaned up")

app.add_event_handler("startup", initialize_services)
app.add_event_handler("shutdown", cleanup_services)

# When running with: uvicorn main:app
# Startup handlers run automatically when server starts
# Shutdown handlers run automatically when server stops (SIGTERM/SIGINT)
```

### Custom Business Events

Create and trigger custom events for application-specific workflows:

```python
app = App()

# E-commerce order processing events
def validate_order(order_data):
    print(f"Validating order {order_data['order_id']}")
    return order_data

def process_payment(order_data):
    print(f"Processing payment for order {order_data['order_id']}")

def update_inventory(order_data):
    print(f"Updating inventory for order {order_data['order_id']}")

def send_confirmation_email(order_data):
    print(f"Sending confirmation email for order {order_data['order_id']}")

# Register event handlers
app.add_event_handler("order_placed", validate_order)
app.add_event_handler("order_placed", process_payment)
app.add_event_handler("order_placed", update_inventory)
app.add_event_handler("order_placed", send_confirmation_email)

# Route handler that triggers the event
async def place_order(request):
    order_data = await request.json()

    # Trigger the custom event
    await app.emit_event("order_placed", order_data)

    return {"message": "Order placed successfully", "order_id": order_data["order_id"]}

app.post("/orders", place_order)
```

### Priority-Based Execution

Control the execution order of event handlers with priorities:

```python
app = App()

# Higher priority numbers execute first
def critical_validation(user_data):
    print("Critical validation (priority 10)")

def standard_processing(user_data):
    print("Standard processing (priority 5)")

def optional_analytics(user_data):
    print("Optional analytics (priority 1)")

# Register with different priorities
app.add_event_handler("user_registered", critical_validation, priority=10)
app.add_event_handler("user_registered", standard_processing, priority=5)
app.add_event_handler("user_registered", optional_analytics, priority=1)

# Execution order: critical_validation -> standard_processing -> optional_analytics
```

### Conditional Event Handlers

Execute handlers only when specific conditions are met:

```python
app = App()

def send_premium_notification(order_data):
    print(f"Sending premium notification for high-value order {order_data['order_id']}")

def send_standard_notification(order_data):
    print(f"Sending standard notification for order {order_data['order_id']}")

# Conditional handler - only for orders over $100
app.add_event_handler(
    "order_placed",
    send_premium_notification,
    condition=lambda data: data.get("amount", 0) > 100
)

# Standard handler - runs for all orders
app.add_event_handler("order_placed", send_standard_notification)

# Usage examples:
# Low-value order ($50) - only standard notification
# High-value order ($150) - both premium and standard notifications
```

### Event Middleware

Add middleware that runs for all events, perfect for cross-cutting concerns:

```python
from artanis import App, EventContext

app = App()

# Event logging middleware
async def event_logger_middleware(event_context: EventContext):
    print(f"Event '{event_context.name}' triggered at {event_context.timestamp}")
    if event_context.source:
        print(f"  Source: {event_context.source}")

# Event timing middleware
import time
async def event_timer_middleware(event_context: EventContext):
    event_context.metadata["start_time"] = time.time()

# Add event middleware
app.add_event_middleware(event_logger_middleware)
app.add_event_middleware(event_timer_middleware)

# All events will now be logged and timed automatically
```

### Event Context and Data Passing

Event handlers can receive data in multiple formats:

```python
from artanis import App, EventContext

app = App()

# Handler that receives just the data
def simple_handler(user_data):
    print(f"User: {user_data}")

# Handler that receives the full event context
def context_handler(event_context: EventContext):
    print(f"Event: {event_context.name}")
    print(f"Data: {event_context.data}")
    print(f"Source: {event_context.source}")
    print(f"Timestamp: {event_context.timestamp}")
    print(f"Metadata: {event_context.metadata}")

# Handler with no parameters
def notification_handler():
    print("Notification sent")

app.add_event_handler("user_action", simple_handler)
app.add_event_handler("user_action", context_handler)
app.add_event_handler("user_action", notification_handler)

# Emit event with metadata
async def some_route(request):
    user_data = {"user_id": "123", "action": "login"}

    await app.emit_event(
        "user_action",
        user_data,
        source="authentication_service",
        session_id="abc123",
        ip_address="192.168.1.1"
    )

    return {"status": "logged"}
```

### Advanced Event Management

The event system provides powerful management capabilities:

```python
app = App()

# List all registered events
def admin_events():
    events = app.list_events()
    return {"registered_events": events}

app.get("/admin/events", admin_events)

# Remove specific event handlers
def maintenance_mode_handler():
    print("System in maintenance mode")

app.add_event_handler("user_login", maintenance_mode_handler)

# Later, remove the handler when maintenance is done
def disable_maintenance():
    app.remove_event_handler("user_login", maintenance_mode_handler)
    return {"message": "Maintenance mode disabled"}

app.post("/admin/maintenance/disable", disable_maintenance)

# Get handlers for a specific event
def get_event_handlers(event_name: str):
    handlers = app.event_manager.get_handlers(event_name)
    return {
        "event": event_name,
        "handler_count": len(handlers),
        "handlers": [
            {
                "priority": h.priority,
                "has_condition": h.condition is not None,
                "has_schema": h.schema is not None
            }
            for h in handlers
        ]
    }
```

### Real-World Use Cases

#### Database Lifecycle Management

```python
import asyncio
import aioredis

app = App()
db_pool = None
redis_client = None

async def setup_database():
    global db_pool, redis_client
    print("Setting up database connections...")

    # Setup database pool (example)
    # db_pool = await create_db_pool()

    # Setup Redis
    redis_client = await aioredis.from_url("redis://localhost")

    print("Database connections established")

async def cleanup_database():
    global db_pool, redis_client
    print("Closing database connections...")

    if redis_client:
        await redis_client.close()

    if db_pool:
        await db_pool.close()

    print("Database connections closed")

app.add_event_handler("startup", setup_database)
app.add_event_handler("shutdown", cleanup_database)
```

#### User Registration Workflow

```python
app = App()

def log_user_registration(user_data):
    print(f"New user registered: {user_data['email']}")

async def send_welcome_email(user_data):
    # Simulate async email sending
    await asyncio.sleep(0.1)
    print(f"Welcome email sent to {user_data['email']}")

def update_user_analytics(user_data):
    print(f"Analytics updated for user {user_data['email']}")

def check_referral_bonus(user_data):
    if user_data.get("referral_code"):
        print(f"Processing referral bonus for {user_data['email']}")

# Register handlers with priorities
app.add_event_handler("user_registered", log_user_registration, priority=10)
app.add_event_handler("user_registered", send_welcome_email, priority=8)
app.add_event_handler("user_registered", update_user_analytics, priority=5)
app.add_event_handler("user_registered", check_referral_bonus, priority=3)

async def register_user(request):
    user_data = await request.json()

    # Create user in database
    # user = await create_user(user_data)

    # Trigger registration event
    await app.emit_event("user_registered", user_data, source="registration_api")

    return {"message": "User registered successfully"}

app.post("/register", register_user)
```

#### Audit Logging System

```python
from datetime import datetime

app = App()

async def audit_logger(event_context: EventContext):
    audit_data = {
        "event": event_context.name,
        "timestamp": event_context.timestamp.isoformat(),
        "source": event_context.source,
        "data": event_context.data,
        "metadata": event_context.metadata
    }

    # Log to audit system
    print(f"AUDIT: {audit_data}")

# Add audit logging to all events
app.add_event_middleware(audit_logger)

# Now all events are automatically audited
```

### Integration with Type System

Artanis event system is fully typed for excellent developer experience:

```python
from typing import Dict, Any, Optional
from artanis import App, EventContext

app = App()

# Type-annotated event handlers
async def typed_user_handler(user_data: Dict[str, Any]) -> None:
    user_id: str = user_data["user_id"]
    email: Optional[str] = user_data.get("email")
    print(f"Processing user {user_id} with email {email}")

def typed_context_handler(event_context: EventContext) -> None:
    event_name: str = event_context.name
    timestamp: datetime = event_context.timestamp
    print(f"Event {event_name} at {timestamp}")

# Type-safe event registration
app.add_event_handler("user_updated", typed_user_handler)
app.add_event_handler("user_updated", typed_context_handler)
```

### Comparison with Other Frameworks

Artanis event system provides several advantages over similar frameworks:

**vs. FastAPI Events:**
- **Unlimited Custom Events**: Not limited to just startup/shutdown
- **Priority Execution**: Control handler execution order
- **Event Middleware**: Cross-cutting concerns for all events
- **Method-Style API**: Clean `app.add_event_handler()` instead of decorators
- **Conditional Handlers**: Execute only when conditions are met

**vs. Flask Signals:**
- **ASGI Integration**: Native support for async/await patterns
- **Structured Context**: Rich event context with metadata
- **Built-in Priority**: No need for external priority systems
- **Type Safety**: Full type annotation support

### Event System Best Practices

1. **Use Descriptive Event Names**: Choose clear, action-based names like `user_registered`, `order_completed`
2. **Handle Errors Gracefully**: Event handlers should not crash the application
3. **Keep Handlers Focused**: Each handler should have a single responsibility
4. **Use Priorities Wisely**: Critical operations first, optional ones last
5. **Leverage Middleware**: Use event middleware for cross-cutting concerns like logging and auditing
6. **Test Event Flows**: Ensure your event-driven workflows work correctly
7. **Document Custom Events**: Maintain documentation of your application's custom events

The event system makes Artanis ideal for building sophisticated, event-driven applications while maintaining the framework's core simplicity and performance.


## 📊 Logging

Artanis includes a comprehensive logging system that provides structured logging with configurable output formats and automatic request/response tracking.

### Basic Logging Configuration

By default, Artanis automatically configures logging and adds request logging middleware:

```python
from artanis import App
from artanis.logging import ArtanisLogger

# Configure logging (optional - has sensible defaults)
ArtanisLogger.configure(
    level="INFO",           # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format_type="text",     # Format: "text" or "json"
    output=None            # Output: None for stdout, or file path
)

app = App()  # Request logging is enabled by default
```

### Disable Request Logging

```python
# Disable automatic request logging
app = App(enable_request_logging=False)
```

### Custom Logging Configuration

```python
from artanis.logging import ArtanisLogger

# Text format logging to file
ArtanisLogger.configure(
    level="DEBUG",
    format_type="text",
    output="app.log"
)

# JSON format logging (great for structured log parsing)
ArtanisLogger.configure(
    level="INFO",
    format_type="json",
    output=None  # stdout
)
```

### Using Loggers in Your Application

```python
from artanis import App
from artanis.logging import ArtanisLogger

# Get loggers for different components
logger = ArtanisLogger.get_logger('app')
db_logger = ArtanisLogger.get_logger('database')
auth_logger = ArtanisLogger.get_logger('auth')

app = App()

async def login_handler(request):
    auth_logger.info("Login attempt started")

    try:
        data = await request.json()
        username = data.get('username')

        # Simulate authentication
        if not username:
            auth_logger.warning("Login failed: missing username")
            return {"error": "Username required"}

        auth_logger.info(f"Login successful for user: {username}")
        return {"message": f"Welcome {username}"}

    except Exception as e:
        auth_logger.error(f"Login error: {str(e)}")
        return {"error": "Login failed"}

app.post("/login", login_handler)
```

### Request Logging Middleware

The built-in request logging middleware automatically logs:

- Request start (method, path, client IP, request ID)
- Request completion (status code, response time)
- Request failures (errors, response time)

```python
from artanis import App
from artanis.logging import RequestLoggingMiddleware
import logging

# Create custom request logger
custom_logger = logging.getLogger('my_requests')
custom_logger.setLevel(logging.INFO)

# Use custom request logging middleware
app = App(enable_request_logging=False)  # Disable default
app.use(RequestLoggingMiddleware(logger=custom_logger))
```

### Log Output Examples

#### Text Format
```
[2024-01-15 10:30:45] INFO in artanis.request: Request started
[2024-01-15 10:30:45] INFO in artanis.auth: Login successful for user: john
[2024-01-15 10:30:45] INFO in artanis.request: Request completed
```

#### JSON Format
```json
{"timestamp": "2024-01-15T10:30:45.123456", "level": "INFO", "logger": "artanis.request", "message": "Request started", "module": "logging", "function": "__call__", "line": 45, "request_id": "abc12345", "method": "POST", "path": "/login", "remote_addr": "127.0.0.1"}
{"timestamp": "2024-01-15T10:30:45.234567", "level": "INFO", "logger": "artanis.auth", "message": "Login successful for user: john", "module": "main", "function": "login_handler", "line": 23}
{"timestamp": "2024-01-15T10:30:45.345678", "level": "INFO", "logger": "artanis.request", "message": "Request completed", "module": "logging", "function": "__call__", "line": 67, "request_id": "abc12345", "method": "POST", "path": "/login", "status_code": 200, "response_time": "45.2ms"}
```

### Accessing Request ID in Handlers

The request logging middleware adds a unique request ID to each request:

```python
async def my_handler(request):
    request_id = getattr(request, 'request_id', 'unknown')
    logger.info(f"Processing request {request_id}")
    return {"request_id": request_id}
```

### Integration with Route Handlers

Framework automatically logs route registration and handler errors:

```python
from artanis import App

app = App()

# Route registration is automatically logged at DEBUG level
app.get("/users/{user_id}", get_user)  # Logs: "Registered GET route: /users/{user_id}"

async def error_handler():
    raise ValueError("Something went wrong")

app.get("/error", error_handler)  # Handler errors are automatically logged
```

### Production Logging Best Practices

```python
import os
from artanis import App
from artanis.logging import ArtanisLogger

# Environment-based configuration
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_format = os.getenv('LOG_FORMAT', 'json')  # json for production
log_file = os.getenv('LOG_FILE')  # None for stdout in containers

ArtanisLogger.configure(
    level=log_level,
    format_type=log_format,
    output=log_file
)

app = App()

# Your routes here...
```

### Custom Log Fields

You can add custom fields to structured JSON logs:

```python
import logging
from artanis.logging import ArtanisLogger

logger = ArtanisLogger.get_logger('custom')

async def handler(request):
    # Create log record with extra fields
    logger.info(
        "User action performed",
        extra={
            'user_id': '12345',
            'action': 'create_post',
            'resource_id': 'post_789'
        }
    )
    return {"message": "Action logged"}
```

This produces JSON output with the extra fields:
```json
{"timestamp": "2024-01-15T10:30:45.123456", "level": "INFO", "logger": "artanis.custom", "message": "User action performed", "user_id": "12345", "action": "create_post", "resource_id": "post_789"}
```

## 🔷 Type Hints Support

Artanis provides comprehensive type hints throughout the framework, enabling excellent IDE support, static type checking, and improved developer experience. All public APIs are fully annotated with type information.

### Framework Type Support

The framework includes complete type annotations for:

- **Route handlers**: Function signatures with proper parameter and return types
- **Request/Response objects**: Full typing for all methods and attributes
- **Middleware functions**: Type annotations for middleware signatures
- **App class**: Complete typing for all methods and properties
- **Logging system**: Type hints for loggers, formatters, and middleware

### IDE Integration

With type hints enabled, your IDE can provide:

- **Autocomplete**: Intelligent code completion for all framework methods
- **Type checking**: Real-time error detection for type mismatches
- **Documentation**: Hover information showing method signatures and docstrings
- **Refactoring**: Safe renaming and refactoring with type awareness

### Type Checking with mypy

Artanis is fully compatible with static type checkers like mypy:

```bash
# Install mypy
pip install mypy

# Type check your application
mypy your_app.py
```

### Type-Annotated Route Handlers

Use type hints in your route handlers for better code quality:

```python
from typing import Dict, Any, Optional
from artanis import App, Request

app = App()

# Type-annotated route handlers
async def get_user(user_id: str) -> Dict[str, Any]:
    """Get user by ID with typed return value."""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "active": True
    }

async def create_user(request: Request) -> Dict[str, str]:
    """Create a new user with typed request and response."""
    user_data: Dict[str, Any] = await request.json()
    username: str = user_data.get("username", "")

    if not username:
        return {"error": "Username required"}

    return {"message": f"Created user {username}"}

async def update_user(user_id: str, request: Request) -> Dict[str, Any]:
    """Update user with mixed parameters."""
    user_data: Dict[str, Any] = await request.json()

    return {
        "user_id": user_id,
        "updated_fields": list(user_data.keys()),
        "success": True
    }

# Register typed routes
app.get("/users/{user_id}", get_user)
app.post("/users", create_user)
app.put("/users/{user_id}", update_user)
```

### Type-Annotated Middleware

Create type-safe middleware functions:

```python
from typing import Callable, Awaitable, Any
from artanis import Request
from artanis.middleware import Response

# Type-annotated middleware
async def auth_middleware(
    request: Request,
    response: Response,
    next_middleware: Callable[[], Awaitable[Any]]
) -> None:
    """Authentication middleware with full type annotations."""

    auth_header: Optional[str] = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        response.set_status(401)
        response.json({"error": "Authentication required"})
        return

    # Add user info to request (typed)
    request.user_id = extract_user_id(auth_header)
    await next_middleware()

async def logging_middleware(
    request: Request,
    response: Response,
    next_middleware: Callable[[], Awaitable[Any]]
) -> None:
    """Request logging middleware with type safety."""
    import time

    start_time: float = time.time()
    method: str = request.scope.get("method", "UNKNOWN")
    path: str = request.scope.get("path", "/")

    print(f"→ {method} {path}")

    await next_middleware()

    duration: float = time.time() - start_time
    status: int = response.status
    print(f"← {method} {path} {status} ({duration:.3f}s)")

app.use(auth_middleware)
app.use(logging_middleware)
```

### Request Object Types

The Request object provides typed methods for accessing request data:

```python
async def typed_request_handler(request: Request) -> Dict[str, Any]:
    """Demonstrate typed request object usage."""

    # Typed body access
    raw_body: bytes = await request.body()

    # Typed JSON parsing
    json_data: Any = await request.json()  # Returns Any for flexibility

    # Type-safe header access
    content_type: Optional[str] = request.headers.get("Content-Type")
    user_agent: str = request.headers.get("User-Agent", "Unknown")

    # Typed path parameters
    path_params: Dict[str, str] = request.path_params

    return {
        "body_size": len(raw_body),
        "has_json": json_data is not None,
        "content_type": content_type,
        "user_agent": user_agent,
        "path_params": path_params
    }
```

### Response Object Types

The Response object methods are fully typed:

```python
from artanis.middleware import Response
from typing import Optional, List, Tuple

async def typed_response_middleware(
    request: Request,
    response: Response,
    next_middleware: Callable[[], Awaitable[Any]]
) -> None:
    """Demonstrate typed response object usage."""

    # Execute handler first
    await next_middleware()

    # Typed response modifications
    response.set_status(200)  # status: int
    response.set_header("X-Custom", "value")  # name: str, value: str

    # Type-safe header retrieval
    custom_header: Optional[str] = response.get_header("X-Custom")

    # Typed response body
    if isinstance(response.body, dict):
        response.body["server"] = "Artanis"

    # Typed header list for ASGI
    headers: List[Tuple[bytes, bytes]] = response.get_headers_list()
    response_bytes: bytes = response.to_bytes()
    is_done: bool = response.is_finished()
```

### Custom Type Definitions

Create your own type definitions for domain objects:

```python
from typing import TypedDict, Optional, List
from dataclasses import dataclass

# Using TypedDict for structured data
class UserData(TypedDict):
    user_id: str
    username: str
    email: Optional[str]
    active: bool

class CreateUserRequest(TypedDict):
    username: str
    email: str
    password: str

# Using dataclasses for complex objects
@dataclass
class User:
    id: str
    username: str
    email: Optional[str] = None
    active: bool = True

    def to_dict(self) -> UserData:
        return {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active
        }

# Typed route handlers with custom types
async def get_user_typed(user_id: str) -> UserData:
    """Return a user with structured typing."""
    user = User(id=user_id, username=f"user_{user_id}")
    return user.to_dict()

async def create_user_typed(request: Request) -> UserData:
    """Create user with structured request/response types."""
    data: CreateUserRequest = await request.json()

    new_user = User(
        id=generate_id(),
        username=data["username"],
        email=data["email"]
    )

    return new_user.to_dict()

app.get("/users/{user_id}", get_user_typed)
app.post("/users", create_user_typed)
```

### Generic Type Support

Use generic types for flexible, reusable code:

```python
from typing import TypeVar, Generic, Dict, Any, List

T = TypeVar('T')

class APIResponse(Generic[T]):
    """Generic API response wrapper."""

    def __init__(self, data: T, message: str = "Success"):
        self.data = data
        self.message = message
        self.success = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "message": self.message,
            "success": self.success
        }

# Typed API responses
async def get_users() -> Dict[str, Any]:
    """Return typed API response."""
    users: List[UserData] = [
        {"user_id": "1", "username": "alice", "email": "alice@example.com", "active": True},
        {"user_id": "2", "username": "bob", "email": None, "active": False}
    ]

    response: APIResponse[List[UserData]] = APIResponse(users, "Users retrieved")
    return response.to_dict()

app.get("/users", get_users)
```

### Type Checking Configuration

For optimal type checking, configure mypy in `mypy.ini` or `pyproject.toml`:

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

### Benefits of Type Hints

Using type hints with Artanis provides:

- **Better IDE Support**: Autocomplete, error detection, and refactoring
- **Reduced Bugs**: Catch type-related errors before runtime
- **Improved Documentation**: Type annotations serve as inline documentation
- **Better Testing**: Type hints help ensure test data matches expected types
- **Team Collaboration**: Clear interfaces make code easier to understand and maintain

The `py.typed` file is included in the package, enabling full type checking support in any project that uses Artanis.

## 🎯 Multiple Methods for Same Path

Artanis supports registering different handlers for the same path with different HTTP methods:

```python
async def get_users():
    return {"users": ["alice", "bob"]}

async def create_user(request):
    data = await request.json()
    return {"created": data}

# Both handlers can be registered for the same path
app.get("/users", get_users)
app.post("/users", create_user)

# Or register for all HTTP methods at once
app.all("/users", universal_handler)
```

## ⚠️ Exception Handling

Artanis provides a comprehensive exception handling system with custom exception classes, structured error responses, and automatic error logging.

### Built-in Exception Classes

Artanis includes a hierarchy of custom exceptions for common web application scenarios:

```python
from artanis.exceptions import (
    RouteNotFound, MethodNotAllowed, ValidationError,
    AuthenticationError, AuthorizationError, HandlerError
)
```

#### Exception Hierarchy

- **`ArtanisException`**: Base exception class with status codes and structured error data
- **`RouteNotFound`** (404): When no route matches the request path
- **`MethodNotAllowed`** (405): When path exists but HTTP method not supported
- **`ValidationError`** (400): For request validation failures
- **`AuthenticationError`** (401): When authentication is required but not provided
- **`AuthorizationError`** (403): When user lacks permission for requested resource
- **`HandlerError`** (500): When route handler execution fails
- **`MiddlewareError`** (500): When middleware encounters errors
- **`ConfigurationError`** (500): For framework configuration issues
- **`RateLimitError`** (429): When rate limits are exceeded

### Structured Error Responses

All exceptions return structured JSON responses with detailed error information:

```json
{
  "error": "Route not found: GET /api/nonexistent",
  "error_code": "ROUTE_NOT_FOUND",
  "status_code": 404,
  "details": {
    "path": "/api/nonexistent",
    "method": "GET"
  }
}
```

### Using Exceptions in Handlers

```python
from artanis import App
from artanis.exceptions import ValidationError, AuthenticationError

app = App()

async def create_user(request):
    try:
        data = await request.json()

        # Validate required fields
        if not data.get('email'):
            raise ValidationError(
                "Email is required",
                field="email",
                validation_errors={"email": "Missing required field"}
            )

        # Check authentication
        if not request.headers.get('authorization'):
            raise AuthenticationError("Bearer token required", auth_type="bearer")

        return {"message": "User created", "data": data}

    except ValidationError:
        # ValidationError is automatically handled by the framework
        raise
    except Exception as e:
        # Other exceptions are wrapped in HandlerError
        raise HandlerError(f"Failed to create user: {str(e)}")

app.post("/users", create_user)
```

### Exception Handler Middleware

Use the built-in exception handler middleware for centralized error handling:

```python
from artanis import App
from artanis.middleware import ExceptionHandlerMiddleware

app = App()

# Add exception handling middleware
exception_handler = ExceptionHandlerMiddleware(
    debug=True,  # Include detailed error info in development
    include_traceback=True  # Include stack traces in debug mode
)
app.use(exception_handler)

# Add custom handler for specific exceptions
def handle_validation_error(exc, request, response):
    response.set_status(400)
    response.json({
        "error": "Validation failed",
        "details": exc.details,
        "suggestions": ["Check required fields", "Validate data types"]
    })
    return response

exception_handler.add_handler(ValidationError, handle_validation_error)
```

### Request Validation Middleware

Automatic request validation with the validation middleware:

```python
from artanis.middleware import ValidationMiddleware

# Create validation middleware
validator = ValidationMiddleware(
    validate_json=True,
    required_fields=["name", "email"],
    custom_validators={
        "email": lambda email: "@" in email and "." in email,
        "age": lambda age: isinstance(age, int) and age >= 0
    }
)

# Apply to specific routes
app.use("/api/users", validator)
```

### Error Logging Integration

All exceptions are automatically logged with structured context:

```python
# Error logs include request context and exception details
# Example log output (JSON format):
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "ERROR",
  "logger": "artanis",
  "message": "VALIDATION_ERROR: Email is required",
  "method": "POST",
  "path": "/api/users",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {"field": "email", "validation_errors": {"email": "Missing required field"}}
}
```

### Creating Custom Exceptions

Extend `ArtanisException` for application-specific errors:

```python
from artanis.exceptions import ArtanisException

class InsufficientCreditsError(ArtanisException):
    def __init__(self, required_credits, available_credits):
        super().__init__(
            message=f"Insufficient credits: need {required_credits}, have {available_credits}",
            status_code=402,  # Payment Required
            error_code="INSUFFICIENT_CREDITS",
            details={
                "required_credits": required_credits,
                "available_credits": available_credits
            }
        )

# Use in handlers
async def purchase_handler(request):
    user_credits = 10
    item_cost = 25

    if user_credits < item_cost:
        raise InsufficientCreditsError(item_cost, user_credits)

    return {"message": "Purchase successful"}
```

### Exception Handling Best Practices

1. **Use Specific Exceptions**: Choose the most appropriate exception type for each scenario
2. **Include Context**: Provide detailed error information in the `details` field
3. **Log Appropriately**: Client errors (4xx) are logged as warnings, server errors (5xx) as errors
4. **Validate Early**: Use validation middleware to catch errors before reaching handlers
5. **Handle Gracefully**: Use exception middleware for consistent error responses
6. **Debug Mode**: Enable debug mode in development for detailed error information

## ✍️ Handler Function Signatures

Artanis automatically inspects your handler functions and provides the appropriate arguments:

### No Parameters

```python
async def simple_handler():
    return {"message": "Hello"}
```

### Path Parameters Only

```python
async def user_handler(user_id):
    return {"user_id": user_id}
```

### Request Object Only

```python
async def create_handler(request):
    data = await request.json()
    return {"created": data}
```

### Mixed Parameters

```python
async def update_handler(user_id, request):
    data = await request.json()
    return {"user_id": user_id, "data": data}
```

## 📄 Response Format

All responses are automatically serialized to JSON with appropriate headers:

- Content-Type: `application/json`
- Content-Length: Set automatically
- Status Code: 200 for successful responses, appropriate error codes for failures

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Project Structure

```md
artanis/
├── src/
│   └── artanis/
│       ├── __init__.py       # Main framework exports
│       ├── _version.py       # Version management
│       ├── application.py    # Main App class
│       ├── asgi.py          # ASGI protocol handling
│       ├── events.py        # Event handling system
│       ├── exceptions.py     # Custom exception classes
│       ├── handlers.py      # Parameter injection and handler execution
│       ├── logging.py        # Logging system
│       ├── request.py       # HTTP request handling
│       ├── routing.py        # Router and Route classes with subrouting
│       ├── py.typed          # Type hints marker
│       └── middleware/       # Middleware system
│           ├── __init__.py   # Middleware exports
│           ├── chain.py      # Middleware execution chain
│           ├── core.py       # Core middleware functionality
│           ├── exception.py  # Exception handling middleware
│           ├── response.py   # Response management
│           └── security.py   # Security middleware (CORS, CSP, HSTS, etc.)
├── tests/
│   ├── test_artanis.py       # Framework tests (18 tests)
│   ├── test_events.py        # Event handling tests (28 tests)
│   ├── test_exceptions.py    # Exception tests (29 tests)
│   ├── test_logging.py       # Logging tests (14 tests)
│   ├── test_middleware.py    # Middleware tests (22 tests)
│   ├── test_routing.py       # Routing tests (34 tests)
│   ├── test_security.py      # Security middleware tests (31 tests)
│   └── test_version.py       # Version tests (15 tests)
│   # Total: 191 comprehensive tests
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

## 🔧 Version Management

Artanis provides comprehensive version management following PEP 396 standards:

### Accessing Version Information

```python
import artanis

# Get version string
print(artanis.__version__)  # "0.1.0"

# Get version tuple for programmatic comparison
print(artanis.VERSION)      # (0, 1, 0)
print(artanis.version_info) # (0, 1, 0) - alias for VERSION

# Use helper functions
from artanis import get_version, get_version_info

version_string = get_version()      # "0.1.0"
version_tuple = get_version_info()  # (0, 1, 0)
```

### Version Components

The version system provides multiple ways to access version information:

- **`__version__`**: String version following semantic versioning (e.g., "0.1.0")
- **`VERSION`**: Tuple of integers for programmatic access (e.g., (0, 1, 0))
- **`version_info`**: Alias for VERSION tuple, similar to `sys.version_info`
- **`get_version()`**: Function that returns the version string
- **`get_version_info()`**: Function that returns the version tuple

### Semantic Versioning

Artanis follows [Semantic Versioning](https://semver.org/) principles:

- **Major version** (0): Breaking changes or major feature releases
- **Minor version** (1): New features that are backwards compatible
- **Patch version** (0): Bug fixes and small improvements

### Version in Applications

```python
from artanis import App, __version__

app = App()

@app.get('/version')
async def get_app_version():
    return {
        "framework": "Artanis",
        "version": __version__,
        "components": {
            "major": artanis.VERSION[0],
            "minor": artanis.VERSION[1],
            "patch": artanis.VERSION[2]
        }
    }
```

### Dynamic Version Management

The version is managed through a single source of truth in `src/artanis/_version.py` and dynamically read by `pyproject.toml` during package building. This ensures consistency across all access methods and package metadata.

## 📋 Requirements

- Python 3.8+
- No runtime dependencies (uses only Python standard library)

## 📜 License

This project is open source. Feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🔌 ASGI Compatibility

Artanis implements the ASGI 3.0 specification and can be used with any ASGI server:

- [Uvicorn](https://www.uvicorn.org/) (recommended)
- [Hypercorn](https://hypercorn.readthedocs.io/)
- [Daphne](https://github.com/django/daphne)

## 📖 Examples

Check the `tests/` directory for comprehensive examples of how to use all features of the framework.
