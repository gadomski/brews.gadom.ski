import os
import sqlite3

from brews.models import Beer

_SCHEMA = """
CREATE TABLE IF NOT EXISTS beers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    brewery TEXT,
    style TEXT,
    abv REAL,
    price TEXT
)
"""


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(os.environ.get("BREWS_DB_PATH", "brews.db"))
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the beers table if it does not already exist."""
    with _connect() as connection:
        connection.execute(_SCHEMA)


def list_beers() -> list[Beer]:
    """Return the current beer list, ordered as inserted."""
    with _connect() as connection:
        rows = connection.execute(
            "SELECT name, brewery, style, abv, price FROM beers ORDER BY position"
        ).fetchall()
    return [Beer(**dict(row)) for row in rows]


def replace_beers(beers: list[Beer]) -> None:
    """Replace the entire beer list in a single transaction."""
    with _connect() as connection:
        connection.execute("DELETE FROM beers")
        connection.executemany(
            "INSERT INTO beers (position, name, brewery, style, abv, price)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (index, beer.name, beer.brewery, beer.style, beer.abv, beer.price)
                for index, beer in enumerate(beers)
            ],
        )
