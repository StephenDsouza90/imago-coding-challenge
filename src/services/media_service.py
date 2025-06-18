import logging
import json
import hashlib

from src.es.handler import ElasticsearchHandler
from src.cache.handler import RedisHandler
from src.api.models import (
    RequestBody,
    ResponseBody,
)


class MediaSearchService:
    """
    MediaSearchService coordinates search operations between Elasticsearch and Redis cache.

    This service validates input, manages caching, and transforms Elasticsearch results into API responses.
    """

    def __init__(
        self,
        elasticsearch_handler: ElasticsearchHandler,
        logger: logging.Logger,
        redis_handler: RedisHandler,
    ):
        """
        MediaSearchService
        -------------
        Initialize the MediaSearchService with handlers for Elasticsearch and Redis, and a logger.

        Args:
            elasticsearch_handler (ElasticsearchHandler): The Elasticsearch handler.
            redis_handler (RedisHandler): The Redis handler for caching.
            logger (logging.Logger): The logger instance for logging messages.
        """
        self.elasticsearch_handler = elasticsearch_handler
        self.redis_handler = redis_handler
        self.logger = logger

    async def search_media(self, search_request: RequestBody) -> ResponseBody:
        """
        Media Search
        -------------
        Search for media items using the provided query parameters.
        Handles validation, caching, and result transformation.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            MediaSearchResponse: A response object containing the search results, total count, and pagination info.

        Raises:
            ValueError: If the keyword is not provided or is less than 2 characters long.
        """
        try:
            cache_key = self._make_cache_key(search_request)
            cached_response = await self.redis_handler.get(cache_key)
            if cached_response:
                self.logger.info("Cache hit for search request.")
                cached_response = json.loads(cached_response)
                return ResponseBody(**cached_response)

            es_response = await self.elasticsearch_handler.search_media(search_request)
            total_results = es_response["hits"]["total"]["value"]
            results = es_response["hits"]["hits"]

            # Use list comprehension to process results
            processed_results = [
                {
                    **hit,
                    "media_url": self._generate_image_url(
                        hit["_source"].get("db"), hit["_source"].get("bildnummer")
                    ),
                    "title": hit["_source"].get("suchtext", "")[:80],
                }
                for hit in results
            ]

            response = ResponseBody(
                total_results=total_results,
                results=processed_results,
                page=search_request.page,
                limit=search_request.limit,
                has_next=(search_request.page * search_request.limit) < total_results,
                has_previous=search_request.page > 1,
            )

            await self.redis_handler.set(
                cache_key, json.dumps(response.model_dump()), expire=3600
            )
            self.logger.info("Cache set for search request.")

            return response

        except Exception as e:
            self.logger.error(f"Error during media search: {e}")
            raise

    def _make_cache_key(self, search_request: RequestBody) -> str:
        """
        Generate Cache Key
        -------------
        Generate a unique and stable cache key based on the search request parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters to generate the cache key from.

        Returns:
            str: The generated cache key.
        """
        dumped = json.dumps(search_request.model_dump(mode="json"), sort_keys=True)
        h = hashlib.blake2b(dumped.encode(), digest_size=16).hexdigest()
        return f"media_search:{h}"

    def _generate_image_url(
        self,
        database: str,
        image_number: str,
        file_prefix: str = "s",
        file_format: str = "jpg",
    ) -> str:
        """
        Generate Image URL
        -------------
        Generate a URL for the image based on the database and image number.

        Args:
            database (str): The database from which the image is retrieved (e.g., "stock" or "sp").
            image_number (str): The image number to be used in the URL.
            file_prefix (str): The prefix for the image file (default is "s").
            file_format (str): The format of the image file (default is "jpg").

        Returns:
            str: The generated URL for the image.
        """
        database_code = self._get_database_code(database)
        formatted_image_number = self._get_formatted_image_number(image_number)
        return f"https://www.imago-images.de/bild/{database_code}/{formatted_image_number}/{file_prefix}.{file_format}"

    def _get_database_code(self, database: str) -> str:
        """
        Get Database Code
        -------------
        Get the database code based on the database name.

        Args:
            database (str): The database name (e.g., "stock" or "sp").

        Returns:
            str: The database code (e.g., "st" for stock or "sp" for sp).
        """
        return "st" if database == "stock" else "sp"

    def _get_formatted_image_number(
        self, image_number: str, max_length: int = 10, pad_with: str = "0"
    ) -> str:
        """
        Format Image Number
        -------------
        Format the image number to ensure it is 10 digits long.

        Args:
            image_number (str): The image number to format.

        Returns:
            str: The formatted image number, padded with leading zeros if necessary.
        """
        formatted_image_number = image_number

        if len(image_number) == max_length:
            formatted_image_number = image_number
        elif len(image_number) < max_length:
            formatted_image_number = (
                pad_with * (max_length - len(image_number)) + image_number
            )

        return formatted_image_number
