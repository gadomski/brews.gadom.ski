from botocore.exceptions import ClientError
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from brews import config, db, extract, images, storage
from brews.models import Beer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://brews.gadom.ski", "http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["X-Upload-Token", "Content-Type"],
)


class UploadUrlRequest(BaseModel):
    """Request body for creating a presigned upload URL."""

    content_type: str


class UploadUrlResponse(BaseModel):
    """A presigned `PUT` URL and the object key to process afterward."""

    url: str
    key: str


class ProcessRequest(BaseModel):
    """Request body for processing a previously uploaded image."""

    key: str


def _require_token(token: str | None) -> None:
    expected = config.get_upload_token()
    if not expected or token != expected:
        raise HTTPException(status_code=401)


@app.get("/api/beers")
def get_beers() -> list[Beer]:
    """Return the current beer list."""
    return db.list_beers()


@app.post("/api/beers/upload-url")
def create_upload_url(
    request: UploadUrlRequest,
    x_upload_token: str | None = Header(default=None),
) -> UploadUrlResponse:
    """Return a presigned `PUT` URL for uploading a photo. Requires the upload token."""
    _require_token(x_upload_token)
    if not request.content_type.startswith("image/"):
        raise HTTPException(status_code=400)
    url, key = storage.create_upload_url(request.content_type)
    return UploadUrlResponse(url=url, key=key)


@app.post("/api/beers/process")
def process_upload(
    request: ProcessRequest,
    x_upload_token: str | None = Header(default=None),
) -> list[Beer]:
    """Read an uploaded photo from S3, extract beers, and replace the list."""
    _require_token(x_upload_token)
    if not request.key.startswith("uploads/"):
        raise HTTPException(status_code=400)
    try:
        image_bytes = storage.get_image(request.key)
    except ClientError:
        raise HTTPException(status_code=404)
    try:
        downscaled, media_type = images.downscale(image_bytes)
    except Exception:
        raise HTTPException(status_code=400)
    try:
        beers = extract.extract_beers(downscaled, media_type)
    except Exception:
        raise HTTPException(status_code=502)
    if not beers:
        raise HTTPException(status_code=422)
    db.replace_beers(beers)
    return db.list_beers()


handler = Mangum(app)
