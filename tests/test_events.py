"""Tests for the Artanis event handling system."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from artanis import App, EventContext, EventManager


class TestEventManager:
    """Test the EventManager class functionality."""

    def test_event_manager_initialization(self):
        """Test EventManager initialization."""
        event_manager = EventManager()
        assert len(event_manager.handlers) == 0
        assert len(event_manager.event_middleware) == 0
        assert not event_manager._startup_executed
        assert not event_manager._shutdown_executed

    def test_add_handler(self):
        """Test adding event handlers."""
        event_manager = EventManager()

        def test_handler():
            pass

        event_manager.add_handler("test_event", test_handler)
        handlers = event_manager.get_handlers("test_event")
        assert len(handlers) == 1
        assert handlers[0].handler == test_handler
        assert handlers[0].priority == 0

    def test_add_handler_with_priority(self):
        """Test adding handlers with different priorities."""
        event_manager = EventManager()

        def handler1():
            pass

        def handler2():
            pass

        def handler3():
            pass

        # Add handlers with different priorities
        event_manager.add_handler("test_event", handler1, priority=5)
        event_manager.add_handler("test_event", handler2, priority=10)
        event_manager.add_handler("test_event", handler3, priority=1)

        handlers = event_manager.get_handlers("test_event")
        assert len(handlers) == 3
        # Should be ordered by priority (highest first)
        assert handlers[0].handler == handler2  # priority 10
        assert handlers[1].handler == handler1  # priority 5
        assert handlers[2].handler == handler3  # priority 1

    def test_remove_handler(self):
        """Test removing event handlers."""
        event_manager = EventManager()

        def test_handler():
            pass

        event_manager.add_handler("test_event", test_handler)
        assert len(event_manager.get_handlers("test_event")) == 1

        result = event_manager.remove_handler("test_event", test_handler)
        assert result is True
        assert len(event_manager.get_handlers("test_event")) == 0

        # Try removing non-existent handler
        result = event_manager.remove_handler("test_event", test_handler)
        assert result is False

    def test_add_event_middleware(self):
        """Test adding event middleware."""
        event_manager = EventManager()

        def middleware(event_context):
            pass

        event_manager.add_event_middleware(middleware)
        assert len(event_manager.event_middleware) == 1
        assert event_manager.event_middleware[0] == middleware

    @pytest.mark.asyncio
    async def test_emit_event_basic(self):
        """Test basic event emission."""
        event_manager = EventManager()
        called = []

        def handler(data):
            called.append(data)

        event_manager.add_handler("test_event", handler)
        await event_manager.emit_event("test_event", "test_data")

        assert called == ["test_data"]

    @pytest.mark.asyncio
    async def test_emit_event_async_handler(self):
        """Test event emission with async handlers."""
        event_manager = EventManager()
        called = []

        async def async_handler(data):
            called.append(data)

        event_manager.add_handler("test_event", async_handler)
        await event_manager.emit_event("test_event", "test_data")

        assert called == ["test_data"]

    @pytest.mark.asyncio
    async def test_emit_event_multiple_handlers(self):
        """Test event emission with multiple handlers."""
        event_manager = EventManager()
        called = []

        def handler1(data):
            called.append(f"h1:{data}")

        def handler2(data):
            called.append(f"h2:{data}")

        event_manager.add_handler("test_event", handler1, priority=1)
        event_manager.add_handler("test_event", handler2, priority=2)
        await event_manager.emit_event("test_event", "test")

        # Should be called in priority order
        assert called == ["h2:test", "h1:test"]

    @pytest.mark.asyncio
    async def test_emit_event_with_condition(self):
        """Test event emission with conditional handlers."""
        event_manager = EventManager()
        called = []

        def handler(data):
            called.append(data)

        def condition(data):
            return data == "allowed"

        event_manager.add_handler("test_event", handler, condition=condition)

        # Should not call handler
        await event_manager.emit_event("test_event", "denied")
        assert called == []

        # Should call handler
        await event_manager.emit_event("test_event", "allowed")
        assert called == ["allowed"]

    @pytest.mark.asyncio
    async def test_emit_event_with_middleware(self):
        """Test event emission with middleware."""
        event_manager = EventManager()
        middleware_called = []
        handler_called = []

        def middleware(event_context):
            middleware_called.append(event_context.name)

        def handler(data):
            handler_called.append(data)

        event_manager.add_event_middleware(middleware)
        event_manager.add_handler("test_event", handler)

        await event_manager.emit_event("test_event", "test_data")

        assert middleware_called == ["test_event"]
        assert handler_called == ["test_data"]

    @pytest.mark.asyncio
    async def test_emit_event_no_args_handler(self):
        """Test event emission with handlers that take no arguments."""
        event_manager = EventManager()
        called = []

        def handler():
            called.append("called")

        event_manager.add_handler("test_event", handler)
        await event_manager.emit_event("test_event", "ignored_data")

        assert called == ["called"]

    @pytest.mark.asyncio
    async def test_emit_event_context_handler(self):
        """Test event emission with handlers that expect EventContext."""
        event_manager = EventManager()
        received_contexts = []

        def handler(event_context: EventContext):
            received_contexts.append(event_context)

        event_manager.add_handler("test_event", handler)
        await event_manager.emit_event("test_event", "test_data", source="test")

        assert len(received_contexts) == 1
        context = received_contexts[0]
        assert context.name == "test_event"
        assert context.data == "test_data"
        assert context.source == "test"

    @pytest.mark.asyncio
    async def test_startup_and_shutdown_handlers(self):
        """Test startup and shutdown event execution."""
        event_manager = EventManager()
        called = []

        def startup_handler():
            called.append("startup")

        def shutdown_handler():
            called.append("shutdown")

        event_manager.add_handler("startup", startup_handler)
        event_manager.add_handler("shutdown", shutdown_handler)

        await event_manager.execute_startup_handlers()
        await event_manager.execute_shutdown_handlers()

        assert called == ["startup", "shutdown"]

    def test_list_events(self):
        """Test listing registered events."""
        event_manager = EventManager()

        def handler():
            pass

        event_manager.add_handler("event1", handler)
        event_manager.add_handler("event2", handler)

        events = event_manager.list_events()
        assert set(events) == {"event1", "event2"}

    def test_clear_handlers(self):
        """Test clearing event handlers."""
        event_manager = EventManager()

        def handler():
            pass

        event_manager.add_handler("event1", handler)
        event_manager.add_handler("event2", handler)

        # Clear specific event
        event_manager.clear_handlers("event1")
        assert "event1" not in event_manager.list_events()
        assert "event2" in event_manager.list_events()

        # Clear all events
        event_manager.clear_handlers()
        assert len(event_manager.list_events()) == 0


class TestAppEventIntegration:
    """Test event handling integration with the App class."""

    def test_app_has_event_manager(self):
        """Test that App instances have an event manager."""
        app = App()
        assert hasattr(app, "event_manager")
        assert isinstance(app.event_manager, EventManager)

    def test_add_event_handler(self):
        """Test adding event handlers through App."""
        app = App()
        called = []

        def handler(data):
            called.append(data)

        app.add_event_handler("test_event", handler)
        handlers = app.event_manager.get_handlers("test_event")
        assert len(handlers) == 1

    @pytest.mark.asyncio
    async def test_emit_event(self):
        """Test emitting events through App."""
        app = App()
        called = []

        def handler(data):
            called.append(data)

        app.add_event_handler("test_event", handler)
        await app.emit_event("test_event", "test_data")

        assert called == ["test_data"]

    def test_remove_event_handler(self):
        """Test removing event handlers through App."""
        app = App()

        def handler():
            pass

        app.add_event_handler("test_event", handler)
        assert len(app.event_manager.get_handlers("test_event")) == 1

        result = app.remove_event_handler("test_event", handler)
        assert result is True
        assert len(app.event_manager.get_handlers("test_event")) == 0

    def test_add_event_middleware(self):
        """Test adding event middleware through App."""
        app = App()

        def middleware(event_context):
            pass

        app.add_event_middleware(middleware)
        assert len(app.event_manager.event_middleware) == 1

    def test_list_events(self):
        """Test listing events through App."""
        app = App()

        def handler():
            pass

        app.add_event_handler("event1", handler)
        app.add_event_handler("event2", handler)

        events = app.list_events()
        assert set(events) == {"event1", "event2"}


class TestASGILifespanIntegration:
    """Test ASGI lifespan protocol integration."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self):
        """Test successful startup lifespan handling."""
        app = App()
        startup_called = []

        def startup_handler():
            startup_called.append("startup")

        app.add_event_handler("startup", startup_handler)

        # Mock ASGI lifespan startup
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()

        await app._handle_lifespan({}, receive, send)

        assert startup_called == ["startup"]
        send.assert_called_with({"type": "lifespan.startup.complete"})

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_success(self):
        """Test successful shutdown lifespan handling."""
        app = App()
        shutdown_called = []

        def shutdown_handler():
            shutdown_called.append("shutdown")

        app.add_event_handler("shutdown", shutdown_handler)

        # Mock ASGI lifespan shutdown
        receive = AsyncMock(return_value={"type": "lifespan.shutdown"})
        send = AsyncMock()

        await app._handle_lifespan({}, receive, send)

        assert shutdown_called == ["shutdown"]
        send.assert_called_with({"type": "lifespan.shutdown.complete"})

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self):
        """Test startup failure handling."""
        app = App()

        def failing_startup():
            msg = "Startup failed"
            raise ValueError(msg)

        app.add_event_handler("startup", failing_startup)

        # Mock ASGI lifespan startup
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()

        await app._handle_lifespan({}, receive, send)

        send.assert_called_with(
            {"type": "lifespan.startup.failed", "message": "Startup failed"}
        )

    @pytest.mark.asyncio
    async def test_asgi_call_lifespan_routing(self):
        """Test that lifespan events are routed correctly in __call__."""
        app = App()
        startup_called = []

        def startup_handler():
            startup_called.append("startup")

        app.add_event_handler("startup", startup_handler)

        # Mock ASGI lifespan call
        scope = {"type": "lifespan"}
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()

        await app(scope, receive, send)

        assert startup_called == ["startup"]
        send.assert_called_with({"type": "lifespan.startup.complete"})


class TestEventSystemExamples:
    """Test real-world usage examples of the event system."""

    @pytest.mark.asyncio
    async def test_database_lifecycle_example(self):
        """Test database setup and cleanup example."""
        app = App()
        database_state = {"connected": False, "pool": None}

        def setup_database():
            database_state["connected"] = True
            database_state["pool"] = "mock_pool"

        def cleanup_database():
            database_state["connected"] = False
            database_state["pool"] = None

        app.add_event_handler("startup", setup_database)
        app.add_event_handler("shutdown", cleanup_database)

        # Simulate startup
        await app.event_manager.execute_startup_handlers()
        assert database_state["connected"] is True
        assert database_state["pool"] == "mock_pool"

        # Simulate shutdown
        await app.event_manager.execute_shutdown_handlers()
        assert database_state["connected"] is False
        assert database_state["pool"] is None

    @pytest.mark.asyncio
    async def test_custom_events_example(self):
        """Test custom business events example."""
        app = App()
        events_log = []

        def log_user_registration(user_data):
            events_log.append(f"User registered: {user_data['email']}")

        def send_welcome_email(user_data):
            events_log.append(f"Welcome email sent to: {user_data['email']}")

        def update_analytics(user_data):
            events_log.append(f"Analytics updated for: {user_data['email']}")

        # Register multiple handlers for the same event
        app.add_event_handler("user_registered", log_user_registration, priority=10)
        app.add_event_handler("user_registered", send_welcome_email, priority=5)
        app.add_event_handler("user_registered", update_analytics, priority=1)

        # Trigger the event
        user_data = {"email": "test@example.com", "name": "Test User"}
        await app.emit_event("user_registered", user_data)

        # Verify execution order based on priority
        assert events_log == [
            "User registered: test@example.com",
            "Welcome email sent to: test@example.com",
            "Analytics updated for: test@example.com",
        ]

    @pytest.mark.asyncio
    async def test_conditional_events_example(self):
        """Test conditional event handling example."""
        app = App()
        notifications_sent = []

        def send_urgent_notification(order_data):
            notifications_sent.append(f"URGENT: Order {order_data['id']}")

        def send_normal_notification(order_data):
            notifications_sent.append(f"Order {order_data['id']} placed")

        # Only send urgent notifications for high-value orders
        app.add_event_handler(
            "order_placed",
            send_urgent_notification,
            condition=lambda data: data.get("amount", 0) > 1000,
        )

        app.add_event_handler("order_placed", send_normal_notification)

        # Normal order
        await app.emit_event("order_placed", {"id": "001", "amount": 50})
        assert notifications_sent == ["Order 001 placed"]

        # High-value order
        notifications_sent.clear()
        await app.emit_event("order_placed", {"id": "002", "amount": 1500})
        assert notifications_sent == ["URGENT: Order 002", "Order 002 placed"]
