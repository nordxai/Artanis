"""Schema generation for OpenAPI from Python type hints.

This module handles the conversion of Python type hints, Pydantic models,
dataclasses, and TypedDict to JSON Schema format for OpenAPI specifications.
"""

from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin


class ResponseSchema:
    """Wrapper for response schema definition.

    Used to define response models for OpenAPI generation.

    Example:
        ```python
        @response_model(UserResponse, status_code=200)
        async def get_user(id: int) -> UserResponse:
            pass

        app.get('/users/{id}', get_user)
        ```
    """

    def __init__(self, model: type[Any], status_code: int = 200, description: str = ""):
        self.model = model
        self.status_code = status_code
        self.description = description


class RequestSchema:
    """Wrapper for request schema definition.

    Used to define request body models for OpenAPI generation.

    Example:
        ```python
        @request_model(CreateUserRequest)
        async def create_user(user: CreateUserRequest):
            pass

        app.post('/users', create_user)
        ```
    """

    def __init__(self, model: type[Any], description: str = ""):
        self.model = model
        self.description = description


class SchemaGenerator:
    """Generates JSON Schema from Python type hints.

    Supports conversion of various Python types to JSON Schema format
    including primitives, collections, dataclasses, TypedDict, and Pydantic models.

    Example:
        ```python
        generator = SchemaGenerator()
        schema = generator.generate_schema(UserModel)
        ```
    """

    def __init__(self) -> None:
        """Initialize the schema generator."""
        self._schemas_cache: dict[str, dict[str, Any]] = {}

    def generate_schema(self, type_hint: type[Any]) -> dict[str, Any]:
        """Generate JSON Schema from a Python type hint.

        Args:
            type_hint: Python type to convert

        Returns:
            JSON Schema dictionary
        """
        return self._convert_type(type_hint)

    def _convert_type(self, type_hint: type[Any]) -> dict[str, Any]:  # noqa: PLR0911
        """Convert a type hint to JSON Schema.

        Args:
            type_hint: Type to convert

        Returns:
            JSON Schema dictionary
        """
        # Handle None/NoneType
        if type_hint is type(None):
            return {"type": "null"}

        # Handle basic types
        if type_hint in (str, int, float, bool):
            return self._convert_primitive(type_hint)

        # Handle Optional[T] (Union[T, None])
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Union:
            return self._convert_union(args)

        # Handle List[T]
        if origin is list or type_hint is list:
            if args:
                return {"type": "array", "items": self._convert_type(args[0])}
            return {"type": "array", "items": {}}

        # Handle Dict[K, V]
        if origin is dict or type_hint is dict:
            if len(args) >= 2:
                return {
                    "type": "object",
                    "additionalProperties": self._convert_type(args[1]),
                }
            return {"type": "object"}

        # Handle dataclasses
        if is_dataclass(type_hint):
            return self._convert_dataclass(type_hint)

        # Handle Enums
        if inspect.isclass(type_hint) and issubclass(type_hint, Enum):
            return self._convert_enum(type_hint)

        # Handle TypedDict
        if hasattr(type_hint, "__annotations__"):
            return self._convert_typed_dict(type_hint)

        # Try to handle Pydantic models
        if hasattr(type_hint, "model_json_schema"):
            schema = type_hint.model_json_schema()
            return schema if isinstance(schema, dict) else {"type": "object"}

        # Default fallback
        return {"type": "object"}

    def _convert_primitive(self, type_hint: type[Any]) -> dict[str, Any]:
        """Convert primitive types to JSON Schema.

        Args:
            type_hint: Primitive type

        Returns:
            JSON Schema for primitive type
        """
        if type_hint is str:
            return {"type": "string"}
        if type_hint is int:
            return {"type": "integer"}
        if type_hint is float:
            return {"type": "number"}
        if type_hint is bool:
            return {"type": "boolean"}
        return {"type": "string"}

    def _convert_union(self, args: tuple[type[Any], ...]) -> dict[str, Any]:
        """Convert Union types to JSON Schema.

        Args:
            args: Union type arguments

        Returns:
            JSON Schema for Union type
        """
        # Handle Optional[T] (Union[T, None])
        if len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            schema = self._convert_type(non_none_type)
            # Mark as nullable
            if "type" in schema:
                schema["nullable"] = True
            return schema

        # Handle general unions with anyOf
        return {"anyOf": [self._convert_type(arg) for arg in args]}

    def _convert_dataclass(self, dataclass_type: type[Any]) -> dict[str, Any]:
        """Convert dataclass to JSON Schema.

        Args:
            dataclass_type: Dataclass type

        Returns:
            JSON Schema for dataclass
        """
        properties = {}
        required = []

        # Get type hints for the dataclass
        from typing import get_type_hints

        try:
            type_hints = get_type_hints(dataclass_type)
        except (NameError, AttributeError):
            type_hints = {}

        for field in fields(dataclass_type):
            # Use type hints if available, otherwise fall back to field.type
            field_type = type_hints.get(field.name, field.type)
            field_schema = self._convert_type(field_type)
            properties[field.name] = field_schema

            # Check if field has no default value
            if (
                field.default is dataclasses.MISSING
                and field.default_factory is dataclasses.MISSING
            ):
                required.append(field.name)

        schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    def _convert_enum(self, enum_type: type[Enum]) -> dict[str, Any]:
        """Convert Enum to JSON Schema.

        Args:
            enum_type: Enum type

        Returns:
            JSON Schema for enum
        """
        values = [item.value for item in enum_type]

        # Determine the type based on the first value
        if values:
            first_value = values[0]
            if isinstance(first_value, str):
                schema_type = "string"
            elif isinstance(first_value, int):
                schema_type = "integer"
            elif isinstance(first_value, float):
                schema_type = "number"
            else:
                schema_type = "string"
        else:
            schema_type = "string"

        return {
            "type": schema_type,
            "enum": values,
        }

    def _convert_typed_dict(self, typed_dict_type: type[Any]) -> dict[str, Any]:
        """Convert TypedDict to JSON Schema.

        Args:
            typed_dict_type: TypedDict type

        Returns:
            JSON Schema for TypedDict
        """
        properties = {}
        required = []

        annotations = getattr(typed_dict_type, "__annotations__", {})

        for field_name, field_type in annotations.items():
            field_schema = self._convert_type(field_type)
            properties[field_name] = field_schema

            # For TypedDict, all fields are required by default
            # unless using typing_extensions.NotRequired
            required.append(field_name)

        schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    def get_schema_name(self, type_hint: type[Any]) -> str:
        """Get a suitable schema name for a type.

        Args:
            type_hint: Type to get name for

        Returns:
            Schema name string
        """
        if hasattr(type_hint, "__name__"):
            return type_hint.__name__
        if hasattr(type_hint, "_name"):
            name = getattr(type_hint, "_name", None)
            if isinstance(name, str):
                return name
        return (
            str(type_hint)
            .replace("typing.", "")
            .replace("[", "_")
            .replace("]", "")
            .replace(", ", "_")
        )

    def generate_component_schema(
        self, type_hint: type[Any]
    ) -> tuple[str, dict[str, Any]]:
        """Generate a component schema with name.

        Args:
            type_hint: Type to generate schema for

        Returns:
            Tuple of (schema_name, schema_dict)
        """
        schema_name = self.get_schema_name(type_hint)
        schema = self.generate_schema(type_hint)
        return schema_name, schema
