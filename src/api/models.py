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


class RequestBody(BaseModel):
    """
    Request body for searching media items.
    """

    keyword: str = PydanticField(
        ...,
        description="Search keyword.",
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\s]+$",  # Regex to allow only alphanumeric characters and spaces
    )
    fields: List[str] = PydanticField(
        default_factory=lambda: [Field.KEYWORD],
        description="Fields to search in. Supported: suchtext, fotografen.",
    )
    match: Match = PydanticField(
        Match.WORDS,
        description="Match type for search. Supported: best_fields, most_fields, cross_fields, phrase, phrase_prefix.",
    )
    limit: Limit = PydanticField(
        Limit.SMALL,
        description="Number of results per page. Supported: 5, 10, 20, 50, 100.",
    )
    page: int = PydanticField(1, description="Page number for pagination.", ge=1)
    sort_by: SortField = PydanticField(
        SortField.DATE,
        description="Field to sort results by. Supported: datum, breite, hoehe.",
    )
    order_by: SortOrder = PydanticField(
        SortOrder.DESC,
        description="Sort order (ascending/descending). Supported: asc, desc.",
    )
    date_from: Optional[str] = PydanticField(
        None,
        description="Start date filter (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex to validate date format (YYYY-MM-DD)
    )
    date_to: Optional[str] = PydanticField(
        None,
        description="End date filter (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex to validate date format (YYYY-MM-DD)
    )
    height_min: Optional[int] = PydanticField(
        None, description="Minimum height filter.", ge=0
    )
    height_max: Optional[int] = PydanticField(
        None, description="Maximum height filter.", ge=0
    )
    width_min: Optional[int] = PydanticField(
        None, description="Minimum width filter.", ge=0
    )
    width_max: Optional[int] = PydanticField(
        None, description="Maximum width filter.", ge=0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keyword": "nature",
                "fields": ["suchtext", "fotografen"],
                "match": ["phrase"],
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
