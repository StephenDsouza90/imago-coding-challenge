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
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
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
        except Exception as e:
            is_alive = False

        return is_alive

    async def search_media(self, params: MediaSearchRequest) -> ObjectApiResponse:
        """
        Search for media in the Elasticsearch index based on the provided parameters.

        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.
        
        Returns:
            ObjectApiResponse: The response from the Elasticsearch search query.
        """
        body = self._build_search_body(params)
        try:
            response = await self.client.search(index=self.INDEX, body=body)

        except BadRequestError as e:
            raise BadRequestError(message=f"Bad request: {str(e)}", meta=e.meta, body=e.body)
        
        except Exception as e:
            raise Exception(f"Error while searching in Elasticsearch: {str(e)}")

        return response

    def _build_search_body(self, params: MediaSearchRequest) -> dict:
        """
        Build the search body for Elasticsearch based on the provided parameters.
        
        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.
        
        Returns:
            dict: The search body for Elasticsearch.
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": params.keyword,
                                "fields": params.fields,
                            }
                        }
                    ],
                    "filter": self._build_filters(params)
                },
            },
        }

        if params.limit:
            body["size"] = params.limit

        if params.page and params.limit:
            body["from"] = (params.page - 1) * params.limit

        if params.sort_by and params.order_by:
            body["sort"] = [{params.sort_by: {"order": params.order_by}}]

        return body

    def _build_filters(self, params: MediaSearchRequest) -> List[dict]:
        """
        Build the filter part of the Elasticsearch query based on the provided parameters.
        
        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.
            
        Returns:
            List[dict]: A list of filter dictionaries for Elasticsearch.
        """
        filters = []

        date_range = self._build_range_filter("datum", params.date_from, params.date_to)
        if date_range:
            filters.append(date_range)

        height_range = self._build_range_filter("hoehe", params.height_min, params.height_max)
        if height_range:
            filters.append(height_range)

        width_range = self._build_range_filter("breite", params.width_min, params.width_max)
        if width_range:
            filters.append(width_range)

        return filters

    def _build_range_filter(self, field: str, gte_val: Union[str, int], lte_val: Union[str, int]) -> Optional[dict]:
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
