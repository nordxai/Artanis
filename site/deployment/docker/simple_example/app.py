"""
Simple Artanis Docker Example

A minimal Artanis application for Docker demonstration.
"""

from __future__ import annotations

import os
import time

import uvicorn

from artanis import App

app = App()


async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Hello from Artanis in Docker!",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "container_id": os.getenv("HOSTNAME", "unknown"),
    }


async def health() -> dict[str, str | float]:
    """Health check for Docker."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


# Route registrations
app.get("/", root)
app.get("/health", health)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104 # Required for Docker container access
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT") == "development",
    )
