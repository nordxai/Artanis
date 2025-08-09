# Examples

Explore practical examples that demonstrate Artanis features and common patterns. Each example includes complete, working code that you can run and modify.

## Featured Examples

<div class="grid cards" markdown>

-   :material-book-open:{ .lg .middle } **Blog API**

    ---

    Complete REST API with CRUD operations, authentication, and data validation

    **Features**: Database integration, middleware, error handling, routing

    [:octicons-arrow-right-24: View Example](blog-api.md)

-   :material-shield-check:{ .lg .middle } **Middleware Demo**

    ---

    Comprehensive middleware examples including security, logging, and custom middleware

    **Features**: CORS, authentication, rate limiting, request logging

    [:octicons-arrow-right-24: View Example](middleware-demo.md)

-   :material-sitemap:{ .lg .middle } **Router Patterns**

    ---

    Advanced routing patterns with subrouting and modular organization

    **Features**: Subrouters, parameterized mounting, nested routes

    [:octicons-arrow-right-24: View Example](router-patterns.md)

</div>

## Quick Start Examples

### Hello World

The simplest possible Artanis application:

```python
from artanis import App

app = App()

async def hello():
    return {"message": "Hello, World!"}

app.get("/", hello)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Path Parameters

Handle dynamic URL segments:

```python
from artanis import App

app = App()

async def get_user(user_id):
    return {"user_id": user_id, "name": f"User {user_id}"}

async def get_user_posts(user_id, post_id):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "title": f"Post {post_id} by User {user_id}"
    }

app.get("/users/{user_id}", get_user)
app.get("/users/{user_id}/posts/{post_id}", get_user_posts)
```

### Request Body Handling

Process JSON request data:

```python
from artanis import App

app = App()

async def create_post(request):
    data = await request.json()

    return {
        "message": "Post created",
        "post": {
            "id": 123,
            "title": data.get("title"),
            "content": data.get("content"),
            "created_at": "2024-01-15T10:30:00Z"
        }
    }

async def update_post(post_id, request):
    data = await request.json()

    return {
        "message": f"Post {post_id} updated",
        "changes": data
    }

app.post("/posts", create_post)
app.put("/posts/{post_id}", update_post)
```

### Basic Middleware

Add functionality that runs for all requests:

```python
from artanis import App
import time

app = App()

# Request timing middleware
async def timing_middleware(request, response, next):
    start_time = time.time()

    await next()

    duration = time.time() - start_time
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

# CORS middleware
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    await next()

app.use(timing_middleware)
app.use(cors_middleware)

async def hello():
    return {"message": "Hello with middleware!"}

app.get("/", hello)
```

## Pattern Categories

### 🌐 Web APIs

Examples for building REST APIs:

- **CRUD Operations** - Create, read, update, delete patterns
- **Authentication** - JWT tokens, API keys, session management
- **Data Validation** - Request validation and error handling
- **Pagination** - Efficient data pagination strategies
- **File Uploads** - Handle file uploads and storage

### 🔒 Security

Security-focused examples:

- **CORS Configuration** - Cross-origin resource sharing
- **Rate Limiting** - Prevent abuse and ensure fair usage
- **Authentication Middleware** - Protect routes and validate users
- **Input Sanitization** - Prevent injection attacks
- **Security Headers** - HSTS, CSP, and other protective headers

### 🏗️ Architecture

Architectural patterns and code organization:

- **Modular Routers** - Organize large applications
- **Dependency Injection** - Manage dependencies cleanly
- **Configuration Management** - Environment-based configuration
- **Database Patterns** - Connection pooling and transaction management
- **Testing Strategies** - Unit and integration testing

### 🔧 Integration

Integration with external services:

- **Database Integration** - SQL and NoSQL databases
- **External APIs** - Consume third-party services
- **Message Queues** - Background task processing
- **Caching** - Redis and in-memory caching strategies
- **Monitoring** - Logging, metrics, and health checks

## Running Examples

Each example includes instructions for running the code:

### 1. Clone the Repository

```bash
git clone https://github.com/nordxai/Artanis
cd Artanis
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Run Examples

```bash
# Run the blog API example
cd docs/examples/blog_api
python app.py

# Run middleware demo
cd ../middleware_demo
python app.py

# Run router patterns
cd ../router_patterns
python app.py
```

## Example Structure

Each example follows this structure:

```
example_name/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── routes/            # Route modules (if applicable)
├── middleware/        # Custom middleware (if applicable)
├── models/           # Data models (if applicable)
└── tests/            # Test files (if applicable)
```

## Testing Examples

All examples include tests that you can run:

```bash
cd docs/examples/blog_api
python -m pytest tests/ -v
```

## Contributing Examples

Have a great example to share? We'd love to include it!

1. **Follow the structure** - Use the standard example layout
2. **Include documentation** - Clear README with setup instructions
3. **Add tests** - Verify your example works correctly
4. **Submit a PR** - Open a pull request with your example

See our contributing guide for more details.

## Getting Help

If you have questions about any example:

1. **Check the README** - Each example has detailed documentation
2. **Review the code** - All examples include comprehensive comments
3. **Run the tests** - Tests show expected behavior
4. **Open an issue** - Ask questions on [GitHub Issues](https://github.com/nordxai/Artanis/issues)

---

These examples demonstrate the flexibility and power of Artanis for building modern web applications. Start with the simpler examples and work your way up to more complex patterns!
