"""HTTP Request handling for Artanis framework.

This module provides the Request class for handling HTTP requests in the
Artanis ASGI web framework, including body parsing and header processing.
"""

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

from .exceptions import ValidationError


class Request:
    """HTTP request object providing access to request data.

    This class encapsulates the ASGI scope and receive callable to provide
    a convenient interface for accessing request data including headers,
    body content, and path parameters.

    Args:
        scope: ASGI scope dictionary containing request metadata
        receive: ASGI receive callable for getting request body

    Attributes:
        scope: The ASGI scope dictionary
        receive: The ASGI receive callable
        path_params: Dictionary of extracted path parameters
        headers: Dictionary of request headers
    """

    def __init__(
        self, scope: dict[str, Any], receive: Callable[[], Awaitable[dict[str, Any]]]
    ) -> None:
        self.scope = scope
        self.receive = receive
        self._body: bytes | None = None
        self.path_params: dict[
            str, str
        ] = {}  # For middleware access to path parameters
        # Convert ASGI headers (list of byte tuples) to string dict
        raw_headers = scope.get("headers", [])
        self.headers: dict[str, str] = {
            name.decode().lower(): value.decode() for name, value in raw_headers
        }

    async def body(self) -> bytes:
        """Get the request body as bytes.

        Reads and caches the complete request body from the ASGI receive callable.
        The body is cached after the first call to avoid multiple reads.

        Returns:
            The complete request body as bytes
        """
        if self._body is None:
            body_parts = []
            while True:
                message = await self.receive()
                if message["type"] == "http.request":
                    body_parts.append(message.get("body", b""))
                    if not message.get("more_body", False):
                        break
            self._body = b"".join(body_parts)
        return self._body

    async def json(self) -> Any:
        """Parse request body as JSON.

        Reads the request body and parses it as JSON data.

        Returns:
            Parsed JSON data (dict, list, or other JSON-serializable types)

        Raises:
            ValidationError: If the body is not valid JSON
        """
        try:
            body = await self.body()
            return json.loads(body.decode())
        except json.JSONDecodeError as e:
            raise ValidationError(
                message="Invalid JSON in request body",
                field="body",
                value=body.decode() if len(body) < 200 else body.decode()[:200] + "...",
                validation_errors={"json_error": str(e)},
            )
