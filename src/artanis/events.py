"""Event handling system for Artanis framework.

This module provides a flexible, extensible event system that allows users to
define custom events beyond the standard ASGI lifecycle events.
"""

from __future__ import annotations

import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from typing import Any as BaseModel

logger = logging.getLogger(__name__)

# Standard ASGI lifecycle events
STARTUP = "startup"
SHUTDOWN = "shutdown"

# Request lifecycle events
REQUEST_START = "request_start"
REQUEST_END = "request_end"
REQUEST_ERROR = "request_error"


@dataclass
class EventContext:
    """Context object passed to event handlers with metadata."""

    name: str
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EventHandler:
    """Internal representation of an event handler."""

    handler: Callable[..., Any]
    priority: int = 0
    condition: Callable[..., bool] | None = None
    schema: type[BaseModel] | None = None

    def __post_init__(self) -> None:
        """Validate handler after initialization."""
        if not callable(self.handler):
            msg = "Handler must be callable"  # type: ignore[unreachable]
            raise TypeError(msg)


class EventManager:
    """Manages event registration, middleware, and execution for Artanis applications.

    Provides a flexible event system that allows users to:
    - Register handlers for any event type
    - Define custom events beyond startup/shutdown
    - Control execution order with priorities
    - Add middleware that runs for all events
    - Validate event data with schemas
    """

    def __init__(self) -> None:
        self.handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self.event_middleware: list[Callable[..., Any]] = []
        self._startup_executed = False
        self._shutdown_executed = False

    def add_handler(
        self,
        event_name: str,
        handler: Callable[..., Any],
        priority: int = 0,
        condition: Callable[..., bool] | None = None,
        schema: type[BaseModel] | None = None,
    ) -> None:
        """Register an event handler.

        Args:
            event_name: Name of the event to handle
            handler: Function to call when event is triggered
            priority: Execution priority (higher numbers run first)
            condition: Optional condition function to determine if handler should run
            schema: Optional Pydantic schema for event data validation

        Examples:
            ```python
            event_manager.add_handler("startup", setup_database)
            event_manager.add_handler("user_registered", send_email, priority=10)
            event_manager.add_handler("payment", process_payment,
                                    condition=lambda data: data.get("amount", 0) > 0)
            ```
        """
        event_handler = EventHandler(
            handler=handler, priority=priority, condition=condition, schema=schema
        )

        # Insert handler in priority order (highest priority first)
        handlers = self.handlers[event_name]
        insert_index = 0
        for i, existing_handler in enumerate(handlers):
            if priority > existing_handler.priority:
                insert_index = i
                break
            insert_index = i + 1

        handlers.insert(insert_index, event_handler)
        logger.debug(f"Added handler for event '{event_name}' with priority {priority}")

    def remove_handler(self, event_name: str, handler: Callable[..., Any]) -> bool:
        """Remove a specific event handler.

        Args:
            event_name: Name of the event
            handler: Handler function to remove

        Returns:
            True if handler was found and removed, False otherwise
        """
        handlers = self.handlers.get(event_name, [])
        for i, event_handler in enumerate(handlers):
            if event_handler.handler == handler:
                handlers.pop(i)
                logger.debug(f"Removed handler for event '{event_name}'")
                return True
        return False

    def add_event_middleware(self, middleware: Callable[..., Any]) -> None:
        """Add middleware that runs for all events.

        Args:
            middleware: Function that will be called for every event

        Example:
            ```python
            async def event_logger(event_context):
                logger.info(f"Event triggered: {event_context.name}")

            event_manager.add_event_middleware(event_logger)
            ```
        """
        self.event_middleware.append(middleware)
        logger.debug("Added event middleware")

    async def emit_event(
        self,
        event_name: str,
        data: Any = None,
        source: str | None = None,
        **metadata: Any,
    ) -> None:
        """Trigger all handlers for an event.

        Args:
            event_name: Name of the event to trigger
            data: Data to pass to event handlers
            source: Optional source identifier for the event
            **metadata: Additional metadata to include in event context

        Examples:
            ```python
            await event_manager.emit_event("user_registered", user_data)
            await event_manager.emit_event("payment_processed",
                                         payment_data,
                                         source="payment_service")
            ```
        """
        event_context = EventContext(
            name=event_name, data=data, source=source, metadata=metadata
        )

        logger.debug(
            f"Emitting event '{event_name}' with {len(self.handlers[event_name])} handlers"
        )

        # Run event middleware first
        for middleware in self.event_middleware:
            try:
                if inspect.iscoroutinefunction(middleware):
                    await middleware(event_context)
                else:
                    middleware(event_context)
            except Exception as e:  # noqa: PERF203
                logger.error(f"Event middleware error for '{event_name}': {e}")

        # Execute handlers in priority order
        handlers = self.handlers.get(event_name, [])
        for event_handler in handlers:
            try:
                # Check condition if specified
                if event_handler.condition and not event_handler.condition(data):
                    logger.debug(
                        f"Skipping handler for '{event_name}' due to condition"
                    )
                    continue

                # Validate data with schema if specified
                if event_handler.schema and data is not None:
                    try:
                        event_handler.schema.model_validate(data)
                    except Exception as e:
                        logger.error(
                            f"Event data validation failed for '{event_name}': {e}"
                        )
                        continue

                # Call handler with appropriate arguments
                handler = event_handler.handler
                sig = inspect.signature(handler)
                params = list(sig.parameters.keys())

                # Determine arguments to pass
                args = []
                if len(params) == 0:
                    # Handler takes no arguments
                    pass
                elif len(params) == 1:
                    # Handler takes either data or event_context
                    first_param = next(iter(sig.parameters.values()))
                    if (
                        first_param.annotation == EventContext
                        or "context" in first_param.name
                    ):
                        args.append(event_context)
                    else:
                        args.append(data)
                else:
                    # Handler takes multiple arguments, pass data and additional metadata
                    args.append(data)
                    args.extend(metadata.values())

                # Execute handler
                if inspect.iscoroutinefunction(handler):
                    await handler(*args)
                else:
                    handler(*args)

            except Exception as e:
                logger.error(f"Event handler error for '{event_name}': {e}")

    async def execute_startup_handlers(self) -> None:
        """Execute all startup event handlers.

        Raises:
            Exception: Any exception from startup handlers is re-raised for ASGI lifecycle handling
        """
        if self._startup_executed:
            logger.warning("Startup handlers already executed")
            return

        self._startup_executed = True
        await self._emit_lifecycle_event(STARTUP)

    async def execute_shutdown_handlers(self) -> None:
        """Execute all shutdown event handlers.

        Raises:
            Exception: Any exception from shutdown handlers is re-raised for ASGI lifecycle handling
        """
        if self._shutdown_executed:
            logger.warning("Shutdown handlers already executed")
            return

        self._shutdown_executed = True
        await self._emit_lifecycle_event(SHUTDOWN)

    async def _emit_lifecycle_event(self, event_name: str) -> None:
        """Emit lifecycle events with exception propagation for ASGI compliance.

        Args:
            event_name: Name of the lifecycle event (startup or shutdown)

        Raises:
            Exception: Re-raises the first exception encountered from any handler
        """
        event_context = EventContext(name=event_name)

        logger.debug(
            f"Emitting lifecycle event '{event_name}' with {len(self.handlers[event_name])} handlers"
        )

        # Run event middleware first (but don't let middleware errors stop lifecycle)
        for middleware in self.event_middleware:
            try:
                if inspect.iscoroutinefunction(middleware):
                    await middleware(event_context)
                else:
                    middleware(event_context)
            except Exception as e:  # noqa: PERF203
                logger.error(f"Event middleware error for '{event_name}': {e}")

        # Execute handlers in priority order, re-raising first exception
        handlers = self.handlers.get(event_name, [])
        for event_handler in handlers:
            try:
                # Call handler with no arguments for lifecycle events
                handler = event_handler.handler
                if inspect.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:  # noqa: PERF203
                logger.error(f"Lifecycle handler error for '{event_name}': {e}")
                raise  # Re-raise for ASGI lifecycle protocol

    def get_handlers(self, event_name: str) -> list[EventHandler]:
        """Get all handlers for a specific event.

        Args:
            event_name: Name of the event

        Returns:
            List of event handlers for the event
        """
        return self.handlers.get(event_name, []).copy()

    def list_events(self) -> list[str]:
        """Get list of all registered event names.

        Returns:
            List of event names that have handlers
        """
        return list(self.handlers.keys())

    def clear_handlers(self, event_name: str | None = None) -> None:
        """Clear handlers for a specific event or all events.

        Args:
            event_name: Event to clear handlers for, or None to clear all
        """
        if event_name is None:
            self.handlers.clear()
            logger.debug("Cleared all event handlers")
        else:
            self.handlers.pop(event_name, None)
            logger.debug(f"Cleared handlers for event '{event_name}'")
