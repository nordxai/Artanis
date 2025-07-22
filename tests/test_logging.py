import pytest
import logging
import json
from unittest.mock import Mock, patch
from artanis import App
from artanis.logging import ArtanisLogger, ArtanisFormatter, RequestLoggingMiddleware


class TestArtanisLogger:
    def test_configure_default(self):
        """Test default logger configuration."""
        ArtanisLogger._configured = False
        ArtanisLogger.configure()
        
        logger = ArtanisLogger.get_logger('test')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'artanis.test'
        # Check parent logger level since child loggers inherit
        root_logger = logging.getLogger('artanis')
        assert root_logger.level == logging.INFO
    
    def test_configure_custom_level(self):
        """Test logger configuration with custom level."""
        ArtanisLogger._configured = False
        ArtanisLogger.configure(level="DEBUG")
        
        logger = ArtanisLogger.get_logger('test')
        # Check parent logger level since child loggers inherit
        root_logger = logging.getLogger('artanis')
        assert root_logger.level == logging.DEBUG
    
    def test_get_logger_caches_instances(self):
        """Test that get_logger returns cached instances."""
        ArtanisLogger._configured = False
        logger1 = ArtanisLogger.get_logger('test')
        logger2 = ArtanisLogger.get_logger('test')
        
        assert logger1 is logger2


class TestArtanisFormatter:
    def test_text_formatter(self):
        """Test text formatter output."""
        formatter = ArtanisFormatter(use_json=False)
        record = logging.LogRecord(
            name='artanis.test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert 'INFO in artanis.test: Test message' in formatted
    
    def test_json_formatter(self):
        """Test JSON formatter output."""
        formatter = ArtanisFormatter(use_json=True)
        record = logging.LogRecord(
            name='artanis.test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.funcName = 'test_func'
        record.module = 'test_module'
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data['level'] == 'INFO'
        assert log_data['logger'] == 'artanis.test'
        assert log_data['message'] == 'Test message'
        assert log_data['function'] == 'test_func'
        assert log_data['module'] == 'test_module'
    
    def test_json_formatter_with_extra_fields(self):
        """Test JSON formatter with extra request fields."""
        formatter = ArtanisFormatter(use_json=True)
        record = logging.LogRecord(
            name='artanis.request',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Request completed',
            args=(),
            exc_info=None
        )
        record.funcName = 'handler'
        record.module = 'request'
        record.request_id = 'abc123'
        record.method = 'GET'
        record.path = '/test'
        record.status_code = 200
        record.response_time = '50.5ms'
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data['request_id'] == 'abc123'
        assert log_data['method'] == 'GET'
        assert log_data['path'] == '/test'
        assert log_data['status_code'] == 200
        assert log_data['response_time'] == '50.5ms'


@pytest.mark.asyncio
class TestRequestLoggingMiddleware:
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        middleware = RequestLoggingMiddleware()
        assert hasattr(middleware, 'logger')
        assert isinstance(middleware.logger, logging.Logger)
    
    def test_middleware_with_custom_logger(self):
        """Test middleware with custom logger."""
        custom_logger = logging.getLogger('custom')
        middleware = RequestLoggingMiddleware(logger=custom_logger)
        assert middleware.logger is custom_logger
    
    async def test_middleware_execution(self):
        """Test middleware request/response logging."""
        # Create mock request and response
        mock_request = Mock()
        mock_request.scope = {
            'method': 'GET',
            'path': '/test',
            'client': ['127.0.0.1', 8000]
        }
        
        mock_response = Mock()
        mock_response.status = 200
        
        # Create middleware with mock logger
        with patch('artanis.logging.request_logger') as mock_logger:
            middleware = RequestLoggingMiddleware(logger=mock_logger)
            
            # Mock next middleware
            next_called = False
            async def mock_next():
                nonlocal next_called
                next_called = True
            
            # Execute middleware
            await middleware(mock_request, mock_response, mock_next)
            
            # Verify next was called
            assert next_called
            
            # Verify logging calls
            assert mock_logger.info.call_count == 2  # Request start and completion
            
            # Check first call (request start)
            start_call = mock_logger.info.call_args_list[0]
            assert start_call[0][0] == "Request started"
            assert 'method' in start_call[1]['extra']
            assert 'path' in start_call[1]['extra']
            assert 'request_id' in start_call[1]['extra']
            
            # Check second call (request completion)
            complete_call = mock_logger.info.call_args_list[1]
            assert complete_call[0][0] == "Request completed"
            assert 'response_time' in complete_call[1]['extra']
    
    async def test_middleware_error_logging(self):
        """Test middleware error logging."""
        mock_request = Mock()
        mock_request.scope = {
            'method': 'POST',
            'path': '/error',
            'client': ['127.0.0.1', 8000]
        }
        
        mock_response = Mock()
        
        with patch('artanis.logging.request_logger') as mock_logger:
            middleware = RequestLoggingMiddleware(logger=mock_logger)
            
            # Mock next middleware that raises exception
            async def mock_next():
                raise Exception("Test error")
            
            # Execute middleware and expect exception
            with pytest.raises(Exception, match="Test error"):
                await middleware(mock_request, mock_response, mock_next)
            
            # Verify error logging
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args
            assert error_call[0][0] == "Request failed"
            assert 'error' in error_call[1]['extra']
            assert 'response_time' in error_call[1]['extra']


class TestAppLogging:
    def test_app_has_logger(self):
        """Test that App has logger attribute."""
        app = App(enable_request_logging=False)
        assert hasattr(app, 'logger')
        assert isinstance(app.logger, logging.Logger)
    
    def test_app_enables_request_logging_by_default(self):
        """Test that App enables request logging by default."""
        app = App()
        
        # Check that request logging middleware is added
        assert len(app.global_middleware) > 0
        assert any(isinstance(mw, RequestLoggingMiddleware) for mw in app.global_middleware)
    
    def test_app_can_disable_request_logging(self):
        """Test that App can disable request logging."""
        app = App(enable_request_logging=False)
        
        # Should not have request logging middleware
        request_logging_middleware = [mw for mw in app.global_middleware 
                                    if isinstance(mw, RequestLoggingMiddleware)]
        assert len(request_logging_middleware) == 0
    
    def test_route_registration_logging(self):
        """Test that route registration is logged."""
        with patch.object(logging.Logger, 'debug') as mock_debug:
            app = App(enable_request_logging=False)
            app.get("/test", lambda: {"test": True})
            
            mock_debug.assert_called_with("Registered GET route: /test")