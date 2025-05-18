import warnings

from elasticsearch import AsyncElasticsearch
from elastic_transport import SecurityWarning, ObjectApiResponse

from src.es.consts import HEADER


warnings.filterwarnings("ignore", category=SecurityWarning)


class ElasticsearchClient:
    """
    ElasticsearchClient manages asynchronous connections and requests to an Elasticsearch cluster.

    It handles authentication, connection settings, and provides a base for executing search and index operations.
    """

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
        ElasticsearchClient
        -------------
        Set up the AsyncElasticsearch client with connection and authentication details.
        Disables SSL certificate verification for development.

        Args:
            host (str): The Elasticsearch host.
            port (int): The Elasticsearch port.
            username (str): The Elasticsearch username.
            password (str): The Elasticsearch password.
            timeout (int, optional): The request timeout in seconds. Defaults to 30.
            max_retries (int, optional): The maximum number of retries for failed requests. Defaults to 3.
            retry_on_timeout (bool, optional): Whether to retry on timeout. Defaults to True.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_on_timeout = retry_on_timeout
        self.client = None

    def connect(self):
        self.client = AsyncElasticsearch(
            hosts=[f"{self.host}:{self.port}"],
            http_auth=(self.username, self.password),
            headers=HEADER,
            request_timeout=self.timeout,
            max_retries=self.max_retries,
            retry_on_timeout=self.retry_on_timeout,
            verify_certs=False,
        )

    async def ping(self) -> bool:
        """
        Ping
        -------------
        Check if the Elasticsearch client is alive.

        Returns:
            bool: True if the client is alive, False otherwise.
        """

        return await self.client.ping()

    async def search(self, index: str, body: dict) -> ObjectApiResponse:
        """
        Search
        -------------
        Perform a search query on the specified Elasticsearch index.

        Args:
            index (str): The name of the Elasticsearch index.
            body (dict): The search query body.

        Returns:
            ObjectApiResponse: The response from the Elasticsearch search query.
        """
        return await self.client.search(index=index, body=body)

    async def close(self):
        """
        Close
        -------------
        Close the Elasticsearch client connection.
        """
        await self.client.close()
