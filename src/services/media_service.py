from src.es.elasticsearch_client import ElasticsearchClient
from src.api.models import MediaSearchQuery, MediaSearchResponse


class MediaSearchService:
    def __init__(self, elasticsearch_client: ElasticsearchClient):
        """
        Initialize the MediaSearchService with an Elasticsearch client.
        """
        self.elasticsearch_client = elasticsearch_client

    def search(self, params: MediaSearchQuery) -> MediaSearchResponse:
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
        if not params.keyword:
            raise ValueError("Keyword is required.")

        if len(params.keyword) < 2:
            raise ValueError("Keyword must be at least 2 characters long.")

        es_response = self.elasticsearch_client.search_by_keyword(params)

        results = []
        for hit in es_response.results:
            db = hit.get("db")
            bildnummer = hit.get("bildnummer")

            if not db or not bildnummer:
                # TODO: Add log and handle this case
                continue

            hit["media_url"] = self.generate_image_url(db, bildnummer)
            # hit = self.remove_unwanted_fields(hit)
            results.append(hit)

        return MediaSearchResponse(
            total_results=es_response.total_results,
            results=results,
            page=es_response.page,
            limit=es_response.limit,
            has_next=(params.page * params.limit)
            < es_response.total_results,  # Check if there are more results
            has_previous=es_response.has_previous,
        )

    def generate_image_url(self, database: str, image_number: str) -> str:
        """
        Generate a URL for the image based on the database and image number.

        Args:
            database (str): The database from which the image is retrieved (e.g., "stock" or "sp").
            image_number (str): The image number to be used in the URL.

        Returns:
            str: The generated URL for the image.
        """
        # Determine the database code based on the database name
        if database == "stock":
            database_code = "st"
        else:
            # TODO: Check if this is valid
            database_code = "sp"

        # Format the image number to be 10 digits long with leading zeros
        if len(image_number) > 10:
            # TODO: Handle this case
            pass
        elif len(image_number) == 10:
            formatted_image_number = image_number
        elif len(image_number) < 10:
            formatted_image_number = "0" * (10 - len(image_number)) + image_number

        file_prefix = "s"

        return f"https://www.imago-images.de/bild/{database_code}/{formatted_image_number}/{file_prefix}.jpg"

    def remove_unwanted_fields(self, data: dict) -> dict:
        """
        Remove unwanted fields from the data dictionary.
        This method is used to clean up the data before returning it to the client.

        Args:
            data (dict): The input data dictionary.

        Returns:
            dict: The cleaned-up data dictionary.
        """
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
