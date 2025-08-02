"""ASGI protocol handling for Artanis framework.

This module provides utilities for sending HTTP responses through the ASGI
interface, including JSON responses and error handling.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .middleware.response import Response


async def send_json_response(send: Callable[..., Any], status: int, data: Any) -> None:
    """Send a JSON response.

    Args:
        send: ASGI send callable
        status: HTTP status code
        data: Data to serialize as JSON
    """
    response_body = json.dumps(data).encode()

    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(response_body)).encode()],
            ],
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": response_body,
        }
    )


async def send_error_response(
    send: Callable[..., Any], status: int, message: str
) -> None:
    """Send an error response.

    Args:
        send: ASGI send callable
        status: HTTP status code
        message: Error message
    """
    await send_json_response(send, status, {"error": message})


async def send_response(send: Callable[..., Any], response: Response) -> None:
    """Send response using middleware Response object.

    Args:
        send: ASGI send callable
        response: Response object with headers, status, and body
    """
    response_body = response.to_bytes()

    # Build headers list, ensuring content-length is set
    headers = response.get_headers_list()

    # Add content-length if not already set
    content_length_set = any(name.lower() == b"content-length" for name, _ in headers)
    if not content_length_set:
        headers.append((b"content-length", str(len(response_body)).encode()))

    # Add content-type if not already set and body is JSON
    content_type_set = any(name.lower() == b"content-type" for name, _ in headers)
    if not content_type_set and response.body is not None:
        if isinstance(response.body, (dict, list)):
            headers.append((b"content-type", b"application/json"))

    await send(
        {
            "type": "http.response.start",
            "status": response.status,
            "headers": headers,
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": response_body,
        }
    )
