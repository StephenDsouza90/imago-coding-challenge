import logging

from fastapi import APIRouter, Query, Depends
from fastapi.exceptions import HTTPException
from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError

from src.api.models import MediaSearchRequest, MediaSearchResponse
from src.services.media_service import MediaSearchService


class Routes:
    """
    This class defines the API routes for the MediaSearch application.
    """

    def __init__(
        self, get_media_search_service: MediaSearchService, logger: logging.Logger
    ):
        """
        Initialize the Routes class.

        Args:
            get_media_search_service (MediaSearchService): The service to handle media search operations.
            logger (logging.Logger): The logger instance for logging.
        """
        self.get_media_search_service = get_media_search_service
        self.logger = logger
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
        async def search(
            search_request: MediaSearchRequest = Query(...),
            media_search_service: MediaSearchService = Depends(
                self.get_media_search_service
            ),
        ) -> MediaSearchResponse:
            """
            Search for media based on the provided query parameters.
            This endpoint allows users to search for media items using various filters and sorting options.
            """
            try:
                return await media_search_service.search_media(search_request)

            except BadRequestError as bre:
                self.logger.error(f"BadRequestError: {bre}")
                raise HTTPException(
                    status_code=400,
                    detail="The search request was invalid. Please check your parameters and try again.",
                )

            except TransportError as te:
                self.logger.error(f"TransportError: {te}")
                raise HTTPException(
                    status_code=502,
                    detail="A transport error occurred while processing your request. Please try again later.",
                )
            
            except ConnectionError as ce:
                self.logger.error(f"ConnectionError: {ce}")
                raise HTTPException(
                    status_code=503,
                    detail="A connection error occurred while processing your request. Please try again later.",
                )
            
            except KeyError as ke:
                self.logger.error(f"KeyError: {ke}")
                raise HTTPException(
                    status_code=400,
                    detail="A required field was missing in the search response.",
                )

            except ValueError as ve:
                self.logger.error(f"ValueError: {ve}")
                raise HTTPException(
                    status_code=422,
                    detail=str(ve),
                )

            except Exception as e:
                self.logger.error(f"Unhandled Exception: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="An unexpected error occurred while processing your request. Please try again later.",
                )
