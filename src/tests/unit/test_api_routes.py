from unittest.mock import AsyncMock, Mock
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from elasticsearch.exceptions import BadRequestError, TransportError, ConnectionError

from src.api.routes import Routes
from src.api.models import (
    ResponseBody,
    Field,
    SortField,
    SortOrder,
    Limit,
    is_valid_date,
)


def get_test_params() -> dict:
    return {
        "keyword": "sunset",
        "fields": [Field.KEYWORD.value, Field.PHOTOGRAPHER.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
    }


@pytest.fixture
def mock_media_search_service():
    service = Mock(spec=[])
    service.search_media = AsyncMock()
    return service


@pytest.fixture
def test_app(mock_media_search_service):
    routes = Routes(lambda: mock_media_search_service)
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
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 200
    assert resp.json()["total_results"] == 2
    assert resp.json()["results"] == [{"media_url": "url1"}, {"media_url": "url2"}]


def test_search_success_with_multiple_fields(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.return_value = ResponseBody(
        total_results=2,
        results=[{"media_url": "url1"}, {"media_url": "url2"}],
        page=1,
        limit=5,
        has_next=False,
        has_previous=False,
    )
    params = get_test_params()
    params["fields"] = [Field.KEYWORD.value, Field.PHOTOGRAPHER.value]
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 200
    assert resp.json()["total_results"] == 2
    assert resp.json()["results"] == [{"media_url": "url1"}, {"media_url": "url2"}]


def test_search_with_missing_keyword(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["keyword"] = ""  # missing keyword
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_page_zero(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["page"] = 0  # invalid page
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_page_negative(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["page"] = -2  # invalid page
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_elasticsearch_wildcard_injection(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["keyword"] = "*"  # wildcard injection
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_elasticsearch_query_dsl_injection(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["keyword"] = '{ "query": { "match_all": {} } }'  # query DSL injection
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_elasticsearch_reserved_characters(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["keyword"] = (
        '+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \\'  # reserved characters
    )
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_missing_fields(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["fields"] = []
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 200


def test_search_with_invalid_width_range(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["width_min"] = 2000  # Invalid width range
    params["width_max"] = 1000
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_height_range(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["height_min"] = 2000  # Invalid width range
    params["height_max"] = 1000
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_date_range(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["date_from"] = "2024-01-10"  # Valid date format - higher from date
    params["date_to"] = "2024-01-01"
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_date_from_format(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["date_from"] = "2024-01-32"  # Invalid date format
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_date_to_format(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["date_to"] = "2024-02-32"  # Invalid date format
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_is_valid_date():
    assert is_valid_date("2024-01-01")
    assert not is_valid_date("2024-13-01")
    assert not is_valid_date("bad-date")


def test_search_with_over_max_limit(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["limit"] = Limit.MAX.value + 1  # Exceeding max limit
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_limit_negative(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["limit"] = -5  # Invalid limit
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_limit_zero(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["limit"] = 0  # Invalid limit
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_request_body_invalid_sort(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["sort_by"] = "invalid_sort"  # Invalid sort field
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_request_body_invalid_order(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["order_by"] = "invalid_order"  # Invalid order
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_with_invalid_field(test_app):
    client = TestClient(test_app)
    params = get_test_params()
    params["fields"] = ["Invalid Field"]  # Invalid field
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 422


def test_search_bad_request_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    meta = SimpleNamespace(status=400)
    mock_media_search_service.search_media.side_effect = BadRequestError(
        meta=meta, body={}, message="Bad request"
    )
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


def test_search_transport_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = TransportError(
        "transport error"
    )
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 502
    assert "transport error" in resp.json()["detail"].lower()


def test_search_connection_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ConnectionError(
        "connection error"
    )
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 503
    assert "connection error" in resp.json()["detail"].lower()


def test_search_key_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = KeyError("missing field")
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "required field" in resp.json()["detail"].lower()


def test_search_value_error(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = ValueError("bad value")
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 400
    assert "bad value" in resp.json()["detail"].lower()


def test_search_unhandled_exception(test_app, mock_media_search_service):
    client = TestClient(test_app)
    mock_media_search_service.search_media.side_effect = Exception("unexpected")
    params = get_test_params()
    resp = client.get("/api/media/search", params=params)
    assert resp.status_code == 500
    assert "unexpected error" in resp.json()["detail"].lower()
