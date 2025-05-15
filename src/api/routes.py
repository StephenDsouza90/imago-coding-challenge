from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from elasticsearch.exceptions import BadRequestError

from src.api.models import MediaSearchRequest, MediaSearchResponse
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
        async def search_media(
            params: MediaSearchRequest = Query(...),
        ) -> MediaSearchResponse:
            """
            Search for media based on the provided query parameters.
            This endpoint allows users to search for media items using various filters and sorting options.

            Args:
                params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.

            Returns:
                MediaSearchResponse: A response object containing the search results, total count, and pagination info.
            """
            try:
                return self.media_search_service.search(params)

            except BadRequestError as bre:
                raise HTTPException(
                    status_code=400,
                    detail=f"Bad request: {str(bre)}",
                )

            except KeyError as ke:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {str(ke)}",
                )

            except ValueError as ve:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid input: {str(ve)}",
                )

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"An error occurred while processing the request: {str(e)}",
                )
