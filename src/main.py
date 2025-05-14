import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.client import FastAPIClient
from src.api.routes import Routes
from src.services.media_service import MediaSearchService
from src.es.elasticsearch import ElasticsearchClient


def create_app(media_search_service: MediaSearchService) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        media_search_service (MediaSearchService): The media search service instance to be used in the application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    api_instance = FastAPIClient()
    router_instance = Routes(media_search_service)
    api_instance.app.include_router(router_instance.router)
    return api_instance.app


def initialize_media_search_services(
    elasticsearch_client: ElasticsearchClient,
) -> MediaSearchService:
    """
    Initialize the media search service.

    Args:
        elasticsearch_client (ElasticsearchClient): The Elasticsearch client instance to be used for search operations.

    Returns:
        MediaSearchService: An instance of the MediaSearchService class.
    """
    return MediaSearchService(elasticsearch_client)


def initialize_elasticsearch_client() -> ElasticsearchClient:
    """
    Initialize the Elasticsearch client.

    Returns:
        ElasticsearchClient: An instance of the ElasticsearchClient class.
    """
    # Load environment variables from .env file
    load_dotenv()

    host = os.getenv("ES_HOST")
    port = int(os.getenv("ES_PORT"))
    username = os.getenv("ES_USERNAME")
    password = os.getenv("ES_PASSWORD")
    return ElasticsearchClient(host, port, username, password)


def initialize_app() -> FastAPI:
    """
    Initialize the FastAPI application with services and routes.

    Returns:
        FastAPI: The initialized FastAPI application instance.
    """
    elasticsearch_client = initialize_elasticsearch_client()
    if elasticsearch_client.ping():
        media_search_service = initialize_media_search_services(elasticsearch_client)
        app = create_app(media_search_service)
        return app
    else:
        raise Exception("Elasticsearch client is not connected.")
