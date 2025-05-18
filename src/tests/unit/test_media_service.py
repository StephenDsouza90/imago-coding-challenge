from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.media_service import MediaSearchService
from src.api.models import RequestBody, Field, SortOrder, SortField, Limit


def get_test_params() -> RequestBody:
    return RequestBody(
        keyword="test",
        fields=[Field.KEYWORD.value, Field.PHOTOGRAPHER.value],
        limit=Limit.MEDIUM.value,
        page=1,
        sort_by=SortField.DATE.value,
        order_by=SortOrder.ASC.value,
    )


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_elasticsearch_handler():
    handler = MagicMock()
    handler.search_media = AsyncMock()
    return handler


@pytest.fixture
def mock_redis_handler():
    handler = MagicMock()
    handler.get = AsyncMock()
    handler.set = AsyncMock()
    return handler


@pytest.fixture
def service(mock_elasticsearch_handler, mock_logger, mock_redis_handler):
    return MediaSearchService(
        mock_elasticsearch_handler, mock_logger, mock_redis_handler
    )


@pytest.mark.asyncio
async def test_search_media_success(
    service, mock_elasticsearch_handler, mock_redis_handler
):
    mock_redis_handler.get.return_value = None
    mock_elasticsearch_handler.search_media.return_value = {
        "hits": {
            "total": {"value": 1},
            "hits": [{"_source": {"db": "stock", "bildnummer": "123"}}],
        }
    }
    request = get_test_params()
    response = await service.search_media(request)
    assert response.total_results == 1
    assert (
        response.results[0]["media_url"]
        == "https://www.imago-images.de/bild/st/0000000123/s.jpg"
    )


@pytest.mark.asyncio
async def test_search_media_with_key_error(
    service, mock_elasticsearch_handler, mock_redis_handler
):
    mock_redis_handler.get.return_value = None
    mock_elasticsearch_handler.search_media.return_value = {"hits": {}}
    request = get_test_params()
    with pytest.raises(KeyError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_field(service):
    request = get_test_params()
    request.fields = ["Invalid Field"]  # Invalid field
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_height_range(service):
    request = get_test_params()
    request.height_min = 2000  # Invalid height range
    request.height_max = 1000
    with pytest.raises(
        ValueError, match="height_min must be less than or equal to height_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_width_range(service):
    request = get_test_params()
    request.width_min = 2000  # Invalid width range
    request.width_max = 1000
    with pytest.raises(
        ValueError, match="width_min must be less than or equal to width_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_from_format(service):
    request = get_test_params()
    request.date_from = "2024-01-32"  # Invalid date format
    with pytest.raises(ValueError, match="date_from must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_to_format(service):
    request = get_test_params()
    request.date_to = "2024-02-32"  # Invalid date format
    with pytest.raises(ValueError, match="date_to must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_range(service):
    request = get_test_params()
    request.date_from = "2024-01-10"  # Valid date format - higher from date
    request.date_to = "2024-01-01"
    with pytest.raises(
        ValueError, match="date_from must be less than or equal to date_to"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_limit_zero(service, mock_redis_handler):
    mock_redis_handler.get.return_value = None
    request = get_test_params()
    request.limit = 0  # Invalid limit
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_limit_negative(service):
    request = get_test_params()
    request.limit = -5  # Invalid limit
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_over_max_limit(service):
    request = get_test_params()
    request.limit = Limit.MAX.value + 1  # Exceeding max limit
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_request_body_invalid_sort(service):
    request = get_test_params()
    request.sort_by = "invalid_sort"  # Invalid sort field
    with pytest.raises(ValueError, match="Invalid sort field: invalid_sort"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_request_body_invalid_order(service):
    request = get_test_params()
    request.order_by = "invalid_order"  # Invalid order
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
