from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from brews import config, db, extract
from brews.models import Beer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://brews.gadom.ski", "http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["X-Upload-Token", "Content-Type"],
)


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
    expected = config.get_upload_token()
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


handler = Mangum(app)
