import logging
from unittest.mock import MagicMock

from src.redis.handler import RedisHandler
from src.redis.client import RedisClient


def test_redis_handler_init():
    mock_client = MagicMock(spec=RedisClient)
    logger = logging.getLogger("test")
    handler = RedisHandler(client=mock_client, logger=logger)
    assert handler.client == mock_client
    assert handler.logger == logger


def test_redis_handler_set_string():
    mock_client = MagicMock(spec=RedisClient)
    mock_client.client = MagicMock()
    logger = logging.getLogger("test")
    handler = RedisHandler(client=mock_client, logger=logger)
    handler.set_string("some_key", "some_value", expire=123)
    mock_client.client.set.assert_called_once_with("some_key", "some_value", ex=123)


def test_redis_handler_get_string():
    mock_client = MagicMock(spec=RedisClient)
    mock_client.client = MagicMock()
    mock_client.client.get.return_value = b"some_value"
    logger = logging.getLogger("test")
    handler = RedisHandler(client=mock_client, logger=logger)
    result = handler.get_string("some_key")
    mock_client.client.get.assert_called_once_with("some_key")
    assert result == b"some_value"
