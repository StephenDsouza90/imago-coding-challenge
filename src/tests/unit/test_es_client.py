from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from src.es.client import ElasticsearchClient


@pytest.mark.asyncio
async def test_elasticsearch_client_init():
    with patch("src.es.client.AsyncElasticsearch") as mock_es:
        client = ElasticsearchClient(
            host="localhost", port=9200, username="user", password="pass"
        )
        client.connect()
        assert hasattr(client, "client")
        mock_es.assert_called_once()


@pytest.mark.asyncio
async def test_elasticsearch_client_ping():
    with patch("src.es.client.AsyncElasticsearch") as mock_es:
        mock_instance = mock_es.return_value
        mock_instance.ping = AsyncMock(return_value=True)
        client = ElasticsearchClient(
            host="localhost", port=9200, username="user", password="pass"
        )
        client.connect()
        result = await client.ping()
        assert result is True
        mock_instance.ping.assert_called_once()


@pytest.mark.asyncio
async def test_elasticsearch_client_close():
    with patch("src.es.client.AsyncElasticsearch") as mock_es:
        mock_instance = mock_es.return_value
        mock_instance.close = AsyncMock(return_value=True)
        client = ElasticsearchClient(
            host="localhost", port=9200, username="user", password="pass"
        )
        client.connect()
        await client.client.close()
        mock_instance.close.assert_called_once()
