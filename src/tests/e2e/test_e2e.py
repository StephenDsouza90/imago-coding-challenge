import pytest
import httpx

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
        "fields": ["suchtext"],
        "match": ["phrase"],
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
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
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
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
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
        "date_from": "2023-13-01",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {
            "detail": "Invalid input: date_from must be in YYYY-MM-DD format."
        }


@pytest.mark.asyncio
async def test_media_search_success_with_height_and_width():
    params = {
        "keyword": "mercedes",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
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
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
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
            "detail": "Invalid input: height_min must be less than or equal to height_max."
        }


@pytest.mark.asyncio
async def test_media_search_missing_keyword():
    params = {
        "keyword": "",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        assert resp.json() == {"detail": "Invalid input: Keyword is required."}


@pytest.mark.asyncio
async def test_media_search_invalid_field():
    params = {
        "keyword": "sunset",
        "fields": "invalid field",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get("/api/media/search", params=params)
        assert resp.status_code == 400
        print(resp.json())
        assert resp.json() == {"detail": "Invalid input: Invalid field: invalid field"}


@pytest.mark.asyncio
async def test_media_search_invalid_limit():
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 0,
        "page": 1,
        "sort_by": "datum",
        "order_by": "asc",
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
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "invalidsort",
        "order_by": "asc",
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
                    "input": "invalidsort",
                    "ctx": {"expected": "'datum', 'breite' or 'hoehe'"},
                }
            ]
        }


@pytest.mark.asyncio
async def test_media_search_invalid_order_by():
    params = {
        "keyword": "sunset",
        "fields": "suchtext",
        "limit": 5,
        "page": 1,
        "sort_by": "datum",
        "order_by": "invalidorder",
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
                    "input": "invalidorder",
                    "ctx": {"expected": "'asc' or 'desc'"},
                }
            ]
        }
