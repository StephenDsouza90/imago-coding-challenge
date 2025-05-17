import logging
from typing import Optional, Union, List

from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError
from elastic_transport import ObjectApiResponse

from src.api.models import RequestBody, SortField
from src.es.client import ElasticsearchClient
from src.es.consts import INDEX


class ElasticsearchHandler:
    """
    ElasticsearchHandler provides high-level methods for querying and managing media data in Elasticsearch.
    This class builds search queries, handles exceptions, and abstracts Elasticsearch operations for the application.
    """

    def __init__(self, client: ElasticsearchClient, logger: logging.Logger):
        """
        Initialize the ElasticsearchHandler with a client and logger.

        Args:
            client (ElasticsearchClient): The Elasticsearch client instance.
            logger (logging.Logger): The logger instance for logging.
        """
        self.client = client
        self.logger = logger

    async def search_media(self, search_request: RequestBody) -> ObjectApiResponse:
        """
        Perform a search for media items in Elasticsearch using the provided search parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            ObjectApiResponse: The raw Elasticsearch response object.
        """

        try:
            body = self._build_search_body(search_request)
            self.logger.info(f"Elasticsearch search body: {body}")

            return await self.client.search(index=INDEX, body=body)

        except BadRequestError as bre:
            self.logger.error(f"Elasticsearch BadRequestError: {bre.meta}, {bre.body}")
            raise BadRequestError(
                message="The Elasticsearch query was invalid.",
                meta=bre.meta,
                body=bre.body,
            )

        except ConnectionError as ce:
            self.logger.error(f"Elasticsearch ConnectionError: {ce}")
            raise ConnectionError(
                message="A connection error occurred while searching in Elasticsearch.",
            )

        except TransportError as te:
            self.logger.error(f"Elasticsearch TransportError: {te}")
            raise TransportError(
                message="A transport error occurred while searching in Elasticsearch.",
            )

        except Exception as e:
            self.logger.error(f"Elasticsearch search error: {e}")
            raise Exception("An error occurred while searching in Elasticsearch.")

    def _build_search_body(self, search_request: RequestBody) -> dict:
        """
        Build the search body for Elasticsearch based on the provided parameters.

        - `bool` is used to combine multiple query clauses.
        - `should` is used to indicate that at least one of the clauses should match.
        - `term` is used for exact matches on fields.
        - `multi_match` is used for matching a query against multiple fields.
        - `type` is used to specify the type of matching (e.g., best_fields, most_fields).
        - `filter` is used to filter results without affecting the score.
        - `minimum_should_match` is used to specify the minimum number of clauses that must match.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            dict: The search body for Elasticsearch.
        """
        should_queries = []
        if search_request.fields:
            for field in search_request.fields:
                should_queries.append({"term": {field: search_request.keyword}})
        else:
            should_queries.append({"term": {}})

        should_queries.append(
            {
                "multi_match": {
                    "query": search_request.keyword,
                    "fields": search_request.fields,
                }
            }
        )

        body = {
            "query": {
                "bool": {
                    "should": should_queries,
                    "filter": self._build_filters(search_request),
                    "minimum_should_match": 1,
                },
            },
        }

        # Set multi_match type if provided
        if search_request.match:
            body["query"]["bool"]["should"][-1]["multi_match"]["type"] = (
                search_request.match
            )

        if search_request.limit:
            body["size"] = search_request.limit

        if search_request.page and search_request.limit:
            body["from"] = (search_request.page - 1) * search_request.limit

        if search_request.sort_by and search_request.order_by:
            body["sort"] = [
                {search_request.sort_by: {"order": search_request.order_by}}
            ]

        return body

    def _build_filters(self, search_request: RequestBody) -> List[dict]:
        """
        Build the filter part of the Elasticsearch query based on the provided parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            List[dict]: A list of filter dictionaries for Elasticsearch.
        """
        filters = []

        date_range = self._build_range_filter(
            SortField.DATE.value, search_request.date_from, search_request.date_to
        )
        if date_range:
            filters.append(date_range)

        height_range = self._build_range_filter(
            SortField.HEIGHT.value, search_request.height_min, search_request.height_max
        )
        if height_range:
            filters.append(height_range)

        width_range = self._build_range_filter(
            SortField.WIDTH.value, search_request.width_min, search_request.width_max
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
