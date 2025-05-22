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


def test_generate_image_url(service):
    url = service._generate_image_url("stock", "123")
    assert url.startswith("https://www.imago-images.de/bild/st/")

    url2 = service._generate_image_url("sp", "456", file_prefix="m", file_format="png")
    assert url2.endswith("/m.png")


def test_get_formatted_image_number(service):
    assert service._get_formatted_image_number("123") == "0000000123"
    assert service._get_formatted_image_number("1234567890") == "1234567890"
