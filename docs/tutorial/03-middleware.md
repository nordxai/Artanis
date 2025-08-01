# 3. Middleware

Middleware functions are a powerful feature of Artanis. They can be used to perform actions before or after a request is handled. In this section, we'll add middleware for logging and error handling.

## Logging Middleware

Artanis has a built-in logging system, but let's create our own simple logging middleware to see how it works.

Update your `main.py` file:

```python
# main.py
import time
from artanis import App
from artanis.exceptions import RouteNotFound
import uvicorn

app = App()

# In-memory database
posts = {
    1: {"title": "First Post", "content": "This is the first post."},
    2: {"title": "Second Post", "content": "This is the second post."},
}

# Logging middleware
async def logging_middleware(request, response, next):
    start_time = time.time()
    await next()
    process_time = (time.time() - start_time) * 1000
    print(f"Request to {request.scope['path']} processed in {process_time:.2f}ms")

app.use(logging_middleware)

# ... (route handlers)

app.get("/", root)
app.get("/posts", get_posts)
# ... (rest of the routes)
```

Now, every time you make a request to the API, you'll see a log message in your console.

## Error Handling Middleware

Artanis has a built-in exception handling system, but you can also create your own error handling middleware. Let's create a middleware that catches `RouteNotFound` exceptions and returns a custom error message.

Update your `main.py` file:

```python
# main.py
import time
from artanis import App
from artanis.exceptions import RouteNotFound
from artanis.middleware.exception import ExceptionHandlerMiddleware
import uvicorn

app = App()

# In-memory database
posts = {
    1: {"title": "First Post", "content": "This is the first post."},
    2: {"title": "Second Post", "content": "This is the second post."},
}

# Logging middleware
async def logging_middleware(request, response, next):
    start_time = time.time()
    await next()
    process_time = (time.time() - start_time) * 1000
    print(f"Request to {request.scope['path']} processed in {process_time:.2f}ms")

app.use(logging_middleware)

# Error handling middleware
def handle_route_not_found(exc, request, response):
    response.set_status(404)
    response.json({"error": str(exc)})
    return response

exception_handler = ExceptionHandlerMiddleware()
exception_handler.add_handler(RouteNotFound, handle_route_not_found)
app.use(exception_handler)

# ... (route handlers and routes)
```

Now, if you try to access a post that doesn't exist (e.g., `/posts/99`), you'll get a custom 404 error message.

In the next section, we'll connect our application to a real database.
