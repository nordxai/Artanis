# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https.keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https.semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-01

### Added

- Initial release of Artanis.
- Core `App` class for creating applications.
- Routing system with support for GET, POST, PUT, DELETE, PATCH, OPTIONS, and ALL methods.
- Support for path parameters (e.g., `/users/{user_id}`).
- `Router` class for modular, nestable subrouters.
- Parameterized subrouting.
- Express-style middleware system with `app.use()`.
- Path-based middleware.
- Built-in security middleware for CORS, CSP, HSTS, and security headers.
- Rate limiting middleware.
- Comprehensive, structured exception handling system.
- Automatic JSON serialization for responses.
- `Request` object with methods for accessing body and JSON data.
- Fully type-annotated codebase with `py.typed` support.
- Structured logging system with text and JSON formatters.
- Automatic request/response logging.
- Detailed `README.md` with quick start and API reference.
- Development environment setup with `pyproject.toml` and optional dependencies.
- Code quality tools setup (Ruff, MyPy, pre-commit).
- Comprehensive test suite with pytest.
- Version management via `_version.py`.
