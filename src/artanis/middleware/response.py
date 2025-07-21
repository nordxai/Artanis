import json
from typing import Dict, Any, Union


class Response:
    """Response object for middleware to modify response data"""
    
    def __init__(self):
        self.status = 200
        self.headers = {}
        self.body = None
        self._finished = False
    
    def json(self, data: Any):
        """Set response body as JSON data"""
        self.body = data
        self.headers["Content-Type"] = "application/json"
    
    def set_header(self, name: str, value: str):
        """Set a response header"""
        self.headers[name] = value
    
    def get_header(self, name: str) -> Union[str, None]:
        """Get a response header"""
        return self.headers.get(name)
    
    def set_status(self, status: int):
        """Set response status code"""
        self.status = status
    
    def finish(self):
        """Mark response as finished (no further processing)"""
        self._finished = True
    
    def is_finished(self) -> bool:
        """Check if response is finished"""
        return self._finished
    
    def to_bytes(self) -> bytes:
        """Convert response body to bytes for ASGI"""
        if self.body is None:
            return b""
        
        if isinstance(self.body, dict) or isinstance(self.body, list):
            return json.dumps(self.body).encode()
        elif isinstance(self.body, str):
            return self.body.encode()
        elif isinstance(self.body, bytes):
            return self.body
        else:
            return str(self.body).encode()
    
    def get_headers_list(self) -> list:
        """Get headers in ASGI format [(name_bytes, value_bytes), ...]"""
        headers = []
        for name, value in self.headers.items():
            name_bytes = name.encode() if isinstance(name, str) else name
            value_bytes = value.encode() if isinstance(value, str) else value
            headers.append((name_bytes, value_bytes))
        return headers