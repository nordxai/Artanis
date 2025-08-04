# OpenAPI API Reference

This document provides a complete reference for Artanis's OpenAPI integration, which enables automatic API documentation generation with interactive Swagger UI and ReDoc interfaces.

## Quick Start

```python
from artanis import App
from artanis.openapi import openapi_route, response_model

app = App()

@openapi_route(summary="Get user", tags=["users"])
@response_model(dict, status_code=200)
async def get_user(user_id: int):
    """Retrieve a user by ID."""
    return {"id": user_id, "name": "John Doe"}

app.get("/users/{user_id}", get_user)

# Generate OpenAPI spec and serve docs
app.generate_openapi_spec(title="My API", version="1.0.0")
app.serve_docs()  # Available at /docs and /redoc
```

## App Class Methods

### `generate_openapi_spec(title, version, description)`

Generates the OpenAPI 3.0.1 specification for your application.

**Parameters:**
- `title` (str): API title
- `version` (str): API version (e.g., "1.0.0")
- `description` (str, optional): API description (supports Markdown)

**Returns:** `dict` - The OpenAPI specification dictionary

**Example:**
```python
spec = app.generate_openapi_spec(
    title="My REST API",
    version="2.1.0",
    description="A comprehensive API for managing users and posts"
)
```

### `serve_docs(docs_path, redoc_path, openapi_path, auto_generate)`

Enables interactive API documentation endpoints.

**Parameters:**
- `docs_path` (str, default="/docs"): Path for Swagger UI
- `redoc_path` (str, default="/redoc"): Path for ReDoc UI
- `openapi_path` (str, default="/openapi.json"): Path for OpenAPI JSON
- `auto_generate` (bool, default=True): Auto-generate spec if not exists

**Example:**
```python
app.serve_docs(
    docs_path="/swagger",
    redoc_path="/documentation",
    openapi_path="/api.json"
)
```

### `add_openapi_metadata(servers, tags)`

Adds metadata to the OpenAPI specification.

**Parameters:**
- `servers` (list, optional): List of server configurations
- `tags` (list, optional): List of tag definitions

**Example:**
```python
app.add_openapi_metadata(
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Development"}
    ],
    tags=[
        {"name": "users", "description": "User management"},
        {"name": "posts", "description": "Blog posts"}
    ]
)
```

### `export_openapi(file_path, format, auto_generate)`

Exports the OpenAPI specification to a file.

**Parameters:**
- `file_path` (str): Output file path
- `format` (str, default="json"): Export format ("json" or "yaml")
- `auto_generate` (bool, default=True): Generate spec if not exists

**Example:**
```python
app.export_openapi("api_spec.json", format="json")
app.export_openapi("api_spec.yaml", format="yaml")
```

### `add_openapi_validation(validate_requests, validate_responses, strict_mode)`

Adds request/response validation middleware.

**Parameters:**
- `validate_requests` (bool, default=True): Validate incoming requests
- `validate_responses` (bool, default=False): Validate outgoing responses
- `strict_mode` (bool, default=False): Strict validation mode

**Example:**
```python
app.add_openapi_validation(
    validate_requests=True,
    validate_responses=True,
    strict_mode=False
)
```

## Decorators

### `@openapi_route(summary, description, tags, responses)`

Adds OpenAPI metadata to route handlers.

**Parameters:**
- `summary` (str, optional): Brief summary of the endpoint
- `description` (str, optional): Detailed description
- `tags` (list, optional): List of tags for grouping
- `responses` (dict, optional): Response definitions

**Example:**
```python
@openapi_route(
    summary="Create user",
    description="Creates a new user account with validation",
    tags=["users", "auth"],
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"}
    }
)
async def create_user():
    pass
```

### `@response_model(model, status_code, description)`

Specifies the response model and status code.

**Parameters:**
- `model` (type): Response model class (dataclass, dict, etc.)
- `status_code` (int, default=200): HTTP status code
- `description` (str, optional): Response description

**Example:**
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

@response_model(User, status_code=200)
async def get_user():
    return User(id=1, name="John", email="john@example.com")
```

### `@request_model(model)`

Specifies the request body model.

**Parameters:**
- `model` (type): Request model class

**Example:**
```python
@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int = None

@request_model(CreateUserRequest)
async def create_user(request):
    data = await request.json()
    # data is validated against CreateUserRequest
    return {"message": "User created"}
```

### `@tag(name)`

Adds a tag to the route for organization.

**Parameters:**
- `name` (str): Tag name

**Example:**
```python
@tag("users")
@tag("admin")
async def admin_users():
    pass
```

### `@deprecated(reason)`

Marks an endpoint as deprecated.

**Parameters:**
- `reason` (str, optional): Deprecation reason

**Example:**
```python
@deprecated("Use GET /v2/users instead")
async def old_users():
    pass
```

### `@operation_id(id)`

Sets a unique operation ID for the endpoint.

**Parameters:**
- `id` (str): Unique operation identifier

**Example:**
```python
@operation_id("getUserById")
async def get_user():
    pass
```

### `@security(requirements)`

Adds security requirements to the endpoint.

**Parameters:**
- `requirements` (list): Security requirement definitions

**Example:**
```python
@security([{"bearerAuth": []}])
async def protected_route():
    pass
```

### `@example(request_example, response_example)`

Adds examples for request/response.

**Parameters:**
- `request_example` (dict, optional): Request body example
- `response_example` (dict, optional): Response body example

**Example:**
```python
@example(
    request_example={"name": "John Doe", "email": "john@example.com"},
    response_example={"id": 1, "name": "John Doe", "status": "created"}
)
async def create_user():
    pass
```

## Type System

Artanis automatically converts Python type hints to OpenAPI schemas:

### Supported Types

| Python Type | OpenAPI Schema |
|-------------|----------------|
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `str` | `{"type": "string"}` |
| `bool` | `{"type": "boolean"}` |
| `list[T]` | `{"type": "array", "items": {...}}` |
| `dict[str, T]` | `{"type": "object", "additionalProperties": {...}}` |
| `Optional[T]` | `{..., "nullable": true}` |
| `dataclass` | Complete object schema with properties |
| `Enum` | `{"type": "string", "enum": [...]}` |

### Dataclass Example

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@dataclass
class User:
    id: int
    name: str
    email: str
    age: Optional[int] = None
    status: UserStatus = UserStatus.ACTIVE

# Automatically generates:
# {
#   "type": "object",
#   "properties": {
#     "id": {"type": "integer"},
#     "name": {"type": "string"},
#     "email": {"type": "string"},
#     "age": {"type": "integer", "nullable": true},
#     "status": {"type": "string", "enum": ["active", "inactive"]}
#   },
#   "required": ["id", "name", "email"]
# }
```

## Validation Middleware

The validation middleware automatically validates requests and responses against OpenAPI schemas.

### Request Validation

```python
app.add_openapi_validation(validate_requests=True)

@request_model(CreateUserRequest)
async def create_user(request):
    # Request body is automatically validated
    # Invalid requests return 422 with detailed errors
    data = await request.json()
    return {"user": data}
```

### Response Validation

```python
app.add_openapi_validation(validate_responses=True)

@response_model(User, status_code=200)
async def get_user():
    # Response is automatically validated against User schema
    # Invalid responses log warnings or raise errors in strict mode
    return User(id=1, name="John", email="john@example.com")
```

### Error Responses

Validation errors return structured JSON responses:

```json
{
  "detail": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "invalid-email"
    }
  ]
}
```

## Complete Example

```python
from artanis import App
from artanis.openapi import *
from dataclasses import dataclass
from typing import Optional

app = App()

@dataclass
class User:
    id: int
    name: str
    email: str
    age: Optional[int] = None

@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: Optional[int] = None

# Health check endpoint
@openapi_route(
    summary="Health Check",
    description="Check if the API is running",
    tags=["monitoring"]
)
async def health():
    return {"status": "healthy"}

# Get user endpoint
@openapi_route(
    summary="Get User",
    description="Retrieve a user by their ID",
    tags=["users"]
)
@response_model(User, status_code=200)
async def get_user(user_id: int):
    return User(id=user_id, name="John Doe", email="john@example.com")

# Create user endpoint
@openapi_route(
    summary="Create User",
    description="Create a new user account",
    tags=["users"]
)
@request_model(CreateUserRequest)
@response_model(User, status_code=201)
async def create_user(request):
    data = await request.json()
    new_user = User(id=123, **data)
    return new_user

# Register routes
app.get("/health", health)
app.get("/users/{user_id}", get_user)
app.post("/users", create_user)

# Configure OpenAPI
app.add_openapi_metadata(
    servers=[{"url": "http://localhost:8000", "description": "Development"}],
    tags=[
        {"name": "monitoring", "description": "Health and monitoring"},
        {"name": "users", "description": "User management"}
    ]
)

# Generate spec and serve docs
app.generate_openapi_spec(
    title="User Management API",
    version="1.0.0",
    description="A simple API for managing users"
)

app.serve_docs()  # Available at /docs and /redoc
app.add_openapi_validation(validate_requests=True)

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
```

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation!

## Best Practices

1. **Use Descriptive Summaries**: Write clear, concise summaries for all endpoints
2. **Leverage Type Hints**: Use proper Python type hints for automatic schema generation
3. **Group with Tags**: Organize endpoints using meaningful tags
4. **Validate Requests**: Enable request validation for better API reliability
5. **Document Responses**: Use `@response_model` to document expected responses
6. **Handle Errors**: Define error responses for different status codes
7. **Use Examples**: Provide examples for complex request/response models
8. **Version Your API**: Include version information in your OpenAPI spec

## Integration with CORS

For browser-based API testing, add CORS middleware:

```python
async def cors_middleware(request, response, next):
    response.set_header("Access-Control-Allow-Origin", "*")
    response.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.set_header("Access-Control-Allow-Headers", "*")

    if hasattr(request, 'scope') and request.scope.get('method') == "OPTIONS":
        response.status_code = 200
        return

    await next()

app.use(cors_middleware)
```

This enables the "Try it out" functionality in Swagger UI to work properly.
