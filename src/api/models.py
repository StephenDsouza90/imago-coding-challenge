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


class Match(str, Enum):
    """
    Enumeration of match types supported in Elasticsearch for searching media items.

    Attributes:
        WORDS (str): This is the default and is used when searching for the best matching field.
        MOST (str): Combines the scores from all matching fields.
        CROSS (str): Used as a single combined field.
        PHRASE (str): Used for exact phrase matching.
        PHRASE_PREFIX (str): Used for matching phrases with a prefix (useful for autocomplete).
    """

    WORDS = "best_fields"
    MOST = "most_fields"
    CROSS = "cross_fields"
    PHRASE = "phrase"
    PHRASE_PREFIX = "phrase_prefix"


class PageNumber:
    """
    Default page number for pagination.
    """

    DEFAULT: int = 1


class RequestBody(BaseModel):
    """
    Request body for searching media items.
    """

    keyword: str = PydanticField(
        ...,  # Required field
        title="Keyword",
        description="Search keyword.",
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\s]+$",  # Regex to allow only alphanumeric characters and spaces
    )
    fields: List[str] = PydanticField(
        default_factory=lambda: [Field.KEYWORD],
        title="Fields",
        description="Fields to search in. Supported: suchtext, fotografen.",
    )
    match: Match = PydanticField(
        Match.WORDS,
        title="Match Type",
        description="Match type for search. Supported: best_fields, most_fields, cross_fields, phrase, phrase_prefix.",
    )
    limit: Limit = PydanticField(
        Limit.SMALL,
        title="Limit",
        description="Number of results per page. Supported: 5, 10, 20, 50, 100.",
        le=Limit.MAX.value,  # Ensure limit is less than or equal to the maximum limit
    )
    page: int = PydanticField(
        PageNumber.DEFAULT,
        title="Page",
        description="Page number for pagination.",
        ge=PageNumber.DEFAULT,  # Ensure page number is greater than or equal to 1
    )
    sort_by: SortField = PydanticField(
        SortField.DATE,
        title="Sort By",
        description="Field to sort results by. Supported: datum, breite, hoehe.",
    )
    order_by: SortOrder = PydanticField(
        SortOrder.DESC,
        title="Order By",
        description="Sort order (ascending/descending). Supported: asc, desc.",
    )
    date_from: Optional[str] = PydanticField(
        None,
        title="Date From",
        description="Start date filter (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex to validate date format (YYYY-MM-DD)
    )
    date_to: Optional[str] = PydanticField(
        None,
        title="Date To",
        description="End date filter (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex to validate date format (YYYY-MM-DD)
    )
    height_min: Optional[int] = PydanticField(
        None,
        title="Height Min",
        description="Minimum height filter.",
        ge=0,  # Ensure height is non-negative
    )
    height_max: Optional[int] = PydanticField(
        None,
        title="Height Max",
        description="Maximum height filter.",
        ge=0,  # Ensure height is non-negative
    )
    width_min: Optional[int] = PydanticField(
        None,
        title="Width Min",
        description="Minimum width filter.",
        ge=0,  # Ensure width is non-negative
    )
    width_max: Optional[int] = PydanticField(
        None, title="Width Max", description="Maximum width filter.", ge=0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keyword": "nature",
                "fields": [Field.KEYWORD.value, Field.PHOTOGRAPHER.value],
                "match": [Match.WORDS.value],
                "limit": Limit.SMALL.value,
                "page": 1,
                "sort_by": SortField.DATE.value,
                "order_by": SortOrder.DESC.value,
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
        ...,  # Required field
        title="Total Results",
        description="Total number of results found.",
    )
    results: List[dict] = PydanticField(
        ...,  # Required field
        title="Results",
        description="List of media items.",
    )
    page: int = PydanticField(
        ...,  # Required field
        title="Page",
        description="Current page number.",
    )
    limit: int = PydanticField(
        ...,  # Required field
        title="Limit",
        description="Number of results per page.",
    )
    has_next: bool = PydanticField(
        ...,  # Required field
        title="Has Next",
        description="Whether there is a next page.",
    )
    has_previous: bool = PydanticField(
        ...,  # Required field
        title="Has Previous",
        description="Whether there is a previous page.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "total_results": 1000,
            "results": [
                {
                    "_index": "imago",
                    "_id": "BE0PZpQBcFpCmfdy_ns1",
                    "_score": "null",
                    "_source": {
                        "bildnummer": "108420352",
                        "datum": "2019-04-20T00:00:00.000Z",
                        "suchtext": "Some text",
                        "fotografen": "TT",
                        "hoehe": "5504",
                        "breite": "8256",
                        "db": "stock",
                    },
                    "sort": [8256],
                    "media_url": "https://www.imago-images.de/bild/st/0108420352/s.jpg",
                },
            ],
            "page": 1,
            "limit": 10,
            "has_next": "true",
            "has_previous": "false",
        }
    )
