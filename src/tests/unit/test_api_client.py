import logging
from unittest.mock import AsyncMock, Mock
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError

from src.api.routes import Routes
from src.api.models import ResponseBody


@pytest.fixture
def mock_logger():
    return Mock(spec=logging.Logger)


@pytest.fixture
def mock_media_search_service():
    service = Mock(spec=[])
    service.search_media = AsyncMock()
    return service


@pytest.fixture
def test_app(mock_media_search_service, mock_logger):
    routes = Routes(lambda: mock_media_search_service, mock_logger)
    app = FastAPI()
    app.include_router(routes.router)
    return app


def test_health_check(test_app):
    client = TestClient(test_app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_search_success(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.return_value = ResponseBody(
        total_results=2,
        results=[{"media_url": "url1"}, {"media_url": "url2"}],
        page=1,
        limit=5,
        has_next=False,
        has_previous=False,
    )
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 200
    assert resp.json()["total_results"] == 2
    assert resp.json()["results"] == [{"media_url": "url1"}, {"media_url": "url2"}]


def test_search_with_missing_keyword(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ValueError(
        "Keyword is required."
    )
    params = {
        "keyword": "",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400


def test_search_with_missing_fields(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ValueError(
        "Fields are required."
    )
    params = {
        "keyword": "sunset",
        "fields": "",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400


def test_search_bad_request_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    meta = SimpleNamespace(status=400)
    mock_media_search_service.search_media.side_effect = BadRequestError(
        meta=meta, body={}, message="Bad request"
    )
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


def test_search_transport_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = TransportError(
        "transport error"
    )
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 502
    assert "transport error" in resp.json()["detail"].lower()


def test_search_connection_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ConnectionError(
        "connection error"
    )
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 503
    assert "connection error" in resp.json()["detail"].lower()


def test_search_key_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = KeyError("missing field")
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "required field" in resp.json()["detail"].lower()


def test_search_value_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ValueError("bad value")
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "bad value" in resp.json()["detail"].lower()


def test_search_unhandled_exception(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = Exception("unexpected")
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 500
    assert "unexpected error" in resp.json()["detail"].lower()
