import random
import time
import asyncio

import pytest
import httpx

from src.api.models import Field, Match, SortField, SortOrder, Limit

BASE_URL = "http://0.0.0.0:8000"


def _get_random_keyword() -> str:
    keywords = [
        "nature",
        "city",
        "people",
        "animals",
        "technology",
        "food",
        "travel",
        "sports",
        "art",
        "music",
        "New York",
        "Northern Lights",
        "Grand Canyon",
        "Great Wall of China",
        "Golden Gate Bridge",
        "Mount Everest",
        "Eiffel Tower",
        "Statue of Liberty",
        "Sydney Opera House",
        "Machu Picchu",
    ]
    return random.choice(keywords)


def _get_fields() -> list:
    return [Field.KEYWORD.value, Field.PHOTOGRAPHER.value]


def _get_random_match() -> str:
    matches = [
        Match.WORDS.value,
        Match.MOST.value,
        Match.CROSS.value,
        Match.PHRASE.value,
        Match.PHRASE_PREFIX.value,
    ]
    return random.choice(matches)


def _get_random_limit() -> int:
    limits = [Limit.SMALL.value, Limit.MEDIUM.value, Limit.LARGE.value]
    return random.choice(limits)


def _get_random_sort_by() -> str:
    sort_fields = [SortField.DATE.value, SortField.WIDTH.value, SortField.HEIGHT.value]
    return random.choice(sort_fields)


def _get_random_order_by() -> str:
    order_by = [SortOrder.ASC.value, SortOrder.DESC.value]
    return random.choice(order_by)


def generate_random_request_body() -> dict:
    body = {
        "keyword": _get_random_keyword(),
        "fields": _get_fields(),
        "match": _get_random_match(),
        "limit": _get_random_limit(),
        "page": 1,
        "sort_by": _get_random_sort_by(),
        "order_by": _get_random_order_by(),
    }
    return body


@pytest.mark.asyncio
async def test_app_performance_load():
    NUM_REQUESTS = 5000  # Adjust as needed
    CONCURRENCY = 50  # Number of concurrent requests
    results = []

    async def send_request(client):
        start = time.perf_counter()
        try:
            resp = await client.get(
                "/api/media/search", params=generate_random_request_body()
            )
            elapsed = time.perf_counter() - start
            return {
                "status": resp.status_code,
                "elapsed": elapsed,
            }
        except Exception as e:
            elapsed = time.perf_counter() - start
            return {
                "status": None,
                "elapsed": elapsed,
                "error": str(e),
            }

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        tasks = []

        # Create a list of tasks
        for _ in range(NUM_REQUESTS):
            tasks.append(send_request(client))

        # Run in batches to avoid overwhelming the system
        for i in range(0, NUM_REQUESTS, CONCURRENCY):
            batch = tasks[i : i + CONCURRENCY]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)

    # Metrics
    success = [r for r in results if r["status"] == 200]
    failures = [r for r in results if r["status"] != 200]
    times = [r["elapsed"] for r in results if r["status"] == 200]
    if times:
        avg = sum(times) / len(times)
        min_t = min(times)
        max_t = max(times)
        p95 = sorted(times)[int(0.95 * len(times)) - 1]
    else:
        avg = min_t = max_t = p95 = None

    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Success: {len(success)}")
    print(f"Failures: {len(failures)}")
    if avg is not None:
        print(f"Avg response time: {avg:.4f}s")
        print(f"Min response time: {min_t:.4f}s")
        print(f"Max response time: {max_t:.4f}s")
        print(f"95th percentile: {p95:.4f}s")
    else:
        print("Avg response time: N/A")
        print("Min response time: N/A")
        print("Max response time: N/A")
        print("95th percentile: N/A")
    if failures:
        print(f"Failure details: {failures[:5]}")
