import boto3
import pytest
from moto import mock_aws

from brews import db
from brews.models import Beer


@pytest.fixture
def table(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("BREWS_TABLE_NAME", "brews-test")
    with mock_aws():
        boto3.client("dynamodb", region_name="us-east-1").create_table(
            TableName="brews-test",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def test_list_is_empty_initially(table):
    assert db.list_beers() == []


def test_replace_then_list_preserves_order(table):
    db.replace_beers([Beer(name="Pils"), Beer(name="Stout", abv=6.2)])
    beers = db.list_beers()
    assert [beer.name for beer in beers] == ["Pils", "Stout"]
    assert beers[1].abv == 6.2


def test_replace_overwrites_previous_list(table):
    db.replace_beers([Beer(name="Old")])
    db.replace_beers([Beer(name="New")])
    assert [beer.name for beer in db.list_beers()] == ["New"]
