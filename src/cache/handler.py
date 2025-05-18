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
        RedisHandler
        -------------
        Initialize the RedisHandler.

        Args:
            client (RedisClient): The Redis client instance.
            logger (logging.Logger): The logger instance.
        """
        self.client = client
        self.logger = logger

    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Set
        -------------
        Store a string value in Redis with an optional expiration time (default: 1 hour).
        Overwrites any existing value for the given key.

        Args:
            key (str): The key to set.
            value (str): The value to set.
            expire (int): The expiration time in seconds. Default is 3600 seconds (1 hour).
        """
        try:
            await self.client.client.set(key, value, ex=expire)
        except Exception as e:
            self.logger.error(f"Failed to set key {key} in Redis: {e}")
            # NOTE: Not raising an exception here to avoid breaking the application flow.

    async def get(self, key: str) -> Optional[str]:
        """
        Get
        -------------
        Retrieve a string value from Redis by key.
        Returns None if the key does not exist.

        Args:
            key (str): The key to get.

        Returns:
            Optional[str]: The value associated with the key.
        """
        try:
            return await self.client.client.get(key)
        except Exception as e:
            self.logger.error(f"Failed to get key {key} from Redis: {e}")
            # NOTE: Not raising an exception here to avoid breaking the application flow.
            return None
