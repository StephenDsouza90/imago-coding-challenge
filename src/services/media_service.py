import logging
import json
from datetime import datetime


from src.es.handler import ElasticsearchHandler
from src.cache.handler import RedisHandler
from src.api.models import (
    RequestBody,
    ResponseBody,
    Field,
    SortOrder,
    SortField,
    Limit,
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
            self._validate_search_request(search_request)

            cache_key = f"media_search:{hash(str(search_request.model_dump()))}"
            cached_response = await self.redis_handler.get(cache_key)
            if cached_response:
                self.logger.info("Cache hit for search request.")
                cached_response = json.loads(cached_response)
                return ResponseBody(**cached_response)

            es_response = await self.elasticsearch_handler.search_media(search_request)
            total_results = es_response["hits"]["total"]["value"]
            results = es_response["hits"]["hits"]

            processed_results = []
            for hit in results:
                source = hit["_source"]
                hit["media_url"] = self._generate_image_url(
                    source.get("db"), source.get("bildnummer")
                )
                processed_results.append(hit)

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

    def _validate_search_request(self, search_request: RequestBody):
        """
        Validate Search Request
        -------------
        Validate the search parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters to validate.

        Raises:
            ValueError: If any of the parameters are invalid
        """
        if not search_request.keyword:
            self.logger.error("Keyword is required.")
            raise ValueError("Keyword is required.")

        if len(search_request.keyword) < 2:
            self.logger.error("Keyword must be at least 2 characters long.")
            raise ValueError("Keyword must be at least 2 characters long.")

        if not all(char.isalnum() or char.isspace() for char in search_request.keyword):
            self.logger.error("Keyword contains invalid characters.")
            raise ValueError("Keyword contains invalid characters.")

        if not search_request.fields:
            self.logger.error("At least one field is required.")
            raise ValueError("At least one field is required.")

        valid_fields = Field.__members__.values()
        for field in search_request.fields:
            if field not in valid_fields:
                self.logger.error(f"Invalid field: {field}")
                raise ValueError(f"Invalid field: {field}")

        if search_request.limit <= 0 or search_request.limit > Limit.MAX.value:
            self.logger.error("Limit must be a positive integer.")
            raise ValueError("Limit must be a positive integer.")

        if search_request.page <= 0:
            self.logger.error("Page must be a positive integer.")
            raise ValueError("Page must be a positive integer.")

        if search_request.sort_by not in SortField.__members__.values():
            self.logger.error(f"Invalid sort field: {search_request.sort_by}")
            raise ValueError(f"Invalid sort field: {search_request.sort_by}")

        if search_request.order_by not in SortOrder.__members__.values():
            self.logger.error(f"Invalid order: {search_request.order_by}")
            raise ValueError(f"Invalid order: {search_request.order_by}")

        if search_request.date_from and search_request.date_to:
            if search_request.date_from > search_request.date_to:
                self.logger.error("date_from must be less than or equal to date_to.")
                raise ValueError("date_from must be less than or equal to date_to.")

        if search_request.date_from and not self._is_valid_date(
            search_request.date_from
        ):
            self.logger.error("date_from must be in YYYY-MM-DD format.")
            raise ValueError("date_from must be in YYYY-MM-DD format.")

        if search_request.date_to and not self._is_valid_date(search_request.date_to):
            self.logger.error("date_to must be in YYYY-MM-DD format.")
            raise ValueError("date_to must be in YYYY-MM-DD format.")

        if search_request.height_min and search_request.height_max:
            if search_request.height_min > search_request.height_max:
                self.logger.error(
                    "height_min must be less than or equal to height_max."
                )
                raise ValueError("height_min must be less than or equal to height_max.")

        if search_request.width_min and search_request.width_max:
            if search_request.width_min > search_request.width_max:
                self.logger.error("width_min must be less than or equal to width_max.")
                raise ValueError("width_min must be less than or equal to width_max.")

    def _is_valid_date(self, date_str: str) -> bool:
        """
        Validate Date Format
        -------------
        Validate if the date string is in YYYY-MM-DD format.

        Args:
            date_str (str): The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            self.logger.error(f"Invalid date format: {date_str}")
            return False

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

    def _get_formatted_image_number(self, image_number: str) -> str:
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

        if len(image_number) == 10:
            formatted_image_number = image_number
        elif len(image_number) < 10:
            formatted_image_number = "0" * (10 - len(image_number)) + image_number

        return formatted_image_number
