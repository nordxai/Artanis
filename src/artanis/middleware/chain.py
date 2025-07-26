"""Middleware chain execution for the Artanis framework.

Provides classes for executing middleware in sequence with Express.js-style
next() function calls and comprehensive error handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from .response import Response


class MiddlewareChain:
    """Executes middleware chain with Express-style next() function.

    Manages the execution of middleware functions in sequence, providing
    each middleware with a next() function to continue the chain. Follows
    the Express.js middleware pattern.

    Args:
        middleware_list: List of middleware functions to execute
        final_handler: Final handler function to call after all middleware

    Attributes:
        middleware_list: List of middleware functions
        final_handler: Final handler function
    """

    def __init__(
        self, middleware_list: list[Callable], final_handler: Callable
    ) -> None:
        self.middleware_list = middleware_list
        self.final_handler = final_handler

    async def execute(self, request: Any, response: Response) -> Any:
        """Execute the middleware chain.

        Starts the middleware chain execution. If no middleware is present,
        calls the final handler directly.

        Args:
            request: Request object
            response: Response object

        Returns:
            Result from the final handler or middleware chain
        """
        if not self.middleware_list:
            # No middleware, call final handler directly
            return await self.final_handler(request)

        return await self._create_next(0)(request, response)

    def _create_next(self, index: int) -> Callable[[Any, Response], Awaitable[Any]]:
        """Create the next function for middleware at given index.

        Creates a closure that represents the next middleware in the chain.
        This implements the Express.js-style next() function pattern.

        Args:
            index: Index of the current middleware in the chain

        Returns:
            Async function that executes the next middleware or final handler
        """

        async def next_function(req: Any, resp: Response) -> Any:
            if index >= len(self.middleware_list):
                # End of middleware chain, call final handler
                return await self.final_handler(req)

            # Get current middleware
            current_middleware = self.middleware_list[index]

            # Create next function for the next middleware in chain
            async def next_in_chain() -> Any:
                return await self._create_next(index + 1)(req, resp)

            # Call current middleware with request, response, and next function
            return await current_middleware(req, resp, next_in_chain)

        return next_function


class MiddlewareExecutor:
    """High-level middleware execution coordinator.

    Coordinates the execution of middleware chains by combining global
    and path-specific middleware, handling errors, and managing the
    overall middleware execution flow.

    Args:
        middleware_manager: MiddlewareManager instance for middleware retrieval

    Attributes:
        middleware_manager: Manager for accessing registered middleware
    """

    def __init__(self, middleware_manager: Any) -> None:
        self.middleware_manager = middleware_manager

    async def execute_for_request(
        self,
        request: Any,
        response: Response,
        request_path: str,
        final_handler: Callable,
    ) -> Any:
        """Execute complete middleware chain for a request.

        Retrieves all applicable middleware for the request path and
        executes them in a chain with the final handler. Handles exceptions
        by setting appropriate error responses.

        Args:
            request: Request object
            response: Response object
            request_path: Path to match middleware against
            final_handler: Final handler to execute after middleware

        Returns:
            Result from the middleware chain execution

        Raises:
            Exception: Re-raises any unhandled exceptions from middleware
        """

        # Get all applicable middleware for this path
        all_middleware = self.middleware_manager.get_all_middleware_for_path(
            request_path
        )

        # Create and execute chain
        chain = MiddlewareChain(all_middleware, final_handler)

        try:
            return await chain.execute(request, response)
        except Exception:
            # If middleware throws an exception and no middleware caught it,
            # set error response
            if not response.is_finished():
                response.set_status(500)
                response.json({"error": "Internal Server Error"})
                response.finish()
            raise

    async def execute_with_error_handling(
        self,
        request: Any,
        response: Response,
        request_path: str,
        final_handler: Callable,
    ) -> Any:
        """Execute middleware chain with built-in error handling.

        Executes the middleware chain and provides comprehensive error handling,
        ensuring that a proper error response is always sent even if middleware
        or handlers throw unhandled exceptions.

        Args:
            request: Request object
            response: Response object
            request_path: Path to match middleware against
            final_handler: Final handler to execute after middleware

        Returns:
            Response object (either from successful execution or error handling)
        """
        try:
            return await self.execute_for_request(
                request, response, request_path, final_handler
            )
        except Exception:
            # Ensure response is set for any unhandled errors
            if not response.is_finished():
                response.set_status(500)
                response.json({"error": "Internal Server Error"})
                response.finish()
            # Log error in real implementation
            # logger.error(f"Middleware chain error: {e}")
            return response
