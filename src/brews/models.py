from pydantic import BaseModel


class Beer(BaseModel):
    name: str
    brewery: str | None = None
    style: str | None = None
    abv: float | None = None
    prices: list[int] | None = None


class Extraction(BaseModel):
    beers: list[Beer]
    comments: list[str]


class UploadUrlResponse(BaseModel):
    url: str
    key: str
