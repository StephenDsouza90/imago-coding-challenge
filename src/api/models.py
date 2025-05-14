from pydantic import BaseModel
from typing import Optional, List


class MediaSearchQuery(BaseModel):
    keyword: Optional[str] = "sunset"  # Default to "sunset"
    limit: Optional[int] = 5  # Default to 5


class MediaSearchResponse(BaseModel):
    total_results: int
    results: List[dict]
    page: int
    limit: int
    has_next: bool
    has_previous: bool

    def to_dict(self):
        return {
            "total_results": self.total_results,
            "results": self.results,
            "page": self.page,
            "limit": self.limit,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }
