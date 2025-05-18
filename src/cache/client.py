import asyncio

import redis.asyncio as redis


class RedisClient:
    """
    RedisClient provides a simple interface for connecting to and interacting with a Redis database.

    This class manages the connection lifecycle and basic operations for caching and retrieving data from Redis.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        db: int = 0,
    ):
        """
        RedisClient
        -------------
        Initialize the Redis client.

        Args:
            logger (logging.Logger): The logger instance.
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number. Default is 0.
        """
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.client = None

    async def connect(self, max_retries: int = 3, delay: int = 2):
        """
        Connect
        -------------
        Establish a connection to the Redis server and verify connectivity with a ping.

        Args:
            max_retries (int): Maximum number of connection attempts. Default is 3.
            delay (int): Delay between connection attempts in seconds. Default is 2.

        Raises:
            ConnectionError: If the connection to the Redis server fails after the specified number of retries.
        """
        for attempt in range(1, max_retries + 1):
            try:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    db=self.db,
                )
                await self.client.ping()
                break  # Success, exit loop
            except redis.ConnectionError as e:
                if attempt == max_retries:
                    raise ConnectionError(
                        f"Failed to connect to Redis server at {self.host}:{self.port} after {max_retries} attempts: {e}"
                    )
            await asyncio.sleep(delay)

    async def disconnect(self):
        """
        Disconnect
        -------------
        Close the connection to the Redis server if it exists.
        """
        if self.client:
            await self.client.close()
