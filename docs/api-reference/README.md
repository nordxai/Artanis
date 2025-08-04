# API Reference

This section provides detailed documentation for all Artanis framework APIs and components.

## Available References

### [OpenAPI Integration](openapi.md)
Complete reference for Artanis's OpenAPI 3.0.1 integration, including:
- App class methods for OpenAPI spec generation
- Decorators for route metadata (`@openapi_route`, `@response_model`, etc.)
- Type system and automatic schema generation
- Request/response validation middleware
- Interactive documentation setup (Swagger UI & ReDoc)
- Complete examples and best practices

## Quick Navigation

| Component | Description | Reference |
|-----------|-------------|-----------|
| **OpenAPI** | API documentation & validation | [openapi.md](openapi.md) |
| **Core App** | Main application class | Coming soon |
| **Routing** | Route registration & handling | Coming soon |
| **Middleware** | Request/response processing | Coming soon |
| **Events** | Event handling system | Coming soon |
| **Logging** | Structured logging | Coming soon |
| **Security** | Security middleware (CORS, CSP, etc.) | Coming soon |

## Getting Started

For a quick start with OpenAPI documentation:

```python
from artanis import App
from artanis.openapi import openapi_route

app = App()

@openapi_route(summary="Hello World", tags=["demo"])
async def hello():
    return {"message": "Hello, World!"}

app.get("/hello", hello)
app.generate_openapi_spec(title="My API", version="1.0.0")
app.serve_docs()  # Visit /docs for interactive documentation
```

See the [OpenAPI reference](openapi.md) for complete documentation.
