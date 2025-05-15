import logging
import warnings
from typing import Optional, Union, List

from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError
from elastic_transport import ObjectApiResponse, SecurityWarning

from src.api.models import RequestBody
from src.es.client import ElasticsearchClient

warnings.filterwarnings("ignore", category=SecurityWarning)


class ElasticsearchHandler:
    """
    A class to handle Elasticsearch operations.
    """

    INDEX = "imago"

    def __init__(self, client: ElasticsearchClient, logger: logging.Logger):
        """
        Initialize the Elasticsearch client.

        Args:
            client (ElasticsearchClient): The Elasticsearch client instance.
            logger (logging.Logger): The logger instance for logging.
        """
        self.client = client
        self.logger = logger

    async def search_media(
        self, search_request: RequestBody
    ) -> ObjectApiResponse:
        """
        Search for media in the Elasticsearch index based on the provided parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            ObjectApiResponse: The response from the Elasticsearch search query.
        """
        body = self._build_search_body(search_request)
        self.logger.info(f"Elasticsearch search body: {body}")

        try:
            response = await self.client.search(index=self.INDEX, body=body)

        except BadRequestError as bre:
            self.logger.error(f"Elasticsearch BadRequestError: {bre.meta}, {bre.body}")
            raise BadRequestError(
                message="The Elasticsearch query was invalid.",
                meta=bre.meta,
                body=bre.body,
            )

        except TransportError as te:
            self.logger.error(f"Elasticsearch TransportError: {te.meta}, {te.body}")
            raise TransportError(
                message="A transport error occurred while searching in Elasticsearch.",
                meta=te.meta,
                body=te.body,
            )

        except ConnectionError as ce:
            self.logger.error(f"Elasticsearch ConnectionError: {ce}")
            raise ConnectionError(
                message="A connection error occurred while searching in Elasticsearch.",
                meta=ce.meta,
                body=ce.body,
            )

        except Exception as e:
            self.logger.error(f"Elasticsearch search error: {e}")
            raise Exception("An error occurred while searching in Elasticsearch.")

        return response

    def _build_search_body(self, search_request: RequestBody) -> dict:
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
