import asyncio
from unittest.mock import AsyncMock, patch

from src.cache.client import RedisClient


def test_redis_client_init():
    client = RedisClient(
        host="localhost",
        port=6379,
        username="default",
        password="default",
        db=0,
    )
    assert client.host == "localhost"
    assert client.port == 6379
    assert client.username == "default"
    assert client.db == 0
    assert client.client is None


def test_redis_client_connect_success():
    with patch("redis.asyncio.Redis") as mock_redis:
        mock_instance = AsyncMock()
        mock_redis.return_value = mock_instance
        client = RedisClient(
            host="localhost",
            port=6379,
            username="default",
            password="default",
            db=0,
        )
        asyncio.run(client.connect())
        mock_redis.assert_called_once_with(
            host="localhost", port=6379, username="default", password="default", db=0
        )
        mock_instance.ping.assert_awaited_once()
        assert client.client == mock_instance


def test_redis_client_disconnect():
    with patch("redis.asyncio.Redis") as mock_redis:
        mock_instance = AsyncMock()
        mock_redis.return_value = mock_instance
        client = RedisClient(
            host="localhost",
            port=6379,
            username="default",
            password="default",
            db=0,
        )
        client.client = mock_instance
        asyncio.run(client.disconnect())
        mock_instance.close.assert_awaited_once()
