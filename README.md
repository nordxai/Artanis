# Artanis

![Tests](https://github.com/nordxai/artanis/workflows/Tests/badge.svg)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Open%20Source-green.svg)](LICENSE)

A lightweight, minimalist ASGI web framework for Python built with simplicity and performance in mind. Artanis provides a clean, intuitive API for building modern web applications using named routes.

## ✨ Features

- **Named Routes**: Clean `app.get(path, handler)` and `app.post(path, handler)` syntax
- **Path Parameters**: Support for dynamic path segments like `/users/{user_id}`
- **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE on the same path
- **ASGI Compliant**: Works with any ASGI server (Uvicorn, Hypercorn, etc.)
- **Express-Style Middleware**: Powerful middleware system with `app.use()` API
- **Path-Based Middleware**: Apply middleware to specific routes or paths
- **Automatic JSON Responses**: Built-in JSON serialization for response data
- **Request Body Parsing**: Easy access to JSON request bodies
- **Proper HTTP Status Codes**: Automatic 404, 405, and 500 error handling
- **Type Hints**: Full type annotation support
- **Structured Logging**: Built-in logging system with configurable formatters and request tracking

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

# Install in development mode
pip install -e .
```

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

### Real-World Middleware Examples

#### CORS Middleware
```python
async def cors_middleware(request, response, next):
    origin = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    if request.scope["method"] == "OPTIONS":
        response.status = 200
        response.body = ""
        return
    
    await next()

app.use(cors_middleware)
```

#### JWT Authentication Middleware
```python
import jwt

async def jwt_auth_middleware(request, response, next):
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        response.status = 401
        response.body = {"error": "Missing or invalid authorization header"}
        return
    
    token = auth_header[7:]  # Remove "Bearer "
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.user = payload  # Add user info to request
        await next()
    except jwt.ExpiredSignatureError:
        response.status = 401
        response.body = {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        response.status = 401
        response.body = {"error": "Invalid token"}

app.use("/api/protected", jwt_auth_middleware)
```

#### Request Logging Middleware
```python
import logging
import time

logger = logging.getLogger("artanis")

async def logging_middleware(request, response, next):
    start_time = time.time()
    method = request.scope["method"]
    path = request.scope["path"]
    
    logger.info(f"→ {method} {path}")
    
    await next()
    
    duration = time.time() - start_time
    logger.info(f"← {method} {path} {response.status} ({duration:.3f}s)")

app.use(logging_middleware)
```

#### Rate Limiting Middleware
```python
import time
from collections import defaultdict

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)
RATE_LIMIT = 100  # requests per minute
WINDOW = 60  # seconds

async def rate_limit_middleware(request, response, next):
    client_ip = request.scope.get("client", ["unknown", None])[0]
    now = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < WINDOW
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        response.status = 429
        response.body = {"error": "Rate limit exceeded"}
        return
    
    # Add current request
    request_counts[client_ip].append(now)
    await next()

app.use("/api", rate_limit_middleware)
```

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
```

## ⚠️ Error Handling

Artanis automatically handles common HTTP errors:

- **404 Not Found**: When no route matches the request path
- **405 Method Not Allowed**: When the path exists but the HTTP method is not supported
- **500 Internal Server Error**: When an unhandled exception occurs in a route handler

All errors are returned as JSON responses:

```json
{
  "error": "Not Found"
}
```

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
│       ├── __init__.py     # Main framework code
│       ├── logging.py      # Logging system
│       └── middleware/     # Middleware system
├── tests/
│   ├── test_artanis.py     # Framework tests (16 tests)
│   ├── test_middleware.py  # Middleware tests (22 tests)
│   └── test_logging.py     # Logging tests (14 tests)
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

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
