from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class Field(str, Enum):
    KEYWORD = "suchtext"
    DATE = "datum"
    WIDTH = "breite"
    HEIGHT = "hoehe"
    PHOTOGRAPHER = "fotografen"
    IMAGE_NUMBER = "bildnummer"


class SortField(str, Enum):
    DATE = Field.DATE
    WIDTH = Field.WIDTH
    HEIGHT = Field.HEIGHT
    PHOTOGRAPHER = Field.PHOTOGRAPHER


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class Limit(int, Enum):
    SMALL = 5
    MEDIUM = 10
    LARGE = 20
    EXTRA_LARGE = 50
    MAX = 100


class MediaSearchRequest(BaseModel):
    # Required
    keyword: str
    fields: List[str] = [Field.KEYWORD] # TODO: Add more fields like "fotografen", "datum", etc.

    # Optional but defaults
    limit: Limit = Limit.SMALL
    page: int = 1
    sort_by: SortField = SortField.DATE
    order_by: SortOrder = SortOrder.ASC

    # Range filters
    date_from: Optional[str] = None  # ISO date string, e.g. '1980-01-01'
    date_to: Optional[str] = None
    height_min: Optional[int] = None
    height_max: Optional[int] = None
    width_min: Optional[int] = None
    width_max: Optional[int] = None


class MediaSearchResponse(BaseModel):
    total_results: int
    results: List[dict]
    page: int
    limit: int
    has_next: bool
    has_previous: bool
