from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import db, extract, images, storage
from .models import Beer, Extraction, UploadUrlResponse
from .settings import Settings

security = HTTPBearer()


def get_settings(request: Request) -> Settings:
    return request.state.settings


def validate_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not credentials.credentials == settings.upload_token.get_secret_value():
        raise HTTPException(status_code=401)


def get_health() -> dict[str, str]:
    """Returns the service health status."""
    return {"status": "ok"}


def get_beers(settings: Annotated[Settings, Depends(get_settings)]) -> list[Beer]:
    """Returns all current beers list."""
    return db.get_beers(settings)


def get_validate_token(
    token: str, settings: Annotated[Settings, Depends(get_settings)]
) -> dict[str, str]:
    if token != settings.upload_token.get_secret_value():
        raise HTTPException(status_code=401)
    return {"status": "ok"}


def post_beers_upload_url(
    token: Annotated[str, Depends(validate_token)],
    content_type: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadUrlResponse:
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400)
    return storage.create_upload_url(content_type, settings)


def post_beers_process(
    token: Annotated[str, Depends(validate_token)],
    key: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Extraction | None:
    image = storage.get_image(key, settings)
    image, content_type = images.downscale(image)
    extraction = extract.beers(image, content_type, settings)
    if extraction is not None:
        db.save_beers(extraction.beers, settings)
        return extraction
    else:
        raise HTTPException(status_code=500)
