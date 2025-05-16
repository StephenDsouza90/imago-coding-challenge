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
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
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
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(KeyError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_keyword(service):
    request = RequestBody(
        keyword="",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_field(service):
    request = RequestBody(
        keyword="test",
        fields=["InvalidField"],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_wildcard_injection(service):
    """
    Wildcard injection is a common attack in Elasticsearch queries.
    This test checks if the service correctly raises an error when a wildcard is used in the keyword.
    """
    request = RequestBody(
        keyword="*",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_query_dsl_injection(service):
    """
    Query DSL (Domain Specific Language) injection is a common attack in Elasticsearch queries.

    This test checks if the service correctly raises an error when a query DSL is used in the keyword.
    """
    request = RequestBody(
        keyword='{ "match_all": {} }',
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_elasticsearch_reserved_characters(service):
    """
    Reserved characters in Elasticsearch queries can lead to unexpected behavior.
    This test checks if the service correctly raises an error when reserved characters are used in the keyword.
    """
    request = RequestBody(
        keyword='+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \\',
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_height_range(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
        height_min=2000,
        height_max=1000,
    )
    with pytest.raises(
        ValueError, match="height_min must be less than or equal to height_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_width_range(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
        width_min=2000,
        width_max=1000,
    )
    with pytest.raises(
        ValueError, match="width_min must be less than or equal to width_max"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_from_format(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
        date_from="2024-13-01",
    )
    with pytest.raises(ValueError, match="date_from must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_to_format(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
        date_to="2024-02-30",
    )
    with pytest.raises(ValueError, match="date_to must be in YYYY-MM-DD format"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_date_range(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=1,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
        date_from="2024-01-10",
        date_to="2024-01-01",
    )
    with pytest.raises(
        ValueError, match="date_from must be less than or equal to date_to"
    ):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_limit_zero():
    with pytest.raises(ValidationError):
        RequestBody(
            keyword="test",
            fields=[Field.KEYWORD],
            limit=0,
            page=1,
            sort_by=SortField.DATE,
            order_by=SortOrder.ASC,
        )


@pytest.mark.asyncio
async def test_search_media_invalid_limit_negative():
    with pytest.raises(ValidationError):
        RequestBody(
            keyword="test",
            fields=[Field.KEYWORD],
            limit=-5,
            page=1,
            sort_by=SortField.DATE,
            order_by=SortOrder.ASC,
        )


@pytest.mark.asyncio
async def test_search_media_invalid_page_zero(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=0,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError, match="Page must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_invalid_page_negative(service):
    request = RequestBody(
        keyword="test",
        fields=[Field.KEYWORD],
        limit=10,
        page=-2,
        sort_by=SortField.DATE,
        order_by=SortOrder.ASC,
    )
    with pytest.raises(ValueError, match="Page must be a positive integer"):
        await service.search_media(request)


@pytest.mark.asyncio
async def test_search_media_over_max_limit():
    with pytest.raises(ValidationError):
        RequestBody(
            keyword="test",
            fields=[Field.KEYWORD],
            limit=Limit.MAX + 1,
            page=1,
            sort_by=SortField.DATE,
            order_by=SortOrder.ASC,
        )


def test_request_body_invalid_sort():
    with pytest.raises(ValidationError):
        RequestBody(
            keyword="test",
            fields=[Field.KEYWORD],
            limit=10,
            page=1,
            sort_by="invalid_sort",
            order_by=SortOrder.ASC,
        )


def test_request_body_invalid_order():
    with pytest.raises(ValidationError):
        RequestBody(
            keyword="test",
            fields=[Field.KEYWORD],
            limit=10,
            page=1,
            sort_by=SortField.DATE,
            order_by="invalid_order",
        )


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
