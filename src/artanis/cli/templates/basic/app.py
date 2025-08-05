"""
{{project_description}}

A simple Artanis application demonstrating basic routing and middleware.
"""

from __future__ import annotations

import time
from typing import Any

import uvicorn

from artanis import App

# Create the application
app = App()


# ================================
# ROUTES
# ================================


async def root() -> dict[str, Any]:
    """Welcome endpoint."""
    return {
        "message": "Welcome to {{project_name}}!",
        "framework": "Artanis",
        "version": "{{artanis_version}}",
        "endpoints": {
            "GET /": "This welcome message",
            "GET /health": "Health check",
            "GET /hello/{name}": "Personalized greeting",
            "POST /echo": "Echo the request body",
        },
        "docs": "Check the README.md file for more information",
    }


async def health() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "project": "{{project_name}}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


async def hello(name: str) -> dict[str, Any]:
    """Personalized greeting with path parameter."""
    return {
        "message": f"Hello, {name}!",
        "project": "{{project_name}}",
        "note": "This demonstrates path parameters in Artanis",
    }


async def echo(request: Any) -> dict[str, Any]:
    """Echo the request body back to the client."""
    try:
        data = await request.json()
        return {
            "echo": data,
            "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "note": "This demonstrates request body parsing",
        }
    except Exception:
        return {
            "error": "Invalid JSON in request body",
            "expected": "Content-Type: application/json",
        }


# ================================
# REGISTER ROUTES
# ================================

app.get("/", root)
app.get("/health", health)
app.get("/hello/{name}", hello)
app.post("/echo", echo)


# ================================
# MAIN APPLICATION
# ================================

if __name__ == "__main__":
    print("🚀 Starting {{project_name}} with Artanis")
    print("📍 Available endpoints:")
    print("   GET    /              - Welcome message")
    print("   GET    /health        - Health check")
    print("   GET    /hello/{name}  - Personalized greeting")
    print("   POST   /echo          - Echo request body")
    print()
    print("🌐 Server starting at: http://127.0.0.1:8000")
    print("⏹️  Press Ctrl+C to stop")
    print()

    # Start the server
    uvicorn.run(
        "app:app",  # Use import string for reload functionality
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
