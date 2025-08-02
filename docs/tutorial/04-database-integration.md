# 4. Database Integration

In this section, we'll replace our in-memory database with a real SQLite database. We'll use the built-in `sqlite3` library for simplicity.

Note: SQLite operations in Python are synchronous by default. For production applications with high concurrency, consider using `aiosqlite` for true async database operations.

First, let's add the database functions directly to our `main.py` file:

```python
# Add these database functions to main.py
import sqlite3

# Shared in-memory database connection
_db_connection = None

def get_db_connection():
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect(":memory:", check_same_thread=False)
    return _db_connection

def create_tables():
    with get_db_connection() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        db.commit()
```

Now, update your `main.py` file to use the database:

```python
# main.py
import time
from artanis import App
from artanis.exceptions import RouteNotFound
from artanis.middleware.exception import ExceptionHandlerMiddleware
from database import get_db_connection, create_tables
import uvicorn

app = App()

# Initialize database tables
create_tables()

# ... (middleware)

async def get_posts():
    with get_db_connection() as db:
        cursor = db.execute("SELECT id, title, content FROM posts")
        rows = cursor.fetchall()
        return [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]

async def create_post(request):
    post_data = await request.json()
    with get_db_connection() as db:
        cursor = db.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (post_data["title"], post_data["content"])
        )
        db.commit()
        return {"message": "Post created", "post_id": cursor.lastrowid}

# ... (update get_post, update_post, delete_post to use the database)

# ... (add routes)

# ... (rest of the file)
```

Now, your application is using a real database to store and retrieve blog posts.

In the next section, we'll look at how to validate request data.
