# Blog API Example

A complete blog API demonstrating production-ready patterns with Artanis framework.

## Features

- **User Authentication**: JWT-based registration, login, and profile management
- **Blog Post Management**: Full CRUD operations with search, filtering, and pagination
- **Content Organization**: Categories and tags system
- **File Uploads**: Featured image handling for posts
- **Security Middleware**: CORS, rate limiting, security headers
- **Input Validation**: Comprehensive validation with detailed error messages
- **Production Ready**: Environment configuration, logging, and error handling

## Project Structure

```
blog_api/
├── app.py                  # Main application with configuration and routing
├── requirements.txt        # Project dependencies
├── routes/                # API route modules
│   ├── auth.py           # Authentication endpoints (register, login, logout)
│   └── posts.py          # Blog post endpoints (CRUD, search, upload)
├── middleware/           # Custom middleware
│   └── auth.py          # Authentication middleware (placeholder)
├── utils/               # Utility modules
│   ├── validation.py    # Input validation functions
│   ├── security.py      # Password hashing, JWT, HTML sanitization
│   └── database.py      # Database connection utilities
└── uploads/             # File upload directory
```

## Quick Start

1. **Clone and navigate**:
   ```bash
   git clone https://github.com/nordxai/Artanis
   cd Artanis/docs/examples/blog_api
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python app.py
   # OR
   uvicorn app:app --host 127.0.0.1 --port 3000
   ```

5. **Test the API**:
   ```bash
   curl http://127.0.0.1:3000/health
   curl http://127.0.0.1:3000/docs
   ```

## API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint
- `GET /docs` - API documentation

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login and get JWT token
- `POST /logout` - User logout (blacklist token)
- `POST /refresh` - Refresh JWT token
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile
- `POST /change-password` - Change user password
- `GET /stats` - Authentication statistics

### Blog Posts (`/api/v1/posts`)
- `GET /` - List posts with filtering, search, and pagination
- `POST /` - Create new post (authentication required)
- `GET /{id}` - Get specific post by ID or slug
- `PUT /{id}` - Update post (authentication + ownership required)
- `DELETE /{id}` - Delete post (authentication + ownership required)
- `POST /{id}/like` - Like a post (authentication required)
- `POST /{id}/upload-image` - Upload featured image (authentication required)
- `GET /categories` - Get all available categories with post counts
- `GET /tags` - Get all tags with usage counts
- `GET /stats` - Get blog statistics

## Key Features Demonstrated

### 1. Authentication & Authorization
- JWT token-based authentication with expiration
- User registration and login system
- Token refresh and blacklisting
- Password hashing with secure algorithms
- Profile management endpoints

### 2. Data Validation & Security
- Comprehensive input validation with detailed error messages
- Email, username, and password strength validation
- HTML content sanitization for XSS prevention
- File upload validation with type and size checks
- Request validation for all endpoints

### 3. Middleware Integration
- Exception handling middleware with debug mode
- Security headers middleware for production
- Rate limiting to prevent API abuse
- CORS configuration for cross-origin requests
- Request logging for development

### 4. Blog Management System
- Full CRUD operations for blog posts
- Search and filtering with multiple criteria
- Pagination with configurable page sizes
- Categories and tags organization
- Post statistics and analytics
- Slug generation for SEO-friendly URLs

### 5. File Upload Handling
- Featured image uploads for posts
- File validation and secure storage
- Image processing and management
- Upload directory organization

### 6. Production-Ready Features
- Environment-based configuration
- Structured logging with JSON output
- Health check endpoints
- API documentation endpoints
- Error handling with proper HTTP status codes

## Example Usage

### 1. User Registration
```bash
curl -X POST http://127.0.0.1:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bloguser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "Blog User"
  }'
```

### 2. User Login
```bash
curl -X POST http://127.0.0.1:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bloguser",
    "password": "SecurePass123!"
  }'
```

### 3. Create Blog Post (with JWT token)
```bash
curl -X POST http://127.0.0.1:3000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post...",
    "summary": "A brief summary of the post",
    "category": "Technology",
    "tags": ["artanis", "python", "web"],
    "status": "published"
  }'
```

### 4. Search Posts
```bash
# Search posts with filtering
curl "http://127.0.0.1:3000/api/v1/posts?search=artanis&category=Technology&page=1&per_page=5"

# Get all categories
curl "http://127.0.0.1:3000/api/v1/posts/categories"

# Get blog statistics
curl "http://127.0.0.1:3000/api/v1/posts/stats"
```

## Configuration

The application supports environment-based configuration:

```bash
# Development settings
export ENVIRONMENT="development"
export DEBUG="true"
export HOST="127.0.0.1"
export PORT="3000"

# Security settings
export SECRET_KEY="your-secret-key-change-in-production"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRES_IN="3600"

# Database settings
export DATABASE_URL="sqlite:///blog.db"

# Upload settings
export UPLOAD_DIR="uploads"
export MAX_FILE_SIZE="5242880"  # 5MB

# CORS settings
export CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"

# Rate limiting
export RATE_LIMIT_REQUESTS="100"
export RATE_LIMIT_WINDOW="3600"

# Logging
export LOG_LEVEL="INFO"
```

## Security Considerations

- **Authentication**: JWT tokens with expiration and refresh mechanism
- **Password Security**: SHA-256 hashing (use bcrypt in production)
- **Input Validation**: Comprehensive validation with detailed error messages
- **Rate Limiting**: Prevents API abuse and DoS attacks
- **CORS Configuration**: Configurable cross-origin request handling
- **Content Sanitization**: HTML content cleaning to prevent XSS
- **File Upload Security**: Type and size validation for uploads

This example demonstrates the complete implementation of a production-ready blog API using Artanis framework with modern security practices and comprehensive feature set.
