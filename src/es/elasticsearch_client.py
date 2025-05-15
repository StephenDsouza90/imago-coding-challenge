from typing import Optional, Union, List

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import BadRequestError
from elastic_transport import ObjectApiResponse

from src.api.models import MediaSearchRequest


class ElasticsearchClient:
    """
    A class to interact with the Elasticsearch client.
    """

    INDEX = "imago"

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_on_timeout: bool = True,
    ):
        """
        Initialize the Elasticsearch client.
        """
        self.client = AsyncElasticsearch(
            hosts=[f"{host}:{port}"],
            http_auth=(username, password),
            headers={
                "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
            },
            request_timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout,
            verify_certs=False,
        )

    async def ping(self) -> bool:
        """
        Check if the Elasticsearch client is alive.

        Returns:
            bool: True if the client is alive, False otherwise.
        """
        is_alive = False

        try:
            result = await self.client.ping()
            is_alive = bool(result)
        except Exception:
            is_alive = False

        return is_alive

    async def search_media(
        self, search_request: MediaSearchRequest
    ) -> ObjectApiResponse:
        """
        Search for media in the Elasticsearch index based on the provided parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            ObjectApiResponse: The response from the Elasticsearch search query.
        """
        body = self._build_search_body(search_request)
        try:
            response = await self.client.search(index=self.INDEX, body=body)
        except BadRequestError as e:
            print(f"Elasticsearch BadRequestError: {e}")
            raise BadRequestError(
                message="The Elasticsearch query was invalid.", meta=e.meta, body=e.body
            )
        except Exception as e:
            print(f"Elasticsearch search error: {e}")
            raise Exception("An error occurred while searching in Elasticsearch.")
        return response

    def _build_search_body(self, search_request: MediaSearchRequest) -> dict:
        """
        Build the search body for Elasticsearch based on the provided parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            dict: The search body for Elasticsearch.
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": search_request.keyword,
                                "fields": search_request.fields,
                            }
                        }
                    ],
                    "filter": self._build_filters(search_request),
                },
            },
        }

        if search_request.limit:
            body["size"] = search_request.limit

        if search_request.page and search_request.limit:
            body["from"] = (search_request.page - 1) * search_request.limit

        if search_request.sort_by and search_request.order_by:
            body["sort"] = [
                {search_request.sort_by: {"order": search_request.order_by}}
            ]

        return body

    def _build_filters(self, search_request: MediaSearchRequest) -> List[dict]:
        """
        Build the filter part of the Elasticsearch query based on the provided parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            List[dict]: A list of filter dictionaries for Elasticsearch.
        """
        filters = []

        date_range = self._build_range_filter(
            "datum", search_request.date_from, search_request.date_to
        )
        if date_range:
            filters.append(date_range)

        height_range = self._build_range_filter(
            "hoehe", search_request.height_min, search_request.height_max
        )
        if height_range:
            filters.append(height_range)

        width_range = self._build_range_filter(
            "breite", search_request.width_min, search_request.width_max
        )
        if width_range:
            filters.append(width_range)

        return filters

    def _build_range_filter(
        self, field: str, gte_val: Union[str, int], lte_val: Union[str, int]
    ) -> Optional[dict]:
        """
        Build a range filter for Elasticsearch.

        Args:
            field (str): The field to filter on.
            gte_val (Union[str, int]): The minimum value for the range.
            lte_val (Union[str, int]): The maximum value for the range.

        Returns:
            Optional[dict]: The range filter for Elasticsearch.
        """
        range_query = {}

        if gte_val:
            range_query["gte"] = gte_val
        if lte_val:
            range_query["lte"] = lte_val
        if range_query:
            return {"range": {field: range_query}}

        return None
