import logging
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.cache.handler import RedisHandler
from src.cache.client import RedisClient


def test_redis_handler_init():
    mock_client = MagicMock(spec=RedisClient)
    logger = logging.getLogger("test")
    handler = RedisHandler(client=mock_client, logger=logger)
    assert handler.client == mock_client
    assert handler.logger == logger


def test_redis_handler_set():
    with patch("redis.asyncio.Redis") as mock_redis:
        mock_instance = AsyncMock()
        mock_redis.return_value = mock_instance
        handler = RedisHandler(
            client=type("FakeClient", (), {"client": mock_instance})(),
            logger=logging.getLogger("test"),
        )
        asyncio.run(handler.set("key", "value", expire=123))
        mock_instance.set.assert_awaited_once_with("key", "value", ex=123)


def test_redis_handler_get():
    with patch("redis.asyncio.Redis") as mock_redis:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = b"some_value"
        mock_redis.return_value = mock_instance
        handler = RedisHandler(
            client=type("FakeClient", (), {"client": mock_instance})(),
            logger=logging.getLogger("test"),
        )
        result = asyncio.run(handler.get("key"))
        mock_instance.get.assert_awaited_once_with("key")
        assert result == b"some_value"
