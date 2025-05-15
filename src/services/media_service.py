from datetime import datetime

from src.es.elasticsearch_client import ElasticsearchClient
from src.api.models import MediaSearchRequest, MediaSearchResponse, Field, SortOrder, SortField


class MediaSearchService:
    def __init__(self, elasticsearch_client: ElasticsearchClient):
        """
        Initialize the MediaSearchService with an Elasticsearch client.
        """
        self.es = elasticsearch_client

    async def search_service(self, params: MediaSearchRequest) -> MediaSearchResponse:
        """
        Search for media based on the provided query parameters.
        This method allows users to search for media items using various filters and sorting options.

        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            MediaSearchResponse: A response object containing the search results, total count, and pagination info.

        Raises:
            ValueError: If the keyword is not provided or is less than 2 characters long.
        """

        try:
            self._validate_params(params)

            response = await self.es.search_media(params)
            total_results = response["hits"]["total"]["value"]
            results = response["hits"]["hits"]

            processed_results = []
            for hit in results:
                source = hit["_source"]

                hit["media_url"] = self._generate_image_url(source["db"], source["bildnummer"])
                # hit = self.remove_unwanted_fields(hit)
                processed_results.append(hit)

        except ValueError as ve:
            raise ValueError(f"Invalid input: {str(ve)}")

        except KeyError as ke:
            raise KeyError(f"Key error: {str(ke)}. Response: {response}")
        
        except Exception as e:
            raise Exception(f"Error while searching in Elasticsearch: {str(e)}")

        return MediaSearchResponse(
            total_results=total_results,
            results=processed_results,
            page=params.page,
            limit=params.limit,
            has_next=(params.page * params.limit) < total_results,
            has_previous=params.page > 1,
        )

    def _validate_params(self, params: MediaSearchRequest) -> bool:
        """
        Validate the search parameters.
        
        Args:
            params (MediaSearchRequest): The search parameters to validate.
        
        Raises:
            ValueError: If any of the parameters are invalid
        """
        # Check if the keyword is provided
        if not params.keyword:
            raise ValueError("Keyword is required.")

        # Check if the keyword is less than 2 characters
        if len(params.keyword) < 2:
            raise ValueError("Keyword must be at least 2 characters long.")

        # Validate fields
        if not params.fields:
            raise ValueError("At least one field is required.")

        # Check if the fields are valid
        valid_fields = Field.__members__.values()
        for field in params.fields:
            if field not in valid_fields:
                raise ValueError(f"Invalid field: {field}")

        # Validate limit
        if params.limit <= 0:
            raise ValueError("Limit must be a positive integer.")

        # Validate page
        if params.page <= 0:
            raise ValueError("Page must be a positive integer.")

        # Validate sort_by
        sort_fields = SortField.__members__.values()
        if params.sort_by not in sort_fields:
            raise ValueError(f"Invalid sort field: {params.sort_by}")
        
        # Validate order_by
        order_fields = SortOrder.__members__.values()
        if params.order_by not in order_fields:
            raise ValueError(f"Invalid order: {params.order_by}")

        # Validate date range
        if params.date_from and params.date_to:
            if params.date_from > params.date_to:
                raise ValueError("date_from must be less than or equal to date_to.")
        
        # Validate date range with format
        if params.date_from and not self._is_valid_date(params.date_from):
            raise ValueError("date_from must be in YYYY-MM-DD format.")
        
        if params.date_to and not self._is_valid_date(params.date_to):
            raise ValueError("date_to must be in YYYY-MM-DD format.")
        
        # Validate height range
        if params.height_min and params.height_max:
            if params.height_min > params.height_max:
                raise ValueError("height_min must be less than or equal to height_max.")
        
        # Validate width range
        if params.width_min and params.width_max:
            if params.width_min > params.width_max:
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
            return False

    def _generate_image_url(self, database: str, image_number: str, file_prefix: str = "s", file_format: str = "jpg") -> str:
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
