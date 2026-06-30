from __future__ import annotations

import functools
import json
from typing import TYPE_CHECKING, cast

import boto3

from .models import Beer
from .settings import Settings

if TYPE_CHECKING:
    from types_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


@functools.cache
def _resource() -> DynamoDBServiceResource:
    return boto3.resource("dynamodb")


def _table(settings: Settings) -> Table:
    return _resource().Table(settings.table_name)


def get_beers(settings: Settings) -> list[Beer]:
    item = _table(settings).get_item(Key={"pk": "current"}).get("Item")
    if item:
        return [
            Beer.model_validate(beer) for beer in json.loads(cast(str, item["beers"]))
        ]
    else:
        return []


def save_beers(beers: list[Beer], settings: Settings) -> None:
    _table(settings).put_item(
        Item={
            "pk": "current",
            "beers": json.dumps([beer.model_dump() for beer in beers]),
        }
    )
