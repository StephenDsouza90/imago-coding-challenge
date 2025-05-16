import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.es.handler import ElasticsearchHandler
from src.api.models import RequestBody


@pytest.mark.asyncio
async def test_search_media_success():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    mock_response = {"hits": {"hits": [1, 2, 3]}}
    mock_client.search = AsyncMock(return_value=mock_response)
    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=10,
        page=1,
        sort_by="datum",
        order_by="asc",
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )
    result = await handler.search_media(req)
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_media_bad_request_error():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    from elasticsearch.exceptions import BadRequestError

    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=10,
        page=1,
        sort_by="datum",
        order_by="asc",
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )
    error = BadRequestError(message="bad request", meta=None, body=None)
    mock_client.search = AsyncMock(side_effect=error)
    with pytest.raises(BadRequestError):
        await handler.search_media(req)


@pytest.mark.asyncio
async def test_search_media_transport_error():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    from elasticsearch.exceptions import TransportError

    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=10,
        page=1,
        sort_by="datum",
        order_by="asc",
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )
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
    from elasticsearch.exceptions import ConnectionError

    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=10,
        page=1,
        sort_by="datum",
        order_by="asc",
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )
    error = ConnectionError(message="connection error")
    mock_client.search = AsyncMock(side_effect=error)
    with pytest.raises(ConnectionError):
        await handler.search_media(req)


@pytest.mark.asyncio
async def test_search_media_generic_exception():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=10,
        page=1,
        sort_by="datum",
        order_by="asc",
        date_from=None,
        date_to=None,
        height_min=None,
        height_max=None,
        width_min=None,
        width_max=None,
    )
    mock_client.search = AsyncMock(side_effect=Exception("unexpected error"))
    with pytest.raises(Exception):
        await handler.search_media(req)


def test_build_search_body():
    mock_client = MagicMock()
    mock_logger = logging.getLogger("test")
    handler = ElasticsearchHandler(client=mock_client, logger=mock_logger)
    req = RequestBody(
        keyword="test",
        fields=["suchtext"],
        limit=5,
        page=2,
        sort_by="datum",
        order_by="asc",
        date_from="2023-01-01",
        date_to="2023-12-31",
        height_min=100,
        height_max=200,
        width_min=50,
        width_max=150,
    )
    body = handler._build_search_body(req)
    assert body["size"] == 5
    assert body["from"] == 5
    assert body["sort"] == [{"datum": {"order": "asc"}}]
    assert body["query"]["bool"]["must"][0]["multi_match"]["query"] == "test"
    assert body["query"]["bool"]["filter"][0]["range"]["datum"]["gte"] == "2023-01-01"
    assert body["query"]["bool"]["filter"][0]["range"]["datum"]["lte"] == "2023-12-31"
    assert body["query"]["bool"]["filter"][1]["range"]["hoehe"]["gte"] == 100
    assert body["query"]["bool"]["filter"][1]["range"]["hoehe"]["lte"] == 200
    assert body["query"]["bool"]["filter"][2]["range"]["breite"]["gte"] == 50
    assert body["query"]["bool"]["filter"][2]["range"]["breite"]["lte"] == 150
