from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class FastAPIClient:
    """
    FastAPIClient initializes and configures the FastAPI application for the Imago Coding Challenge API.

    This class sets up the FastAPI app with metadata for automatic OpenAPI documentation, including title, description, and version.
    It also configures CORS middleware to allow cross-origin requests, which is essential for frontend-backend integration during development and production.
    """

    def __init__(self, lifespan):
        """
        Initialize the FastAPI application with OpenAPI metadata and CORS middleware.

        Args:
            lifespan (asyncio.Lifespan): Lifespan context manager for the FastAPI app.
        """
        self.app = FastAPI(
            title="Imago Coding Challenge API",
            description="""
            The Imago Coding Challenge API provides endpoints for searching and retrieving media items from an Elasticsearch backend.\n\n
            **Features:**
            - Advanced search with filters and sorting
            - Pagination support
            - Health check endpoint
            - OpenAPI/Swagger documentation available at `/docs` and `/redoc`
            """,
            version="1.0.0",
            lifespan=lifespan,
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
