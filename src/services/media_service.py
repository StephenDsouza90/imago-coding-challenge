import logging
from datetime import datetime

from src.es.handler import ElasticsearchHandler
from src.api.models import (
    RequestBody,
    ResponseBody,
    Field,
    SortOrder,
    SortField,
)


class MediaSearchService:
    def __init__(
        self, elasticsearch_handler: ElasticsearchHandler, logger: logging.Logger
    ):
        """
        Initialize the MediaSearchService with an Elasticsearch client.

        Args:
            elasticsearch_handler (ElasticsearchHandler): The Elasticsearch handler.
            logger (logging.Logger): The logger instance for logging messages.
        """
        self.elasticsearch_handler = elasticsearch_handler
        self.logger = logger

    async def search_media(
        self, search_request: RequestBody
    ) -> ResponseBody:
        """
        Search for media based on the provided query parameters.

        Args:
            search_request (MediaSearchRequest): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            MediaSearchResponse: A response object containing the search results, total count, and pagination info.

        Raises:
            ValueError: If the keyword is not provided or is less than 2 characters long.
        """
        try:
            self._validate_search_request(search_request)
            response = await self.elasticsearch_handler.search_media(search_request)
            total_results = response["hits"]["total"]["value"]
            results = response["hits"]["hits"]
            processed_results = []
            for hit in results:
                source = hit["_source"]
                hit["media_url"] = self._generate_image_url(
                    source.get("db"), source.get("bildnummer")
                )
                processed_results.append(hit)

        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise ValueError("Invalid input: " + str(ve))

        except KeyError as ke:
            self.logger.error(
                f"Key error: {ke}. Elasticsearch response: {locals().get('response', None)}"
            )
            raise KeyError(
                "A required field was missing in the Elasticsearch response."
            )

        except Exception as e:
            self.logger.error(f"Unexpected error during media search: {e}")
            raise Exception("An unexpected error occurred while searching for media.")

        return ResponseBody(
            total_results=total_results,
            results=processed_results,
            page=search_request.page,
            limit=search_request.limit,
            has_next=(search_request.page * search_request.limit) < total_results,
            has_previous=search_request.page > 1,
        )

    def _validate_search_request(self, search_request: RequestBody):
        """
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

        if not search_request.fields:
            self.logger.error("At least one field is required.")
            raise ValueError("At least one field is required.")

        valid_fields = Field.__members__.values()
        for field in search_request.fields:
            if field not in valid_fields:
                self.logger.error(f"Invalid field: {field}")
                raise ValueError(f"Invalid field: {field}")

        if search_request.limit <= 0:
            self.logger.error("Limit must be a positive integer.")
            raise ValueError("Limit must be a positive integer.")

        if search_request.page <= 0:
            self.logger.error("Page must be a positive integer.")
            raise ValueError("Page must be a positive integer.")

        sort_fields = SortField.__members__.values()
        if search_request.sort_by not in sort_fields:
            self.logger.error(f"Invalid sort field: {search_request.sort_by}")
            raise ValueError(f"Invalid sort field: {search_request.sort_by}")

        order_fields = SortOrder.__members__.values()
        if search_request.order_by not in order_fields:
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
        Get the database code based on the database name.

        Args:
            database (str): The database name (e.g., "stock" or "sp").

        Returns:
            str: The database code (e.g., "st" for stock or "sp" for sp).
        """
        return "st" if database == "stock" else "sp"

    def _get_formatted_image_number(self, image_number: str) -> str:
        if len(image_number) > 10:
            # TODO: Handle this case
            pass

        if len(image_number) == 10:
            formatted_image_number = image_number
        elif len(image_number) < 10:
            formatted_image_number = "0" * (10 - len(image_number)) + image_number

        return formatted_image_number

    def _remove_unwanted_fields(self, data: dict) -> dict:
        """
        Remove unwanted fields from the data dictionary.
        This method is used to clean up the data before returning it to the client.

        Args:
            data (dict): The input data dictionary.

        Returns:
            dict: The cleaned-up data dictionary.
        """
        # TODO : Check if this is needed
        fields_to_remove = [
            "bildnummer",
            "datum",
            "suchtext",
            "fotografen",
            "hoehe",
            "breite",
            "db",
        ]

        for field in fields_to_remove:
            data.pop(field, None)

        return data
