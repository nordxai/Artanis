"""Tests for Artanis security middleware.

This module contains comprehensive tests for all security middleware
components including CORS, CSP, HSTS, rate limiting, and security headers.
"""

import time
from unittest.mock import Mock

import pytest

from artanis.exceptions import RateLimitError
from artanis.middleware.response import Response
from artanis.middleware.security import (
    CORSMiddleware,
    CSPMiddleware,
    HSTSMiddleware,
    RateLimitMiddleware,
    SecurityConfig,
    SecurityHeadersMiddleware,
)


class TestSecurityConfig:
    """Test SecurityConfig class."""

    def test_default_configuration(self):
        """Test SecurityConfig with default values."""
        config = SecurityConfig()

        assert config.cors_enabled is True
        assert config.cors_allow_origins == "*"
        assert config.cors_allow_methods == ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        assert config.cors_allow_headers == ["Content-Type", "Authorization"]
        assert config.cors_allow_credentials is False
        assert config.cors_max_age == 86400

        assert config.csp_enabled is True
        assert "default-src" in config.csp_directives
        assert config.csp_directives["default-src"] == "'self'"

        assert config.hsts_enabled is True
        assert config.hsts_max_age == 31536000
        assert config.hsts_include_subdomains is True

        assert config.security_headers_enabled is True

        assert config.rate_limit_enabled is True
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 3600

    def test_custom_configuration(self):
        """Test SecurityConfig with custom values."""
        custom_csp = {"default-src": "'none'", "script-src": "'self'"}

        config = SecurityConfig(
            cors_enabled=False,
            cors_allow_origins=["https://example.com"],
            cors_allow_credentials=True,
            csp_directives=custom_csp,
            hsts_max_age=86400,
            rate_limit_requests=50,
        )

        assert config.cors_enabled is False
        assert config.cors_allow_origins == ["https://example.com"]
        assert config.cors_allow_credentials is True
        assert config.csp_directives == custom_csp
        assert config.hsts_max_age == 86400
        assert config.rate_limit_requests == 50


class TestCORSMiddleware:
    """Test CORS middleware functionality."""

    def test_middleware_initialization(self):
        """Test CORS middleware initialization."""
        cors = CORSMiddleware()

        assert cors.allow_origins == "*"
        assert cors.allow_methods == ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        assert cors.allow_headers == ["Content-Type", "Authorization"]
        assert cors.allow_credentials is False
        assert cors.max_age == 86400

    def test_custom_initialization(self):
        """Test CORS middleware with custom values."""
        cors = CORSMiddleware(
            allow_origins=["https://example.com"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
            allow_credentials=True,
            max_age=3600,
        )

        assert cors.allow_origins == ["https://example.com"]
        assert cors.allow_methods == ["GET", "POST"]
        assert cors.allow_headers == ["Content-Type"]
        assert cors.allow_credentials is True
        assert cors.max_age == 3600

    def test_preflight_request_handling(self):
        """Test CORS preflight OPTIONS request."""
        cors = CORSMiddleware()

        # Mock preflight request
        request = Mock()
        request.method = "OPTIONS"
        request.headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }

        def next_func(req):
            return "should not be called"

        response = cors(request, next_func)

        assert isinstance(response, Response)
        assert response.status == 204
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Max-Age" in response.headers

    def test_regular_request_with_wildcard_origin(self):
        """Test CORS with regular request and wildcard origin."""
        cors = CORSMiddleware()

        request = Mock()
        request.method = "GET"
        request.headers = {"Origin": "https://example.com"}

        def next_func(req):
            return "response content"

        response = cors(request, next_func)

        assert isinstance(response, Response)
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Expose-Headers" in response.headers

    def test_regular_request_with_specific_origins(self):
        """Test CORS with specific allowed origins."""
        cors = CORSMiddleware(allow_origins=["https://example.com", "https://test.com"])

        request = Mock()
        request.method = "GET"
        request.headers = {"Origin": "https://example.com"}

        def next_func(req):
            response = Response()
            response.body = "test response"
            return response

        response = cors(request, next_func)

        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"

    def test_credentials_with_specific_origin(self):
        """Test CORS with credentials enabled."""
        cors = CORSMiddleware(
            allow_origins=["https://example.com"], allow_credentials=True
        )

        request = Mock()
        request.method = "GET"
        request.headers = {"Origin": "https://example.com"}

        def next_func(req):
            response = Response()
            response.body = "test response"
            return response

        response = cors(request, next_func)

        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

    def test_origin_not_allowed(self):
        """Test CORS with origin not in allowed list."""
        cors = CORSMiddleware(allow_origins=["https://example.com"])

        request = Mock()
        request.method = "GET"
        request.headers = {"Origin": "https://malicious.com"}

        def next_func(req):
            response = Response()
            response.body = "test response"
            return response

        response = cors(request, next_func)

        # Should not add CORS headers for disallowed origin
        assert "Access-Control-Allow-Origin" not in response.headers


class TestCSPMiddleware:
    """Test Content Security Policy middleware."""

    def test_middleware_initialization(self):
        """Test CSP middleware initialization."""
        csp = CSPMiddleware()

        assert "default-src" in csp.directives
        assert csp.directives["default-src"] == "'self'"
        assert csp.report_only is False
        assert csp.report_uri is None

    def test_custom_directives(self):
        """Test CSP middleware with custom directives."""
        custom_directives = {
            "default-src": "'none'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self'",
        }

        csp = CSPMiddleware(directives=custom_directives, report_only=True)

        assert csp.directives == custom_directives
        assert csp.report_only is True

    def test_csp_header_generation(self):
        """Test CSP header generation."""
        directives = {
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self'",
        }

        csp = CSPMiddleware(directives=directives)

        request = Mock()
        request.method = "GET"

        def next_func(req):
            return "response content"

        response = csp(request, next_func)

        assert isinstance(response, Response)
        assert "Content-Security-Policy" in response.headers

        policy = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in policy
        assert "script-src 'self' 'unsafe-inline'" in policy
        assert "style-src 'self'" in policy

    def test_csp_report_only_mode(self):
        """Test CSP in report-only mode."""
        csp = CSPMiddleware(report_only=True)

        request = Mock()

        def next_func(req):
            response = Response()
            response.body = "test"
            return response

        response = csp(request, next_func)

        assert "Content-Security-Policy-Report-Only" in response.headers
        assert "Content-Security-Policy" not in response.headers

    def test_csp_with_report_uri(self):
        """Test CSP with report URI."""
        csp = CSPMiddleware(report_uri="/csp-report")

        request = Mock()

        def next_func(req):
            response = Response()
            response.body = "test"
            return response

        response = csp(request, next_func)

        policy = response.headers["Content-Security-Policy"]
        assert "report-uri /csp-report" in policy


class TestHSTSMiddleware:
    """Test HTTP Strict Transport Security middleware."""

    def test_middleware_initialization(self):
        """Test HSTS middleware initialization."""
        hsts = HSTSMiddleware()

        assert hsts.max_age == 31536000  # 1 year
        assert hsts.include_subdomains is True
        assert hsts.preload is False

    def test_custom_initialization(self):
        """Test HSTS middleware with custom values."""
        hsts = HSTSMiddleware(max_age=86400, include_subdomains=False, preload=True)

        assert hsts.max_age == 86400
        assert hsts.include_subdomains is False
        assert hsts.preload is True

    def test_hsts_header_for_https_request(self):
        """Test HSTS header for HTTPS request."""
        hsts = HSTSMiddleware(max_age=86400, include_subdomains=True, preload=True)

        request = Mock()
        request.scheme = "https"
        request.headers = {}

        def next_func(req):
            return "response content"

        response = hsts(request, next_func)

        assert isinstance(response, Response)
        assert "Strict-Transport-Security" in response.headers

        hsts_value = response.headers["Strict-Transport-Security"]
        assert "max-age=86400" in hsts_value
        assert "includeSubDomains" in hsts_value
        assert "preload" in hsts_value

    def test_hsts_with_forwarded_proto_header(self):
        """Test HSTS detection via X-Forwarded-Proto header."""
        hsts = HSTSMiddleware()

        request = Mock()
        request.scheme = "http"  # Original scheme is HTTP
        request.headers = {"X-Forwarded-Proto": "https"}  # But forwarded as HTTPS

        def next_func(req):
            response = Response()
            response.body = "test"
            return response

        response = hsts(request, next_func)

        assert "Strict-Transport-Security" in response.headers

    def test_no_hsts_header_for_http_request(self):
        """Test no HSTS header for HTTP request."""
        hsts = HSTSMiddleware()

        request = Mock()
        request.scheme = "http"
        request.headers = {}

        def next_func(req):
            response = Response()
            response.body = "test"
            return response

        response = hsts(request, next_func)

        assert "Strict-Transport-Security" not in response.headers


class TestSecurityHeadersMiddleware:
    """Test general security headers middleware."""

    def test_middleware_initialization(self):
        """Test security headers middleware initialization."""
        security = SecurityHeadersMiddleware()

        assert security.x_frame_options == "DENY"
        assert security.x_content_type_options == "nosniff"
        assert security.x_xss_protection == "1; mode=block"
        assert security.referrer_policy == "strict-origin-when-cross-origin"
        assert security.permissions_policy is None

    def test_custom_headers(self):
        """Test security headers with custom values."""
        security = SecurityHeadersMiddleware(
            x_frame_options="SAMEORIGIN",
            x_content_type_options="nosniff",
            x_xss_protection="0",
            referrer_policy="no-referrer",
            permissions_policy="geolocation=(), microphone=()",
        )

        assert security.x_frame_options == "SAMEORIGIN"
        assert security.x_xss_protection == "0"
        assert security.referrer_policy == "no-referrer"
        assert security.permissions_policy == "geolocation=(), microphone=()"

    def test_security_headers_added(self):
        """Test that security headers are added to response."""
        security = SecurityHeadersMiddleware(
            permissions_policy="geolocation=(), microphone=()"
        )

        request = Mock()

        def next_func(req):
            return "response content"

        response = security(request, next_func)

        assert isinstance(response, Response)
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=()"

    def test_disabled_headers(self):
        """Test that None values disable headers."""
        security = SecurityHeadersMiddleware(
            x_frame_options=None, x_xss_protection=None
        )

        request = Mock()

        def next_func(req):
            response = Response()
            response.body = "test"
            return response

        response = security(request, next_func)

        assert "X-Frame-Options" not in response.headers
        assert "X-XSS-Protection" not in response.headers
        assert "X-Content-Type-Options" in response.headers  # Still enabled
        assert "Referrer-Policy" in response.headers  # Still enabled


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def test_middleware_initialization(self):
        """Test rate limit middleware initialization."""
        rate_limit = RateLimitMiddleware()

        assert rate_limit.requests_per_window == 100
        assert rate_limit.window_seconds == 3600
        assert rate_limit.storage == "memory"
        assert rate_limit.skip_successful_requests is False

    def test_custom_initialization(self):
        """Test rate limit middleware with custom values."""

        def custom_key_func(request):
            return f"user:{request.user_id}"

        rate_limit = RateLimitMiddleware(
            requests_per_window=50,
            window_seconds=300,
            key_function=custom_key_func,
            skip_successful_requests=True,
        )

        assert rate_limit.requests_per_window == 50
        assert rate_limit.window_seconds == 300
        assert rate_limit.key_function == custom_key_func
        assert rate_limit.skip_successful_requests is True

    def test_default_key_function(self):
        """Test default key function using IP address."""
        rate_limit = RateLimitMiddleware()

        # Test with X-Forwarded-For header
        request = Mock()
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}

        key = rate_limit.key_function(request)
        assert key == "rate_limit:192.168.1.1"

        # Test with X-Real-IP header
        request.headers = {"X-Real-IP": "192.168.1.2"}
        key = rate_limit.key_function(request)
        assert key == "rate_limit:192.168.1.2"

        # Test with client attribute
        request.headers = {}
        request.client = {"host": "192.168.1.3"}
        key = rate_limit.key_function(request)
        assert key == "rate_limit:192.168.1.3"

    def test_rate_limit_allows_initial_requests(self):
        """Test that initial requests are allowed."""
        rate_limit = RateLimitMiddleware(requests_per_window=5, window_seconds=60)

        request = Mock()
        request.headers = {}
        request.client = {"host": "192.168.1.1"}

        def next_func(req):
            response = Response()
            response.body = "success"
            response.status = 200
            return response

        # First few requests should be allowed
        for i in range(5):
            response = rate_limit(request, next_func)
            assert isinstance(response, Response)
            assert response.status == 200

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers

            assert response.headers["X-RateLimit-Limit"] == "5"
            assert int(response.headers["X-RateLimit-Remaining"]) == 4 - i

    def test_rate_limit_blocks_excess_requests(self):
        """Test that rate limit blocks excess requests."""
        rate_limit = RateLimitMiddleware(requests_per_window=2, window_seconds=60)

        request = Mock()
        request.headers = {}
        request.client = {"host": "192.168.1.1"}

        def next_func(req):
            response = Response()
            response.body = "success"
            response.status = 200
            return response

        # Allow first 2 requests
        for _ in range(2):
            response = rate_limit(request, next_func)
            assert response.status == 200

        # Third request should be rate limited
        with pytest.raises(RateLimitError) as exc_info:
            rate_limit(request, next_func)

        error = exc_info.value
        assert "Rate limit exceeded" in str(error)
        assert error.details["limit"] == 2
        assert error.details["window"] == 60
        assert "retry_after" in error.details

    def test_rate_limit_with_skip_successful_requests(self):
        """Test rate limiting that only counts failed requests."""
        rate_limit = RateLimitMiddleware(
            requests_per_window=2, window_seconds=60, skip_successful_requests=True
        )

        request = Mock()
        request.headers = {}
        request.client = {"host": "192.168.1.1"}

        def success_func(req):
            response = Response()
            response.body = "success"
            response.status = 200
            return response

        def error_func(req):
            response = Response()
            response.body = "error"
            response.status = 400
            return response

        # Successful requests shouldn't count
        for _ in range(5):
            response = rate_limit(request, success_func)
            assert response.status == 200

        # Failed requests should count
        response1 = rate_limit(request, error_func)
        assert response1.status == 400

        response2 = rate_limit(request, error_func)
        assert response2.status == 400

        # Third failed request should be rate limited
        with pytest.raises(RateLimitError):
            rate_limit(request, error_func)

    def test_rate_limit_window_expiry(self):
        """Test that rate limit window resets after expiry."""
        rate_limit = RateLimitMiddleware(requests_per_window=1, window_seconds=1)

        request = Mock()
        request.headers = {}
        request.client = {"host": "192.168.1.1"}

        def next_func(req):
            response = Response()
            response.body = "success"
            response.status = 200
            return response

        # First request should be allowed
        response = rate_limit(request, next_func)
        assert response.status == 200

        # Second request should be rate limited
        with pytest.raises(RateLimitError):
            rate_limit(request, next_func)

        # Wait for window to expire
        time.sleep(1.1)

        # Request should be allowed again
        response = rate_limit(request, next_func)
        assert response.status == 200

    def test_rate_limit_different_keys(self):
        """Test that different keys have separate limits."""
        rate_limit = RateLimitMiddleware(requests_per_window=1, window_seconds=60)

        request1 = Mock()
        request1.headers = {}
        request1.client = {"host": "192.168.1.1"}

        request2 = Mock()
        request2.headers = {}
        request2.client = {"host": "192.168.1.2"}

        def next_func(req):
            response = Response()
            response.body = "success"
            response.status = 200
            return response

        # Both requests should be allowed (different IPs)
        response1 = rate_limit(request1, next_func)
        assert response1.status == 200

        response2 = rate_limit(request2, next_func)
        assert response2.status == 200

        # Second request from first IP should be rate limited
        with pytest.raises(RateLimitError):
            rate_limit(request1, next_func)

        # Second request from second IP should also be rate limited (limit is 1)
        with pytest.raises(RateLimitError):
            rate_limit(request2, next_func)
