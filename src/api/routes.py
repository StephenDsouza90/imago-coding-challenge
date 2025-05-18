from fastapi import APIRouter, Query, Depends

from src.api.models import RequestBody, ResponseBody
from src.services.media_service import MediaSearchService
from src.api.error_map import map_service_exception


class Routes:
    """
    This class defines the API routes for the MediaSearch application.
    """

    def __init__(self, get_media_search_service: MediaSearchService):
        """
        Routes
        -------------
        Initialize the Routes class.

        Args:
            get_media_search_service (MediaSearchService): The service to handle media search operations.
        """
        self.get_media_search_service = get_media_search_service
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        @self.router.get(
            "/health",
            summary="Health check endpoint",
            description="Check if the API is running and healthy.",
            tags=["Health"],
            response_description="A simple status message.",
        )
        async def health_check():
            """
            Health Check
            -------------
            Returns a simple status message to verify that the API is up and running.

            Returns:
                dict: A dictionary containing the status message.
            """
            return {"status": "healthy"}

        @self.router.get(
            "/api/media/search",
            summary="Search for media",
            description=(
                "Search for media items using various filters and sorting options.<br/><br/>"
                "<b>Query Parameters:</b><br/>"
                "- All fields of <code>RequestBody</code> can be used as query parameters.<br/><br/>"
                "<b>Returns:</b><br/>"
                "- <b>200 OK</b>: A list of media items matching the search criteria, wrapped in a <code>ResponseBody</code>.<br/>"
                "- <b>400/422/503/502/500</b>: Error details if the request is invalid or a server error occurs."
            ),
            tags=["Media Search"],
            response_model=ResponseBody,
            response_description="A list of media items matching the search criteria.",
        )
        async def search(
            search_request: RequestBody = Query(
                ..., description="Search parameters for media items."
            ),
            media_search_service: MediaSearchService = Depends(
                self.get_media_search_service
            ),
        ) -> ResponseBody:
            """
            Media Search Endpoint
            ---------------------
            Allows users to search for media items by providing various filters and sorting options.

            Args:
                search_request (RequestBody): The request body containing search parameters.
                media_search_service (MediaSearchService): The media search service instance.

            Returns:
                ResponseBody: A response body containing the search results.

            Raises:
                HTTPException: If the search request is invalid or if a server error occurs.
            """
            try:
                return await media_search_service.search_media(search_request)
            except Exception as exc:
                raise map_service_exception(exc)
