from pydantic import BaseModel


class Beer(BaseModel):
    """A single beer on the list."""

    name: str
    brewery: str | None = None
    style: str | None = None
    abv: float | None = None
    price: str | None = None


class Extraction(BaseModel):
    """The structured result of reading a beer-list photo."""

    beers: list[Beer]
