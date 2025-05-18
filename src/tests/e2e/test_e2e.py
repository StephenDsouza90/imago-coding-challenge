import pytest
import httpx

from src.api.models import Field, Match, SortField, SortOrder, Limit

BASE_URL = "http://0.0.0.0:8000"


@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_media_search_success():
    params = {
        "keyword": "northern lights",
        "fields": [Field.KEYWORD.value, Field.PHOTOGRAPHER.value],
        "match": [Match.PHRASE.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        data = resp.json()
        for result in data["results"]:
            media_url = result["media_url"]
            media_url_id = media_url.split("/")[-2]
            assert len(media_url_id) == 10
        assert "total_results" in data
        assert "page" in data
        assert "limit" in data
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_media_search_success_with_date():
    params = {
        "keyword": "sunshine",
        "fields": [Field.KEYWORD.value, Field.PHOTOGRAPHER.value],
        "limit": Limit.SMALL.value,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
        "date_from": "2023-01-01",
        "date_to": "2023-12-31",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        data = resp.json()
        for result in data["results"]:
            media_url = result["media_url"]
            media_url_id = media_url.split("/")[-2]
            assert len(media_url_id) == 10
        assert "total_results" in data
        assert "page" in data
        assert "limit" in data
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_media_search_success_with_invalid_date():
    params = {
        "keyword": "sunset",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.HEIGHT.value,
        "order_by": SortOrder.DESC.value,
        "date_from": "2023-13-01",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "The search request has a bad value. Please check your parameters and try again."
        }


@pytest.mark.asyncio
async def test_media_search_success_with_height_and_width():
    params = {
        "keyword": "mercedes",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
        "date_from": "2023-01-01",
        "date_to": "2024-12-31",
        "height_min": 1000,
        "height_max": 3000,
        "width_min": 1000,
        "width_max": 5000,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        data = resp.json()
        for result in data["results"]:
            media_url = result["media_url"]
            media_url_id = media_url.split("/")[-2]
            assert len(media_url_id) == 10
        assert "total_results" in data
        assert "page" in data
        assert "limit" in data
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_media_search_success_with_invalid_height_and_width():
    params = {
        "keyword": "mercedes",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
        "date_from": "2023-01-01",
        "date_to": "2024-12-31",
        "height_min": 3000,
        "height_max": 1000,
        "width_min": 5000,
        "width_max": 1000,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "The search request has a bad value. Please check your parameters and try again."
        }


@pytest.mark.asyncio
async def test_media_search_missing_keyword():
    params = {
        "keyword": "",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "The search request has a bad value. Please check your parameters and try again."
        }


@pytest.mark.asyncio
async def test_media_search_invalid_field():
    params = {
        "keyword": "sunset",
        "fields": ["invalid field"],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "The search request has a bad value. Please check your parameters and try again."
        }


@pytest.mark.asyncio
async def test_media_search_invalid_limit():
    params = {
        "keyword": "sunset",
        "fields": [Field.KEYWORD.value],
        "limit": 0,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": SortOrder.ASC.value,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 422
        assert resp.json() == {
            "detail": [
                {
                    "type": "enum",
                    "loc": ["query", "limit"],
                    "msg": "Input should be 5, 10, 20, 50 or 100",
                    "input": "0",
                    "ctx": {"expected": "5, 10, 20, 50 or 100"},
                }
            ]
        }


@pytest.mark.asyncio
async def test_media_search_invalid_sort_by():
    params = {
        "keyword": "sunset",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": "invalid sort",
        "order_by": SortOrder.ASC.value,
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 422
        assert resp.json() == {
            "detail": [
                {
                    "type": "enum",
                    "loc": ["query", "sort_by"],
                    "msg": "Input should be 'datum', 'breite' or 'hoehe'",
                    "input": "invalid sort",
                    "ctx": {"expected": "'datum', 'breite' or 'hoehe'"},
                }
            ]
        }


@pytest.mark.asyncio
async def test_media_search_invalid_order_by():
    params = {
        "keyword": "sunset",
        "fields": [Field.KEYWORD.value],
        "limit": Limit.SMALL.value,
        "page": 1,
        "sort_by": SortField.DATE.value,
        "order_by": "invalid order",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 422
        assert resp.json() == {
            "detail": [
                {
                    "type": "enum",
                    "loc": ["query", "order_by"],
                    "msg": "Input should be 'asc' or 'desc'",
                    "input": "invalid order",
                    "ctx": {"expected": "'asc' or 'desc'"},
                }
            ]
        }
