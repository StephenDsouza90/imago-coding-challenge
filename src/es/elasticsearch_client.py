from typing import Tuple

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import BadRequestError

from src.api.models import MediaSearchQuery


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
        self.client = Elasticsearch(
            [f"{host}:{port}"],
            http_auth=(username, password),
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout,
            verify_certs=False,
        )

    def ping(self) -> bool:
        """
        Check if the Elasticsearch client is alive.

        Returns:
            bool: True if the client is alive, False otherwise.
        """
        is_alive = False

        if self.client.ping():
            is_alive = True

        return is_alive

    def search_media(self, params: MediaSearchQuery) -> Tuple[int, list]:
        """
        Search for media in the Elasticsearch index based on the provided parameters.

        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.
        
        Returns:
            Tuple[int, list]: A tuple containing the total number of results and the list of media items.
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
                    "filter": []
                },
            },
        }

        # Date Range Filters
        if params.date_from or params.date_to:
            date_range = {}
            if params.date_from:
                date_range["gte"] = params.date_from
            if params.date_to:
                date_range["lte"] = params.date_to
            body["query"]["bool"]["filter"].append({
                "range": {"datum": date_range}
            })

        # Height Range Filters
        if params.height_min or params.height_max:
            height_range = {}
            if params.height_min is not None:
                height_range["gte"] = params.height_min
            if params.height_max is not None:
                height_range["lte"] = params.height_max
            body["query"]["bool"]["filter"].append({
                "range": {"hoehe": height_range}
            })

        # Width Range Filters
        if params.width_min or params.width_max:
            width_range = {}
            if params.width_min is not None:
                width_range["gte"] = params.width_min
            if params.width_max is not None:
                width_range["lte"] = params.width_max
            body["query"]["bool"]["filter"].append({
                "range": {"breite": width_range}
            })

        # Limit
        if params.limit:
            body["size"] = params.limit

        # Pagination
        if params.page and params.limit:
            body["from"] = (params.page - 1) * params.limit

        # Sorting
        if params.sort_by and params.order_by:
            body["sort"] = [{params.sort_by: {"order": params.order_by}}]

        try:
            response = self.client.search(index=self.INDEX, body=body)

        except BadRequestError as e:
            raise BadRequestError(message=f"Bad request: {str(e)}", meta=e.meta, body=e.body)

        except Exception as e:
            raise Exception(f"Error while searching in Elasticsearch: {str(e)}")

        total_results = response["hits"]["total"]["value"]
        results = response["hits"]["hits"]
        return total_results, results
