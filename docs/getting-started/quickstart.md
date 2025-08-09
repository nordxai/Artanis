# Quick Start

Get up and running with Artanis in just a few minutes! This guide will show you how to create your first application.

## Prerequisites

Make sure you have:

- [Python 3.8+](installation.md#requirements) installed
- [Artanis installed](installation.md) (`pip install artanis`)
- An ASGI server like Uvicorn (`pip install uvicorn[standard]`)

## Your First Application

### 1. Create the Application File

Create a new file called `main.py`:

```python title="main.py"
from artanis import App

# Create the application
app = App()

# Define a simple route
async def hello():
    return {"message": "Hello, World!"}

# Register the route
app.get("/", hello)
```

### 2. Run the Application

Start the development server:

```bash
uvicorn main:app --reload
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Test Your Application

Open your browser and visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

You should see:

```json
{"message": "Hello, World!"}
```

🎉 **Congratulations!** You've created your first Artanis application!

## Adding More Routes

Let's expand our application with more functionality:

```python title="main.py"
from artanis import App

app = App()

# Home route
async def home():
    return {"message": "Welcome to Artanis!"}

# Route with path parameter
async def greet_user(name):
    return {"message": f"Hello, {name}!"}

# Route that handles request data
async def create_item(request):
    data = await request.json()
    return {
        "message": "Item created",
        "item": data
    }

# Register routes
app.get("/", home)
app.get("/hello/{name}", greet_user)
app.post("/items", create_item)
```

Now restart your server and test these endpoints:

=== "GET /"
    ```bash
    curl http://127.0.0.1:8000/
    ```
    ```json
    {"message": "Welcome to Artanis!"}
    ```

=== "GET /hello/{name}"
    ```bash
    curl http://127.0.0.1:8000/hello/Alice
    ```
    ```json
    {"message": "Hello, Alice!"}
    ```

=== "POST /items"
    ```bash
    curl -X POST http://127.0.0.1:8000/items \
         -H "Content-Type: application/json" \
         -d '{"name": "My Item", "price": 29.99}'
    ```
    ```json
    {
      "message": "Item created",
      "item": {"name": "My Item", "price": 29.99}
    }
    ```

## Adding Middleware

Middleware allows you to add functionality that runs before or after your route handlers. Here's how to add CORS support:

```python title="main.py"
from artanis import App

app = App()

# CORS middleware
async def cors_middleware(request, response, next):
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    # Continue to the next middleware or route handler
    await next()

# Register middleware globally
app.use(cors_middleware)

# Your routes here...
async def hello():
    return {"message": "Hello with CORS!"}

app.get("/", hello)
```

## Project Structure

As your application grows, organize it like this:

```
my-artanis-app/
├── main.py              # Application entry point
├── routes/
│   ├── __init__.py
│   ├── users.py         # User-related routes
│   └── items.py         # Item-related routes
├── middleware/
│   ├── __init__.py
│   ├── auth.py          # Authentication middleware
│   └── logging.py       # Logging middleware
├── models/
│   ├── __init__.py
│   └── database.py      # Database models
└── requirements.txt     # Dependencies
```

## Using the CLI

Artanis provides a CLI tool to generate new projects:

```bash
# Create a new project
artanis new my-project

# Navigate to the project
cd my-project

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The CLI creates a basic project structure with:

- `app.py` - Main application file
- `requirements.txt` - Dependencies
- `README.md` - Project documentation

## Development Tips

### 1. Enable Debug Mode

For development, run with auto-reload:

```bash
uvicorn main:app --reload --log-level debug
```

### 2. Environment Variables

Use environment variables for configuration:

```python
import os

app = App()

# Configure based on environment
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=DEBUG)
```

### 3. Type Hints

Use type hints for better IDE support:

```python
from typing import Dict, Any
from artanis import App, Request

app = App()

async def typed_handler(user_id: str) -> Dict[str, Any]:
    return {"user_id": user_id, "type": "user"}

async def json_handler(request: Request) -> Dict[str, str]:
    data: Dict[str, Any] = await request.json()
    return {"received": str(data)}

app.get("/users/{user_id}", typed_handler)
app.post("/data", json_handler)
```

## Common Patterns

### Error Handling

```python
from artanis import App
from artanis.exceptions import ValidationError

app = App()

async def create_user(request):
    data = await request.json()

    # Validate required fields
    if not data.get('email'):
        raise ValidationError("Email is required")

    return {"message": "User created", "email": data['email']}

app.post("/users", create_user)
```

### Path-based Middleware

```python
# Authentication middleware for admin routes only
async def auth_middleware(request, response, next):
    token = request.headers.get('Authorization')
    if not token:
        response.status = 401
        response.body = {"error": "Authentication required"}
        return

    await next()

# Apply only to /admin/* routes
app.use("/admin", auth_middleware)

async def admin_dashboard():
    return {"message": "Welcome to admin dashboard"}

app.get("/admin/dashboard", admin_dashboard)
```

### Multiple HTTP Methods

```python
# Handle both GET and POST on the same path
async def get_items():
    return {"items": ["item1", "item2"]}

async def create_item(request):
    data = await request.json()
    return {"created": data}

app.get("/items", get_items)
app.post("/items", create_item)
```

## Next Steps

Now that you have a working Artanis application, explore these topics:

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } **Learn More**

    ---

    Follow our comprehensive tutorial to build a complete blog API

    [:octicons-arrow-right-24: Tutorial](../tutorials/index.md)

-   :material-book:{ .lg .middle } **User Guide**

    ---

    Deep dive into routing, middleware, security, and more

    [:octicons-arrow-right-24: User Guide](../guide/routing.md)

-   :material-code-braces:{ .lg .middle } **Examples**

    ---

    See working examples for common patterns and use cases

    [:octicons-arrow-right-24: Examples](../examples/index.md)

-   :material-rocket-launch:{ .lg .middle } **Deployment**

    ---

    Learn how to deploy your application to production

    [:octicons-arrow-right-24: Deployment](../deployment/production.md)

</div>

## Get Help

- **Documentation**: You're reading it! 📖
- **GitHub Issues**: [Report bugs or ask questions](https://github.com/nordxai/Artanis/issues)
- **Discussions**: [Community discussions](https://github.com/nordxai/Artanis/discussions)
- **Examples**: Check the `/examples` directory in the repository
