"""
Router Patterns - Artanis Example

Demonstrates advanced routing patterns with Artanis:
- Router creation and mounting
- Nested routing structures
- Path parameter patterns
- Route organization
- Subrouter patterns

Run with: python app.py
"""

from __future__ import annotations

import time
from typing import Any

import uvicorn

from artanis import App, Router
from artanis.middleware.security import CORSMiddleware

# Create the main application
app = App()

# ================================
# MIDDLEWARE
# ================================

app.use(
    CORSMiddleware(
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
)

# ================================
# DATA STORAGE (In-Memory)
# ================================

users = [
    {"id": 1, "username": "alice", "email": "alice@example.com", "posts": []},
    {"id": 2, "username": "bob", "email": "bob@example.com", "posts": []},
]

posts = [
    {"id": 1, "title": "Alice's First Post", "content": "Hello world!", "user_id": 1},
    {"id": 2, "title": "Bob's Thoughts", "content": "Artanis is great!", "user_id": 2},
]

comments = [
    {"id": 1, "post_id": 1, "user_id": 2, "content": "Great post, Alice!"},
    {"id": 2, "post_id": 2, "user_id": 1, "content": "I agree, Bob!"},
]

next_user_id = 3
next_post_id = 3
next_comment_id = 3

# ================================
# HELPER FUNCTIONS
# ================================


def find_user(user_id: int) -> dict[str, Any] | None:
    """Find user by ID."""
    return next((u for u in users if u["id"] == user_id), None)


def find_post(post_id: int) -> dict[str, Any] | None:
    """Find post by ID."""
    return next((p for p in posts if p["id"] == post_id), None)


def find_comment(comment_id: int) -> dict[str, Any] | None:
    """Find comment by ID."""
    return next((c for c in comments if c["id"] == comment_id), None)


# ================================
# MAIN APP ROUTES
# ================================


async def root() -> dict[str, Any]:
    """API root with routing information."""
    return {
        "name": "Router Patterns Demo",
        "version": "1.0.0",
        "routing_structure": {
            "/": "API root (this endpoint)",
            "/health": "Health check",
            "/api/v1/users": "User management router",
            "/api/v1/users/{user_id}/posts": "User posts subrouter",
            "/api/v1/posts": "Posts router",
            "/api/v1/posts/{post_id}/comments": "Post comments subrouter",
            "/admin": "Admin router",
            "/admin/stats": "Admin statistics",
        },
        "patterns_demonstrated": [
            "Router creation and mounting",
            "Nested routing with path parameters",
            "Subrouter organization",
            "Route parameter extraction",
            "Modular route structure",
        ],
    }


async def health() -> dict[str, Any]:
    """Health check."""
    return {"status": "healthy", "routers_mounted": 4, "total_routes": len(app.routes)}


app.get("/", root)
app.get("/health", health)

# ================================
# USERS ROUTER
# ================================

users_router = Router()


async def list_users() -> dict[str, Any]:
    """List all users."""
    return {"users": users, "count": len(users)}


async def get_user(user_id: str) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Get specific user."""
    try:
        user_id_int = int(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    user = find_user(user_id_int)
    if not user:
        return {"error": "User not found"}, 404

    # Include user's posts
    user_posts = [p for p in posts if p["user_id"] == user_id_int]
    return {"user": user, "posts": user_posts, "post_count": len(user_posts)}


async def create_user(request: Any) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Create new user."""
    global next_user_id  # noqa: PLW0603

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()

    if not username or not email:
        return {"error": "Username and email are required"}, 400

    new_user = {"id": next_user_id, "username": username, "email": email, "posts": []}

    users.append(new_user)
    next_user_id += 1

    return {"message": "User created", "user": new_user}, 201


# Register routes on users router
users_router.get("/", list_users)
users_router.get("/{user_id}", get_user)
users_router.post("/", create_user)

# ================================
# USER POSTS SUBROUTER
# ================================

user_posts_router = Router()


async def get_user_posts(user_id: str) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Get posts for a specific user."""
    try:
        user_id_int = int(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    user = find_user(user_id_int)
    if not user:
        return {"error": "User not found"}, 404

    user_posts = [p for p in posts if p["user_id"] == user_id_int]
    return {
        "user": {"id": user["id"], "username": user["username"]},
        "posts": user_posts,
        "count": len(user_posts),
    }


async def create_user_post(
    user_id: str, request: Any
) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Create post for specific user."""
    global next_post_id  # noqa: PLW0603

    try:
        user_id_int = int(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    user = find_user(user_id_int)
    if not user:
        return {"error": "User not found"}, 404

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return {"error": "Title and content are required"}, 400

    new_post = {
        "id": next_post_id,
        "title": title,
        "content": content,
        "user_id": user_id_int,
    }

    posts.append(new_post)
    next_post_id += 1

    return {"message": "Post created", "post": new_post}, 201


user_posts_router.get("/", get_user_posts)
user_posts_router.post("/", create_user_post)

# ================================
# POSTS ROUTER
# ================================

posts_router = Router()


async def list_posts() -> dict[str, Any]:
    """List all posts with author info."""
    enriched_posts = []
    for post in posts:
        user_id = post["user_id"]
        assert isinstance(user_id, int)
        user = find_user(user_id)
        enriched_post = post.copy()
        enriched_post["author"] = user["username"] if user else "Unknown"
        enriched_posts.append(enriched_post)

    return {"posts": enriched_posts, "count": len(enriched_posts)}


async def get_post(post_id: str) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Get specific post with comments."""
    try:
        post_id_int = int(post_id)
    except ValueError:
        return {"error": "Invalid post ID"}, 400

    post = find_post(post_id_int)
    if not post:
        return {"error": "Post not found"}, 404

    # Get author info
    user = find_user(post["user_id"])
    post_with_author = post.copy()
    post_with_author["author"] = user["username"] if user else "Unknown"

    # Get comments
    post_comments = [c for c in comments if c["post_id"] == post_id_int]

    return {
        "post": post_with_author,
        "comments": post_comments,
        "comment_count": len(post_comments),
    }


posts_router.get("/", list_posts)
posts_router.get("/{post_id}", get_post)

# ================================
# POST COMMENTS SUBROUTER
# ================================

post_comments_router = Router()


async def get_post_comments(
    post_id: str,
) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Get comments for a specific post."""
    try:
        post_id_int = int(post_id)
    except ValueError:
        return {"error": "Invalid post ID"}, 400

    post = find_post(post_id_int)
    if not post:
        return {"error": "Post not found"}, 404

    post_comments = [c for c in comments if c["post_id"] == post_id_int]

    # Enrich with user info
    enriched_comments = []
    for comment in post_comments:
        comment_user_id = comment["user_id"]
        assert isinstance(comment_user_id, int)
        user = find_user(comment_user_id)
        enriched_comment = comment.copy()
        enriched_comment["author"] = user["username"] if user else "Unknown"
        enriched_comments.append(enriched_comment)

    return {
        "post_id": post_id_int,
        "post_title": post["title"],
        "comments": enriched_comments,
        "count": len(enriched_comments),
    }


async def create_post_comment(
    post_id: str, request: Any
) -> dict[str, Any] | tuple[dict[str, Any], int]:
    """Create comment on specific post."""
    global next_comment_id  # noqa: PLW0603

    try:
        post_id_int = int(post_id)
    except ValueError:
        return {"error": "Invalid post ID"}, 400

    post = find_post(post_id_int)
    if not post:
        return {"error": "Post not found"}, 404

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    content = data.get("content", "").strip()
    user_id = data.get("user_id")

    if not content:
        return {"error": "Content is required"}, 400

    if not user_id or not find_user(user_id):
        return {"error": "Valid user_id is required"}, 400

    new_comment = {
        "id": next_comment_id,
        "post_id": post_id_int,
        "user_id": user_id,
        "content": content,
    }

    comments.append(new_comment)
    next_comment_id += 1

    return {"message": "Comment created", "comment": new_comment}, 201


post_comments_router.get("/", get_post_comments)
post_comments_router.post("/", create_post_comment)

# ================================
# ADMIN ROUTER
# ================================

admin_router = Router()


async def admin_dashboard() -> dict[str, Any]:
    """Admin dashboard."""
    return {
        "message": "Admin Dashboard",
        "endpoints": {
            "GET /admin": "This dashboard",
            "GET /admin/stats": "System statistics",
            "GET /admin/users": "User management",
            "GET /admin/posts": "Post management",
        },
    }


async def admin_stats() -> dict[str, Any]:
    """System statistics."""
    return {
        "statistics": {
            "total_users": len(users),
            "total_posts": len(posts),
            "total_comments": len(comments),
            "posts_per_user": len(posts) / len(users) if users else 0,
            "comments_per_post": len(comments) / len(posts) if posts else 0,
        },
        "recent_activity": {
            "latest_user": users[-1]["username"] if users else None,
            "latest_post": posts[-1]["title"] if posts else None,
        },
    }


async def admin_users() -> dict[str, Any]:
    """User management."""
    return {"users": users, "actions": ["view", "edit", "delete", "ban"]}


async def admin_posts() -> dict[str, Any]:
    """Post management."""
    return {"posts": posts, "actions": ["view", "edit", "delete", "feature"]}


admin_router.get("/", admin_dashboard)
admin_router.get("/stats", admin_stats)
admin_router.get("/users", admin_users)
admin_router.get("/posts", admin_posts)

# ================================
# MOUNT ROUTERS
# ================================

# Create API v1 router
api_v1 = Router()

# Mount subrouters on API v1
api_v1.mount("/users", users_router)
api_v1.mount("/users/{user_id}/posts", user_posts_router)  # Nested with params
api_v1.mount("/posts", posts_router)
api_v1.mount("/posts/{post_id}/comments", post_comments_router)  # Nested with params

# Mount API v1 on main app
app.mount("/api/v1", api_v1)

# Mount admin router directly on main app
app.mount("/admin", admin_router)

# ================================
# MAIN APPLICATION
# ================================

if __name__ == "__main__":
    print("🚀 Starting Router Patterns Demo with Artanis")
    print()
    print("🏗️  Routing Structure:")
    print("   Main App")
    print("   ├── GET /")
    print("   ├── GET /health")
    print("   ├── /api/v1/ (Router)")
    print("   │   ├── /users/ (Router)")
    print("   │   │   ├── GET /")
    print("   │   │   ├── GET /{user_id}")
    print("   │   │   └── POST /")
    print("   │   ├── /users/{user_id}/posts/ (Subrouter)")
    print("   │   │   ├── GET /")
    print("   │   │   └── POST /")
    print("   │   ├── /posts/ (Router)")
    print("   │   │   ├── GET /")
    print("   │   │   └── GET /{post_id}")
    print("   │   └── /posts/{post_id}/comments/ (Subrouter)")
    print("   │       ├── GET /")
    print("   │       └── POST /")
    print("   └── /admin/ (Router)")
    print("       ├── GET /")
    print("       ├── GET /stats")
    print("       ├── GET /users")
    print("       └── GET /posts")
    print()
    print("📍 Test URLs:")
    print("   curl http://127.0.0.1:8000/")
    print("   curl http://127.0.0.1:8000/api/v1/users")
    print("   curl http://127.0.0.1:8000/api/v1/users/1")
    print("   curl http://127.0.0.1:8000/api/v1/users/1/posts")
    print("   curl http://127.0.0.1:8000/api/v1/posts")
    print("   curl http://127.0.0.1:8000/api/v1/posts/1/comments")
    print("   curl http://127.0.0.1:8000/admin/stats")
    print()
    print("🌐 Server starting at: http://127.0.0.1:8000")
    print("⏹️  Press Ctrl+C to stop")
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, log_level="info")


"""
🧪 Testing Router Patterns:

1. Main routes:
   curl http://127.0.0.1:8000/
   curl http://127.0.0.1:8000/health

2. User management:
   curl http://127.0.0.1:8000/api/v1/users
   curl http://127.0.0.1:8000/api/v1/users/1

3. User posts (nested routing):
   curl http://127.0.0.1:8000/api/v1/users/1/posts

4. Create user post:
   curl -X POST http://127.0.0.1:8000/api/v1/users/1/posts \
     -H "Content-Type: application/json" \
     -d '{"title": "New Post", "content": "Post content"}'

5. Posts:
   curl http://127.0.0.1:8000/api/v1/posts
   curl http://127.0.0.1:8000/api/v1/posts/1

6. Post comments (nested routing):
   curl http://127.0.0.1:8000/api/v1/posts/1/comments

7. Create comment:
   curl -X POST http://127.0.0.1:8000/api/v1/posts/1/comments \
     -H "Content-Type: application/json" \
     -d '{"content": "Great post!", "user_id": 2}'

8. Admin routes:
   curl http://127.0.0.1:8000/admin
   curl http://127.0.0.1:8000/admin/stats
   curl http://127.0.0.1:8000/admin/users

🔍 Router Pattern Benefits:

1. **Organization**: Related routes grouped together
2. **Modularity**: Routers can be reused across applications
3. **Nested Routing**: Complex URL structures with parameters
4. **Separation of Concerns**: Each router handles one domain
5. **Scalability**: Easy to add new route groups
6. **Maintainability**: Clear structure for large applications

💡 Key Concepts:

- **Router Creation**: Router() creates a new router instance
- **Route Registration**: router.get(), router.post(), etc.
- **Router Mounting**: app.mount(path, router)
- **Nested Parameters**: /users/{user_id}/posts pattern
- **Path Inheritance**: Mount paths combine with route paths
- **Subrouter Access**: Parameters from mount path available in handlers

This example demonstrates how to build complex, hierarchical
routing structures that scale well for large applications.
"""
