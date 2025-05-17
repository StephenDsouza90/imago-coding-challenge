import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError

from src.es.handler import ElasticsearchHandler
from src.api.models import RequestBody, Field, Limit, SortField, SortOrder, Match


def get_test_params() -> RequestBody:
    return RequestBody(
        keyword="test",
        fields=[Field.KEYWORD.value],
        match=Match.WORDS.value,
        limit=Limit.MEDIUM.value,
        page=1,
        sort_by=SortField.DATE.value,
        order_by=SortOrder.ASC.value,
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )


@pytest.mark.asyncio
async def test_search_media_success():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    mock_response = {"hits": {"hits": [1, 2, 3]}}
    mock_client.search = AsyncMock(return_value=mock_response)
    req = get_test_params()
    result = await handler.search_media(req)
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_media_bad_request_error():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = get_test_params()
    error = BadRequestError(message="bad request", meta=None, body=None)
    mock_client.search = AsyncMock(side_effect=error)
    with pytest.raises(BadRequestError):
        await handler.search_media(req)


@pytest.mark.asyncio
async def test_search_media_transport_error():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = get_test_params()
    error = TransportError(
        message="A transport error occurred while searching in Elasticsearch."
    )
    mock_client.search = AsyncMock(side_effect=error)
    with pytest.raises(TransportError):
        await handler.search_media(req)


@pytest.mark.asyncio
async def test_search_media_connection_error():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = get_test_params()
    error = ConnectionError(message="connection error")
    mock_client.search = AsyncMock(side_effect=error)
    with pytest.raises(ConnectionError):
        await handler.search_media(req)


@pytest.mark.asyncio
async def test_search_media_generic_exception():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = get_test_params()
    mock_client.search = AsyncMock(side_effect=Exception("unexpected error"))
    with pytest.raises(Exception):
        await handler.search_media(req)


def test_build_search_body():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = get_test_params()
    req.limit = Limit.SMALL.value
    req.page = 2
    req.date_from = "2023-01-01"
    req.date_to = "2023-12-31"
    req.height_min = 100
    req.height_max = 200
    req.width_min = 50
    req.width_max = 150
    body = handler._build_search_body(req)
    assert body["size"] == 5
    assert body["from"] == 5
    assert body["sort"] == [{"datum": {"order": "asc"}}]
    assert body["query"]["bool"]["should"][1]["multi_match"]["query"] == "test"
    assert body["query"]["bool"]["filter"][0]["range"]["datum"]["gte"] == "2023-01-01"
    assert body["query"]["bool"]["filter"][0]["range"]["datum"]["lte"] == "2023-12-31"
    assert body["query"]["bool"]["filter"][1]["range"]["hoehe"]["gte"] == 100
    assert body["query"]["bool"]["filter"][1]["range"]["hoehe"]["lte"] == 200
    assert body["query"]["bool"]["filter"][2]["range"]["breite"]["gte"] == 50
    assert body["query"]["bool"]["filter"][2]["range"]["breite"]["lte"] == 150
