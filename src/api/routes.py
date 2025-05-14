from fastapi import APIRouter, Query

from src.api.models import MediaSearchQuery
from src.services.media_service import MediaSearchService


class Routes:
    """
    This class defines the API routes for the MediaSearch application.
    """

    def __init__(self, media_search_service: MediaSearchService):
        self.media_search_service = media_search_service
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/health")
        async def health_check():
            """
            Health check endpoint to verify if the API is running.
            """
            return {"status": "healthy"}

        @self.router.get("/api/media/search")
        async def search_media(params: MediaSearchQuery = Query(...)) -> dict:
            """
            Search for media based on the provided query parameters.
            This endpoint allows users to search for media items using various filters and sorting options.

            Args:
                params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.

            Returns:
                dict: A dictionary containing the search results, total count, and pagination info.
            """
            resp = self.media_search_service.search(params)
            return resp
