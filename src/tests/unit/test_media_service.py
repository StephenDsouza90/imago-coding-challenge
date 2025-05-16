from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from src.services.media_service import MediaSearchService
from src.api.models import RequestBody, Field, SortOrder, SortField, Limit


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_elasticsearch_handler():
    handler = MagicMock()
    handler.search_media = AsyncMock()
    return handler


@pytest.fixture
def service(mock_elasticsearch_handler, mock_logger):
    return MediaSearchService(mock_elasticsearch_handler, mock_logger)


def get_test_params() -> RequestBody:
    return RequestBody(
        keyword="test",
        fields=[Field.KEYWORD.value],
        limit=Limit.MEDIUM.value,
        page=1,
        sort_by=SortField.DATE.value,
        order_by=SortOrder.ASC.value,
    )

@pytest.mark.asyncio
async def test_search_media_success(service, mock_elasticsearch_handler):
    mock_response = {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {"_source": {"db": "stock", "bildnummer": "123"}},
                {"_source": {"db": "sp", "bildnummer": "456"}},
            ],
        }
    }
    mock_elasticsearch_handler.search_media.return_value = mock_response
    request = get_test_params()
    response = await service.search_media(request)
    assert response.total_results == 2
    assert len(response.results) == 2
    assert response.page == 1
    assert response.limit == 10
    assert response.has_next is False
    assert response.has_previous is False
    for hit in response.results:
        assert "media_url" in hit


@pytest.mark.asyncio
async def test_search_media_with_key_error(service, mock_elasticsearch_handler):
    mock_response = {"hits": {}}
    mock_elasticsearch_handler.search_media.return_value = mock_response
    request = get_test_params()
    with pytest.raises(KeyError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_keyword(service):
    request = get_test_params()
    request.keyword = ""
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_field(service):
    request = get_test_params()
    request.fields = ["Invalid Field"]
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_wildcard_injection(service):
    """
    Wildcard injection is a common attack in Elasticsearch queries.
    This test checks if the service correctly raises an error when a wildcard is used in the keyword.
    """
    request = get_test_params()
    request.keyword = "*"
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_query_dsl_injection(service):
    """
    Query DSL (Domain Specific Language) injection is a common attack in Elasticsearch queries.

    This test checks if the service correctly raises an error when a query DSL is used in the keyword.
    """
    request = get_test_params()
    request.keyword = '{ "query": { "match_all": {} } }'
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_reserved_characters(service):
    """
    Reserved characters in Elasticsearch queries can lead to unexpected behavior.
    This test checks if the service correctly raises an error when reserved characters are used in the keyword.
    """
    request = get_test_params()
    request.keyword = "+ - = && || > < ! ( ) { } [ ] ^ \" ~ * ? : \\"
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_height_range(service):
    request = get_test_params()
    request.height_min = 2000
    request.height_max = 1000
    with pytest.raises(
        ValueError, match="height_min must be less than or equal to height_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_width_range(service):
    request = get_test_params()
    request.width_min = 2000
    request.width_max = 1000
    with pytest.raises(
        ValueError, match="width_min must be less than or equal to width_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_from_format(service):
    request = get_test_params()
    request.date_from = "2024-01-32"
    with pytest.raises(ValueError, match="date_from must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_to_format(service):
    request = get_test_params()
    request.date_to = "2024-02-32"
    with pytest.raises(ValueError, match="date_to must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_range(service):
    request = get_test_params()
    request.date_from = "2024-01-10"
    request.date_to = "2024-01-01"
    with pytest.raises(
        ValueError, match="date_from must be less than or equal to date_to"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_limit_zero(service):
    request = get_test_params()
    request.limit = 0
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_limit_negative(service):
    request = get_test_params()
    request.limit = -5
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_page_zero(service):
    request = get_test_params()
    request.page = 0
    with pytest.raises(ValueError, match="Page must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_page_negative(service):
    request = get_test_params()
    request.page = -2
    with pytest.raises(ValueError, match="Page must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_over_max_limit(service):
    request = get_test_params()
    request.limit = Limit.MAX.value + 1
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_request_body_invalid_sort(service):
    request = get_test_params()
    request.sort_by = "invalid_sort"
    with pytest.raises(ValueError, match="Invalid sort field: invalid_sort"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_request_body_invalid_order(service):
    request = get_test_params()
    request.order_by = "invalid_order"
    with pytest.raises(ValueError, match="Invalid order: invalid_order"):
        await service.search_media(request)


def test_generate_image_url(service):
    url = service._generate_image_url("stock", "123")
    assert url.startswith("https://www.imago-images.de/bild/st/")

    url2 = service._generate_image_url("sp", "456", file_prefix="m", file_format="png")
    assert url2.endswith("/m.png")


def test_is_valid_date(service):
    assert service._is_valid_date("2024-01-01")
    assert not service._is_valid_date("2024-13-01")
    assert not service._is_valid_date("bad-date")


def test_get_formatted_image_number(service):
    assert service._get_formatted_image_number("123") == "0000000123"
    assert service._get_formatted_image_number("1234567890") == "1234567890"
