# Router Patterns Example

This example demonstrates advanced routing patterns with the Artanis framework, showcasing how to build complex, hierarchical routing structures that scale well for large applications.

## Features Demonstrated

- **Router Creation and Mounting**: Create modular router instances and mount them at specific paths
- **Nested Routing Structures**: Build complex URL hierarchies with multiple levels
- **Path Parameter Patterns**: Extract parameters from URLs at any nesting level
- **Route Organization**: Separate concerns by grouping related routes together
- **Subrouter Patterns**: Create reusable routing components

## Architecture

### Routing Structure

```
Main App
├── GET /                          # API root with routing information
├── GET /health                    # Health check endpoint
├── /api/v1/ (Router)             # API version 1 router
│   ├── /users/ (Router)          # User management
│   │   ├── GET /                 # List all users
│   │   ├── GET /{user_id}        # Get specific user
│   │   └── POST /                # Create new user
│   ├── /users/{user_id}/posts/   # User posts subrouter (nested parameters)
│   │   ├── GET /                 # Get user's posts
│   │   └── POST /                # Create post for user
│   ├── /posts/ (Router)          # Posts management
│   │   ├── GET /                 # List all posts
│   │   └── GET /{post_id}        # Get specific post
│   └── /posts/{post_id}/comments/ # Post comments subrouter (nested parameters)
│       ├── GET /                 # Get post comments
│       └── POST /                # Create comment on post
└── /admin/ (Router)              # Admin panel
    ├── GET /                     # Admin dashboard
    ├── GET /stats                # System statistics
    ├── GET /users                # User management
    └── GET /posts                # Post management
```

### Key Concepts

1. **Router Creation**: `Router()` creates a new router instance for organizing related routes
2. **Route Registration**: Use `router.get()`, `router.post()`, etc. to register routes on specific routers
3. **Router Mounting**: `app.mount(path, router)` mounts a router at a specific path prefix
4. **Nested Parameters**: Paths like `/users/{user_id}/posts` allow parameter extraction at mount level
5. **Path Inheritance**: Mount paths combine with route paths for final URL resolution
6. **Parameter Access**: Parameters from mount paths are available in route handlers

## Quick Start

1. **Navigate to the example**:
   ```bash
   git clone https://github.com/nordxai/Artanis
   cd Artanis/docs/examples/router_patterns
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Test the routes**:
   ```bash
   curl http://127.0.0.1:8000/
   ```

## Testing the API

### Basic Endpoints

```bash
# API root - shows routing structure
curl http://127.0.0.1:8000/

# Health check
curl http://127.0.0.1:8000/health
```

### User Management

```bash
# List all users
curl http://127.0.0.1:8000/api/v1/users

# Get specific user
curl http://127.0.0.1:8000/api/v1/users/1

# Create new user
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "newuser@example.com"}'
```

### User Posts (Nested Routing)

```bash
# Get posts for specific user
curl http://127.0.0.1:8000/api/v1/users/1/posts

# Create post for specific user
curl -X POST http://127.0.0.1:8000/api/v1/users/1/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "My New Post", "content": "This is the content of my post."}'
```

### Posts Management

```bash
# List all posts with author information
curl http://127.0.0.1:8000/api/v1/posts

# Get specific post with comments
curl http://127.0.0.1:8000/api/v1/posts/1
```

### Post Comments (Nested Routing)

```bash
# Get comments for specific post
curl http://127.0.0.1:8000/api/v1/posts/1/comments

# Create comment on specific post
curl -X POST http://127.0.0.1:8000/api/v1/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "Great post!", "user_id": 2}'
```

### Admin Panel

```bash
# Admin dashboard
curl http://127.0.0.1:8000/admin

# System statistics
curl http://127.0.0.1:8000/admin/stats

# Admin user management
curl http://127.0.0.1:8000/admin/users

# Admin post management
curl http://127.0.0.1:8000/admin/posts
```

## Router Implementation

### Basic Router Creation

```python
from artanis import App, Router

app = App()

# Create routers for different domains
users_router = Router()
posts_router = Router()
admin_router = Router()

# Register routes on specific routers
users_router.get("/", list_users)
users_router.get("/{user_id}", get_user)
users_router.post("/", create_user)

# Mount routers to main application
app.mount("/api/v1/users", users_router)
app.mount("/api/v1/posts", posts_router)
app.mount("/admin", admin_router)
```

### Nested Parameter Routing

```python
# User posts router (receives user_id from mount path)
user_posts_router = Router()

async def get_user_posts(user_id: str):
    """Get posts for a specific user."""
    return {
        "user_id": user_id,
        "posts": [post for post in posts if post["user_id"] == user_id]
    }

async def create_user_post(user_id: str, request):
    """Create a post for a specific user."""
    data = await request.json()
    new_post = {
        "id": len(posts) + 1,
        "user_id": user_id,
        "title": data["title"],
        "content": data["content"],
        "created_at": "2024-01-15T10:30:00Z"
    }
    posts.append(new_post)
    return {"message": "Post created", "post": new_post}

user_posts_router.get("/", get_user_posts)
user_posts_router.post("/", create_user_post)

# Mount with parameter path
app.mount("/api/v1/users/{user_id}/posts", user_posts_router)
```

### Multi-Level Router Hierarchy

```python
# Create hierarchical structure
api_router = Router()
v1_router = Router()
v2_router = Router()

# V1 routes
v1_router.mount("/users", users_v1_router)
v1_router.mount("/posts", posts_v1_router)

# V2 routes (different implementation)
v2_router.mount("/users", users_v2_router)
v2_router.mount("/posts", posts_v2_router)

# Mount versions to API router
api_router.mount("/v1", v1_router)
api_router.mount("/v2", v2_router)

# Mount API router to main app
app.mount("/api", api_router)

# Final paths:
# /api/v1/users/
# /api/v1/posts/
# /api/v2/users/
# /api/v2/posts/
```

## Router Pattern Benefits

### 1. **Organization**
Related routes are grouped together in logical units, making the codebase easier to navigate and maintain.

### 2. **Modularity**
Routers can be developed independently and reused across different applications or API versions.

### 3. **Nested Routing**
Complex URL structures with parameters can be handled elegantly with proper parameter extraction.

### 4. **Separation of Concerns**
Each router handles one specific domain (users, posts, admin), promoting clean architecture.

### 5. **Scalability**
Easy to add new route groups without modifying existing code structure.

### 6. **Maintainability**
Clear structure makes large applications easier to understand and modify.

## Advanced Patterns

### Parameter Inheritance

```python
# Mount path parameters are available in subrouter handlers
api_v1.mount("/users/{user_id}/posts", user_posts_router)

# Handler receives both mount and route parameters
async def get_user_posts(user_id: str):
    # user_id comes from the mount path /users/{user_id}/posts
    # Additional route parameters would also be available
    return {"user_id": user_id, "posts": get_posts_for_user(user_id)}
```

### Router with Middleware

```python
# Apply middleware to entire router
async def auth_middleware(request, response, next):
    if not request.headers.get('Authorization'):
        response.status = 401
        response.body = {"error": "Authentication required"}
        return
    await next()

# Apply to admin router
app.use("/admin", auth_middleware)
admin_router = Router()
admin_router.get("/", admin_dashboard)
app.mount("/admin", admin_router)
```

### Conditional Router Mounting

```python
import os

# Environment-based router mounting
if os.getenv('ENABLE_ADMIN', 'false').lower() == 'true':
    app.mount("/admin", admin_router)

if os.getenv('API_VERSION', 'v1') == 'v2':
    app.mount("/api", v2_api_router)
else:
    app.mount("/api", v1_api_router)
```

## Best Practices

1. **Logical Grouping**: Group related functionality in the same router
2. **Consistent Naming**: Use clear, consistent router and path names
3. **Parameter Validation**: Validate path parameters in handlers
4. **Error Handling**: Provide meaningful error responses
5. **Documentation**: Document your routing structure clearly
6. **Testing**: Test all route combinations and parameter patterns

## Implementation Notes

- **CORS Middleware**: Included for cross-origin API access
- **In-Memory Storage**: Uses simple Python data structures for demonstration
- **Parameter Validation**: Basic validation with error handling
- **Structured Responses**: Consistent JSON response format
- **Error Handling**: Proper HTTP status codes and error messages

This example serves as a comprehensive reference for implementing complex routing patterns in Artanis applications, demonstrating best practices for API organization and scalability.
