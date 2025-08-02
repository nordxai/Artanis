# 2. Creating Routes

In this section, we'll add routes for our blog posts. We'll need routes to:

*   Get all posts
*   Create a new post
*   Get a single post
*   Update a post
*   Delete a post

For now, we'll use in-memory data. We'll connect to a real database in a later section.

Update your `main.py` file with the following code:

```python
# main.py
from artanis import App
from artanis.exceptions import RouteNotFound
import uvicorn

app = App()

# In-memory database
posts = {
    1: {"title": "First Post", "content": "This is the first post."},
    2: {"title": "Second Post", "content": "This is the second post."},
}

async def root():
    return {"message": "Welcome to the Blog API!"}

async def get_posts():
    return posts

async def create_post(request):
    post_data = await request.json()
    post_id = max(posts.keys()) + 1
    posts[post_id] = post_data
    return {"message": "Post created", "post_id": post_id}

async def get_post(post_id: int):
    post_id = int(post_id)
    if post_id not in posts:
        raise RouteNotFound(f"Post with ID {post_id} not found")
    return posts[post_id]

async def update_post(post_id: int, request):
    post_id = int(post_id)
    if post_id not in posts:
        raise RouteNotFound(f"Post with ID {post_id} not found")
    post_data = await request.json()
    posts[post_id] = post_data
    return {"message": f"Post {post_id} updated"}

async def delete_post(post_id: int):
    post_id = int(post_id)
    if post_id not in posts:
        raise RouteNotFound(f"Post with ID {post_id} not found")
    del posts[post_id]
    return {"message": f"Post {post_id} deleted"}

app.get("/", root)
app.get("/posts", get_posts)
app.post("/posts", create_post)
app.get("/post/{post_id}", get_post)
app.put("/post/{post_id}", update_post)
app.delete("/post/{post_id}", delete_post)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

Now you can try out the new routes using a tool like `curl` or an API client like Postman.

In the next section, we'll learn how to use middleware for logging and error handling.
