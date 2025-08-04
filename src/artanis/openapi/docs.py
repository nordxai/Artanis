"""Interactive API documentation for Artanis OpenAPI.

This module provides Swagger UI and ReDoc integration for serving interactive
API documentation based on OpenAPI specifications.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict

from src.artanis.middleware.response import Response

if TYPE_CHECKING:
    from .spec import OpenAPISpec


class SwaggerUI:
    """Swagger UI integration for interactive API documentation.

    Provides a complete Swagger UI interface for exploring and testing
    API endpoints based on OpenAPI specifications.

    Example:
        ```python
        swagger = SwaggerUI(openapi_spec)
        app.get('/docs', swagger.get_docs_handler())
        ```
    """

    def __init__(
        self,
        openapi_spec: OpenAPISpec,
        swagger_ui_version: str = "5.9.0",
        title: str = "API Documentation",
    ) -> None:
        """Initialize Swagger UI.

        Args:
            openapi_spec: OpenAPI specification instance
            swagger_ui_version: Swagger UI version to use
            title: HTML page title
        """
        self.openapi_spec = openapi_spec
        self.swagger_ui_version = swagger_ui_version
        self.title = title

    def get_docs_handler(self) -> Callable[[], Awaitable[str]]:
        """Get the Swagger UI route handler.

        Returns:
            Async handler function for serving Swagger UI
        """

        async def docs_handler() -> str:
            return self._generate_swagger_html()

        # Mark the handler to set HTML content type
        docs_handler._artanis_content_type = "text/html"  # type: ignore[attr-defined] # noqa: SLF001
        return docs_handler

    def get_openapi_json_handler(self) -> Callable[[], Awaitable[str]]:
        """Get the OpenAPI JSON specification handler.

        Returns:
            Async handler function for serving OpenAPI JSON
        """

        async def openapi_json_handler() -> str:
            return self.openapi_spec.to_json()

        # Mark the handler to set JSON content type
        openapi_json_handler._artanis_content_type = "application/json"  # type: ignore[attr-defined] # noqa: SLF001
        return openapi_json_handler

    def _generate_swagger_html(self) -> str:
        """Generate Swagger UI HTML page.

        Returns:
            Complete HTML page with embedded Swagger UI
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                tryItOutEnabled: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch', 'head', 'options'],
                docExpansion: 'none',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                showExtensions: true,
                showCommonExtensions: true,
            }});
        }};
    </script>
</body>
</html>"""


class ReDocUI:
    """ReDoc UI integration for interactive API documentation.

    Provides an alternative ReDoc interface for API documentation
    with a cleaner, more modern appearance.

    Example:
        ```python
        redoc = ReDocUI(openapi_spec)
        app.get('/redoc', redoc.get_docs_handler())
        ```
    """

    def __init__(
        self,
        openapi_spec: OpenAPISpec,
        redoc_version: str = "2.1.0",
        title: str = "API Documentation",
    ) -> None:
        """Initialize ReDoc UI.

        Args:
            openapi_spec: OpenAPI specification instance
            redoc_version: ReDoc version to use
            title: HTML page title
        """
        self.openapi_spec = openapi_spec
        self.redoc_version = redoc_version
        self.title = title

    def get_docs_handler(self) -> Callable[[], Awaitable[str]]:
        """Get the ReDoc UI route handler.

        Returns:
            Async handler function for serving ReDoc UI
        """

        async def docs_handler() -> str:
            return self._generate_redoc_html()

        # Mark the handler to set HTML content type
        docs_handler._artanis_content_type = "text/html"  # type: ignore[attr-defined] # noqa: SLF001
        return docs_handler

    def _generate_redoc_html(self) -> str:
        """Generate ReDoc UI HTML page.

        Returns:
            Complete HTML page with embedded ReDoc UI
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{self.title}</title>
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url='./openapi.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/{self.redoc_version}/bundles/redoc.standalone.js"></script>
</body>
</html>"""


class OpenAPIDocsManager:
    """Manager for serving multiple documentation interfaces.

    Handles the setup and serving of both Swagger UI and ReDoc interfaces
    along with the OpenAPI specification endpoint.

    Example:
        ```python
        docs_manager = OpenAPIDocsManager(openapi_spec)
        docs_manager.setup_docs_routes(app)
        ```
    """

    def __init__(
        self,
        openapi_spec: OpenAPISpec,
        docs_path: str = "/docs",
        redoc_path: str = "/redoc",
        openapi_path: str = "/openapi.json",
    ) -> None:
        """Initialize the documentation manager.

        Args:
            openapi_spec: OpenAPI specification instance
            docs_path: Path for Swagger UI
            redoc_path: Path for ReDoc UI
            openapi_path: Path for OpenAPI JSON specification
        """
        self.openapi_spec = openapi_spec
        self.docs_path = docs_path
        self.redoc_path = redoc_path
        self.openapi_path = openapi_path

        self.swagger_ui = SwaggerUI(openapi_spec)
        self.redoc_ui = ReDocUI(openapi_spec)

    def setup_docs_routes(self, app: Any) -> None:
        """Setup documentation routes on an Artanis app.

        Args:
            app: Artanis application instance
        """
        # OpenAPI JSON specification
        app.get(self.openapi_path, self.swagger_ui.get_openapi_json_handler())

        # Swagger UI documentation
        app.get(self.docs_path, self.swagger_ui.get_docs_handler())

        # ReDoc UI documentation
        app.get(self.redoc_path, self.redoc_ui.get_docs_handler())

    def get_routes_info(self) -> dict[str, str]:
        """Get information about documentation routes.

        Returns:
            Dictionary mapping route names to paths
        """
        return {
            "openapi_json": self.openapi_path,
            "swagger_ui": self.docs_path,
            "redoc_ui": self.redoc_path,
        }
