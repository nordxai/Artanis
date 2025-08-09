# Your First App

Let's build a simple but feature-rich application to explore Artanis capabilities. We'll create a task management API that demonstrates routing, middleware, and data handling.

## What We'll Build

Our task management API will have:

- ✅ **List all tasks** - `GET /tasks`
- ✅ **Get a specific task** - `GET /tasks/{task_id}`
- ✅ **Create a new task** - `POST /tasks`
- ✅ **Update a task** - `PUT /tasks/{task_id}`
- ✅ **Delete a task** - `DELETE /tasks/{task_id}`
- ✅ **Request logging middleware**
- ✅ **CORS support**
- ✅ **Error handling**

## Step 1: Project Setup

Create a new directory and set up your environment:

```bash
mkdir task-api
cd task-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install artanis uvicorn[standard]
```

## Step 2: Create the Basic Application

Create `app.py`:

```python title="app.py"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Create the application
app = App()

# In-memory storage (in production, use a database)
tasks: Dict[str, Dict[str, Any]] = {}

async def hello():
    return {
        "message": "Welcome to Task API",
        "version": "1.0.0",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a new task",
            "GET /tasks/{task_id}": "Get a specific task",
            "PUT /tasks/{task_id}": "Update a task",
            "DELETE /tasks/{task_id}": "Delete a task"
        }
    }

app.get("/", hello)
```

Test it:

```bash
uvicorn app:app --reload
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to see the welcome message.

## Step 3: Add Task Routes

Add the CRUD operations to `app.py`:

```python title="app.py" hl_lines="20-74"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any

app = App()

# In-memory storage
tasks: Dict[str, Dict[str, Any]] = {}

async def hello():
    return {
        "message": "Welcome to Task API",
        "version": "1.0.0",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a new task",
            "GET /tasks/{task_id}": "Get a specific task",
            "PUT /tasks/{task_id}": "Update a task",
            "DELETE /tasks/{task_id}": "Delete a task"
        }
    }

# List all tasks
async def list_tasks():
    return {
        "tasks": list(tasks.values()),
        "count": len(tasks)
    }

# Get a specific task
async def get_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    return {"task": tasks[task_id]}

# Create a new task
async def create_task(request):
    data = await request.json()

    # Validate required fields
    if not data.get("title"):
        return {"error": "Title is required"}, 400

    # Create the task
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    tasks[task_id] = task
    return {"message": "Task created", "task": task}, 201

# Update a task
async def update_task(task_id: str, request):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    data = await request.json()
    task = tasks[task_id]

    # Update fields
    if "title" in data:
        task["title"] = data["title"]
    if "description" in data:
        task["description"] = data["description"]
    if "completed" in data:
        task["completed"] = data["completed"]

    task["updated_at"] = datetime.now().isoformat()

    return {"message": "Task updated", "task": task}

# Delete a task
async def delete_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    deleted_task = tasks.pop(task_id)
    return {"message": "Task deleted", "task": deleted_task}

# Register routes
app.get("/", hello)
app.get("/tasks", list_tasks)
app.get("/tasks/{task_id}", get_task)
app.post("/tasks", create_task)
app.put("/tasks/{task_id}", update_task)
app.delete("/tasks/{task_id}", delete_task)
```

## Step 4: Add Middleware

Add request logging and CORS support:

```python title="app.py" hl_lines="5-6 10-25 27-32"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any
import time
import logging

app = App()

# Request logging middleware
async def logging_middleware(request, response, next):
    start_time = time.time()
    method = request.scope.get("method", "UNKNOWN")
    path = request.scope.get("path", "/")

    print(f"→ {method} {path}")

    await next()

    duration = time.time() - start_time
    status = getattr(response, 'status', 200)
    print(f"← {method} {path} {status} ({duration:.3f}s)")

# CORS middleware
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    await next()

# Register middleware
app.use(logging_middleware)
app.use(cors_middleware)

# In-memory storage
tasks: Dict[str, Dict[str, Any]] = {}

# ... rest of the code remains the same
```

## Step 5: Test Your API

Restart your server and test the endpoints:

### Create a Task

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Artanis",
    "description": "Complete the Artanis tutorial"
  }'
```

Response:
```json
{
  "message": "Task created",
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Learn Artanis",
    "description": "Complete the Artanis tutorial",
    "completed": false,
    "created_at": "2024-01-15T10:30:45.123456",
    "updated_at": "2024-01-15T10:30:45.123456"
  }
}
```

### List All Tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Get Specific Task

```bash
curl http://127.0.0.1:8000/tasks/123e4567-e89b-12d3-a456-426614174000
```

### Update a Task

```bash
curl -X PUT http://127.0.0.1:8000/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

### Delete a Task

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/123e4567-e89b-12d3-a456-426614174000
```

## Step 6: Add Error Handling

Improve error handling throughout the application:

```python title="app.py" hl_lines="34-48"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any
import time
import json

app = App()

# Request logging middleware
async def logging_middleware(request, response, next):
    start_time = time.time()
    method = request.scope.get("method", "UNKNOWN")
    path = request.scope.get("path", "/")

    print(f"→ {method} {path}")

    await next()

    duration = time.time() - start_time
    status = getattr(response, 'status', 200)
    print(f"← {method} {path} {status} ({duration:.3f}s)")

# CORS middleware
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    await next()

# Error handling middleware
async def error_handling_middleware(request, response, next):
    try:
        await next()
    except json.JSONDecodeError:
        response.status = 400
        response.body = {"error": "Invalid JSON in request body"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        response.status = 500
        response.body = {"error": "Internal server error"}

# Register middleware
app.use(error_handling_middleware)
app.use(logging_middleware)
app.use(cors_middleware)

# In-memory storage
tasks: Dict[str, Dict[str, Any]] = {}

# ... rest of the routes remain the same
```

## Step 7: Add Input Validation

Create a helper function for validating task data:

```python title="app.py" hl_lines="50-66 78-84 105-108"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import time
import json

app = App()

# ... middleware code remains the same ...

# In-memory storage
tasks: Dict[str, Dict[str, Any]] = {}

def validate_task_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Validate task data and return (is_valid, error_message)"""
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object"

    # Check title
    title = data.get("title", "").strip()
    if not title:
        return False, "Title is required and cannot be empty"
    if len(title) > 200:
        return False, "Title must be 200 characters or less"

    # Check description
    description = data.get("description", "")
    if description and len(description) > 1000:
        return False, "Description must be 1000 characters or less"

    return True, None

async def hello():
    return {
        "message": "Welcome to Task API",
        "version": "1.0.0",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a new task",
            "GET /tasks/{task_id}": "Get a specific task",
            "PUT /tasks/{task_id}": "Update a task",
            "DELETE /tasks/{task_id}": "Delete a task"
        }
    }

async def list_tasks():
    return {
        "tasks": list(tasks.values()),
        "count": len(tasks)
    }

async def get_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404
    return {"task": tasks[task_id]}

async def create_task(request):
    data = await request.json()

    # Validate input
    is_valid, error_message = validate_task_data(data)
    if not is_valid:
        return {"error": error_message}, 400

    # Create the task
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": data["title"].strip(),
        "description": data.get("description", "").strip(),
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    tasks[task_id] = task
    return {"message": "Task created", "task": task}, 201

async def update_task(task_id: str, request):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    data = await request.json()

    # Validate if title is being updated
    if "title" in data:
        temp_data = {"title": data["title"]}
        is_valid, error_message = validate_task_data(temp_data)
        if not is_valid:
            return {"error": error_message}, 400

    task = tasks[task_id]

    # Update fields
    if "title" in data:
        task["title"] = data["title"].strip()
    if "description" in data:
        task["description"] = data["description"].strip()
    if "completed" in data:
        task["completed"] = bool(data["completed"])

    task["updated_at"] = datetime.now().isoformat()

    return {"message": "Task updated", "task": task}

async def delete_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    deleted_task = tasks.pop(task_id)
    return {"message": "Task deleted", "task": deleted_task}

# Register routes
app.get("/", hello)
app.get("/tasks", list_tasks)
app.get("/tasks/{task_id}", get_task)
app.post("/tasks", create_task)
app.put("/tasks/{task_id}", update_task)
app.delete("/tasks/{task_id}", delete_task)
```

## Complete Application

Here's your complete first Artanis application:

```python title="app.py"
from artanis import App
import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import time
import json

app = App()

# Error handling middleware
async def error_handling_middleware(request, response, next):
    try:
        await next()
    except json.JSONDecodeError:
        response.status = 400
        response.body = {"error": "Invalid JSON in request body"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        response.status = 500
        response.body = {"error": "Internal server error"}

# Request logging middleware
async def logging_middleware(request, response, next):
    start_time = time.time()
    method = request.scope.get("method", "UNKNOWN")
    path = request.scope.get("path", "/")

    print(f"→ {method} {path}")

    await next()

    duration = time.time() - start_time
    status = getattr(response, 'status', 200)
    print(f"← {method} {path} {status} ({duration:.3f}s)")

# CORS middleware
async def cors_middleware(request, response, next):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    await next()

# Register middleware
app.use(error_handling_middleware)
app.use(logging_middleware)
app.use(cors_middleware)

# In-memory storage
tasks: Dict[str, Dict[str, Any]] = {}

def validate_task_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Validate task data and return (is_valid, error_message)"""
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object"

    title = data.get("title", "").strip()
    if not title:
        return False, "Title is required and cannot be empty"
    if len(title) > 200:
        return False, "Title must be 200 characters or less"

    description = data.get("description", "")
    if description and len(description) > 1000:
        return False, "Description must be 1000 characters or less"

    return True, None

# Route handlers
async def hello():
    return {
        "message": "Welcome to Task API",
        "version": "1.0.0",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a new task",
            "GET /tasks/{task_id}": "Get a specific task",
            "PUT /tasks/{task_id}": "Update a task",
            "DELETE /tasks/{task_id}": "Delete a task"
        }
    }

async def list_tasks():
    return {
        "tasks": list(tasks.values()),
        "count": len(tasks)
    }

async def get_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404
    return {"task": tasks[task_id]}

async def create_task(request):
    data = await request.json()

    is_valid, error_message = validate_task_data(data)
    if not is_valid:
        return {"error": error_message}, 400

    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": data["title"].strip(),
        "description": data.get("description", "").strip(),
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    tasks[task_id] = task
    return {"message": "Task created", "task": task}, 201

async def update_task(task_id: str, request):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    data = await request.json()

    if "title" in data:
        temp_data = {"title": data["title"]}
        is_valid, error_message = validate_task_data(temp_data)
        if not is_valid:
            return {"error": error_message}, 400

    task = tasks[task_id]

    if "title" in data:
        task["title"] = data["title"].strip()
    if "description" in data:
        task["description"] = data["description"].strip()
    if "completed" in data:
        task["completed"] = bool(data["completed"])

    task["updated_at"] = datetime.now().isoformat()

    return {"message": "Task updated", "task": task}

async def delete_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}, 404

    deleted_task = tasks.pop(task_id)
    return {"message": "Task deleted", "task": deleted_task}

# Register routes
app.get("/", hello)
app.get("/tasks", list_tasks)
app.get("/tasks/{task_id}", get_task)
app.post("/tasks", create_task)
app.put("/tasks/{task_id}", update_task)
app.delete("/tasks/{task_id}", delete_task)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## What You've Learned

Congratulations! You've built a complete REST API that demonstrates:

- ✅ **Route registration** with different HTTP methods
- ✅ **Path parameters** for dynamic URLs
- ✅ **Request body handling** with JSON data
- ✅ **Middleware** for cross-cutting concerns
- ✅ **Error handling** with proper HTTP status codes
- ✅ **Input validation** for data integrity
- ✅ **CORS support** for browser compatibility

## Next Steps

Now you're ready to explore more advanced features:

- **[Learn about advanced routing](../guide/routing.md)** - Subrouting and complex patterns
- **[Master middleware](../guide/middleware.md)** - Custom middleware and security
- **[Explore examples](../examples/index.md)** - See more complex applications
- **[Follow the tutorial](../tutorials/index.md)** - Build a complete blog API with database integration

Your Artanis journey has just begun! 🚀
