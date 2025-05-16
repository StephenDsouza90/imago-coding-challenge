from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field as PydanticField, ConfigDict


class Field(str, Enum):
    """
    Fields available for searching media items.
    """

    KEYWORD = "suchtext"
    PHOTOGRAPHER = "fotografen"


class SortField(str, Enum):
    """
    Fields available for sorting search results.
    """

    DATE = "datum"
    WIDTH = "breite"
    HEIGHT = "hoehe"


class SortOrder(str, Enum):
    """
    Sort order for search results.
    """

    ASC = "asc"
    DESC = "desc"


class Limit(int, Enum):
    """
    Limits for number of results per page.
    """

    SMALL = 5
    MEDIUM = 10
    LARGE = 20
    EXTRA_LARGE = 50
    MAX = 100


class RequestBody(BaseModel):
    """
    Request body for searching media items.
    """

    keyword: str = PydanticField(..., description="Search keyword.")
    fields: List[str] = PydanticField(
        default_factory=lambda: [Field.KEYWORD], description="Fields to search in."
    )
    limit: Limit = PydanticField(
        Limit.SMALL, description="Number of results per page (1-100)."
    )
    page: int = PydanticField(1, description="Page number for pagination.")
    sort_by: SortField = PydanticField(
        SortField.DATE, description="Field to sort results by."
    )
    order_by: SortOrder = PydanticField(
        SortOrder.ASC, description="Sort order (ascending/descending)."
    )
    date_from: Optional[str] = PydanticField(
        None, description="Start date filter (YYYY-MM-DD)."
    )
    date_to: Optional[str] = PydanticField(
        None, description="End date filter (YYYY-MM-DD)."
    )
    height_min: Optional[int] = PydanticField(
        None, description="Minimum height filter."
    )
    height_max: Optional[int] = PydanticField(
        None, description="Maximum height filter."
    )
    width_min: Optional[int] = PydanticField(None, description="Minimum width filter.")
    width_max: Optional[int] = PydanticField(None, description="Maximum width filter.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keyword": "nature",
                "fields": ["suchtext", "fotografen"],
                "limit": 10,
                "page": 1,
                "sort_by": "datum",
                "order_by": "asc",
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "height_min": 500,
                "height_max": 2000,
                "width_min": 800,
                "width_max": 3000,
            }
        }
    )


class ResponseBody(BaseModel):
    """
    Response body for media search results.
    """

    total_results: int = PydanticField(
        ..., description="Total number of results found."
    )
    results: List[dict] = PydanticField(..., description="List of media items.")
    page: int = PydanticField(..., description="Current page number.")
    limit: int = PydanticField(..., description="Number of results per page.")
    has_next: bool = PydanticField(..., description="Whether there is a next page.")
    has_previous: bool = PydanticField(
        ..., description="Whether there is a previous page."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_results": 42,
                "results": [
                    {
                        "id": 1,
                        "title": "Sunset",
                        "photographer": "Alice",
                        "date": "2024-05-01",
                    }
                ],
                "page": 1,
                "limit": 10,
                "has_next": True,
                "has_previous": False,
            }
        }
    )
