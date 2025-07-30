# Docker Deployment Guide

This guide shows how to containerize and deploy Artanis applications using Docker, including development and production configurations.

## 📋 Table of Contents

- [Basic Docker Setup](#basic-docker-setup)
- [Multi-stage Builds](#multi-stage-builds)
- [Docker Compose](#docker-compose)
- [Production Optimization](#production-optimization)
- [Environment Variables](#environment-variables)
- [Health Checks](#health-checks)
- [Security Best Practices](#security-best-practices)

## 🐳 Basic Docker Setup

### Simple Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "app.py"]
```

### Basic requirements.txt

```
artanis>=1.0.0
uvicorn[standard]>=0.20.0
```

### Build and Run

```bash
# Build the image
docker build -t my-artanis-app .

# Run the container
docker run -p 8000:8000 my-artanis-app

# Run with environment variables
docker run -p 8000:8000 -e ENVIRONMENT=production my-artanis-app
```

## 🏗️ Multi-stage Builds

For production optimization, use multi-stage builds:

```dockerfile
# Multi-stage Dockerfile
FROM python:3.11 as builder

WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r app && useradd -r -g app app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use uvicorn for production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐙 Docker Compose

### Development Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - DATABASE_URL=postgresql://user:password@db:5432/artanis_dev
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app  # Mount source code for development
    depends_on:
      - db
      - redis
    command: ["python", "app.py"]  # Development server with reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: artanis_dev
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production Setup

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped
    command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Commands

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f app

# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## 🚀 Production Optimization

### Optimized Production Dockerfile

```dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build stage
FROM base as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Production stage
FROM base as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Create non-root user
RUN groupadd -r app && useradd -r -g app app && \
    chown -R app:app /app

# Set PATH to include user installed packages
ENV PATH=/root/.local/bin:$PATH

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["tini", "--"]

# Production command with optimizations
CMD ["uvicorn", "app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--loop", "uvloop", \
     "--http", "httptools"]
```

## 🌍 Environment Variables

### .env file for development

```bash
# .env
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/artanis_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-development-secret-key
JWT_SECRET=your-jwt-secret

# External Services
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_smtp_user
SMTP_PASS=your_smtp_pass
```

### Production environment variables

```bash
# Production .env (use secrets management in real deployment)
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:secure_password@db:5432/artanis_prod

# Redis
REDIS_URL=redis://redis:6379/0

# Security (use secrets management)
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
```

## 🏥 Health Checks

### Application health endpoint

```python
# app.py
async def health_check():
    """Comprehensive health check for Docker."""
    try:
        # Check database connection
        # db_status = await check_database()

        # Check Redis connection
        # redis_status = await check_redis()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "checks": {
                "api": "healthy",
                "database": "healthy",  # db_status
                "cache": "healthy"      # redis_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503

# Register the health check route
app.get("/health", health_check)
```

### Docker health check

```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Custom health check script

```bash
#!/bin/bash
# healthcheck.sh

set -e

# Check if application is responding
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$response" != "200" ]; then
    echo "Health check failed with status: $response"
    exit 1
fi

echo "Health check passed"
exit 0
```

## 🔒 Security Best Practices

### 1. Non-root User

```dockerfile
# Create and use non-root user
RUN groupadd -r app && useradd -r -g app app
USER app
```

### 2. Minimal Base Image

```dockerfile
# Use slim or alpine images
FROM python:3.11-slim
# or
FROM python:3.11-alpine
```

### 3. Secret Management

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
    secrets:
      - secret_key

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
```

### 4. Network Security

```yaml
# docker-compose.yml
services:
  app:
    networks:
      - backend
    # Don't expose database ports to host

  db:
    networks:
      - backend
    # No ports exposed to host

networks:
  backend:
    driver: bridge
```

### 5. Read-only Filesystem

```dockerfile
# Add to Dockerfile for extra security
USER app
VOLUME ["/tmp"]
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Run with read-only filesystem
# docker run --read-only --tmpfs /tmp my-artanis-app
```

## 📊 Monitoring with Docker

### Logging Configuration

```yaml
# docker-compose.yml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Prometheus Metrics

```python
# Add to your Artanis app
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": "text/plain"}

# Register the metrics route
app.get("/metrics", metrics)
```

## 🚢 Deployment Commands

### Build and Deploy

```bash
# Build for production
docker build -t my-artanis-app:latest -f Dockerfile.prod .

# Tag for registry
docker tag my-artanis-app:latest registry.example.com/my-artanis-app:v1.0.0

# Push to registry
docker push registry.example.com/my-artanis-app:v1.0.0

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps --build app
```

### Maintenance Commands

```bash
# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app bash

# Database migrations
docker-compose exec app python manage.py migrate

# Backup database
docker-compose exec db pg_dump -U user artanis_prod > backup.sql

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

This comprehensive Docker guide covers everything from basic containerization to production-ready deployments with security, monitoring, and best practices.
