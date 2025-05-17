import logging

import redis


class RedisClient:
    """
    RedisClient provides a simple interface for connecting to and interacting with a Redis database.
    This class manages the connection lifecycle and basic operations for caching and retrieving data from Redis.
    """

    def __init__(
        self,
        logger: logging.Logger,
        host: str,
        port: int,
        username: str,
        password: str,
        db: int = 0,
    ):
        """
        Initialize the Redis client.

        Args:
            logger (logging.Logger): The logger instance.
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number. Default is 0.
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        """
        Establish a connection to the Redis server and verify connectivity with a ping.
        """
        self.client = redis.StrictRedis(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            db=self.db,
        )
        self.client.ping()

    def disconnect(self):
        """
        Close the connection to the Redis server if it exists.
        """
        if self.client:
            self.client.close()
