# 6. Organizing Code with Routers

As your application grows, it's a good idea to organize your routes into separate files. Artanis provides a `Router` class for this purpose.

Let's create a new file called `posts_router.py` and move all of our post-related routes into it.

```python
# posts_router.py
from artanis import Router
from artanis.exceptions import RouteNotFound, ValidationError
from database import get_db_connection

router = Router()

async def get_posts():
    # ... (implementation)

async def create_post(request):
    # ... (implementation)

# ... (the rest of the post handlers)

router.get("/posts", get_posts)
router.post("/posts", create_post)
# ... (the rest of the post routes)
```

Now, update your `main.py` file to use the new router:

```python
# main.py
from artanis import App
from database import create_tables
from posts_router import router as posts_router
import uvicorn

app = App()

async def startup():
    await create_tables()

app.add_event_handler("startup", startup)

app.mount("/", posts_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

By using routers, you can keep your `main.py` file clean and organized, even as your application grows in complexity.

This concludes our tutorial on building a simple blog API with Artanis. We hope you've found it helpful!
