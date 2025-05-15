from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


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


class MediaSearchQuery(BaseModel):
    # Required
    keyword: str # Required

    # Defaults
    fields: List[str] = ["suchtext"]
    limit: Limit = Limit.SMALL
    page: int = 1
    sort_by: SortField = SortField.DATE
    order_by: SortOrder = SortOrder.ASC


class MediaSearchResponse(BaseModel):
    total_results: int
    results: List[dict]
    page: int
    limit: int
    has_next: bool
    has_previous: bool
