from fastapi import HTTPException, status
from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError


def map_service_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, AssertionError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The search request was invalid. Please check your parameters and try again.",
        )
    if isinstance(exc, BadRequestError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The search request was invalid. Please check your parameters and try again.",
        )
    if isinstance(exc, ConnectionError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A connection error occurred while processing your request. Please try again later.",
        )
    if isinstance(exc, TransportError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A transport error occurred while processing your request. Please try again later.",
        )
    if isinstance(exc, KeyError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A required field was missing in the search response.",
        )
    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The search request has a bad value. Please check your parameters and try again.",
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred while processing your request. Please try again later.",
    )
