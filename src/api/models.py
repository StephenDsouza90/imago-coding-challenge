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
    DATE = "datum"
    WIDTH = "breite"
    HEIGHT = "hoehe"
    PHOTOGRAPHER = "fotografen"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class Limit(int, Enum):
    SMALL = 5
    MEDIUM = 10
    LARGE = 20
    EXTRA_LARGE = 50
    MAX = 100


class RequestBody(BaseModel):
    # Required
    keyword: str
    fields: List[str] = [
        Field.KEYWORD
    ]  # TODO: Add more fields like "fotografen", "datum", etc.

    # Optional but defaults
    limit: Limit = Limit.SMALL
    page: int = 1
    sort_by: SortField = SortField.DATE
    order_by: SortOrder = SortOrder.ASC

    # Range filters
    date_from: Optional[str] = None  # ISO date string, e.g. 'YYYY-MM-DD'
    date_to: Optional[str] = None
    height_min: Optional[int] = None
    height_max: Optional[int] = None
    width_min: Optional[int] = None
    width_max: Optional[int] = None


class ResponseBody(BaseModel):
    total_results: int
    results: List[dict]
    page: int
    limit: int
    has_next: bool
    has_previous: bool
