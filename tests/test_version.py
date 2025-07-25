"""
Test suite for version management functionality.

Tests the version module and ensures proper version information
is available throughout the framework.
"""

import pytest
import re
from artanis import __version__, VERSION, version_info, get_version, get_version_info
from artanis._version import __version__ as version_module_version


class TestVersionManagement:
    """Test version management system."""
    
    def test_version_string_format(self):
        """Test that version string follows semantic versioning format."""
        # Test that version is a string
        assert isinstance(__version__, str)
        
        # Test semantic version format (major.minor.patch)
        version_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(version_pattern, __version__)
        
    def test_version_consistency(self):
        """Test that version is consistent across all access methods."""
        # Version from main module should match version module
        assert __version__ == version_module_version
        
        # get_version() should return same as __version__
        assert get_version() == __version__
        
        # Version should be "0.1.0" for initial release
        assert __version__ == "0.1.0"
        
    def test_version_tuple(self):
        """Test version tuple functionality."""
        # VERSION should be a tuple of 3 integers
        assert isinstance(VERSION, tuple)
        assert len(VERSION) == 3
        assert all(isinstance(v, int) for v in VERSION)
        
        # version_info should be same as VERSION
        assert version_info == VERSION
        
        # get_version_info() should return same tuple
        assert get_version_info() == VERSION
        
        # VERSION should match string version
        assert VERSION == (0, 1, 0)
        
    def test_version_components(self):
        """Test individual version components."""
        major, minor, patch = VERSION
        
        # Test components are non-negative integers
        assert isinstance(major, int) and major >= 0
        assert isinstance(minor, int) and minor >= 0
        assert isinstance(patch, int) and patch >= 0
        
        # Test that string version matches tuple
        expected_version = f"{major}.{minor}.{patch}"
        assert __version__ == expected_version
        
    def test_version_module_imports(self):
        """Test that version module imports work correctly."""
        from artanis._version import __version__, VERSION, version_info, get_version, get_version_info
        
        # All imports should be available
        assert __version__ is not None
        assert VERSION is not None
        assert version_info is not None
        assert callable(get_version)
        assert callable(get_version_info)
        
    def test_version_functions(self):
        """Test version getter functions."""
        # get_version should return string
        version_str = get_version()
        assert isinstance(version_str, str)
        assert version_str == __version__
        
        # get_version_info should return tuple
        version_tuple = get_version_info()
        assert isinstance(version_tuple, tuple)
        assert version_tuple == VERSION
        
    def test_version_public_api(self):
        """Test that version is properly exposed in public API."""
        # Test that artanis module has __version__
        import artanis
        assert hasattr(artanis, '__version__')
        assert artanis.__version__ == __version__
        
        # Test that other version attributes are available
        assert hasattr(artanis, 'VERSION')
        assert hasattr(artanis, 'version_info')
        assert hasattr(artanis, 'get_version')
        assert hasattr(artanis, 'get_version_info')
        
    def test_version_immutability(self):
        """Test that version components are properly structured."""
        # VERSION should be a tuple (immutable)
        assert isinstance(VERSION, tuple)
        
        # Should not be able to modify VERSION (will raise TypeError)
        with pytest.raises(TypeError):
            VERSION[0] = 999
            
    def test_version_docstrings(self):
        """Test that version functions have proper documentation."""
        # Test that functions have docstrings
        assert get_version.__doc__ is not None
        assert get_version_info.__doc__ is not None
        
        # Test that docstrings contain useful information
        assert "version string" in get_version.__doc__.lower()
        assert "tuple" in get_version_info.__doc__.lower()
        
    def test_semantic_versioning_compliance(self):
        """Test that version follows semantic versioning principles."""
        major, minor, patch = VERSION
        
        # For 0.1.0 release
        assert major == 0  # Pre-1.0 release
        assert minor == 1  # Minor version
        assert patch == 0  # Initial patch level
        
    def test_version_string_parsing(self):
        """Test that version string can be parsed correctly."""
        parts = __version__.split('.')
        assert len(parts) == 3
        
        # Each part should be a valid integer
        major_str, minor_str, patch_str = parts
        assert major_str.isdigit()
        assert minor_str.isdigit() 
        assert patch_str.isdigit()
        
        # Should match VERSION tuple
        assert int(major_str) == VERSION[0]
        assert int(minor_str) == VERSION[1]
        assert int(patch_str) == VERSION[2]


class TestVersionIntegration:
    """Test version integration with framework components."""
    
    def test_app_version_access(self):
        """Test that App class can access version information."""
        from artanis import App
        
        app = App()
        
        # Should be able to access version through artanis module
        import artanis
        assert artanis.__version__ == "0.1.0"
        
    def test_version_in_error_responses(self):
        """Test that version info doesn't interfere with error handling."""
        from artanis import App
        
        app = App()
        
        # Version should not affect route registration
        async def test_handler():
            return {'version': get_version()}
        
        app.get('/test', test_handler)
            
        # Should have one route registered
        assert len(app.routes) == 1
        
    def test_logging_with_version(self):
        """Test that version doesn't interfere with logging."""
        from artanis import App, logger
        
        app = App()
        
        # Should be able to log version information
        logger.info(f"Artanis version: {__version__}")
        
        # Logger should still work normally
        assert app.logger is not None
        
    def test_middleware_version_access(self):
        """Test version access in middleware context."""
        from artanis import App
        
        app = App()
        
        async def version_middleware(request, next_handler):
            # Should be able to access version in middleware
            version = get_version()
            response = await next_handler(request)
            return response
            
        app.use(version_middleware)
        
        # Middleware should be registered without issues
        assert len(app.global_middleware) == 2  # Request logging + version middleware