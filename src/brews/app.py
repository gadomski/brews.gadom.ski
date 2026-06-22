import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from brews import db, extract
from brews.models import Beer


@asynccontextmanager
async def _lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(lifespan=_lifespan)


@app.get("/api/beers")
def get_beers() -> list[Beer]:
    """Return the current beer list."""
    return db.list_beers()


@app.post("/api/beers/upload")
async def upload_beers(
    file: UploadFile = File(...),
    x_upload_token: str | None = Header(default=None),
) -> list[Beer]:
    """Replace the beer list from an uploaded photo. Requires the upload token."""
    expected = os.environ.get("BREWS_UPLOAD_TOKEN")
    if not expected or x_upload_token != expected:
        raise HTTPException(status_code=401)
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400)
    image_bytes = await file.read()
    try:
        beers = extract.extract_beers(image_bytes, file.content_type)
    except Exception:
        raise HTTPException(status_code=502)
    if not beers:
        raise HTTPException(status_code=422)
    db.replace_beers(beers)
    return db.list_beers()


_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")
