from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import routes
from .settings import Settings


class State(TypedDict):
    settings: Settings


def create(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[State]:
        yield {"settings": settings or Settings()}  # pyright: ignore[reportCallIssue]

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://brews.gadom.ski", "http://localhost:5173"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.add_api_route("/health", routes.get_health, methods=["GET"])
    app.add_api_route("/validate-token", routes.get_validate_token, methods=["GET"])
    app.add_api_route("/beers", routes.get_beers, methods=["GET"])
    app.add_api_route(
        "/beers/upload-url", routes.post_beers_upload_url, methods=["POST"]
    )
    app.add_api_route("/beers/process", routes.post_beers_process, methods=["POST"])

    return app
