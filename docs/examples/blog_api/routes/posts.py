"""
Blog Posts Routes

Handles CRUD operations for blog posts, including search, filtering, and file uploads.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

from typing_extensions import TypedDict
from utils.database import get_db_connection
from utils.security import sanitize_html
from utils.validation import validate_file_upload, validate_post_data

from artanis import Router
from artanis.exceptions import AuthenticationError, ValidationError
from artanis.logging import ArtanisLogger


class PostDict(TypedDict):
    """Type definition for post data."""

    id: int
    title: str
    slug: str
    content: str
    summary: str
    author_id: int
    author_username: str
    category: str
    tags: list[str]
    status: str
    featured_image: str | None
    view_count: int
    like_count: int
    comment_count: int
    created_at: str
    updated_at: str
    published_at: str | None


logger = ArtanisLogger.get_logger("posts")
posts_router = Router()

# In-memory storage for demo (replace with database)
posts: list[PostDict] = [
    {
        "id": 1,
        "title": "Welcome to Our Blog",
        "slug": "welcome-to-our-blog",
        "content": "This is our first blog post! Welcome to our amazing blog platform.",
        "summary": "Welcome post introducing our blog platform",
        "author_id": 1,
        "author_username": "admin",
        "category": "Announcements",
        "tags": ["welcome", "introduction"],
        "status": "published",
        "featured_image": None,
        "view_count": 45,
        "like_count": 12,
        "comment_count": 3,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
        "published_at": "2024-01-01T10:00:00Z",
    },
    {
        "id": 2,
        "title": "Getting Started with Artanis",
        "slug": "getting-started-with-artanis",
        "content": "Artanis is a powerful Python web framework that makes building APIs simple and enjoyable. In this post, we'll explore the basics...",
        "summary": "Learn the fundamentals of the Artanis web framework",
        "author_id": 1,
        "author_username": "admin",
        "category": "Technology",
        "tags": ["artanis", "python", "web", "framework"],
        "status": "published",
        "featured_image": None,
        "view_count": 128,
        "like_count": 34,
        "comment_count": 8,
        "created_at": "2024-01-02T14:30:00Z",
        "updated_at": "2024-01-02T14:30:00Z",
        "published_at": "2024-01-02T14:30:00Z",
    },
]
next_post_id = 3

categories = [
    "Technology",
    "Lifestyle",
    "Travel",
    "Food",
    "Health",
    "Business",
    "Announcements",
]


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title."""
    import re

    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")


def get_post_by_id_or_slug(identifier: str) -> PostDict | None:
    """Get post by ID or slug."""
    # Try ID first
    try:
        post_id = int(identifier)
        return next((p for p in posts if p["id"] == post_id), None)
    except ValueError:
        # Try slug
        return next((p for p in posts if p["slug"] == identifier), None)


async def get_posts(request: Any) -> dict[str, Any]:
    """Get all posts with filtering and search."""
    query_params = request.query_params

    # Start with all published posts
    filtered_posts = [p for p in posts if p["status"] == "published"]

    # Search filter
    search = query_params.get("search", "").strip()
    if search:
        search_lower = search.lower()
        filtered_posts = [
            p
            for p in filtered_posts
            if search_lower in p["title"].lower()
            or search_lower in p["content"].lower()
            or search_lower in p["summary"].lower()
            or search_lower in " ".join(p["tags"]).lower()
        ]

    # Category filter
    category = query_params.get("category", "").strip()
    if category:
        filtered_posts = [p for p in filtered_posts if p["category"] == category]

    # Tag filter
    tag = query_params.get("tag", "").strip()
    if tag:
        filtered_posts = [p for p in filtered_posts if tag in p["tags"]]

    # Author filter
    author = query_params.get("author", "").strip()
    if author:
        filtered_posts = [p for p in filtered_posts if p["author_username"] == author]

    # Sorting
    sort_by = query_params.get("sort", "created_at")
    sort_order = query_params.get("order", "desc")

    if sort_by in [
        "created_at",
        "updated_at",
        "published_at",
        "view_count",
        "like_count",
    ]:
        reverse = sort_order == "desc"
        if sort_by == "created_at":
            filtered_posts.sort(key=lambda x: x["created_at"], reverse=reverse)
        elif sort_by == "updated_at":
            filtered_posts.sort(key=lambda x: x["updated_at"], reverse=reverse)
        elif sort_by == "published_at":
            filtered_posts.sort(key=lambda x: x["published_at"] or "", reverse=reverse)
        elif sort_by == "view_count":
            filtered_posts.sort(key=lambda x: x["view_count"], reverse=reverse)
        elif sort_by == "like_count":
            filtered_posts.sort(key=lambda x: x["like_count"], reverse=reverse)

    # Pagination
    try:
        page = int(query_params.get("page", 1))
        per_page = min(int(query_params.get("per_page", 10)), 50)  # Max 50 per page
    except ValueError:
        page = 1
        per_page = 10

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_posts = filtered_posts[start_idx:end_idx]

    # Calculate pagination metadata
    total_posts = len(filtered_posts)
    total_pages = (total_posts + per_page - 1) // per_page

    return {
        "posts": paginated_posts,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_posts,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "filters": {
            "search": search,
            "category": category,
            "tag": tag,
            "author": author,
            "sort": sort_by,
            "order": sort_order,
        },
    }


async def get_post(post_id: str) -> dict[str, PostDict]:
    """Get a specific post by ID or slug."""
    post = get_post_by_id_or_slug(post_id)

    if not post:
        msg = "Post not found"
        raise ValidationError(msg)

    if post["status"] != "published":
        msg = "Post not available"
        raise ValidationError(msg)

    # Increment view count
    post["view_count"] += 1

    return {"post": post}


async def create_post(request: Any) -> tuple[dict[str, Any], int]:
    """Create a new blog post (requires authentication)."""
    current_user = getattr(request, "current_user", None)
    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    global next_post_id  # noqa: PLW0603

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    # Validate post data
    validated_data = validate_post_data(data)

    # Generate slug
    slug = generate_slug(validated_data["title"])

    # Ensure slug is unique
    base_slug = slug
    counter = 1
    while any(p["slug"] == slug for p in posts):
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create new post
    new_post: PostDict = {
        "id": next_post_id,
        "title": validated_data["title"],
        "slug": slug,
        "content": sanitize_html(validated_data["content"]),
        "summary": validated_data["summary"],
        "author_id": current_user["id"],
        "author_username": current_user["username"],
        "category": validated_data["category"],
        "tags": validated_data["tags"],
        "status": validated_data.get("status", "draft"),
        "featured_image": None,
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "published_at": datetime.now(timezone.utc).isoformat() + "Z"
        if validated_data.get("status") == "published"
        else None,
    }

    posts.append(new_post)
    next_post_id += 1

    logger.info(f"New post created: {new_post['title']} by {current_user['username']}")

    return {"message": "Post created successfully", "post": new_post}, 201


def _update_post_title(post: PostDict, title: str) -> None:
    """Helper function to update post title and regenerate slug."""
    if not title.strip():
        msg = "Title cannot be empty"
        raise ValidationError(msg, field="title")

    post["title"] = title.strip()

    # Regenerate slug if title changed
    new_slug = generate_slug(post["title"])
    base_slug = new_slug
    counter = 1
    while any(p["slug"] == new_slug and p["id"] != post["id"] for p in posts):
        new_slug = f"{base_slug}-{counter}"
        counter += 1
    post["slug"] = new_slug


def _update_post_content(post: PostDict, content: str) -> None:
    """Helper function to update post content."""
    if not content.strip():
        msg = "Content cannot be empty"
        raise ValidationError(msg, field="content")
    post["content"] = sanitize_html(content)


def _update_post_metadata(post: PostDict, data: dict[str, Any]) -> None:
    """Helper function to update post metadata fields."""
    if "summary" in data:
        post["summary"] = data["summary"].strip()

    if "category" in data:
        if data["category"] not in categories:
            categories_str = ", ".join(categories)
            msg = f"Category must be one of: {categories_str}"
            raise ValidationError(msg, field="category")
        post["category"] = data["category"]

    if "tags" in data:
        if not isinstance(data["tags"], list):
            msg = "Tags must be an array"
            raise ValidationError(msg, field="tags")
        post["tags"] = [tag.strip() for tag in data["tags"] if tag.strip()]

    if "status" in data:
        if data["status"] not in ["draft", "published"]:
            msg = "Status must be 'draft' or 'published'"
            raise ValidationError(msg, field="status")

        old_status = post["status"]
        post["status"] = data["status"]

        # Set published_at when publishing
        if old_status != "published" and data["status"] == "published":
            post["published_at"] = datetime.now(timezone.utc).isoformat() + "Z"


async def update_post(post_id: str, request: Any) -> dict[str, Any]:
    """Update an existing post (requires authentication and ownership)."""
    current_user = getattr(request, "current_user", None)
    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    post = get_post_by_id_or_slug(post_id)
    if not post:
        msg = "Post not found"
        raise ValidationError(msg)

    # Check ownership (or admin)
    if post["author_id"] != current_user["id"] and not current_user.get(
        "is_admin", False
    ):
        msg = "You can only edit your own posts"
        raise AuthenticationError(msg)

    try:
        data = await request.json()
    except Exception:
        msg = "Invalid JSON in request body"
        raise ValidationError(msg)

    # Update fields using helper functions
    if "title" in data:
        _update_post_title(post, data["title"])

    if "content" in data:
        _update_post_content(post, data["content"])

    # Update metadata fields
    _update_post_metadata(post, data)

    post["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"

    logger.info(f"Post updated: {post['title']} by {current_user['username']}")

    return {"message": "Post updated successfully", "post": post}


async def delete_post(post_id: str, request: Any) -> dict[str, str]:
    """Delete a post (requires authentication and ownership)."""
    current_user = getattr(request, "current_user", None)
    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    post = get_post_by_id_or_slug(post_id)
    if not post:
        msg = "Post not found"
        raise ValidationError(msg)

    # Check ownership (or admin)
    if post["author_id"] != current_user["id"] and not current_user.get(
        "is_admin", False
    ):
        msg = "You can only delete your own posts"
        raise AuthenticationError(msg)

    # Remove post
    global posts  # noqa: PLW0603
    posts = [p for p in posts if p["id"] != post["id"]]

    logger.info(f"Post deleted: {post['title']} by {current_user['username']}")

    return {"message": "Post deleted successfully"}


async def like_post(post_id: str, request: Any) -> dict[str, str | int]:
    """Like a post (requires authentication)."""
    current_user = getattr(request, "current_user", None)
    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    post = get_post_by_id_or_slug(post_id)
    if not post:
        msg = "Post not found"
        raise ValidationError(msg)

    # In a real app, track user likes to prevent duplicates
    post["like_count"] += 1

    return {"message": "Post liked successfully", "like_count": post["like_count"]}


async def upload_post_image(post_id: str, request: Any) -> dict[str, str]:
    """Upload featured image for a post."""
    current_user = getattr(request, "current_user", None)
    if not current_user:
        msg = "Authentication required"
        raise AuthenticationError(msg)

    post = get_post_by_id_or_slug(post_id)
    if not post:
        msg = "Post not found"
        raise ValidationError(msg)

    # Check ownership (or admin)
    if post["author_id"] != current_user["id"] and not current_user.get(
        "is_admin", False
    ):
        msg = "You can only upload images to your own posts"
        raise AuthenticationError(msg)

    # Get uploaded file from request
    # This is a simplified example - in reality, you'd handle multipart/form-data
    try:
        form_data = await request.form()
        uploaded_file = form_data.get("image")

        if not uploaded_file:
            msg = "No image file provided"
            raise ValidationError(msg)

        # Validate file
        validate_file_upload(
            uploaded_file, allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"]
        )

        # Save file (simplified)
        upload_dir = Path("uploads/posts")
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{post['id']}_{int(time.time())}_{uploaded_file.filename}"
        file_path = upload_dir / filename

        with file_path.open("wb") as f:
            f.write(await uploaded_file.read())

        # Update post with image URL
        post["featured_image"] = f"/uploads/posts/{filename}"
        post["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        logger.info(f"Image uploaded for post: {post['title']}")

        image_url = post["featured_image"] or ""
        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
        }

    except Exception as e:
        msg = f"File upload failed: {e!s}"
        raise ValidationError(msg)


async def get_categories() -> dict[str, Any]:
    """Get all available categories."""
    # Count posts per category
    category_counts: dict[str, int] = {}
    for post in posts:
        if post["status"] == "published":
            category = post["category"]
            category_counts[category] = category_counts.get(category, 0) + 1

    category_list = [
        {"name": cat, "post_count": category_counts.get(cat, 0)} for cat in categories
    ]

    return {"categories": category_list, "total": len(categories)}


async def get_tags() -> dict[str, Any]:
    """Get all tags with usage count."""
    tag_counts: dict[str, int] = {}

    for post in posts:
        if post["status"] == "published":
            for tag in post["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by usage count
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    tag_list = [{"name": tag, "post_count": count} for tag, count in sorted_tags]

    return {"tags": tag_list, "total": len(tag_list)}


async def get_post_stats() -> dict[str, Any]:
    """Get blog statistics."""
    published_posts = [p for p in posts if p["status"] == "published"]
    draft_posts = [p for p in posts if p["status"] == "draft"]

    total_views = sum(p["view_count"] for p in published_posts)
    total_likes = sum(p["like_count"] for p in published_posts)
    total_comments = sum(p["comment_count"] for p in published_posts)

    return {
        "posts": {
            "total": len(posts),
            "published": len(published_posts),
            "drafts": len(draft_posts),
        },
        "engagement": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_views_per_post": total_views / len(published_posts)
            if published_posts
            else 0,
        },
        "categories": len(categories),
        "tags": len({tag for post in posts for tag in post["tags"]}),
    }


# Route registrations
posts_router.get("/", get_posts)
posts_router.get("/{post_id}", get_post)
posts_router.post("/", create_post)
posts_router.put("/{post_id}", update_post)
posts_router.delete("/{post_id}", delete_post)
posts_router.post("/{post_id}/like", like_post)
posts_router.post("/{post_id}/upload-image", upload_post_image)
posts_router.get("/categories", get_categories)
posts_router.get("/tags", get_tags)
posts_router.get("/stats", get_post_stats)


"""
📝 Blog Posts Routes Documentation:

Endpoints:
- GET /posts - List posts with filtering/search/pagination
- GET /posts/{id} - Get specific post by ID or slug
- POST /posts - Create new post (auth required)
- PUT /posts/{id} - Update post (auth required, ownership)
- DELETE /posts/{id} - Delete post (auth required, ownership)
- POST /posts/{id}/like - Like a post (auth required)
- POST /posts/{id}/upload-image - Upload featured image (auth required)
- GET /posts/categories - Get all categories
- GET /posts/tags - Get all tags with counts
- GET /posts/stats - Get blog statistics

Features:
1. **CRUD Operations**: Complete post management
2. **Search & Filtering**: By title, content, category, tags, author
3. **Pagination**: Configurable page size with metadata
4. **Slug Generation**: SEO-friendly URLs
5. **File Uploads**: Featured image handling
6. **Like System**: Post engagement tracking
7. **Categories & Tags**: Content organization
8. **Statistics**: Analytics and metrics
9. **Access Control**: Owner/admin permissions
10. **Content Sanitization**: HTML cleaning for security

Query Parameters for GET /posts:
- search: Full-text search
- category: Filter by category
- tag: Filter by tag
- author: Filter by author
- sort: Sort field (created_at, view_count, etc.)
- order: Sort order (asc/desc)
- page: Page number
- per_page: Items per page

Example Usage:

1. List posts:
   GET /api/v1/posts?search=artanis&category=Technology&page=1&per_page=5

2. Create post:
   POST /api/v1/posts
   Authorization: Bearer <token>
   {
     "title": "My Blog Post",
     "content": "Post content...",
     "summary": "Brief summary",
     "category": "Technology",
     "tags": ["python", "web"],
     "status": "published"
   }

3. Upload image:
   POST /api/v1/posts/1/upload-image
   Authorization: Bearer <token>
   Content-Type: multipart/form-data
   [image file in 'image' field]

Security Features:
- Authentication required for write operations
- Ownership verification for updates/deletes
- Input validation and sanitization
- File upload validation
- Rate limiting (via middleware)
- HTML content sanitization

The posts system provides a complete blog management solution with all the features
needed for a production blog platform, including content management, SEO optimization,
file handling, and comprehensive analytics.
"""
