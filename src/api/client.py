from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class FastAPIClient:
    """
    API class to initialize the FastAPI application.
    """

    def __init__(self):
        """
        Initializes the FastAPI application with title, description, and version.
        Adds CORS middleware to allow cross-origin requests.
        """
        self.app = FastAPI(
            title="MediaSearch",
            description="A media search API",
            version="1.0.0",
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
