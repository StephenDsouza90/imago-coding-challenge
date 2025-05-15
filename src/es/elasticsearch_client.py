from elasticsearch import Elasticsearch

from src.api.models import MediaSearchQuery, MediaSearchResponse


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

    def search_by_keyword(self, params: MediaSearchQuery) -> MediaSearchResponse:
        """
        Perform a search based on a keyword.

        Args:
            params (MediaSearchQuery): The search parameters including the query string.

        Returns:
            MediaSearchResponse: An object containing the search results and total count.
        """
        body = {
            "query": {
                "multi_match": {
                    "query": params.keyword,
                    "fields": params.fields,
                },
            },
        }

        if params.limit:
            body["size"] = params.limit

        if params.page and params.limit:
            body["from"] = (params.page - 1) * params.limit

        if params.sort_by and params.order_by:
            body["sort"] = [{params.sort_by: {"order": params.order_by}}]

        response = self.client.search(index=self.INDEX, body=body)

        total_results = response["hits"]["total"]["value"]
        results = response["hits"]["hits"]

        return MediaSearchResponse(
            total_results=total_results,
            results=[hit["_source"] for hit in results],
            page=1,
            limit=len(results),
            has_next=False,
            has_previous=False,
        )
