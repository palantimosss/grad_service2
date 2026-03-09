"""Tests for middleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.middleware.logging import LoggingMiddleware

_RESPONSE_OK = "response"


@pytest.mark.asyncio
class TestLoggingMiddleware:
    """Tests for logging middleware."""

    async def test_logging_middleware_message(self) -> None:
        """Test logging middleware with message."""
        middleware = LoggingMiddleware()
        mock_handler = AsyncMock(return_value=_RESPONSE_OK)

        mock_message = MagicMock()
        mock_message.text = "Test message"
        mock_message.from_user.username = "testuser"

        handler_data: dict = {}

        response = await middleware(mock_handler, mock_message, handler_data)
        assert response == _RESPONSE_OK

    async def test_logging_middleware_callback(self) -> None:
        """Test logging middleware with callback."""
        middleware = LoggingMiddleware()
        mock_handler = AsyncMock(return_value=_RESPONSE_OK)

        mock_callback = MagicMock()
        mock_callback.data = "callback_data"
        mock_callback.from_user.username = "testuser"

        handler_data: dict = {}

        response = await middleware(mock_handler, mock_callback, handler_data)
        assert response == _RESPONSE_OK
