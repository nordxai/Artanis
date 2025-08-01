# 4. Database Integration

In this section, we'll replace our in-memory database with a real SQLite database. We'll use the `aiosqlite` library to interact with the database asynchronously.

First, let's install `aiosqlite`:

```bash
pip install aiosqlite
```

Next, create a new file called `database.py` and add the following code:

```python
# database.py
import aiosqlite

DATABASE_URL = "blog.db"

async def get_db_connection():
    return await aiosqlite.connect(DATABASE_URL)

async def create_tables():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        await db.commit()
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

async def startup():
    await create_tables()

app.add_event_handler("startup", startup)

# ... (middleware)

async def get_posts():
    async with get_db_connection() as db:
        cursor = await db.execute("SELECT id, title, content FROM posts")
        rows = await cursor.fetchall()
        return [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]

async def create_post(request):
    post_data = await request.json()
    async with get_db_connection() as db:
        cursor = await db.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (post_data["title"], post_data["content"])
        )
        await db.commit()
        return {"message": "Post created", "post_id": cursor.lastrowid}

# ... (update get_post, update_post, delete_post to use the database)

# ... (add routes)

# ... (rest of the file)
```

Now, your application is using a real database to store and retrieve blog posts.

In the next section, we'll look at how to validate request data.
