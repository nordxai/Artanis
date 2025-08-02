"""Handler parameter injection and execution for Artanis framework.

This module provides utilities for calling route handlers with appropriate
parameter injection based on function signatures.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

from .exceptions import HandlerError

if TYPE_CHECKING:
    from .request import Request


async def call_handler(
    handler: Callable[..., Any],
    path_params: dict[str, str],
    request: Request | None = None,
    route_info: dict[str, Any] | None = None,
) -> Any:
    """Call a route handler with appropriate parameters.

    Inspects the handler signature and provides path parameters and
    request object as needed.

    Args:
        handler: Route handler function
        path_params: Extracted path parameters
        request: Request object (optional)
        route_info: Route information for error context (optional)

    Returns:
        Handler response data

    Raises:
        HandlerError: If handler execution fails
    """
    try:
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())

        args: list[Any] = []
        for param in params:
            if param in path_params:
                args.append(path_params[param])
            elif param == "request" and request:
                args.append(request)

        if inspect.iscoroutinefunction(handler):
            return await handler(*args)
        return handler(*args)
    except Exception as e:
        route_path = route_info.get("path") if route_info else None
        method = route_info.get("method") if route_info else None
        raise HandlerError(
            message=f"Handler execution failed: {e!s}",
            route_path=route_path,
            method=method,
            original_error=e,
        )
