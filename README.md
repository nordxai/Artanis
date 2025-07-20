# Artanis ASGI Framework

A lightweight, minimalist ASGI web framework for Python built with simplicity and performance in mind. Artanis provides a clean, intuitive API for building modern web applications using named routes.

## Features

- **Named Routes**: Clean `app.get(path, handler)` and `app.post(path, handler)` syntax
- **Path Parameters**: Support for dynamic path segments like `/users/{user_id}`
- **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE on the same path
- **ASGI Compliant**: Works with any ASGI server (Uvicorn, Hypercorn, etc.)
- **Automatic JSON Responses**: Built-in JSON serialization for response data
- **Request Body Parsing**: Easy access to JSON request bodies
- **Proper HTTP Status Codes**: Automatic 404, 405, and 500 error handling
- **Type Hints**: Full type annotation support

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd projectArtanis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Quick Start

### Basic Application

```python
from src.asgi import App

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
from src.asgi import App

app = App()

# Add your routes here...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# Run with uvicorn
uvicorn main:app --reload
```

## API Reference

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

## Path Parameters

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

## Multiple Methods for Same Path

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

## Error Handling

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

## Handler Function Signatures

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

## Response Format

All responses are automatically serialized to JSON with appropriate headers:

- Content-Type: `application/json`
- Content-Length: Set automatically
- Status Code: 200 for successful responses, appropriate error codes for failures

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Project Structure

```
projectArtanis/
├── src/
│   └── asgi.py          # Main framework code
├── tests/
│   └── test_asgi.py     # Test suite
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## Requirements

- Python 3.8+
- No runtime dependencies (uses only Python standard library)

## License

This project is open source. Feel free to use, modify, and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## ASGI Compatibility

Artanis implements the ASGI 3.0 specification and can be used with any ASGI server:

- [Uvicorn](https://www.uvicorn.org/) (recommended)
- [Hypercorn](https://hypercorn.readthedocs.io/)
- [Daphne](https://github.com/django/daphne)

## Examples

Check the `tests/` directory for comprehensive examples of how to use all features of the framework.