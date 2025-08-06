"""Artanis ASGI Web Framework.

A lightweight, fast ASGI web framework for Python with
middleware support, path parameters, and comprehensive logging.
"""

from __future__ import annotations

# Version information
from ._version import (
    VERSION as VERSION,
)
from ._version import (
    __version__ as __version__,
)
from ._version import (
    get_version as get_version,
)
from ._version import (
    get_version_info as get_version_info,
)
from ._version import (
    version_info as version_info,
)

# Core application and request classes
from .application import App as App

# Event system
from .events import (
    EventContext as EventContext,
)
from .events import (
    EventManager as EventManager,
)

# Exception classes
from .exceptions import (
    ArtanisException as ArtanisException,
)
from .exceptions import (
    AuthenticationError as AuthenticationError,
)
from .exceptions import (
    AuthorizationError as AuthorizationError,
)
from .exceptions import (
    ConfigurationError as ConfigurationError,
)
from .exceptions import (
    HandlerError as HandlerError,
)
from .exceptions import (
    MethodNotAllowed as MethodNotAllowed,
)
from .exceptions import (
    MiddlewareError as MiddlewareError,
)
from .exceptions import (
    RateLimitError as RateLimitError,
)
from .exceptions import (
    RouteNotFound as RouteNotFound,
)
from .exceptions import (
    ValidationError as ValidationError,
)

# Logging system
from .logging import (
    ArtanisLogger as ArtanisLogger,
)
from .logging import (
    RequestLoggingMiddleware as RequestLoggingMiddleware,
)
from .logging import (
    logger,
)

# Middleware system
from .middleware import (
    ExceptionHandlerMiddleware as ExceptionHandlerMiddleware,
)
from .middleware import (
    MiddlewareExecutor,
    MiddlewareManager,
    Response,
)
from .middleware import (
    ValidationMiddleware as ValidationMiddleware,
)
from .request import Request as Request

# Routing system
from .routing import (
    Route as Route,
)
from .routing import (
    Router as Router,
)

# OpenAPI system (optional import)
try:
    from .openapi import (
        OpenAPIGenerator as OpenAPIGenerator,
    )
    from .openapi import (
        OpenAPISpec as OpenAPISpec,
    )
    from .openapi import (
        ReDocUI as ReDocUI,
    )
    from .openapi import (
        SchemaGenerator as SchemaGenerator,
    )
    from .openapi import (
        SwaggerUI as SwaggerUI,
    )
    from .openapi import (
        ValidationMiddleware as OpenAPIValidationMiddleware,
    )
    from .openapi import (
        openapi_route as openapi_route,
    )
    from .openapi import (
        request_model as request_model,
    )
    from .openapi import (
        response_model as response_model,
    )

    _OPENAPI_AVAILABLE = True
except ImportError:
    _OPENAPI_AVAILABLE = False
