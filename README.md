<div align="center">
  <img src="https://raw.githubusercontent.com/nordxai/Artanis/main/assets/artanis-logo.png" alt="Artanis Framework Logo" width="200" height="200">

  # Artanis

  A lightweight, minimalist ASGI web framework for Python built with simplicity and performance in mind.

  **📚 [Complete Documentation](https://nordxai.github.io/Artanis/) | 🚀 [Quick Start Guide](https://nordxai.github.io/Artanis/getting-started/quickstart/) | 💡 [Examples](https://nordxai.github.io/Artanis/examples/) | 🔍 [API Reference](https://nordxai.github.io/Artanis/api/core/app/)**
</div>

[![Tests](https://github.com/nordxai/Artanis/actions/workflows/test.yml/badge.svg)](https://github.com/nordxai/Artanis/actions/workflows/test.yml)
[![Code Quality](https://github.com/nordxai/Artanis/actions/workflows/code-quality.yml/badge.svg)](https://github.com/nordxai/Artanis/actions/workflows/code-quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Open%20Source-green.svg)](LICENSE)

Artanis provides a clean, intuitive API for building modern web applications with Express.js-style middleware and comprehensive built-in features.

## ✨ Key Features

- **🚀 Express.js-Style API**: Clean `app.get()`, `app.post()`, `app.use()` middleware patterns
- **🏗️ Advanced Routing**: Modular routers, path parameters, nested subrouting, parameterized mounts
- **🔐 Built-in Security**: CORS, CSP, HSTS, rate limiting, security headers, comprehensive middleware suite
- **📡 Event System**: Startup/shutdown events, custom business events, priority execution, event middleware
- **⚠️ Exception Handling**: Custom exception hierarchy, structured error responses, automatic logging
- **📊 Professional Logging**: Structured logging, JSON/text formats, request tracking, component-specific loggers
- **🔷 Type Safety**: Complete type hints, mypy compatibility, excellent IDE support
- **🎯 ASGI Compliant**: Works with Uvicorn, Hypercorn, Daphne - zero runtime dependencies

> **📖 [View Complete Feature List & Documentation →](https://nordxai.github.io/Artanis/)**

## 📦 Installation

```bash
pip install artanis
```

**Requirements**: Python 3.8+ • Zero runtime dependencies

> **📚 [Development Setup Guide](https://nordxai.github.io/Artanis/getting-started/installation/) | 🔧 [Contributing Guidelines](https://nordxai.github.io/Artanis/contributing/documentation/)**

## 🚀 Quick Start

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

# POST route with JSON body
async def create_user(request):
    data = await request.json()
    return {"created": data}

app.post("/users", create_user)

# Run with: uvicorn main:app --reload
```

> **🚀 [Complete Quick Start Tutorial](https://nordxai.github.io/Artanis/getting-started/quickstart/) | 💡 [View More Examples](https://nordxai.github.io/Artanis/examples/)**

## 📚 Documentation & Resources

**Complete Documentation**: [nordxai.github.io/Artanis](https://nordxai.github.io/Artanis/)

### Quick Links

- **🚀 [Quick Start Guide](https://nordxai.github.io/Artanis/getting-started/quickstart/)** - Get started in minutes
- **💡 [Examples](https://nordxai.github.io/Artanis/examples/)** - Real-world applications and patterns
- **🔍 [API Reference](https://nordxai.github.io/Artanis/api/core/app/)** - Complete API documentation
- **🏗️ [Tutorial](https://nordxai.github.io/Artanis/getting-started/first-app/)** - Build your first application
- **🛠️ [Contributing](https://nordxai.github.io/Artanis/contributing/documentation/)** - Development setup and guidelines

## 🚀 CLI Tool

Create new projects instantly:

```bash
# Create a new Artanis project
artanis new my-project
cd my-project

# Run your application
uvicorn main:app --reload
```

## 🛠️ Development & Testing

```bash
# Clone repository
git clone https://github.com/nordxai/Artanis
cd Artanis

# Install in development mode
pip install -e ".[dev]"

# Run tests (191 comprehensive tests)
pytest

# Code quality checks
ruff check . && mypy src/artanis
```

## 🤝 Community & Support

- **📚 [Documentation](https://nordxai.github.io/Artanis/)** - Complete guides and API reference
- **🐛 [Issues](https://github.com/nordxai/Artanis/issues)** - Bug reports and feature requests
- **💬 [Discussions](https://github.com/nordxai/Artanis/discussions)** - Community support and questions
- **📦 [PyPI](https://pypi.org/project/artanis/)** - Package releases and changelog
- **⭐ [GitHub](https://github.com/nordxai/Artanis)** - Source code and contributions

**Requirements**: Python 3.8+ • Zero runtime dependencies • ASGI compliant

---

<div align="center">
<strong>Built with ❤️ for the Python community</strong><br>
<em>Express.js simplicity meets Python performance</em>
</div>
