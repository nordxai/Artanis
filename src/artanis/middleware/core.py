import re
from typing import List, Dict, Callable, Any


class MiddlewareManager:
    """Manages global and path-based middleware registration and retrieval"""
    
    def __init__(self):
        self.global_middleware = []
        self.path_middleware = {}
    
    def add_global(self, middleware_func: Callable):
        """Add global middleware that runs on all routes"""
        self.global_middleware.append(middleware_func)
    
    def add_path(self, path: str, middleware_func: Callable):
        """Add path-based middleware that runs on specific routes"""
        if path not in self.path_middleware:
            self.path_middleware[path] = []
        self.path_middleware[path].append(middleware_func)
    
    def find_matching_middleware(self, request_path: str) -> List[Callable]:
        """Find all path middleware that match the request path"""
        matching_middleware = []
        
        for pattern, middleware_list in self.path_middleware.items():
            if self._path_matches(pattern, request_path):
                matching_middleware.extend(middleware_list)
        
        return matching_middleware
    
    def _path_matches(self, pattern: str, request_path: str) -> bool:
        """Check if a path pattern matches the request path"""
        # Convert path pattern to regex
        regex_pattern = self._compile_path_pattern(pattern)
        return bool(regex_pattern.match(request_path))
    
    def _compile_path_pattern(self, path: str) -> re.Pattern:
        """Compile path pattern to regex, handling parameters like {id}"""
        # Escape special regex characters except for our parameter syntax
        pattern = re.escape(path)
        
        # Replace escaped parameter syntax with regex groups
        # \{param\} becomes (?P<param>[^/]+)
        pattern = pattern.replace(r'\{', '(?P<').replace(r'\}', r'>[^/]+)')
        
        # Handle nested paths - /api should match /api/users
        if not pattern.endswith('$'):
            pattern = f"^{pattern}(?:/.*)?$"
        else:
            pattern = f"^{pattern}"
        
        return re.compile(pattern)
    
    def get_all_middleware_for_path(self, request_path: str) -> List[Callable]:
        """Get combined global and path middleware for a specific path"""
        path_middleware = self.find_matching_middleware(request_path)
        return self.global_middleware + path_middleware
    
    def clear(self):
        """Clear all middleware (useful for testing)"""
        self.global_middleware.clear()
        self.path_middleware.clear()
    
    def middleware_count(self) -> Dict[str, int]:
        """Get count of middleware for debugging"""
        path_count = sum(len(middleware_list) for middleware_list in self.path_middleware.values())
        return {
            "global": len(self.global_middleware),
            "path": path_count,
            "total": len(self.global_middleware) + path_count
        }