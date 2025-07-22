import logging
import sys
from typing import Optional, Dict, Any
import json
from datetime import datetime


class ArtanisFormatter(logging.Formatter):
    """Custom formatter for Artanis framework with structured output."""
    
    def __init__(self, use_json: bool = False):
        self.use_json = use_json
        if use_json:
            super().__init__()
        else:
            super().__init__(
                '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def format(self, record):
        if self.use_json:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'method'):
                log_entry['method'] = record.method
            if hasattr(record, 'path'):
                log_entry['path'] = record.path
            if hasattr(record, 'status_code'):
                log_entry['status_code'] = record.status_code
            if hasattr(record, 'response_time'):
                log_entry['response_time'] = record.response_time
                
            return json.dumps(log_entry)
        else:
            return super().format(record)


class ArtanisLogger:
    """Artanis logging configuration and utilities."""
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    @classmethod
    def configure(cls, 
                  level: str = "INFO",
                  format_type: str = "text",
                  output: Optional[str] = None) -> None:
        """Configure logging for Artanis framework.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: Output format ("text" or "json")
            output: Output destination (None for stdout, or file path)
        """
        if cls._configured:
            return
            
        root_logger = logging.getLogger('artanis')
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create handler
        if output:
            handler = logging.FileHandler(output)
        else:
            handler = logging.StreamHandler(sys.stdout)
        
        # Set formatter
        formatter = ArtanisFormatter(use_json=(format_type == "json"))
        handler.setFormatter(formatter)
        
        root_logger.addHandler(handler)
        root_logger.propagate = False
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance for the given name."""
        if not cls._configured:
            cls.configure()
            
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(f'artanis.{name}')
            
        return cls._loggers[name]


# Default logger instances
logger = ArtanisLogger.get_logger('core')
middleware_logger = ArtanisLogger.get_logger('middleware')
request_logger = ArtanisLogger.get_logger('request')


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or request_logger
    
    async def __call__(self, request, response, next_middleware):
        import time
        import uuid
        
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Log request
        start_time = time.time()
        self.logger.info(
            "Request started",
            extra={
                'request_id': request_id,
                'method': request.scope.get('method'),
                'path': request.scope.get('path'),
                'remote_addr': request.scope.get('client', ['unknown'])[0]
            }
        )
        
        # Add request_id to request for other middleware
        request.request_id = request_id
        
        try:
            # Execute next middleware
            await next_middleware()
            
            # Log successful response
            response_time = round((time.time() - start_time) * 1000, 2)
            self.logger.info(
                "Request completed",
                extra={
                    'request_id': request_id,
                    'method': request.scope.get('method'),
                    'path': request.scope.get('path'),
                    'status_code': response.status,
                    'response_time': f"{response_time}ms"
                }
            )
            
        except Exception as e:
            # Log error response
            response_time = round((time.time() - start_time) * 1000, 2)
            self.logger.error(
                "Request failed",
                extra={
                    'request_id': request_id,
                    'method': request.scope.get('method'),
                    'path': request.scope.get('path'),
                    'error': str(e),
                    'response_time': f"{response_time}ms"
                }
            )
            raise