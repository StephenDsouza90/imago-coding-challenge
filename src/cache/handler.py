import logging

from src.cache.client import RedisClient


class RedisHandler:
    """
    A class to handle Redis operations.
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

    def set_string(self, key: str, value: str, expire: int = 3600):
        """
        Set a key-value pair in Redis where the value is a string.

        Args:
            key (str): The key to set.
            value (str): The value to set.
            expire (int): The expiration time in seconds. Default is 3600 seconds (1 hour).
        """
        self.client.client.set(key, value, ex=expire)

    def get_string(self, key: str) -> str:
        """
        Get a string from Redis by key.

        Args:
            key (str): The key to get.

        Returns:
            str: The value associated with the key.
        """
        return self.client.client.get(key)
