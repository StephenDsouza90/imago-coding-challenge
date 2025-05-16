import logging

import redis


class RedisClient:
    """
    A class to interact with the Redis client.
    """

    def __init__(self, logger: logging.Logger, host: str, port: int, db: int = 0):
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
        self.client = None

    def connect(self):
        """
        Connect to the Redis server.
        """

        self.client = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        self.client.ping()

    def disconnect(self):
        """
        Disconnect from the Redis server.
        """
        if self.client:
            self.client.close()
