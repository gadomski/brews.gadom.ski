import json
import os

import boto3

from brews.models import Beer

_PARTITION_VALUE = "current"


def _table():
    return boto3.resource("dynamodb").Table(os.environ["BREWS_TABLE_NAME"])


def list_beers() -> list[Beer]:
    """Return the current beer list, or an empty list if none is stored."""
    item = _table().get_item(Key={"pk": _PARTITION_VALUE}).get("Item")
    if not item:
        return []
    return [Beer(**beer) for beer in json.loads(item["beers"])]


def replace_beers(beers: list[Beer]) -> None:
    """Replace the entire stored beer list with one item."""
    payload = json.dumps([beer.model_dump() for beer in beers])
    _table().put_item(Item={"pk": _PARTITION_VALUE, "beers": payload})
