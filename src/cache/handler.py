import logging
from typing import Optional

from src.cache.client import RedisClient


class RedisHandler:
    """
    RedisHandler provides high-level methods for interacting with Redis, such as setting and getting string values.
    This class abstracts away direct Redis commands and provides a clean interface for caching logic in the application.
    """

    def __init__(self, client: RedisClient, logger: logging.Logger):
        """
        Initialize the RedisHandler.

        Args:
            client (RedisClient): The Redis client instance.
            logger (logging.Logger): The logger instance.
        """
        self.client = client
        self.logger = logger

    def set(self, key: str, value: str, expire: int = 3600):
        """
        Store a string value in Redis with an optional expiration time (default: 1 hour).
        Overwrites any existing value for the given key.

        Args:
            key (str): The key to set.
            value (str): The value to set.
            expire (int): The expiration time in seconds. Default is 3600 seconds (1 hour).
        """
        self.client.client.set(key, value, ex=expire)

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis by key.
        Returns None if the key does not exist.

        Args:
            key (str): The key to get.

        Returns:
            Optional[str]: The value associated with the key.
        """
        return self.client.client.get(key)
