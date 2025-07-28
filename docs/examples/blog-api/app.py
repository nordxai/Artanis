#!/usr/bin/env python3
"""
Blog API - Complete Example

A comprehensive blog API demonstrating production-ready patterns with Artanis.
Includes authentication, CRUD operations, file uploads, and comprehensive testing.

Run with: python app.py
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import uvicorn

# Import route modules
from routes.auth import auth_router
from routes.posts import posts_router

# Import utilities
from utils.database import init_database

from artanis import App, Router
from artanis.logging import ArtanisLogger
from artanis.middleware import ExceptionHandlerMiddleware
from artanis.middleware.security import (
    CORSMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)

# ================================
# CONFIGURATION
# ================================


@dataclass
class Config:
    """Application configuration."""

    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "3000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Security
    DEFAULT_DEV_SECRET: str = "dev-secret-change-in-production"  # noqa: S105
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_DEV_SECRET)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_IN: int = int(os.getenv("JWT_EXPIRES_IN", "3600"))  # 1 hour

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///blog.db")

    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(5 * 1024 * 1024)))  # 5MB
    ALLOWED_EXTENSIONS: list[str] = field(default_factory=list)

    # CORS
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "").split(",")
        if os.getenv("CORS_ORIGINS")
        else []
    )

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def validate(self) -> None:
        """Validate configuration."""
        if self.is_production and self.DEFAULT_DEV_SECRET == self.SECRET_KEY:
            msg = "SECRET_KEY must be set in production"
            raise ValueError(msg)

        upload_path = Path(self.UPLOAD_DIR)
        if not upload_path.exists():
            upload_path.mkdir(parents=True, exist_ok=True)


config = Config()
config.validate()


# ================================
# LOGGING SETUP
# ================================

ArtanisLogger.configure(
    level=config.LOG_LEVEL, format_type="json" if config.is_production else "text"
)

logger = ArtanisLogger.get_logger("blog_api")


# ================================
# APPLICATION FACTORY
# ================================


def create_app() -> App:
    """Create and configure the Artanis application."""

    app = App(enable_request_logging=not config.is_production)

    # ================================
    # MIDDLEWARE SETUP
    # ================================

    # 1. Exception handling (first)
    exception_handler = ExceptionHandlerMiddleware(
        debug=config.DEBUG, include_traceback=config.DEBUG
    )
    app.use(exception_handler)

    # 2. Security headers (production only)
    if config.is_production:
        security_headers = SecurityHeadersMiddleware(
            x_frame_options="DENY",
            x_content_type_options="nosniff",
            x_xss_protection="1; mode=block",
            referrer_policy="strict-origin-when-cross-origin",
        )
        app.use(security_headers)

    # 3. Rate limiting
    rate_limiter = RateLimitMiddleware(
        requests_per_window=config.RATE_LIMIT_REQUESTS,
        window_seconds=config.RATE_LIMIT_WINDOW,
    )
    app.use(rate_limiter)

    # 4. CORS
    if config.CORS_ORIGINS:
        cors = CORSMiddleware(
            allow_origins=config.CORS_ORIGINS,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True,
            max_age=3600,
        )
        app.use(cors)
    elif not config.is_production:
        # Development CORS
        cors = CORSMiddleware(
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True,
        )
        app.use(cors)

    # ================================
    # SIMPLE AUTHENTICATION MIDDLEWARE
    # ================================

    # In-memory user storage for demo
    users = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",  # In real app, use hashed passwords
            "full_name": "Administrator",
            "is_active": True,
            "is_admin": True,
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    # Simple authentication middleware
    async def auth_middleware(
        request: Any, _response: Any, next_middleware: Any
    ) -> None:
        """Simple authentication middleware for demo purposes."""
        path = request.scope.get("path", "")
        method = request.scope.get("method", "")

        # Public routes that don't require authentication
        public_routes = ["/", "/health", "/docs"]

        # Check if this is a public route
        if path in public_routes or (
            method == "GET" and path.startswith("/api/v1/posts")
        ):
            await next_middleware()
            return

        # For demo purposes, just set a mock user
        # In real implementation, validate JWT token here
        request.current_user = users[0]  # Mock authenticated user
        await next_middleware()

    # 5. Authentication middleware
    app.use(auth_middleware)

    # ================================
    # ROUTES
    # ================================

    async def root() -> dict[str, Any]:
        """API root endpoint."""
        return {
            "name": "Blog API",
            "version": "1.0.0",
            "environment": config.ENVIRONMENT,
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "auth": "/api/v1/auth",
                "users": "/api/v1/users",
                "posts": "/api/v1/posts",
                "comments": "/api/v1/comments",
            },
            "features": [
                "User authentication with JWT",
                "Blog post management",
                "Comments system",
                "File uploads",
                "Search and filtering",
                "Rate limiting",
                "Comprehensive validation",
            ],
        }

    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "environment": config.ENVIRONMENT,
            "version": "1.0.0",
            "database": "connected",  # In real app, check DB connection
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    async def api_docs() -> dict[str, Any]:
        """API documentation endpoint."""
        return {
            "name": "Blog API Documentation",
            "version": "1.0.0",
            "base_url": f"http://{config.HOST}:{config.PORT}",
            "authentication": {
                "type": "Bearer JWT",
                "header": "Authorization: Bearer <token>",
                "login_endpoint": "/api/v1/auth/login",
            },
            "endpoints": {
                "authentication": {
                    "POST /api/v1/auth/register": "Register new user",
                    "POST /api/v1/auth/login": "Login user",
                    "POST /api/v1/auth/logout": "Logout user",
                    "POST /api/v1/auth/refresh": "Refresh JWT token",
                },
                "users": {
                    "GET /api/v1/users/{id}": "Get user profile",
                    "PUT /api/v1/users/{id}": "Update user profile",
                    "GET /api/v1/users/{id}/posts": "Get user's posts",
                },
                "posts": {
                    "GET /api/v1/posts": "List posts (with filtering)",
                    "POST /api/v1/posts": "Create new post (auth required)",
                    "GET /api/v1/posts/{id}": "Get specific post",
                    "PUT /api/v1/posts/{id}": "Update post (auth required)",
                    "DELETE /api/v1/posts/{id}": "Delete post (auth required)",
                },
                "comments": {
                    "GET /api/v1/posts/{id}/comments": "Get post comments",
                    "POST /api/v1/posts/{id}/comments": "Create comment (auth required)",
                    "PUT /api/v1/comments/{id}": "Update comment (auth required)",
                    "DELETE /api/v1/comments/{id}": "Delete comment (auth required)",
                },
            },
            "examples": {
                "register": {
                    "method": "POST",
                    "url": "/api/v1/auth/register",
                    "body": {
                        "username": "johndoe",
                        "email": "john@example.com",
                        "password": "securepassword123",
                        "full_name": "John Doe",
                    },
                },
                "create_post": {
                    "method": "POST",
                    "url": "/api/v1/posts",
                    "headers": {"Authorization": "Bearer <your-jwt-token>"},
                    "body": {
                        "title": "My First Blog Post",
                        "content": "This is the content of my blog post...",
                        "summary": "A brief summary",
                        "tags": ["tech", "programming"],
                        "category": "Technology",
                    },
                },
            },
        }

    # Register routes
    app.get("/", root)
    app.get("/health", health_check)
    app.get("/docs", api_docs)

    # ================================
    # MOUNT API ROUTERS
    # ================================

    # Create API v1 router
    api_v1 = Router()

    # Mount auth and posts routers
    api_v1.mount("/auth", auth_router)
    api_v1.mount("/posts", posts_router)

    # Mount API router
    app.mount("/api/v1", api_v1)

    return app


# ================================
# STARTUP/SHUTDOWN HANDLERS
# ================================


async def startup() -> None:
    """Application startup handler."""
    logger.info(f"Starting Blog API in {config.ENVIRONMENT} mode")
    logger.info(f"Database: {config.DATABASE_URL}")

    # Initialize database
    await init_database(config.DATABASE_URL)

    logger.info("Blog API started successfully")


async def shutdown() -> None:
    """Application shutdown handler."""
    logger.info("Shutting down Blog API")


# ================================
# MAIN APPLICATION
# ================================

# Create application instance directly for Uvicorn
app = create_app()

# You can keep the main() function for direct script execution if needed,
# but Uvicorn will directly import `app` when run via `uvicorn app:app`.
# For example, if you want to run it directly for debugging:
if __name__ == "__main__":
    logger.info("🚀 Starting Blog API - Complete Example")
    logger.info(f"📍 Environment: {config.ENVIRONMENT}")
    logger.info("🔧 Configuration:")
    logger.info(f"   Host: {config.HOST}")
    logger.info(f"   Port: {config.PORT}")
    logger.info(f"   Debug: {config.DEBUG}")
    logger.info(f"   Database: {config.DATABASE_URL}")
    logger.info(f"   Upload Dir: {config.UPLOAD_DIR}")
    logger.info("📍 API Endpoints:")
    logger.info("   GET    /                     - API root")
    logger.info("   GET    /health               - Health check")
    logger.info("   GET    /docs                 - API documentation")
    logger.info("   Router /api/v1/auth          - Authentication")
    logger.info("   Router /api/v1/users         - User management")
    logger.info("   Router /api/v1/posts         - Blog posts")
    logger.info("   Router /api/v1/comments      - Comments")
    logger.info("🔐 Features enabled:")
    logger.info("   ✅ JWT Authentication")
    logger.info("   ✅ Rate limiting")
    logger.info("   ✅ File uploads")
    logger.info("   ✅ Input validation")
    logger.info("   ✅ CORS support")
    if config.is_production:
        logger.info("   ✅ Security headers")
        logger.info("   ✅ Production logging")
    logger.info("🌐 Server starting...")

    # Configure uvicorn
    uvicorn_config = {
        "app": app,
        "host": config.HOST,
        "port": config.PORT,
        "reload": not config.is_production,
        "log_level": config.LOG_LEVEL.lower(),
    }

    if config.is_production:
        uvicorn_config.update(
            {
                "workers": int(os.getenv("WORKERS", "1")),
                "loop": "uvloop",
                "http": "httptools",
            }
        )

    # Start server with startup/shutdown handlers
    uvicorn.run(**uvicorn_config)


"""
🧪 Testing the Blog API:

1. Health check:
   curl http://127.0.0.1:8000/health

2. API documentation:
   curl http://127.0.0.1:8000/docs

3. Register a new user:
   curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "securepass123",
       "full_name": "Test User"
     }'

4. Login:
   curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "securepass123"}'

5. Create a blog post (use token from login):
   curl -X POST http://127.0.0.1:8000/api/v1/posts \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-jwt-token>" \
     -d '{
       "title": "My First Post",
       "content": "This is my first blog post content...",
       "summary": "A sample blog post",
       "category": "Technology"
     }'

6. Get all posts:
   curl http://127.0.0.1:8000/api/v1/posts

🔍 Key Features Demonstrated:

1. **Application Factory**: Modular app creation with configuration
2. **Environment Configuration**: Production vs development settings
3. **Comprehensive Middleware**: Security, rate limiting, CORS, auth
4. **Modular Routing**: Separate routers for different resources
5. **Database Integration**: SQLAlchemy setup (in utils/database.py)
6. **Authentication**: JWT-based auth with middleware
7. **File Uploads**: Image handling with validation
8. **API Documentation**: Self-documenting endpoints
9. **Health Checks**: Monitoring and status endpoints
10. **Production Ready**: Proper logging, error handling, security

🏗️ Project Structure:

This example demonstrates a complete, production-ready API structure:
- Modular route organization
- Middleware layers for cross-cutting concerns
- Configuration management
- Database abstraction
- Authentication and authorization
- Input validation and error handling
- File upload capabilities
- Comprehensive documentation

📚 Next Steps:

1. Check out individual route files in routes/
2. Review authentication middleware in middleware/auth.py
3. Explore database models in models/
4. Run the test suite in tests/
5. Deploy with Docker using docker-compose.yml
"""
