from typing import List, Callable, Any
from .response import Response


class MiddlewareChain:
    """Executes middleware chain with Express-style next() function"""
    
    def __init__(self, middleware_list: List[Callable], final_handler: Callable):
        self.middleware_list = middleware_list
        self.final_handler = final_handler
    
    async def execute(self, request: Any, response: Response) -> Any:
        """Execute the middleware chain"""
        if not self.middleware_list:
            # No middleware, call final handler directly
            return await self.final_handler(request)
        
        return await self._create_next(0)(request, response)
    
    def _create_next(self, index: int) -> Callable:
        """Create the next function for middleware at given index"""
        
        async def next_function(req: Any, resp: Response) -> Any:
            if index >= len(self.middleware_list):
                # End of middleware chain, call final handler
                return await self.final_handler(req)
            
            # Get current middleware
            current_middleware = self.middleware_list[index]
            
            # Create next function for the next middleware in chain
            async def next_in_chain():
                return await self._create_next(index + 1)(req, resp)
            
            # Call current middleware with request, response, and next function
            return await current_middleware(req, resp, next_in_chain)
        
        return next_function


class MiddlewareExecutor:
    """High-level middleware execution coordinator"""
    
    def __init__(self, middleware_manager):
        self.middleware_manager = middleware_manager
    
    async def execute_for_request(self, request: Any, response: Response, 
                                 request_path: str, final_handler: Callable) -> Any:
        """Execute complete middleware chain for a request"""
        
        # Get all applicable middleware for this path
        all_middleware = self.middleware_manager.get_all_middleware_for_path(request_path)
        
        # Create and execute chain
        chain = MiddlewareChain(all_middleware, final_handler)
        
        try:
            return await chain.execute(request, response)
        except Exception as e:
            # If middleware throws an exception and no middleware caught it,
            # set error response
            if not response.is_finished():
                response.set_status(500)
                response.json({"error": "Internal Server Error"})
                response.finish()
            raise
    
    async def execute_with_error_handling(self, request: Any, response: Response,
                                        request_path: str, final_handler: Callable) -> Any:
        """Execute middleware chain with built-in error handling"""
        try:
            return await self.execute_for_request(request, response, request_path, final_handler)
        except Exception as e:
            # Ensure response is set for any unhandled errors
            if not response.is_finished():
                response.set_status(500)
                response.json({"error": "Internal Server Error"})
                response.finish()
            # Log error in real implementation
            # logger.error(f"Middleware chain error: {e}")
            return response