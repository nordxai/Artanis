"""Response object for middleware to modify response data.

Provides the Response class that middleware and route handlers can use
to build HTTP responses with headers, status codes, and body content.
"""

import json
from typing import Any, Dict, List, Optional, Tuple


class Response:
    """Response object for middleware to modify response data.

    Provides a convenient interface for building HTTP responses with
    status codes, headers, and body content. Can be used by middleware
    and route handlers to construct responses.

    Attributes:
        status: HTTP status code (default: 200)
        headers: Dictionary of response headers
        body: Response body content (JSON, string, or bytes)
        _finished: Internal flag indicating if response is complete

    Example:
        ```python
        response = Response()
        response.set_status(201)
        response.set_header('Content-Type', 'application/json')
        response.json({'message': 'Created successfully'})
        ```
    """

    def __init__(self) -> None:
        self.status: int = 200
        self.headers: Dict[str, str] = {}
        self.body: Any = None
        self._finished: bool = False

    def json(self, data: Any) -> None:
        """Set response body as JSON data.

        Sets the response body to the provided data and automatically
        sets the Content-Type header to 'application/json'.

        Args:
            data: JSON-serializable data (dict, list, string, number, etc.)
        """
        self.body = data
        self.headers["Content-Type"] = "application/json"

    def set_header(self, name: str, value: str) -> None:
        """Set a response header.

        Args:
            name: Header name
            value: Header value
        """
        self.headers[name] = value

    def get_header(self, name: str) -> Optional[str]:
        """Get a response header.

        Args:
            name: Header name to retrieve

        Returns:
            Header value if exists, None otherwise
        """
        return self.headers.get(name)

    def set_status(self, status: int) -> None:
        """Set response status code.

        Args:
            status: HTTP status code (e.g., 200, 404, 500)
        """
        self.status = status

    def finish(self) -> None:
        """Mark response as finished (no further processing).

        Marks the response as complete, preventing further modifications.
        Used by middleware to indicate that no additional processing
        should occur.
        """
        self._finished = True

    def is_finished(self) -> bool:
        """Check if response is finished.

        Returns:
            True if response is marked as finished, False otherwise
        """
        return self._finished

    def to_bytes(self) -> bytes:
        """Convert response body to bytes for ASGI.

        Converts various body types to bytes suitable for ASGI transmission.
        Handles JSON serialization for dict/list objects.

        Returns:
            Response body as bytes
        """
        if self.body is None:
            return b""

        if isinstance(self.body, dict) or isinstance(self.body, list):
            return json.dumps(self.body).encode()
        if isinstance(self.body, str):
            return self.body.encode()
        if isinstance(self.body, bytes):
            return self.body
        return str(self.body).encode()

    def get_headers_list(self) -> List[Tuple[bytes, bytes]]:
        """Get headers in ASGI format [(name_bytes, value_bytes), ...].

        Converts header dictionary to ASGI-compatible list format
        with byte-encoded names and values.

        Returns:
            List of tuples containing header names and values as bytes
        """
        headers = []
        for name, value in self.headers.items():
            name_bytes = name.encode() if isinstance(name, str) else name
            value_bytes = value.encode() if isinstance(value, str) else value
            headers.append((name_bytes, value_bytes))
        return headers
