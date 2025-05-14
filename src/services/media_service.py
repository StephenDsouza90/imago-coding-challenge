from src.es.elasticsearch import ElasticsearchClient
from src.api.models import MediaSearchQuery


class MediaSearchService:
    def __init__(self, elasticsearch_client: ElasticsearchClient):
        """
        Initialize the MediaSearchService with an Elasticsearch client.
        """
        self.elasticsearch_client = elasticsearch_client

    def search(self, params: MediaSearchQuery) -> dict:
        """
        Search for media based on the provided query parameters.
        This method allows users to search for media items using various filters and sorting options.

        Args:
            params (MediaSearchQuery): The search parameters including query, filters, sorting, pagination, etc.

        Returns:
            dict: A dictionary containing the search results, total count, and pagination info.
        """
        search_response = self.elasticsearch_client.search_by_keyword(params)

        search_results = search_response.to_dict()

        for media_item in search_results["results"]:
            media_item["media_url"] = self.generate_image_url(
                media_item["db"], media_item["bildnummer"]
            )
            media_item = self.remove_unwanted_fields(media_item)

        return search_results

    def generate_image_url(self, database: str, image_number: str) -> str:
        """
        Generate a URL for the image based on the database and image number.

        Args:
            database (str): The database from which the image is retrieved (e.g., "stock" or "sp").
            image_number (str): The image number to be used in the URL.

        Returns:
            str: The generated URL for the image.
        """
        if database == "stock":
            database_code = "st"
        else:
            # TODO: Check if this is valid
            database_code = "sp"

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
