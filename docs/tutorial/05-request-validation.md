# 5. Request Validation

It's important to validate the data that your API receives. In this section, we'll add validation to our `create_post` and `update_post` routes.

Artanis has a built-in `ValidationError` exception that we can use. Let's update our `create_post` handler to validate the request body.

```python
# main.py
# ... (imports)
from artanis.exceptions import ValidationError

# ... (app, startup, middleware)

async def create_post(request):
    post_data = await request.json()
    if not post_data.get("title") or not post_data.get("content"):
        raise ValidationError("Both title and content are required")

    async with get_db_connection() as db:
        cursor = await db.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (post_data["title"], post_data["content"])
        )
        await db.commit()
        return {"message": "Post created", "post_id": cursor.lastrowid}

# ... (update update_post with similar validation)

# ... (add routes)

# ... (rest of the file)
```

Now, if you try to create a post without a title or content, you'll get a 400 Bad Request error with a helpful message.

For more complex validation scenarios, you can use a library like `pydantic`.

In the next section, we'll learn how to organize our code with routers.
