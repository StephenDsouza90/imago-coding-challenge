import os
import logging
from typing import AsyncGenerator, Tuple
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request
from dotenv import load_dotenv

from src.api.client import FastAPIClient
from src.api.routes import Routes
from src.services.media_service import MediaSearchService
from src.es.client import ElasticsearchClient
from src.es.handler import ElasticsearchHandler
from src.utils.logger import Logger
from src.cache.client import RedisClient
from src.cache.handler import RedisHandler


def init_logger(app=None) -> logging.Logger:
    """
    Initialize the logger for the application.

    Args:
        app (FastAPI, optional): The FastAPI application instance. Defaults to None.
    """
    logger = Logger().get_logger()
    if app:
        app.state.logger = logger
    return logger


def load_and_validate_es_env(app: FastAPI) -> Tuple[str, int, str, str]:
    """
    Load and validate environment variables for Elasticsearch configuration.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        tuple: A tuple containing the host, port, username, and password for Elasticsearch.
    """
    load_dotenv()
    host = os.getenv("ES_HOST")
    port = int(os.getenv("ES_PORT"))
    username = os.getenv("ES_USERNAME")
    password = os.getenv("ES_PASSWORD")
    if not all([host, port, username, password]):
        app.state.logger.error(
            "Missing one or more Elasticsearch environment variables."
        )
        raise ValueError("Missing one or more Elasticsearch environment variables.")
    return host, port, username, password


def load_and_validate_redis_env(app: FastAPI) -> Tuple[str, int, str, str]:
    """
    Load and validate environment variables for Redis configuration.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        tuple: A tuple containing the host and port for Redis.
    """
    load_dotenv()
    host = os.getenv("REDIS_HOST")
    port = int(os.getenv("REDIS_PORT"))
    username = os.getenv("REDIS_USERNAME")
    password = os.getenv("REDIS_PASSWORD")
    if not all([host, port, username, password]):
        app.state.logger.error("Missing one or more Redis environment variables.")
        raise ValueError("Missing one or more Redis environment variables.")
    return host, port, username, password


def init_es_client(app: FastAPI, host: str, port: int, username: str, password: str):
    """
    Initialize the Elasticsearch client and store it in the application state.

    Args:
        app (FastAPI): The FastAPI application instance.
        host (str): The Elasticsearch host.
        port (int): The Elasticsearch port.
        username (str): The Elasticsearch username.
        password (str): The Elasticsearch password.

    Returns:
    """
    app.state.logger.info("Initializing Elasticsearch client...")
    try:
        app.state.client = ElasticsearchClient(host, port, username, password)
        app.state.client.connect()
        app.state.logger.info("Elasticsearch client connected.")
        app.state.handler = ElasticsearchHandler(app.state.client, app.state.logger)
    except Exception as e:
        app.state.logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise Exception("Elasticsearch client connection failed.")


def init_redis_client(app: FastAPI, host: str, port: int, username: str, password: str):
    """
    Initialize the Redis client and store it in the application state.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.state.logger.info("Initializing Redis client and handler...")
    app.state.redis_client = RedisClient(host, port, username, password)

    try:
        app.state.redis_client.connect()
        app.state.redis_handler = RedisHandler(app.state.redis_client, app.state.logger)
    except Exception as e:
        app.state.logger.error(f"Failed to connect to Redis: {e}")
        raise Exception("Redis client connection failed.")

    app.state.logger.info("Redis client and handler initialized.")


async def check_es_connection(app: FastAPI):
    """
    Check the connection to the Elasticsearch client.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    try:
        if not await app.state.client.ping():
            app.state.logger.error("Elasticsearch client is not connected.")
            raise Exception("Elasticsearch client is not connected.")

        app.state.logger.info("Elasticsearch client is connected.")

    except Exception as e:
        app.state.logger.error(f"Elasticsearch ping failed: {e}")
        raise Exception("Elasticsearch client is not connected.")


def init_media_search_service(app: FastAPI):
    """
    Initialize the MediaSearchService and store it in the application state.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.state.logger.info("Initializing MediaSearchService...")
    app.state.media_search_service = MediaSearchService(
        app.state.handler, app.state.logger, app.state.redis_handler
    )
    app.state.logger.info("MediaSearchService initialized.")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application, initializing async resources on startup.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        # Initialize logger
        logger = init_logger(app)
        logger.info("Starting up the application...")

        # Load and validate environment variables
        host, port, username, password = load_and_validate_es_env(app)

        # Initialize Elasticsearch client
        init_es_client(app, host, port, username, password)
        await check_es_connection(app)

        # Load and validate Redis environment variables
        redis_host, redis_port, redis_username, redis_password = (
            load_and_validate_redis_env(app)
        )

        # Initialize Redis client
        init_redis_client(app, redis_host, redis_port, redis_username, redis_password)

        # Initialize MediaSearchService
        init_media_search_service(app)
        yield

        # Cleanup on shutdown
        app.state.logger.info("Shutting down the application...")
        await app.state.es_client.close()
        app.state.logger.info("Elasticsearch client closed.")

    # Create FastAPI application
    logger = init_logger()
    logger.info("Creating FastAPI application...")
    app_instance = FastAPIClient(lifespan=lifespan)
    app = app_instance.app

    # Dependency for routes to access the service
    def get_media_search_service(request: Request) -> MediaSearchService:
        return request.app.state.media_search_service

    router_instance = Routes(get_media_search_service)
    app.include_router(router_instance.router)
    logger.info("FastAPI application created and routes included.")
    return app
