import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request

from src.api.client import FastAPIClient
from src.api.routes import Routes
from src.services.media_service import MediaSearchService
from src.es.elasticsearch_client import ElasticsearchClient


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application, initializing async resources on startup.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """
        Lifespan context manager for the FastAPI application.
        This function is called on application startup and shutdown.
        """
        load_dotenv()
        host = os.getenv("ES_HOST")
        port = int(os.getenv("ES_PORT"))
        username = os.getenv("ES_USERNAME")
        password = os.getenv("ES_PASSWORD")
        if not all([host, port, username, password]):
            raise ValueError("Missing one or more Elasticsearch environment variables.")

        app.state.es_client = ElasticsearchClient(host, port, username, password)
        try:
            if not await app.state.es_client.ping():
                raise Exception("Elasticsearch client is not connected.")
        except Exception as e:
            print(f"Elasticsearch ping failed: {e}")
            raise

        media_search_service = MediaSearchService(app.state.es_client)
        app.state.media_search_service = media_search_service
        yield

    app_instance = FastAPIClient(lifespan=lifespan)
    app = app_instance.app

    # Dependency for routes to access the service
    def get_media_search_service(request: Request):
        return request.app.state.media_search_service

    router_instance = Routes(get_media_search_service)
    app.include_router(router_instance.router)
    return app
