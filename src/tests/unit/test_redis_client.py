import logging
from unittest.mock import patch, MagicMock

from src.redis.client import RedisClient


def test_redis_client_init():
    logger = logging.getLogger("test")
    client = RedisClient(logger, host="localhost", port=6379, db=1)
    assert client.logger == logger
    assert client.host == "localhost"
    assert client.port == 6379
    assert client.db == 1
    assert client.client is None


def test_redis_client_connect_success():
    logger = logging.getLogger("test")
    with patch("src.redis.client.redis.StrictRedis") as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        client = RedisClient(logger, host="localhost", port=6379)
        client.connect()
        mock_redis.assert_called_once_with(host="localhost", port=6379, db=0)
        mock_instance.ping.assert_called_once()
        assert client.client == mock_instance


def test_redis_client_disconnect():
    logger = logging.getLogger("test")
    with patch("src.redis.client.redis.StrictRedis") as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        client = RedisClient(logger, host="localhost", port=6379)
        client.connect()
        client.disconnect()
        mock_instance.close.assert_called_once()
