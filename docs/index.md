# Artanis Framework

<div align="center">
  <img src="./assets/artanis-logo.png" alt="Artanis Framework Logo" width="200" height="200">
</div>

**A lightweight, minimalist ASGI web framework for Python built with simplicity and performance in mind.**

[![Tests](https://github.com/nordxai/Artanis/actions/workflows/test.yml/badge.svg)](https://github.com/nordxai/Artanis/actions/workflows/test.yml)
[![Code Quality](https://github.com/nordxai/Artanis/actions/workflows/code-quality.yml/badge.svg)](https://github.com/nordxai/Artanis/actions/workflows/code-quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Open%20Source-green.svg)](https://github.com/nordxai/Artanis/blob/main/LICENSE)

Artanis provides a clean, intuitive API for building modern web applications and APIs using named routes and a powerful middleware system.

## ✨ Key Features

=== "🚀 Simple & Fast"
    - **Named Routes**: Clean `app.get(path, handler)` and `app.post(path, handler)` syntax
    - **Zero Dependencies**: Uses only Python standard library for maximum compatibility
    - **ASGI Compliant**: Works with Uvicorn, Hypercorn, and other ASGI servers
    - **Type Safe**: Full type annotation support with mypy compatibility

=== "🗂️ Advanced Routing"
    - **Path Parameters**: Dynamic segments like `/users/{user_id}`
    - **Multiple HTTP Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS on the same path
    - **Subrouting**: Mount routers at specific paths for modular applications
    - **Parameterized Mounts**: Dynamic subrouter mounting at paths like `/users/{user_id}`

=== "🔧 Powerful Middleware"
    - **Express-Style**: Intuitive `app.use()` API for middleware
    - **Path-Based**: Apply middleware to specific routes or paths
    - **Security Built-in**: CORS, CSP, HSTS, rate limiting, security headers
    - **Request Logging**: Structured logging with automatic request tracking

=== "📡 Event System"
    - **Extensible Events**: Custom business events with priority execution
    - **ASGI Lifecycle**: Automatic startup and shutdown event handling
    - **Event Middleware**: Cross-cutting concerns for all events
    - **Conditional Handlers**: Execute only when specific conditions are met

## Quick Example

```python
from artanis import App

app = App()

# Simple route
async def hello():
    return {"message": "Hello, World!"}

app.get("/", hello)

# Route with path parameter
async def get_user(user_id):
    return {"user_id": user_id, "name": f"User {user_id}"}

app.get("/users/{user_id}", get_user)

# POST route with request body
async def create_user(request):
    data = await request.json()
    return {"message": "User created", "data": data}

app.post("/users", create_user)
```

## Why Choose Artanis?

!!! success "Perfect for Modern Python Development"
    - **🐍 Python 3.8+**: Built for modern Python with async/await support
    - **📦 Zero Dependencies**: No external runtime dependencies to manage
    - **🔒 Security First**: Comprehensive security middleware included
    - **📖 Excellent Documentation**: Detailed guides, tutorials, and API reference
    - **🧪 Well Tested**: 191+ comprehensive tests ensuring reliability

!!! info "Framework Comparison"
    | Feature | Artanis | FastAPI | Flask | Starlette |
    |---------|---------|---------|-------|-----------|
    | Zero Dependencies | ✅ | ❌ | ❌ | ❌ |
    | Built-in Security | ✅ | ❌ | ❌ | ❌ |
    | Express-style Middleware | ✅ | ❌ | ❌ | ❌ |
    | Event System | ✅ | ❌ | ❌ | ❌ |
    | Subrouting | ✅ | ❌ | ❌ | ❌ |

## What's Next?

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Get Started**

    ---

    Install Artanis and build your first application in minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-book-open:{ .lg .middle } **Learn the Basics**

    ---

    Follow our comprehensive tutorial to build a complete blog API

    [:octicons-arrow-right-24: Tutorial](tutorials/index.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Explore the complete API documentation with examples

    [:octicons-arrow-right-24: API Docs](api/core/app.md)

-   :material-code-braces:{ .lg .middle } **Examples**

    ---

    See working examples for common patterns and use cases

    [:octicons-arrow-right-24: Examples](examples/index.md)

</div>

## Community & Support

- **GitHub Repository**: [nordxai/Artanis](https://github.com/nordxai/Artanis)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/nordxai/Artanis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nordxai/Artanis/discussions)
- **PyPI Package**: [artanis](https://pypi.org/project/artanis/)

## License

Artanis is open source software released under an open source license. Feel free to use, modify, and distribute.
