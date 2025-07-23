"""Artanis logging system with structured output and request tracking.

Provides comprehensive logging capabilities including structured JSON output,
request tracking with unique IDs, and middleware for automatic request/response
logging.
"""

import logging
import sys
from typing import Optional, Dict, Any, TextIO, Union
import json
from datetime import datetime


class ArtanisFormatter(logging.Formatter):
    """Custom formatter for Artanis framework with structured output.
    
    Supports both human-readable text format for development and structured
    JSON format for production environments. JSON format includes additional
    metadata fields for better log analysis.
    
    Args:
        use_json: If True, output logs in JSON format; otherwise use text format
    
    Attributes:
        use_json: Whether to use JSON format for output
    """
    
    def __init__(self, use_json: bool = False) -> None:
        self.use_json = use_json
        if use_json:
            super().__init__()
        else:
            super().__init__(
                '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as either JSON or text.
        
        For JSON format, creates a structured log entry with timestamp,
        level, logger name, message, and optional extra fields like
        request_id, method, path, etc.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted log message as string
        """
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
    """Artanis logging configuration and utilities.
    
    Provides centralized logging configuration for the Artanis framework
    with support for different output formats, log levels, and destinations.
    Manages logger instances and ensures consistent configuration across
    the application.
    
    Class Attributes:
        _loggers: Cache of created logger instances
        _configured: Flag to prevent duplicate configuration
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured: bool = False
    
    @classmethod
    def configure(cls, 
                  level: str = "INFO",
                  format_type: str = "text",
                  output: Optional[str] = None) -> None:
        """Configure logging for Artanis framework.
        
        Sets up the root 'artanis' logger with the specified configuration.
        This method should be called once at application startup to establish
        consistent logging behavior across all framework components.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: Output format ("text" for development, "json" for production)
            output: Output destination (None for stdout, or file path for file output)
            
        Note:
            Configuration is applied only once. Subsequent calls are ignored
            to prevent configuration conflicts.
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
        """Get a logger instance for the given name.
        
        Creates and caches logger instances with consistent naming convention.
        If logging hasn't been configured yet, applies default configuration.
        
        Args:
            name: Logger name (will be prefixed with 'artanis.')
            
        Returns:
            Configured logger instance
            
        Example:
            ```python
            logger = ArtanisLogger.get_logger('auth')
            logger.info('User authenticated successfully')
            ```
        """
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
    """Middleware for logging HTTP requests and responses.
    
    Automatically logs incoming requests and outgoing responses with timing
    information, unique request IDs for tracing, and structured metadata.
    Integrates seamlessly with the Artanis middleware system.
    
    Args:
        logger: Custom logger instance (defaults to request_logger)
        
    Attributes:
        logger: Logger instance used for request/response logging
        
    Example:
        ```python
        # Use default logger
        app.use(RequestLoggingMiddleware())
        
        # Use custom logger
        custom_logger = ArtanisLogger.get_logger('api')
        app.use(RequestLoggingMiddleware(custom_logger))
        ```
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or request_logger
    
    async def __call__(self, request: Any, response: Any, next_middleware: Any) -> None:
        """Process request through middleware chain with logging.
        
        Logs request start, generates unique request ID for tracing, measures
        response time, and logs completion or failure. The request ID is added
        to the request object for use by subsequent middleware.
        
        Args:
            request: Request object from Artanis framework
            response: Response object from Artanis framework  
            next_middleware: Next middleware function in the chain
            
        Raises:
            Exception: Re-raises any exceptions from downstream middleware
        """
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