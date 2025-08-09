# Middleware Demo

A comprehensive demonstration of Artanis middleware capabilities, showcasing various middleware patterns and security implementations.

## Overview

This example demonstrates:

- **Security Middleware**: CORS, rate limiting, security headers
- **Authentication Middleware**: JWT token validation
- **Logging Middleware**: Request/response logging
- **Custom Middleware**: Application-specific functionality
- **Error Handling**: Comprehensive error middleware
- **Middleware Chaining**: Proper execution order

## Features

### 🛡️ Security Middleware
- **CORS Configuration**: Cross-origin resource sharing
- **Rate Limiting**: Prevent API abuse
- **Security Headers**: HSTS, CSP, X-Frame-Options
- **Content Security Policy**: XSS protection
- **Request Validation**: Input sanitization

### 📊 Logging & Monitoring
- **Request Logging**: Detailed request/response tracking
- **Performance Metrics**: Response time measurement
- **Error Logging**: Structured error information
- **Access Logs**: IP tracking and user agent logging

### 🔐 Authentication
- **JWT Middleware**: Token validation
- **User Context**: Request user injection
- **Permission Checking**: Role-based access
- **Session Management**: Token refresh handling

## Project Structure

```
middleware_demo/
├── app.py                    # Main application
├── middleware/
│   ├── __init__.py          # Middleware exports
│   ├── security.py          # Security middleware implementations
│   ├── auth.py             # Authentication middleware
│   ├── logging.py          # Request logging middleware
│   └── validation.py       # Input validation middleware
└── utils/
    ├── jwt_helper.py       # JWT token utilities
    └── rate_limiter.py     # Rate limiting implementation
```

## Quick Start

1. **Navigate to the demo**:
   ```bash
   git clone https://github.com/nordxai/Artanis
   cd Artanis/docs/examples/middleware_demo
   ```

2. **Install dependencies**:
   ```bash
   pip install artanis uvicorn[standard]
   ```

3. **Run the demo**:
   ```bash
   python app.py
   ```

4. **Test middleware**:
   ```bash
   # Test basic endpoint
   curl http://127.0.0.1:8000/

   # Test rate limiting
   for i in {1..10}; do curl http://127.0.0.1:8000/api/data; done

   # Test authentication
   curl -H "Authorization: Bearer invalid-token" http://127.0.0.1:8000/api/protected
   ```

## Middleware Examples

### 1. CORS Middleware

```python
async def cors_middleware(request, response, next):
    """Comprehensive CORS middleware with preflight support."""
    origin = request.headers.get('origin')

    # Handle preflight requests
    if request.scope.get('method') == 'OPTIONS':
        response.headers.update({
            'Access-Control-Allow-Origin': origin or '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        })
        response.status = 200
        return

    await next()

    # Add CORS headers to actual response
    response.headers.update({
        'Access-Control-Allow-Origin': origin or '*',
        'Access-Control-Allow-Credentials': 'true'
    })
```

### 2. Rate Limiting Middleware

```python
import time
from collections import defaultdict

# Simple in-memory rate limiter
rate_limits = defaultdict(list)

async def rate_limit_middleware(request, response, next):
    """Rate limiting middleware with configurable limits."""
    client_ip = request.scope.get('client', ['unknown'])[0]
    now = time.time()
    window = 60  # 1 minute
    max_requests = 100

    # Clean old requests
    rate_limits[client_ip] = [
        req_time for req_time in rate_limits[client_ip]
        if now - req_time < window
    ]

    # Check rate limit
    if len(rate_limits[client_ip]) >= max_requests:
        response.status = 429
        response.body = {
            "error": "Rate limit exceeded",
            "retry_after": window
        }
        return

    # Record this request
    rate_limits[client_ip].append(now)
    await next()
```

### 3. Security Headers Middleware

```python
async def security_headers_middleware(request, response, next):
    """Add comprehensive security headers."""
    await next()

    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    })
```

### 4. Request Logging Middleware

```python
import time
import json
import logging

logger = logging.getLogger('artanis.requests')

async def request_logging_middleware(request, response, next):
    """Comprehensive request logging with metrics."""
    start_time = time.time()

    # Log request
    request_data = {
        'method': request.scope.get('method'),
        'path': request.scope.get('path'),
        'query_string': request.scope.get('query_string', b'').decode(),
        'user_agent': request.headers.get('user-agent', 'Unknown'),
        'client_ip': request.scope.get('client', ['unknown'])[0],
        'timestamp': time.time()
    }

    logger.info(f"→ {request_data['method']} {request_data['path']}")

    await next()

    # Log response
    duration = time.time() - start_time
    response_data = {
        'status': response.status,
        'duration': f"{duration:.3f}s",
        'response_size': len(str(response.body)) if response.body else 0
    }

    logger.info(f"← {request_data['method']} {request_data['path']} "
                f"{response_data['status']} ({response_data['duration']})")

    # Add performance headers
    response.headers['X-Response-Time'] = response_data['duration']
```

### 5. Authentication Middleware

```python
import jwt

async def auth_middleware(request, response, next):
    """JWT authentication middleware."""
    auth_header = request.headers.get('authorization', '')

    if not auth_header.startswith('Bearer '):
        response.status = 401
        response.body = {"error": "Missing or invalid authorization header"}
        return

    token = auth_header[7:]  # Remove 'Bearer ' prefix

    try:
        payload = jwt.decode(token, 'secret-key', algorithms=['HS256'])
        request.user = payload  # Add user info to request
        await next()
    except jwt.ExpiredSignatureError:
        response.status = 401
        response.body = {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        response.status = 401
        response.body = {"error": "Invalid token"}
```

### 6. Error Handling Middleware

```python
import traceback
import logging

logger = logging.getLogger('artanis.errors')

async def error_handling_middleware(request, response, next):
    """Comprehensive error handling and logging."""
    try:
        await next()
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        response.status = 400
        response.body = {
            "error": "Validation failed",
            "message": str(e),
            "field": getattr(e, 'field', None)
        }
    except PermissionError as e:
        logger.warning(f"Permission denied: {e}")
        response.status = 403
        response.body = {
            "error": "Permission denied",
            "message": "You don't have permission to access this resource"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())

        response.status = 500
        response.body = {
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
```

## Middleware Chain Example

```python
from artanis import App

app = App()

# Apply middleware in order (first registered = outermost)
app.use(error_handling_middleware)     # Catch all errors
app.use(request_logging_middleware)    # Log all requests
app.use(security_headers_middleware)   # Add security headers
app.use(cors_middleware)              # Handle CORS
app.use(rate_limit_middleware)        # Rate limiting

# Path-specific middleware
app.use("/api", rate_limit_middleware)        # API rate limiting
app.use("/api/protected", auth_middleware)    # Authentication required

# Routes
async def public_endpoint():
    return {"message": "This is public", "middleware": "basic"}

async def protected_endpoint(request):
    return {
        "message": "This is protected",
        "user": request.user,
        "middleware": "auth + basic"
    }

app.get("/", public_endpoint)
app.get("/api/protected/data", protected_endpoint)
```

## Testing Middleware

### 1. Test CORS
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://127.0.0.1:8000/api/data
```

### 2. Test Rate Limiting
```bash
# Exceed rate limit
for i in {1..110}; do
  curl -s http://127.0.0.1:8000/api/data | head -1
done
```

### 3. Test Authentication
```bash
# Without token (should fail)
curl http://127.0.0.1:8000/api/protected/data

# With invalid token (should fail)
curl -H "Authorization: Bearer invalid-token" \
     http://127.0.0.1:8000/api/protected/data

# Generate valid token first, then test
# (Implementation depends on your JWT setup)
```

### 4. Test Security Headers
```bash
curl -I http://127.0.0.1:8000/
# Check for security headers in response
```

## Middleware Best Practices

### 1. Order Matters
```python
# Correct order:
app.use(error_handling_middleware)    # 1. Catch errors first
app.use(logging_middleware)          # 2. Log everything
app.use(security_middleware)         # 3. Apply security
app.use(auth_middleware)             # 4. Check authentication
# Routes come last
```

### 2. Path-Specific Middleware
```python
# Apply middleware only to specific paths
app.use("/api", rate_limit_middleware)
app.use("/admin", admin_auth_middleware)
app.use("/uploads", file_validation_middleware)
```

### 3. Conditional Middleware
```python
async def conditional_middleware(request, response, next):
    if should_apply_logic(request):
        # Apply middleware logic
        await next()
    else:
        # Skip middleware, go to next
        await next()
```

### 4. Middleware Configuration
```python
def create_rate_limiter(max_requests=100, window=60):
    async def rate_limit_middleware(request, response, next):
        # Use max_requests and window parameters
        # ... implementation
        pass
    return rate_limit_middleware

app.use(create_rate_limiter(max_requests=50, window=300))
```

## Production Considerations

- **Performance**: Minimize middleware overhead
- **Logging**: Use structured logging (JSON)
- **Rate Limiting**: Use Redis for distributed rate limiting
- **Authentication**: Implement proper JWT validation
- **Security**: Regular security header updates
- **Monitoring**: Add metrics and alerting

This middleware demo showcases the power and flexibility of Artanis middleware system for building secure, monitored, and well-structured web applications.
