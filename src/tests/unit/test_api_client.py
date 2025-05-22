from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from src.api.client import FastAPIClient


def dummy_lifespan(app: FastAPI):
    async def lifespan_context():
        yield

    return lifespan_context


def test_fastapi_client_initialization():
    client = FastAPIClient(lifespan=dummy_lifespan)
    app = client.app
    assert app.title == "Media Search API"
    assert app.version == "1.0.0"
    cors_middleware = [mw for mw in app.user_middleware if mw.cls is CORSMiddleware]
    assert cors_middleware, "CORS middleware should be added to the app"
