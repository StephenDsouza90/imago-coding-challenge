from elasticsearch import Elasticsearch

from src.api.models import MediaSearchQuery, MediaSearchResponse


class ElasticsearchClient:
    """
    A class to interact with the Elasticsearch client.
    """

    INDEX = "imago"

    def __init__(self, host: str, port: int, username: str, password: str):
        """
        Initialize the Elasticsearch client.
        """
        self.client = Elasticsearch(
            [f"{host}:{port}"],
            http_auth=(username, password),
            verify_certs=False,
        )
        self.ping()

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

    # def check_index(self):
    #     # Check if the index exists
    #     if self.es_client.indices.exists(index=self.INDEX):
    #         print(f"Index '{self.INDEX}' exists")

    #         # Count total documents in the index
    #         count = self.es_client.count(index=self.INDEX)['count']
    #         print(f"Total documents in index: {count}")
    #     else:
    #         print(f"Index '{self.INDEX}' does NOT exist")

    # def get_sample_documents(self, size=5):
    #     body = {
    #         "query": {
    #             "match_all": {}  # Match all documents
    #         },
    #         "size": size
    #     }
    #     result = self.es_client.search(index=self.INDEX, body=body)
    #     sample_docs = result["hits"]["hits"]
    #     for i, doc in enumerate(sample_docs, 1):
    #         print(f"\nDocument {i}:")
    #         print(f"ID: {doc['_id']}")
    #         print("Content:")
    #         print(doc['_source'])

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
                "match": {
                    "suchtext": params.keyword,
                }
            },
            "size": params.limit,
        }

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
